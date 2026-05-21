from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth.models import User
from django.conf import settings
from django.shortcuts import redirect

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

import cloudinary.uploader
import requests as http_requests
import urllib.parse

from .models import EvidenciaProyecto
from .serializers import EvidenciaSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({'status': 'ok'})


class EvidenciaViewSet(viewsets.ModelViewSet):
    queryset = EvidenciaProyecto.objects.all().order_by('-fecha_registro')
    serializer_class = EvidenciaSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    filterset_fields = ['categoria']
    search_fields = ['titulo', 'proyecto', 'responsable']
    ordering_fields = ['fecha_registro', 'titulo', 'proyecto']

    def subir_archivo_cloudinary(self, archivo):
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

    def validar_archivo(self, archivo):
        tipos_permitidos = [
            'image/png',
            'image/jpeg',
            'application/pdf'
        ]

        if archivo.content_type not in tipos_permitidos:
            return Response(
                {
                    'error': 'Tipo de archivo no permitido. Solo se permiten JPG, PNG y PDF.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        tamano_maximo = 5 * 1024 * 1024

        if archivo.size > tamano_maximo:
            return Response(
                {
                    'error': 'El archivo no debe superar los 5 MB.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return None

    def create(self, request, *args, **kwargs):
        archivo = request.FILES.get('archivo')

        if not archivo:
            return Response(
                {
                    'error': 'Debe adjuntar un archivo.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        error_archivo = self.validar_archivo(archivo)

        if error_archivo:
            return error_archivo

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            datos_archivo = self.subir_archivo_cloudinary(archivo)
        except Exception as error:
            return Response(
                {
                    'error': 'No se pudo subir el archivo a Cloudinary.',
                    'detalle': str(error)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        evidencia = serializer.save(**datos_archivo)
        respuesta = self.get_serializer(evidencia)

        return Response(
            respuesta.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        evidencia = self.get_object()
        archivo = request.FILES.get('archivo')

        serializer = self.get_serializer(
            evidencia,
            data=request.data,
            partial=partial
        )

        serializer.is_valid(raise_exception=True)

        datos_archivo = {}

        if archivo:
            error_archivo = self.validar_archivo(archivo)

            if error_archivo:
                return error_archivo

            try:
                datos_archivo = self.subir_archivo_cloudinary(archivo)
            except Exception as error:
                return Response(
                    {
                        'error': 'No se pudo subir el archivo a Cloudinary.',
                        'detalle': str(error)
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        evidencia_actualizada = serializer.save(**datos_archivo)
        respuesta = self.get_serializer(evidencia_actualizada)

        return Response(
            respuesta.data,
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        evidencia = self.get_object()
        evidencia.delete()

        return Response(
            {
                'mensaje': 'Evidencia eliminada correctamente.'
            },
            status=status.HTTP_200_OK
        )


class GoogleAuthRedirectView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        params = {
            'client_id': settings.GOOGLE_CLIENT_ID,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'response_type': 'code',
            'scope': 'openid email profile',
            'access_type': 'offline',
            'prompt': 'select_account consent',
            'include_granted_scopes': 'true',
        }

        url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)
        return redirect(url)


class GoogleCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        code = request.GET.get('code')

        if not code:
            return Response(
                {'error': 'Código de autorización no recibido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token_response = http_requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code': code,
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uri': settings.GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code',
            }
        )

        token_data = token_response.json()

        if 'error' in token_data:
            return Response(
                {
                    'error': 'No se pudo obtener el token de Google.',
                    'detalle': token_data
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user_info_response = http_requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f"Bearer {token_data['access_token']}"}
        )

        user_info = user_info_response.json()

        email = user_info.get('email')
        nombre = user_info.get('given_name', '')
        apellido = user_info.get('family_name', '')

        if not email:
            return Response(
                {'error': 'No se pudo obtener el email del usuario.'},
                status=status.HTTP_400_BAD_REQUEST
            )

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
