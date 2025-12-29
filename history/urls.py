# history/urls.py
from django.urls import path
from .views import (
    CheckReceiverAPIView,
    TransactionAPIView,
    QRScanAPIView,
    HistoryListAPIView,
    RecentTransactionsAPIView,
)

urlpatterns = [
    # Transfer endpoints - These will be under /api/points/
    path('check-receiver/', CheckReceiverAPIView.as_view(), name='check-receiver'),
    path('transfer/', TransactionAPIView.as_view(), name='points-transfer'),
    
    # QR Scan endpoints
    path('qr-scan/', QRScanAPIView.as_view(), name='qr-scan'),
    
    # History endpoints - REMOVE 'history/' prefix since it's already in the main URL
    path('', HistoryListAPIView.as_view(), name='history-list'),  # This will be /api/points/
    path('recent/', RecentTransactionsAPIView.as_view(), name='recent-history'),  # This will be /api/points/recent/
]