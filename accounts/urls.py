from django.urls import path
from rest_framework.routers import DefaultRouter
from accounts.auth_views import LoginAPIView, RegisterAPIView
from accounts.views import UserViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
	path('auth/register/', RegisterAPIView.as_view(), name='auth_register'),
	path('auth/login/', LoginAPIView.as_view(), name='auth_login'),
] + router.urls