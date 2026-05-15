from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [

    path('admin/', admin.site.urls),

    path('api/', include('evidencias.urls')),

    path('api/schema/', SpectacularAPIView.as_view()),

    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(
            url_name='schema'
        ),
    ),

    path(
    'api/token/',
    TokenObtainPairView.as_view(),
),

path(
    'api/token/refresh/',
    TokenRefreshView.as_view(),
),
]