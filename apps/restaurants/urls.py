from django.urls import path
from .views import RecommendationView

urlpatterns = [
    #GET /api/recommendations?lat=52.5200&lng=13.4050&max_distance=5&price_level=2&limit=4
    path('recommendations/', RecommendationView.as_view(), name='restaurant-recommendations'),
]