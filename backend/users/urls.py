# backend/users/urls.py

from django.urls import path
from users.views import RegisterAPIView, LoginAPIView, VerifyEmailView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
]