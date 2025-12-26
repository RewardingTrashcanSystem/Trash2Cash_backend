from django.urls import path
from .views import RegisterAPIView, LoginAPIView, LogoutAPIView,ProfileAPIView,CheckRegistrationView

urlpatterns = [
    path('check-registration/', CheckRegistrationView.as_view(), name='check-registration'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('profile/', ProfileAPIView.as_view(), name='profile'),
]