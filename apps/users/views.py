from rest_framework import generics, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from common.pagination import DefaultPagination
from common.permissions import IsAdminToDelete, IsSelfOrAdmin
from django_filters.rest_framework import DjangoFilterBackend
from apps.users.models import User
from apps.users.serializers import UserSerializer, RegisterSerializer
from apps.users.roles import UserRoles


class RegisterView(generics.CreateAPIView):
    """Open endpoint for user registration. No authentication required."""
    serializer_class = RegisterSerializer
    authentication_classes = []
    permission_classes = [AllowAny]


class UserListView(generics.ListAPIView):
    """
    List users:
    - Admins see all
    - Guests only see themselves
    """
    serializer_class = UserSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role']
    search_fields = ['email']
    ordering_fields = ['id', 'email', 'role']
    ordering = ['-id']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        user = self.request.user
        base_qs = User.objects.only('id', 'email', 'role').order_by('-id')
        if user.role == UserRoles.GUEST.value:
            return base_qs.filter(id=user.id)
        return base_qs


class UserRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user:
    - Guests can only access themselves
    - Admins can update/delete anyone
    """
    queryset = User.objects.only('id', 'email', 'role')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsSelfOrAdmin, IsAdminToDelete]

    def get_object(self):
        obj = super().get_object()
        user = self.request.user
        if user.role == UserRoles.GUEST.value and obj.id != user.id:
            raise PermissionDenied("Guests can only access their own data.")
        return obj
