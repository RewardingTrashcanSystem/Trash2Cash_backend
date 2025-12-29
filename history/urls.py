from django.urls import path
from .views import (
    CheckReceiverAPIView,
    TransactionAPIView,
    QRScanAPIView,
    HistoryListAPIView,
    RecentTransactionsAPIView,
)

urlpatterns = [
    # Transfer endpoints
    path('check-receiver/', CheckReceiverAPIView.as_view(), name='check-receiver'),
    path('transfer/', TransactionAPIView.as_view(), name='points-transfer'),
    
    # QR Scan endpoints
    path('qr-scan/', QRScanAPIView.as_view(), name='qr-scan'),
    
    # History endpoints
    path('history/', HistoryListAPIView.as_view(), name='history-list'),
    path('history/recent/', RecentTransactionsAPIView.as_view(), name='recent-history'),
]