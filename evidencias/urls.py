from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import EvidenciaViewSet

router = DefaultRouter()
router.register(r'evidencias', EvidenciaViewSet, basename='evidencia')

urlpatterns = [
    path('', include(router.urls)),
]