from django.db.models import TextChoices


class UserRoles(TextChoices):
    ADMIN = 'ADMIN', 'Admin'
    MANAGER = 'MANAGER', 'Manager'
    GUEST = 'GUEST', 'Guest'