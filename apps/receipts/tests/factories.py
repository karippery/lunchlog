import factory
from factory.django import DjangoModelFactory
from apps.users.tests.factories import UserFactory
from ..models import Receipt
from django.utils import timezone


class ReceiptFactory(DjangoModelFactory):
    class Meta:
        model = Receipt

    user = factory.SubFactory(UserFactory)
    date = factory.LazyFunction(timezone.now)
    price = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
    restaurant= factory.Faker('company')
    address = factory.Faker('address')
    image_url = factory.Faker('image_url')