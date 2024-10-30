from django.urls import path, include
from rest_framework import routers

from best_route.cache import load_fuel_station_data_to_cache


load_fuel_station_data_to_cache()

route = routers.DefaultRouter()


urlpatterns = [
    path("", include(route.urls)),
]
