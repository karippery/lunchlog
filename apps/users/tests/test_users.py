from apps.users.tests.factories import UserFactory
import pytest
from apps.users.models import User, UserRoles
from django.urls import reverse
from rest_framework import status

pytest_plugins = ['apps.users.tests.fixtures']

@pytest.mark.django_db
class TestUserRegistration:
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        self.client = api_client
        self.url = reverse('register')
        self.valid_payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'role': UserRoles.GUEST
        }

    def test_register_valid_user(self):
        response = self.client.post(self.url, self.valid_payload)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email=self.valid_payload['email']).exists()
        user = User.objects.get(email=self.valid_payload['email'])
        assert user.check_password(self.valid_payload['password'])
        assert user.role == self.valid_payload['role']

    def test_register_invalid_email(self):
        invalid_payload = self.valid_payload.copy()
        invalid_payload['email'] = 'invalid-email'
        response = self.client.post(self.url, invalid_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_register_missing_password(self):
        invalid_payload = self.valid_payload.copy()
        del invalid_payload['password']
        response = self.client.post(self.url, invalid_payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data


@pytest.mark.django_db
class TestUserListView:
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        self.client = api_client
        self.url = reverse('user-list')

    def test_list_users_unauthenticated(self):
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_users_as_guest(self, authenticated_guest_client):
        client, user = authenticated_guest_client
        UserFactory.create_batch(3, role=UserRoles.GUEST)
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == user.id

    def test_list_users_as_admin(self, authenticated_admin_client):
        client, user = authenticated_admin_client
        UserFactory.create_batch(3, role=UserRoles.GUEST)
        response = client.get(self.url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 4  # Admin + 3 guests

    def test_filter_users_by_role(self, authenticated_admin_client):
        client, user = authenticated_admin_client
        UserFactory.create(role=UserRoles.GUEST)
        UserFactory.create(role=UserRoles.ADMIN)
        response = client.get(self.url, {'role': UserRoles.GUEST})
        assert response.status_code == status.HTTP_200_OK
        assert all(u['role'] == UserRoles.GUEST for u in response.data['results'])

    def test_search_users_by_email(self, authenticated_admin_client):
        client, user = authenticated_admin_client
        target_user = UserFactory.create(email='unique@example.com')
        response = client.get(self.url, {'search': 'unique@example'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['email'] == target_user.email


@pytest.mark.django_db
class TestUserRetrieveUpdateDeleteView:
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        self.client = api_client

    def test_retrieve_own_data_as_guest(self, authenticated_guest_client):
        client, user = authenticated_guest_client
        url = reverse('user-detail', kwargs={'pk': user.id})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email

    def test_retrieve_other_user_as_guest(self, authenticated_guest_client):
        client, user = authenticated_guest_client
        other_user = UserFactory.create()
        url = reverse('user-detail', kwargs={'pk': other_user.id})
        response = client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_user_as_admin(self, authenticated_admin_client):
        client, user = authenticated_admin_client
        other_user = UserFactory.create()
        url = reverse('user-detail', kwargs={'pk': other_user.id})
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_update_own_data_as_guest(self, authenticated_guest_client):
        client, user = authenticated_guest_client
        url = reverse('user-detail', kwargs={'pk': user.id})
        payload = {'email': 'newemail@example.com'}
        response = client.patch(url, payload)
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == payload['email']

    def test_delete_user_as_admin(self, authenticated_admin_client):
        client, user = authenticated_admin_client
        target_user = UserFactory.create()
        url = reverse('user-detail', kwargs={'pk': target_user.id})
        response = client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(id=target_user.id).exists()

    def test_delete_user_as_guest(self, authenticated_guest_client):
        client, user = authenticated_guest_client
        url = reverse('user-detail', kwargs={'pk': user.id})
        response = client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert User.objects.filter(id=user.id).exists()


@pytest.mark.django_db
class TestAuthentication:
    @pytest.fixture(autouse=True)
    def setup(self, api_client):
        self.client = api_client
        self.url = reverse('token_obtain_pair')

    def test_successful_login(self, guest_user):
        guest_user.set_password('testpass123')
        guest_user.save()
        payload = {
            'email': guest_user.email,
            'password': 'testpass123'
        }
        response = self.client.post(self.url, payload, format='json')
        assert response.status_code == status.HTTP_200_OK, response.json()

    def test_invalid_credentials(self):
        payload = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.url, payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
