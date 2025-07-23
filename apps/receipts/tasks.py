import logging
from apps.restaurants.services.google_place_services import GooglePlacesService
from celery import shared_task
from apps.receipts.models import Receipt
from apps.restaurants.models import Restaurant
from django.db import transaction
from requests.exceptions import RequestException
from django.contrib.gis.geos import Point

logger = logging.getLogger(__name__)

@shared_task(bind=True, autoretry_for=(RequestException,), retry_backoff=True, retry_kwargs={'max_retries': 3})
def fetch_and_store_restaurant(self, receipt_id):
    try:
        receipt = Receipt.objects.select_related('restaurant').get(id=receipt_id)
        if receipt.restaurant:
            return

        service = GooglePlacesService()
        result = service.search_text(receipt.restaurant,receipt.address)

        if not result or 'results' not in result or not result['results']:
            receipt.is_processed = True
            receipt.save()
            return

        data = result['results'][0]

        place_id = data.get('place_id')
        name = data.get('name')
        address = data.get('formatted_address')
        location_data = data.get('geometry', {}).get('location', {})
        latitude = location_data.get('lat')
        longitude = location_data.get('lng')
        rating = data.get('rating')
        price_level = data.get('price_level')
        types = data.get('types', [])
        website = data.get('website', None)
        phone_number = data.get('formatted_phone_number', None)
        hours = data.get('opening_hours', None)

        # Create Point from longitude and latitude if present
        location_point = None
        if latitude is not None and longitude is not None:
            location_point = Point(float(longitude), float(latitude))  # Point(x=lng, y=lat)

        with transaction.atomic():
            restaurant, _ = Restaurant.objects.update_or_create(
                place_id=place_id,
                defaults={
                    'name': name,
                    'address': address,
                    'cuisine_types': types,
                    'rating': rating,
                    'price_level': price_level,
                    'location': location_point,
                    'website': website,
                    'phone_number': phone_number,
                    'hours': hours,
                }
            )
            receipt.restaurant = restaurant
            receipt.is_processed = True
            receipt.save()

    except Receipt.DoesNotExist:
        logger.warning(f"Receipt {receipt_id} does not exist")
    except Exception as e:
        logger.error(f"Task failed for receipt {receipt_id}: {e}")
        raise self.retry(exc=e)