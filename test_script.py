from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import pandas as pd
import os
from dotenv import load_dotenv
import geopy.distance
from scipy.spatial import cKDTree
import numpy as np

load_dotenv()

app = FastAPI()

# Load the fuel prices data from the new CSV with geolocation data
fuel_prices_df = pd.read_csv('./fuel_stations_with_coords_geo_location.csv')

# Ensure that 'FullAddress' is properly formatted (if needed)
fuel_prices_df['FullAddress'] = fuel_prices_df['Address'] + ', ' + fuel_prices_df['City'] + ', ' + fuel_prices_df['State']
fuel_prices_df['FullAddress'] = fuel_prices_df['FullAddress'].str.replace(r'\s{2,}', ' ', regex=True)


# Build the KDTree once at startup
fuel_coords = np.array(list(zip(fuel_prices_df['Latitude'], fuel_prices_df['Longitude'])))
fuel_tree = cKDTree(fuel_coords)

class RouteRequest(BaseModel):
    start: str
    finish: str

@app.post("/route")
def get_route(data: RouteRequest):
    start = data.start
    finish = data.finish

    # Get multiple routes from MapQuest Directions API
    routes_response = fetch_route_from_mapquest(start, finish)

    # Include the primary route and alternate routes
    route_options = [routes_response['route']]  # Primary route
    alternate_routes = routes_response['route'].get('alternateRoutes', [])
    route_options.extend([alt['route'] for alt in alternate_routes])

    # Initialize variables to store the optimal solution
    optimal_total_cost = float('inf')
    optimal_route = None
    optimal_stops_for_optimal_route = None

    # Iterate over each route option
    for route_option in route_options:
        # Calculate optimal fuel stops and total cost for each route
        optimal_stops = calculate_optimal_stops(route_option)
        if optimal_stops is None:
            continue  # Try the next route option

        total_cost = calculate_total_cost(optimal_stops)

        # Update optimal route if this one is better
        if total_cost < optimal_total_cost:
            optimal_total_cost = total_cost
            optimal_route = route_option
            optimal_stops_for_optimal_route = optimal_stops

    if optimal_route is None:
        # No route found with fuel stations
        return {
            'message': 'No optimal route found with fuel stations within the specified radius.'
        }
    else:
        return {
            'route': optimal_route,
            'optimal_stops': optimal_stops_for_optimal_route,
            'total_cost': optimal_total_cost
        }

def fetch_route_from_mapquest(start, finish):
    mapquest_api_key = os.getenv('key')
    max_routes = 3  # Number of alternative routes you want to fetch (1-5)
    url = f'http://www.mapquestapi.com/directions/v2/alternateroutes?key={mapquest_api_key}&from={start}&to={finish}&maxRoutes={max_routes}'

    response = requests.get(url)
    if response.status_code == 200:
        print("\nRoutes fetched successfully.\n")
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Error fetching routes")

def calculate_optimal_stops(route):
    max_range = 500  # Maximum range of the vehicle in miles
    miles_per_gallon = 10
    optimal_stops = []
    current_miles = 0
    print("Calculating optimal stops...")

    for leg in route['legs']:
        for maneuver in leg['maneuvers']:
            distance = maneuver['distance']  # Distance in miles
            current_miles += distance

            if current_miles >= max_range:
                # Find the cheapest fuel stop near the current location
                stop_location = f"{maneuver['startPoint']['lat']},{maneuver['startPoint']['lng']}"
                optimal_stop = find_cheapest_fuel_stop(stop_location)
                if optimal_stop is None:
                    return None  # Cannot find fuel stop; this route is not viable
                optimal_stops.append(optimal_stop)
                current_miles = 0  # Reset miles after refueling

    return optimal_stops

def find_cheapest_fuel_stop(stop_location):
    stop_lat, stop_lng = map(float, stop_location.split(','))
    radius = 10 / 69  # Approximate conversion from miles to degrees

    # Query the KDTree
    indices = fuel_tree.query_ball_point([stop_lat, stop_lng], radius)
    if not indices:
        print("No fuel stations found within the radius.")
        return None

    nearby_stations = fuel_prices_df.iloc[indices]
    cheapest_station = nearby_stations.loc[nearby_stations['Retail Price'].idxmin()]

    print("Nearby stations found:", len(nearby_stations))
    print("Cheapest station selected:", cheapest_station['Truckstop Name'])

    return {
        'Truckstop Name': cheapest_station['Truckstop Name'],
        'Address': cheapest_station['FullAddress'],
        'Retail Price': cheapest_station['Retail Price'],
        'Latitude': cheapest_station['Latitude'],
        'Longitude': cheapest_station['Longitude']
    }


def calculate_total_cost(stops):
    miles_per_gallon = 10
    total_cost = 0

    # Assume full refuel at each stop
    for stop in stops:
        gallons_needed = 500 / miles_per_gallon  # Full tank refill
        fuel_price = float(stop['Retail Price'])
        total_cost += fuel_price * gallons_needed

    return total_cost
