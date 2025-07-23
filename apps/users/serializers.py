from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from .models import User, UserRoles


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model, exposing email, role"""
    email = serializers.EmailField(
        validators=[EmailValidator(message="Enter a valid email address.")]
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'role')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration with email, password, and optional role."""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        min_length=5
    )
    email = serializers.EmailField(
        required=True,
        validators=[EmailValidator(message="Enter a valid email address.")]
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'role')
        extra_kwargs = {
            'role': {
                'required': False
            }
        }

    def create(self, validated_data):
        """Create a new user with the provided email, password, and role."""
        user = User.objects.create(
            email=validated_data['email'],
            role=validated_data.get('role', UserRoles.GUEST)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer including email and role in the token."""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data