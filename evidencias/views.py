from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import User
from django.conf import settings

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

import cloudinary.uploader

from .models import EvidenciaProyecto
from .serializers import EvidenciaSerializer


@api_view(['GET'])
@permission_classes([AllowAny])  # health no requiere autenticación
def health(request):
    return Response({'status': 'ok'})


def subir_archivo_cloudinary(archivo):
    """Sube un archivo a Cloudinary y retorna los datos relevantes."""

    import cloudinary
    print("CLOUD NAME:", cloudinary.config().cloud_name)
    print("API KEY:", cloudinary.config().api_key)
    print("API SECRET:", cloudinary.config().api_secret)
    
    resultado = cloudinary.uploader.upload(
        archivo,
        folder='evidencias_proyectos',
        resource_type='auto'
    )
    return {
        'archivo_url': resultado['secure_url'],
        'nombre_archivo': archivo.name,
        'tipo_archivo': archivo.content_type,
        'tamano_archivo': archivo.size,

    
    }


class EvidenciaViewSet(viewsets.ModelViewSet):

    queryset = EvidenciaProyecto.objects.all().order_by('-fecha_registro')
    serializer_class = EvidenciaSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    filterset_fields = ['categoria']
    search_fields = ['titulo', 'proyecto', 'responsable']
    ordering_fields = ['fecha_registro', 'titulo', 'proyecto']

    def create(self, request, *args, **kwargs):
        archivo = request.FILES.get('archivo')

        if not archivo:
            return Response(
                {'error': 'Debe adjuntar un archivo.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validar archivo mediante el serializer antes de subir
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Subir a Cloudinary solo si el serializer es válido
        datos_archivo = subir_archivo_cloudinary(archivo)

        serializer.save(**datos_archivo)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        archivo = request.FILES.get('archivo')

        data = request.data.copy()

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)

        # Si viene archivo nuevo, subirlo a Cloudinary
        if archivo:
            datos_archivo = subir_archivo_cloudinary(archivo)
            serializer.save(**datos_archivo)
        else:
            serializer.save()

        return Response(serializer.data)
    

class GoogleLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')

        if not token:
            return Response(
                {'error': 'Token de Google requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            info = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
        except ValueError:
            return Response(
                {'error': 'Token de Google inválido o expirado.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        email = info.get('email')
        nombre = info.get('given_name', '')
        apellido = info.get('family_name', '')

        user, _ = User.objects.get_or_create(
            username=email,
            defaults={
                'email': email,
                'first_name': nombre,
                'last_name': apellido,
            }
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'email': email,
            'nombre': f'{nombre} {apellido}'.strip(),
        })