from django.urls import path

from apps.receipts.views import ReceiptListCreateView, ReceiptRetrieveUpdateDestroyView


urlpatterns = [
    path('receipts/', ReceiptListCreateView.as_view(), name='receipt-list-create'),
    path('receipts/<int:id>/', ReceiptRetrieveUpdateDestroyView.as_view(), name='receipt-detail'),
]