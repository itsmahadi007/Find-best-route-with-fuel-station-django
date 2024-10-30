from django.urls import path, include
from rest_framework import routers

from best_route.cache import load_fuel_station_data_to_cache
from best_route.views import OptimalRouteView


load_fuel_station_data_to_cache()

route = routers.DefaultRouter()


urlpatterns = [
    path("", include(route.urls)),
    path('optimal-route/', OptimalRouteView.as_view(), name='optimal-route'),
]
