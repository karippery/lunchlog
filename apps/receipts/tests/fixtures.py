import os
from apps.users.tests.factories import UserFactory
import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from apps.users.models import UserRoles
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
from django.core.files.storage import default_storage

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


@pytest.fixture
def receipt_data():
    return {
        'date': '2023-01-15',
        'price': '12.50',
        'restaurant': 'Test Restaurant',
        'address': '123 Test St',
        'image_url': 'http://example.com/receipt.jpg'
    }


@pytest.fixture(autouse=True)
def use_local_storage(settings, monkeypatch):
    """Force use of local file storage for all tests."""
    test_media_root = '/tmp/test_media'
    os.makedirs(test_media_root, exist_ok=True)

    # Override Django settings
    settings.DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
    settings.STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
            'OPTIONS': {
                'location': test_media_root,
            }
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        }
    }
    settings.MEDIA_ROOT = test_media_root
    
    # Clear any existing default storage to force reinitialization
    if hasattr(default_storage, '_wrapped'):
        default_storage._wrapped = None
    
    # Monkey patch to ensure local storage is used
    from django.core.files.storage import FileSystemStorage
    local_storage = FileSystemStorage(location=test_media_root)
    monkeypatch.setattr('django.core.files.storage.default_storage', local_storage)

    yield

    # Clean up after test
    shutil.rmtree(test_media_root, ignore_errors=True)

@pytest.fixture
def sample_image():
    """Create a sample image file for testing."""
    from PIL import Image
    import io
    
    # Create a simple 1x1 pixel image
    image = Image.new('RGB', (1, 1), color='red')
    
    # Save to bytes buffer
    image_buffer = io.BytesIO()
    image.save(image_buffer, format='JPEG')
    image_buffer.seek(0)
    
    return SimpleUploadedFile(
        name='sample_receipt.jpg',
        content=image_buffer.getvalue(),
        content_type='image/jpeg'
    )