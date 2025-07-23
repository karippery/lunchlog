# receipts/views.py
from apps.receipts.models import Receipt
from apps.receipts.serializers import ReceiptSerializer
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import parsers, filters
from django_filters.rest_framework import DjangoFilterBackend
from datetime import datetime
from django.db.models import Q

from common.pagination import DefaultPagination
from common.permissions import IsReceiptOwner


class ReceiptListCreateView(ListCreateAPIView):
    """
    API endpoint that allows receipts to be viewed or created.
    
    Supports:
    - Filtering by month (YYYY-MM format)
    - Search by restaurant or address
    - Ordering by date, price, or created_at
    - Pagination
    """

    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['restaurant', 'address']
    ordering_fields = ['date', 'price', 'created_at']
    ordering = ['-date', '-created_at']
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        queryset = Receipt.objects.filter(user=self.request.user).select_related('user')
        
        # Filter by month if provided
        month = self.request.query_params.get('month')
        if month:
            try:
                month_date = datetime.strptime(month, '%Y-%m').date()
                queryset = queryset.filter(
                    Q(date__year=month_date.year) &
                    Q(date__month=month_date.month)
                )
            except ValueError:
               pass
                
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, is_processed=False)

class ReceiptRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated, IsReceiptOwner]
    lookup_field = 'id'
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        return Receipt.objects.filter(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.image:
            instance.image.delete()  # Delete from S3
        instance.delete()