from jsonschema import ValidationError
import pytest
from django.contrib.gis.geos import Point
from django.core.cache import cache
from rest_framework import status

from apps.restaurants.models import Restaurant
from apps.restaurants.serializers import RecommendationSerializer, RestaurantSerializer
from apps.restaurants.services.recommendation_service import RecommendationService
from apps.restaurants.tests.factories import RestaurantFactory

pytest_plugins = [
    'apps.users.tests.fixtures',
    'pytest_mock'
]

# Test Restaurant Model
@pytest.mark.django_db
def test_restaurant_model_creation():
    restaurant = RestaurantFactory.create(
        name="Test Restaurant",
        cuisine_types=['Italian', 'Mediterranean'],
        rating=4.5,
        price_level=3
    )
    
    assert restaurant.place_id
    assert restaurant.name == "Test Restaurant"
    assert restaurant.cuisine_types == ['Italian', 'Mediterranean']
    assert restaurant.rating == 4.5
    assert restaurant.price_level == 3
    assert str(restaurant) == f"Test Restaurant ({restaurant.place_id})"


# Test RecommendationService
@pytest.mark.django_db
def test_recommendation_service_no_restaurants(guest_user):
    service = RecommendationService(
        user=guest_user,
        lat=52.5200,
        lng=13.4050,
        max_distance_km=5
    )
    
    recommendations = service.get_recommendations(limit=10)
    assert len(recommendations) == 0

@pytest.mark.django_db
def test_recommendation_service_with_restaurants(guest_user):
    # Create test restaurants
    RestaurantFactory.create(
        location=Point(13.4050, 52.5200),
        cuisine_types=['Italian'],
        rating=4.5,
        price_level=2
    )
    RestaurantFactory.create(
        location=Point(13.4060, 52.5210),
        cuisine_types=['Mexican'],
        rating=4.0,
        price_level=2
    )
    
    service = RecommendationService(
        user=guest_user,
        lat=52.5200,
        lng=13.4050,
        max_distance_km=5,
        price_level=2
    )
    
    recommendations = service.get_recommendations(limit=2)
    assert len(recommendations) <= 2
    assert all(r.price_level == 2 for r in recommendations)
    assert all(r.location.distance(Point(13.4050, 52.5200)) <= 5 for r in recommendations)

@pytest.mark.django_db
def test_recommendation_service_cuisine_preference(guest_user, mocker):
    # Mock user cuisine preferences
    mocker.patch(
        'apps.restaurants.services.recommendation_service.RecommendationService.get_user_top_cuisines',
        return_value=['Italian']
    )
    
    # Create restaurants
    italian_restaurant = RestaurantFactory.create(
        location=Point(13.4050, 52.5200),
        cuisine_types=['Italian'],
        rating=4.0
    )
    mexican_restaurant = RestaurantFactory.create(
        location=Point(13.4050, 52.5200),
        cuisine_types=['Mexican'],
        rating=4.5
    )
    
    service = RecommendationService(
        user=guest_user,
        lat=52.5200,
        lng=13.4050,
        max_distance_km=5
    )
    
    recommendations = service.get_recommendations(limit=2)
    assert recommendations[0].id == italian_restaurant.id  # Italian should come first due to preference

# # Test RecommendationView API
@pytest.mark.django_db
def test_recommendation_view_missing_params(authenticated_guest_client):
    client, _ = authenticated_guest_client
    response = client.get('/api/v1/recommendations/')
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['error'] == 'lat and lng parameters are required'

@pytest.mark.django_db
def test_recommendation_view_invalid_params(authenticated_guest_client):
    client, _ = authenticated_guest_client
    response = client.get('/api/v1/recommendations/?lat=invalid&lng=13.4050')
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'Invalid parameters' in response.json()['error']

@pytest.mark.django_db
def test_recommendation_view_success(authenticated_guest_client):
    client, user = authenticated_guest_client
    
    # Create test restaurant
    RestaurantFactory.create(
        location=Point(13.4050, 52.5200),
        cuisine_types=['Italian'],
        rating=4.5,
        price_level=2
    )
    
    response = client.get('/api/v1/recommendations/?lat=52.5200&lng=13.4050&max_distance=5&price_level=2&limit=1')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['total_count'] == 1
    assert len(response.json()['recommendations']) == 1
    assert response.json()['location'] == '52.5200, 13.4050'
    assert response.json()['max_distance_km'] == 5.0
    assert response.json()['price_level_filter'] == 2

@pytest.mark.django_db
def test_recommendation_view_cache(authenticated_guest_client, mocker):
    client, user = authenticated_guest_client
    cache_key = f"rec_{user.id}_52.5200_13.4050_5_2_1"
    
    # Mock cache
    cached_data = {
        'recommendations': [],
        'total_count': 0,
        'location': '52.5200, 13.4050',
        'max_distance_km': 5.0,
        'price_level_filter': 2,
        'user_preferences': []
    }
    cache.set(cache_key, cached_data, 300)
    
    response = client.get('/api/v1/recommendations/?lat=52.5200&lng=13.4050&max_distance=5&price_level=2&limit=1')
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == cached_data
    
@pytest.mark.django_db
def test_recommendation_serializer():
    restaurant = RestaurantFactory.create(
        location=Point(13.4050, 52.5200),
        cuisine_types=['Italian', 'Pizza'],
        rating=4.5
    )

    data = {
        'recommendations': [restaurant],
        'total_count': 1,
        'location': '52.5200, 13.4050',
        'max_distance_km': 5.0,
        'price_level_filter': 2,
        'user_preferences': ['Italian']
    }

    serializer = RecommendationSerializer(instance=data)
    serialized = serializer.data

    rec = serialized['recommendations'][0]
    assert rec['cuisine_display'] == 'Italian, Pizza'
    assert float(rec['latitude']) == 52.5200
    assert float(rec['longitude']) == 13.4050