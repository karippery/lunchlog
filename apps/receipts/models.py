from datetime import date
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models import Q

from config.storage_backends import ReceiptImageStorage



def receipt_image_path(instance, filename):
    return f"user_{instance.user.id}/{timezone.now().strftime('%Y/%m/%d')}/{filename}"

class Receipt(models.Model):
    """Model representing a lunch receipt with associated metadata."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='receipts'
    )
    date = models.DateField(default=date.today)
    price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    validators=[MinValueValidator(0)],
    help_text="Price of the receipt in decimal format"
    )
    address = models.TextField()
    is_processed = models.BooleanField(default=False)
    restaurant = models.TextField()
    
    # For direct image upload
    image = models.ImageField(
        upload_to=receipt_image_path,
        storage=ReceiptImageStorage(),
        blank=True,
        null=True,
        help_text="Receipt image file"
    )
    
    # Keep URL field for cases where image is hosted elsewhere
    image_url = models.URLField(max_length=1024, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['user', '-date']),
        ]
    
    def __str__(self):
        return f"Receipt #{self.id} - {self.restaurant} - {self.date}"
    