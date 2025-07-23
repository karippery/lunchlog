from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.core.cache import cache
from django.db import connection
from apps.restaurants.models import Restaurant

class RecommendationService:
    """
    Generates restaurant recommendations for a user based on location,
    cuisine preferences, distance, and price level.

    - Caches top cuisines from user's receipt history.
    - Filters and ranks restaurants by proximity, rating, and match with preferences.
    - Uses PostGIS for geospatial filtering and efficient queries.
    """

    def __init__(self, user, lat, lng, max_distance_km=10, price_level=None):
        self.user = user
        self.user_location = Point(float(lng), float(lat))
        self.max_distance_km = float(max_distance_km)
        self.price_level = price_level

    def get_user_top_cuisines(self, limit=5):
        cache_key = f"user_cuisines_{self.user.id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        top_cuisines = self.get_top_cuisines_from_db(self.user.id, limit)
        cache.set(cache_key, top_cuisines, 3600)
        return top_cuisines

    @staticmethod
    def get_top_cuisines_from_db(user_id, limit=5):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT unnest(restaurant.cuisine_types) AS cuisine, COUNT(*) as count
                FROM receipts_receipt AS receipt
                JOIN restaurants_restaurant AS restaurant ON receipt.restaurant_id = restaurant.id
                WHERE receipt.user_id = %s
                GROUP BY cuisine
                ORDER BY count DESC
                LIMIT %s;
            """, [user_id, limit])
            return [row[0] for row in cursor.fetchall()]

    def get_recommendations(self, limit=20):
        """Get restaurant recommendations"""
        user_cuisines = self.get_user_top_cuisines()

        base_queryset = Restaurant.objects.filter(
            location__isnull=False,
            location__distance_lte=(self.user_location, D(km=self.max_distance_km))
        )

        if self.price_level is not None:
            base_queryset = base_queryset.filter(price_level=self.price_level)

        base_queryset = base_queryset.annotate(distance=Distance('location', self.user_location))

        if user_cuisines:
            preferred = (
                base_queryset.filter(cuisine_types__overlap=user_cuisines)
                .order_by('-rating', 'distance')
            )
            preferred_ids = list(preferred.values_list('id', flat=True)[:limit // 2])
            preferred_restaurants = list(preferred.filter(id__in=preferred_ids))

            other = (
                base_queryset.exclude(id__in=preferred_ids)
                .filter(rating__gte=3.5)
                .order_by('-rating', 'distance')[:limit - len(preferred_restaurants)]
            )

            results = preferred_restaurants + list(other)
        else:
            results = list(
                base_queryset.filter(rating__gte=3.5)
                .order_by('-rating', 'distance')[:limit]
            )

        return results[:limit]
