from django.core.cache import cache
from .models import FuelStationModel


def load_fuel_station_data_to_cache():
    if cache.get("all_fuel_stations"):
        print("Data already in cache")
        return  # Data already in cache

    all_fuel_stations = FuelStationModel.objects.all()
    cache.set("all_fuel_stations", all_fuel_stations)
    print(
        f"Successfully loaded {len(all_fuel_stations)} rows of fuel station data to cache"
    )
    