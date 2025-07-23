from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.receipts.models import Receipt
from apps.receipts.tasks import fetch_and_store_restaurant

@receiver(post_save, sender=Receipt)
def trigger_restaurant_fetch(sender, instance, created, **kwargs):
    if created:
        fetch_and_store_restaurant.delay(instance.id)
