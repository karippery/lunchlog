import factory
from django.contrib.gis.geos import Point

from apps.restaurants.models import Restaurant
from apps.users.models import User
from apps.users.roles import UserRoles

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
        skip_postgeneration_save = True
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'defaultpassword')
    role = UserRoles.GUEST

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