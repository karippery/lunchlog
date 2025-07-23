from apps.restaurants.models import Restaurant
from rest_framework import serializers

class RestaurantSerializer(serializers.ModelSerializer):
    distance_km = serializers.SerializerMethodField()
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    cuisine_display = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = [
            'place_id', 'name', 'address', 'cuisine_types', 'cuisine_display',
            'rating', 'price_level', 'latitude', 'longitude', 'website',
            'phone_number', 'distance_km'
        ]

    def get_distance_km(self, obj):
        """Get distance in kilometers if annotated"""
        if hasattr(obj, 'distance'):
            return round(obj.distance.km, 2)
        return None

    def get_latitude(self, obj):
        """Extract latitude from PostGIS Point field"""
        return obj.location.y if obj.location else None

    def get_longitude(self, obj):
        """Extract longitude from PostGIS Point field"""
        return obj.location.x if obj.location else None

    def get_cuisine_display(self, obj):
        """Display cuisines as comma-separated string"""
        return ", ".join(obj.cuisine_types) if obj.cuisine_types else "Various"


class RecommendationSerializer(serializers.Serializer):
    """Serializer for the complete recommendation response"""
    
    recommendations = RestaurantSerializer(many=True)
    total_count = serializers.IntegerField()
    location = serializers.CharField()
    max_distance_km = serializers.FloatField(required=False)
    price_level_filter = serializers.IntegerField(required=False, allow_null=True)
    user_preferences = serializers.ListField(
        child=serializers.CharField(), 
        required=False
    )

    def validate(self, data):
        # Skip validation for existing restaurants in recommendations
        if 'recommendations' in data:
            for rec in data['recommendations']:
                if 'place_id' in rec:
                    rec.pop('place_id', None)
        return data

