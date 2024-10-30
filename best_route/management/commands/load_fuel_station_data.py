import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Load Fuel Station Data"

    def handle(self, *args, **options):
        csv_file = "csv_files/fuel_stations_with_coords_geo_location.csv"

        if not os.path.exists(csv_file):
            print(f"File {csv_file} does not exist")
            return

        try:
            df = pd.read_csv(csv_file)
            from best_route.models import FuelStationModel

            with transaction.atomic():
                fuel_stations = [
                    FuelStationModel(
                        truckstop_id=row["OPIS Truckstop ID"],
                        truckstop_name=row["Truckstop Name"],
                        address=row["Address"],
                        city=row["City"],
                        state=row["State"],
                        rack_id=row["Rack ID"],
                        retail_price=row["Retail Price"],
                        full_address=row["FullAddress"],
                        latitude=row["Latitude"],
                        longitude=row["Longitude"],
                    )
                    for _, row in df.iterrows()
                ]
                FuelStationModel.objects.bulk_create(fuel_stations)

                print(
                    f"Successfully loaded {len(fuel_stations)} rows of fuel station data"
                )

        except Exception as e:
            print(f"Error loading data: {str(e)}")
