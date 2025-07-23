import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.roles import UserRoles
from apps.users.tests.factories import UserFactory


@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def admin_user(db):
    return UserFactory.create(role=UserRoles.ADMIN)

@pytest.fixture
def guest_user(db):
    return UserFactory.create(role=UserRoles.GUEST)

@pytest.fixture
def authenticated_guest_client(api_client, guest_user):
    refresh = RefreshToken.for_user(guest_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client, guest_user

@pytest.fixture
def authenticated_admin_client(api_client, admin_user):
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client, admin_user