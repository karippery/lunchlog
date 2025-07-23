from apps.receipts.models import Receipt
from apps.receipts.tests.factories import ReceiptFactory
import pytest
from apps.restaurants.tests.factories import RestaurantFactory
from apps.users.tests.factories import UserFactory
from apps.users.models import UserRoles
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ValidationError
import shutil
from pathlib import Path

pytest_plugins = [
    'receipts.tests.fixtures',
    'apps.users.tests.fixtures'
]


@pytest.mark.django_db
class TestReceiptModel:
    """Test Receipt model functionality."""
    
    def test_receipt_creation(self):
        """Test basic receipt creation with all required fields."""
        user = UserFactory()
        restaurant = RestaurantFactory(name="Test Restaurant")
        receipt = Receipt.objects.create(
            user=user,
            date=date.today(),
            price=Decimal('25.99'),
            restaurant=restaurant,
            address="123 Main St",
            image_url="http://example.com/receipt.jpg"
        )
        
        assert receipt.id is not None
        assert receipt.user == user
        assert receipt.date == date.today()
        assert receipt.price == Decimal('25.99')
        assert receipt.restaurant.name == "Test Restaurant"
        assert receipt.address == "123 Main St"
        assert receipt.image_url == "http://example.com/receipt.jpg"
        assert receipt.is_processed is False  # Default value
        assert receipt.created_at is not None
        assert receipt.updated_at is not None
    
    def test_receipt_str_representation(self):
        """Test string representation of receipt."""
        restaurant = RestaurantFactory(name="Test Restaurant")
        receipt = ReceiptFactory(restaurant=restaurant)
        
        # Get the full datetime string as it appears in the model
        expected = f"Receipt #{receipt.id} - Test Restaurant ({restaurant.place_id}) - {receipt.date}"
        assert str(receipt) == expected
    
    def test_receipt_default_values(self):
        """Test receipt default field values."""
        user = UserFactory()
        restaurant = RestaurantFactory(name="Test Restaurant")
        receipt = Receipt.objects.create(
            user=user,
            price=Decimal('10.00'),
            restaurant=restaurant,
            address="123 Main St",
            image_url="http://example.com/receipt.jpg"
        )
        
        assert receipt.date == date.today()  # Default to today
        assert receipt.is_processed is False  # Default to False
    
    def test_receipt_price_validation(self):
        """Test price field validation (minimum value)."""
        user = UserFactory()
        restaurant = RestaurantFactory(name="Test Restaurant")
        # Valid price
        valid_receipt = Receipt(
            user=user,
            price=Decimal('0.01'),
            restaurant=restaurant,
            address="123 Main St",
            image_url="http://example.com/receipt.jpg"
        )
        valid_receipt.full_clean()  # Should not raise
        
        # Invalid negative price
        with pytest.raises(ValidationError):
            invalid_receipt = Receipt(
                user=user,
                price=Decimal('-1.00'),
                restaurant=restaurant,
                address="123 Main St",
                image_url="http://example.com/receipt.jpg"
            )
            invalid_receipt.full_clean()
        
        # Zero price should be valid (MinValueValidator(0))
        zero_receipt = Receipt(
            user=user,
            price=Decimal('0.00'),
            restaurant=restaurant,
            address="123 Main St",
            image_url="http://example.com/receipt.jpg"
        )
        zero_receipt.full_clean()  # Should not raise
    
    def test_receipt_user_relationship(self):
        """Test receipt-user foreign key relationship."""
        user = UserFactory()
        receipt = ReceiptFactory(user=user)
        assert receipt.user == user
        assert receipt in user.receipts.all()
        
        # Test cascade delete
        user_id = user.id
        user.delete()
        assert not Receipt.objects.filter(user_id=user_id).exists()


  

@pytest.mark.django_db
class TestReceiptListCreateView:
    """Test ReceiptListCreateView (ListCreateAPIView)."""
    
    def test_list_receipts_authenticated_user(self, authenticated_guest_client):
        """Test listing receipts for authenticated user."""
        client, user = authenticated_guest_client
        
        # Create receipts for this user and another user
        user_receipts = ReceiptFactory.create_batch(3, user=user)
        other_user_receipts = ReceiptFactory.create_batch(2)
        
        url = reverse('receipt-list-create')  # Adjust URL name as needed
        response = client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 3  # Only user's receipts
        
        receipt_ids = [receipt['id'] for receipt in response.data['results']]
        for receipt in user_receipts:
            assert receipt.id in receipt_ids
        
        # Ensure other user's receipts are not included
        for receipt in other_user_receipts:
            assert receipt.id not in receipt_ids
    
    def test_list_receipts_unauthenticated(self, api_client):
        """Test listing receipts without authentication."""
        ReceiptFactory.create_batch(3)
        
        url = reverse('receipt-list-create')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_receipt_with_image_url(self, authenticated_guest_client):
        """Test creating a new receipt with image_url."""
        client, user = authenticated_guest_client
        restaurant = RestaurantFactory(name="Test Restaurant")
        
        test_data = {
            'date': '2023-01-15',
            'price': '12.50',
            'restaurant': restaurant.id,  # Changed to ID
            'address': '123 Test St',
            'image_url': 'http://example.com/receipt.jpg'
        }
        
        url = reverse('receipt-list-create')
        response = client.post(url, data=test_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Receipt.objects.filter(user=user).count() == 1
        
        created_receipt = Receipt.objects.get(user=user)
        assert created_receipt.restaurant.id == restaurant.id  # Compare IDs
        assert str(created_receipt.price) == test_data['price']
        assert created_receipt.image_url == test_data['image_url']
        assert created_receipt.is_processed is False

    def test_create_receipt_with_image_file(self, authenticated_guest_client, sample_image):
        """Test creating receipt with image file upload."""
        client, user = authenticated_guest_client
        restaurant = RestaurantFactory(name="Test Restaurant")
        
        data = {
            'date': '2023-01-15',
            'price': '15.99',
            'restaurant': restaurant.id,
            'address': '456 Image St',
            'image': sample_image
        }
        
        url = reverse('receipt-list-create')
        response = client.post(url, data, format='multipart')
        
        assert response.status_code == status.HTTP_201_CREATED
        receipt = Receipt.objects.get(user=user)
        assert receipt.image is not None
        assert receipt.image.name.startswith(f'user_{user.id}/')
    
    def test_create_receipt_validation_error(self, authenticated_guest_client):
        """Test creating receipt without image or image_url raises validation error."""
        client, user = authenticated_guest_client
        restaurant = RestaurantFactory(name="Test Restaurant")
        
        data = {
            'date': '2023-01-15',
            'price': '15.99',
            'restaurant': restaurant.id,
            'address': '456 Test St',
            # Missing both image and image_url
        }
        
        url = reverse('receipt-list-create')
        response = client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Either image or image_url must be provided' in str(response.data)
    
    def test_filter_by_month(self, authenticated_guest_client):
        """Test filtering receipts by month parameter."""
        client, user = authenticated_guest_client
        
        # Create receipts in different months
        jan_receipt = ReceiptFactory(
            user=user,
            date=date(2023, 1, 15)
        )
        feb_receipt = ReceiptFactory(
            user=user,
            date=date(2023, 2, 15)
        )
        
        url = reverse('receipt-list-create')
        response = client.get(url, {'month': '2023-01'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        
        receipt_ids = [receipt['id'] for receipt in response.data['results']]
        assert jan_receipt.id in receipt_ids
        assert feb_receipt.id not in receipt_ids
    
    def test_invalid_month_filter(self, authenticated_guest_client):
        """Test invalid month filter format is ignored."""
        client, user = authenticated_guest_client
        
        receipt = ReceiptFactory(user=user)
        
        url = reverse('receipt-list-create')
        response = client.get(url, {'month': 'invalid-month'})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1  # No filtering applied
    
