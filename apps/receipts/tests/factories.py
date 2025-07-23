import factory
from factory.django import DjangoModelFactory
from apps.restaurants.models import Restaurant
from apps.users.tests.factories import UserFactory
from ..models import Receipt
from django.utils import timezone
from django.contrib.gis.geos import Point


class RestaurantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Restaurant
    
    place_id = factory.Sequence(lambda n: f'place_{n}')
    name = factory.Faker('company')
    address = factory.Faker('address')
    cuisine_types = ['Italian', 'Pizza']
    rating = 4.0
    price_level = 2
    location = Point(13.4050, 52.5200)
    website = factory.Faker('url')
    phone_number = factory.Faker('msisdn')   

class ReceiptFactory(DjangoModelFactory):
    class Meta:
        model = Receipt

    user = factory.SubFactory(UserFactory)
    date = factory.LazyFunction(timezone.now)
    price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    restaurant= factory.SubFactory(RestaurantFactory)
    address = factory.Faker('address')
    image_url = factory.Faker('image_url')

