# users/urls.py
from django.urls import path
from .views import RegisterAPIView, LoginAPIView, VerifyEmailView, PasswordResetRequestView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register-api'),
    path('login/', LoginAPIView.as_view(), name='login-api'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset-request'),
]