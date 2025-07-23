from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.users.views import (
    UserListView,
    UserRetrieveUpdateDeleteView,
    RegisterView
)
from apps.users.serializers import CustomTokenObtainPairSerializer

urlpatterns = [
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserRetrieveUpdateDeleteView.as_view(), name='user-detail'),
    path('auth/login/', TokenObtainPairView.as_view(
        serializer_class=CustomTokenObtainPairSerializer
    ), name='token_obtain_pair'),
    path('auth/register/', RegisterView.as_view(), name='register'),
]
