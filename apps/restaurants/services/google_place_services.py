import requests
import logging

from config import settings

logger = logging.getLogger(__name__)

class GooglePlacesService:
    def __init__(self):
        self.api_key = getattr(settings, 'GOOGLE_PLACES_API_KEY', None)
        self.text_search_url = 'https://places.googleapis.com/v1/places:searchText'

    def search_text(self, query):
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': self.api_key,
            'X-Goog-FieldMask': 'places.displayName,places.formattedAddress,places.priceLevel,places.rating,places.location,places.id'
        }
        payload = {"textQuery": query}
        try:
            response = requests.post(self.text_search_url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Google Places API error: {e}")
            return None


    
    
    