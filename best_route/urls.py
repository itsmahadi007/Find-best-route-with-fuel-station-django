from django.urls import path, include
from rest_framework import routers

from best_route.views import OptimalRouteView



route = routers.DefaultRouter()


urlpatterns = [
    path("", include(route.urls)),
    path('optimal-route/', OptimalRouteView.as_view(), name='optimal-route'),
]
