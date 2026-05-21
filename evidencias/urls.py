from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    EvidenciaViewSet,
    GoogleAuthRedirectView,
    GoogleCallbackView,
    GoogleLoginView
)

router = DefaultRouter()
router.register(r'evidencias', EvidenciaViewSet, basename='evidencia')

urlpatterns = [
    
    path('', include(router.urls)),
    
    
    path('auth/google/', GoogleAuthRedirectView.as_view(), name='google-auth-redirect'),
    path('auth/google/callback/', GoogleCallbackView.as_view(), name='google-auth-callback'),
    path('auth/google/login/', GoogleLoginView.as_view(), name='google-login-token'),
]