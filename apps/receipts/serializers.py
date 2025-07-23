# receipts/serializers.py
from datetime import datetime
from decimal import Decimal
from rest_framework import serializers
from .models import Receipt

class ReceiptSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Receipt
        fields = [
            'id', 'user', 'date', 'price', 'address',
            'image', 'image_url', 'created_at', 'updated_at',
            'is_processed', 'restaurant'
        ]
        read_only_fields = ['user', 'is_processed', 'created_at', 'updated_at']
        extra_kwargs = {
            'image': {'required': False},
            'image_url': {'required': False},
        }
    
    def validate(self, data):
        """
        Validate that either image or image_url is provided.
        """
        if not data.get('image') and not data.get('image_url'):
            raise serializers.ValidationError("Either image or image_url must be provided")
        return data

    def validate_price(self, value):
        """Ensure price is properly converted to Decimal."""
        if isinstance(value, str):
            try:
                return Decimal(value)
            except (TypeError, ValueError):
                raise serializers.ValidationError("Price must be a valid decimal number.")
        return value
    
    def validate_date(self, value):
        """Ensure date is properly parsed."""
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                raise serializers.ValidationError("Date must be in YYYY-MM-DD format.")
        return value
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
    

class ReceiptUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = [
            'id', 'date', 'price', 'restaurant', 'address',
            'image', 'image_url'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']