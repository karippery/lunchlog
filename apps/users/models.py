from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models
from apps.users.roles import UserRoles



class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(
        max_length=50,
        choices=UserRoles.choices,
        default=UserRoles.GUEST
    )

    def __str__(self):
        return self.email
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

