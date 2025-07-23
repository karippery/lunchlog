from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.gis.db import models as gis_models

class Restaurant(models.Model):
    place_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    address = models.TextField()
    cuisine_types = ArrayField(
        models.CharField(max_length=50),
        blank=True,
        default=list
    )
    rating = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    price_level = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(4)]
    )
    
    location = gis_models.PointField(geography=True, null=True, blank=True) 
    
    website = models.URLField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    hours = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['place_id']),
            models.Index(fields=['name']),
            models.Index(fields=['cuisine_types']),
            models.Index(fields=['rating']),
            gis_models.Index(fields=["location"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.place_id})"
    
