# history/urls.py
from django.urls import path
from .views import HistoryListAPIView, TransactionAPIView

urlpatterns = [
    path('history/', HistoryListAPIView.as_view(), name='history-list'),
    path('transaction/', TransactionAPIView.as_view(), name='transaction'),
]
