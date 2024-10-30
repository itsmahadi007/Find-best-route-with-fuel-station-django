from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.permissions import AllowAny
from best_route.utils import RouteManagement



class OptimalRouteView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RouteRequestSerializer(data=request.data)
        if serializer.is_valid():
            start = serializer.validated_data['start']
            finish = serializer.validated_data['finish']
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Get multiple routes from MapQuest Directions API
        print("Fetching routes from MapQuest Directions API")
        route_management = RouteManagement()
        print("Routes fetched from MapQuest Directions API")
        routes_response = route_management.fetch_route_from_mapquest(start, finish)
        print("Routes processed")

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
            print("Calculating optimal fuel stops and total cost for each route")
            optimal_stops = route_management.calculate_optimal_stops(route_option)
            if optimal_stops is None:
                continue  # Try the next route option

            total_cost = route_management.calculate_total_cost(optimal_stops)
            print("Total cost calculated")
            # Update optimal route if this one is better
            if total_cost < optimal_total_cost:
                optimal_total_cost = total_cost
                optimal_route = route_option
                optimal_stops_for_optimal_route = optimal_stops

        if optimal_route is None:
            return Response({
                'message': 'No optimal route found with fuel stations within the specified radius.'
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'route': optimal_route,
                'optimal_stops': optimal_stops_for_optimal_route,
                'total_cost': optimal_total_cost
            }, status=status.HTTP_200_OK)


# Serializer for RouteRequest
class RouteRequestSerializer(serializers.Serializer):
    start = serializers.CharField(required=True)
    finish = serializers.CharField(required=True)
