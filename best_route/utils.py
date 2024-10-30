
from http.client import HTTPException
import os
import requests
from django.core.cache import cache

from backend.settings import API_KEY
from best_route.models import FuelStationModel
from scipy.spatial import cKDTree
import numpy as np

# Get fuel stations from cache

    
class RouteManagement:
    def __init__(self):
        self.mapquest_api_key = API_KEY
        self.fuel_prices_df = self.get_fuel_stations_from_cache()
        self.fuel_tree = self.build_fuel_tree()
        
        
        
    def get_fuel_stations_from_cache(self):
        all_fuel_stations = cache.get("all_fuel_stations")
        if all_fuel_stations:
            print(f"Fuel stations already cached: {len(all_fuel_stations)} rows")
            return all_fuel_stations
        else:
            all_fuel_stations = FuelStationModel.objects.all()
            cache.set("all_fuel_stations", all_fuel_stations)
            print(f"Fuel stations cached: {len(all_fuel_stations)} rows")
            return all_fuel_stations

    
    def build_fuel_tree(self):
        # Convert Django queryset objects to coordinates array
        fuel_coords = np.array([(station.latitude, station.longitude) for station in self.fuel_prices_df])
        return cKDTree(fuel_coords)
    
    def fetch_route_from_mapquest(self, start, finish):
        max_routes = 3  # Number of alternative routes you want to fetch (1-5)
        url = f'http://www.mapquestapi.com/directions/v2/alternateroutes?key={self.mapquest_api_key}&from={start}&to={finish}&maxRoutes={max_routes}'

        response = requests.get(url)
        if response.status_code == 200:
            print("\nRoutes fetched successfully.\n")
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail="Error fetching routes")

    def calculate_optimal_stops(self, route):
        max_range = 500  # Maximum range of the vehicle in miles
        miles_per_gallon = 10
        optimal_stops = []
        current_miles = 0
        for leg in route['legs']:
            for maneuver in leg['maneuvers']:
                distance = maneuver['distance']  # Distance in miles
                current_miles += distance

                if current_miles >= max_range:
                    # Find the cheapest fuel stop near the current location
                    stop_location = f"{maneuver['startPoint']['lat']},{maneuver['startPoint']['lng']}"
                    optimal_stop = self.find_cheapest_fuel_stop(stop_location)
                    if optimal_stop is None:
                        return None  # Cannot find fuel stop; this route is not viable
                    optimal_stops.append(optimal_stop)
                    current_miles = 0  # Reset miles after refueling

        return optimal_stops

    def find_cheapest_fuel_stop(self, stop_location):
        stop_lat, stop_lng = map(float, stop_location.split(','))
        radius = 10 / 69  # Approximate conversion from miles to degrees

        # Query the KDTree
        indices = self.fuel_tree.query_ball_point([stop_lat, stop_lng], radius)
        if not indices:
            print("No fuel stations found within the radius.")
            return None

        # Get nearby stations from the Django queryset using indices
        nearby_stations = [self.fuel_prices_df[i] for i in indices]
        
        # Find cheapest station
        cheapest_station = min(nearby_stations, key=lambda x: x.retail_price)

        print("Nearby stations found:", len(nearby_stations))
        print("Cheapest station selected:", cheapest_station.truckstop_name)

        return {
            'Truckstop Name': cheapest_station.truckstop_name,
            'Address': f"{cheapest_station.address}, {cheapest_station.city}, {cheapest_station.state}",
            'Retail Price': cheapest_station.retail_price,
            'Latitude': cheapest_station.latitude, 
            'Longitude': cheapest_station.longitude
        }


    def calculate_total_cost(self, stops):
        miles_per_gallon = 10
        total_cost = 0

        # Assume full refuel at each stop
        for stop in stops:
            gallons_needed = 500 / miles_per_gallon  # Full tank refill
            fuel_price = float(stop['Retail Price'])
            total_cost += fuel_price * gallons_needed

        return total_cost
