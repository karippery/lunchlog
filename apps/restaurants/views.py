from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiParameter
from apps.restaurants.serializers import RecommendationSerializer
from apps.restaurants.services.recommendation_service import RecommendationService
from common.pagination import DefaultPagination

class RecommendationView(ListAPIView):
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    serializer_class = RecommendationSerializer

    def list(self, request, *args, **kwargs):
        # Get required parameters
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        
        if not lat or not lng:
            return Response({
                "error": "lat and lng parameters are required"
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get optional parameters
        max_distance = request.query_params.get('max_distance', 10)
        price_level = request.query_params.get('price_level')
        limit = min(int(request.query_params.get('limit', 20)), 50)

        try:
            # Check cache first
            cache_key = f"rec_{request.user.id}_{lat}_{lng}_{max_distance}_{price_level}_{limit}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                return Response(cached_result)

            # Get recommendations
            service = RecommendationService(
                user=request.user,
                lat=float(lat),
                lng=float(lng),
                max_distance_km=float(max_distance),
                price_level=int(price_level) if price_level else None
            )
            
            restaurants = service.get_recommendations(limit)
            
            if not restaurants:
                return Response({
                    "message": "No restaurants found",
                    "recommendations": []
                }, status=status.HTTP_200_OK)

            # Prepare response data
            user_cuisines = service.get_user_top_cuisines()
            
            result = {
                "recommendations": restaurants,
                "total_count": len(restaurants),
                "location": f"{lat}, {lng}",
                "max_distance_km": float(max_distance),
                "price_level_filter": int(price_level) if price_level else None,
                "user_preferences": user_cuisines
            }
            
            # Serialize the complete response
            serializer = self.get_serializer(result)
            response_data = serializer.data
            
            # Cache for 5 minutes
            cache.set(cache_key, response_data, 300)
            
            return Response(response_data)

        except ValueError as e:
            return Response({
                "error": f"Invalid parameters: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                "error": "Something went wrong"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)