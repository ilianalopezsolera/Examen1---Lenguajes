from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import cloudinary.uploader

from .models import EvidenciaProyecto
from .serializers import EvidenciaSerializer


@api_view(['GET'])
def health(request):
    return Response({
        'status': 'ok'
    })


class EvidenciaViewSet(viewsets.ModelViewSet):

    queryset = EvidenciaProyecto.objects.all()
    serializer_class = EvidenciaSerializer
    permission_classes = [IsAuthenticated]

    filterset_fields = ['categoria']
    search_fields = ['titulo', 'proyecto']
    ordering_fields = ['fecha_registro']

    def create(self, request, *args, **kwargs):
        archivo = request.FILES.get('archivo')

        if not archivo:
            return Response(
                {'error': 'Debe adjuntar un archivo.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tipos_permitidos = [
            'image/jpeg',
            'image/png',
            'application/pdf'
        ]

        if archivo.content_type not in tipos_permitidos:
            return Response(
                {'error': 'Tipo de archivo no permitido. Solo se permiten JPG, PNG y PDF.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tamano_maximo = 5 * 1024 * 1024

        if archivo.size > tamano_maximo:
            return Response(
                {'error': 'El archivo no debe superar los 5 MB.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        resultado = cloudinary.uploader.upload(
            archivo,
            folder='evidencias_proyectos',
            resource_type='auto'
        )

        data = request.data.copy()

        data['archivo_url'] = resultado['secure_url']
        data['nombre_archivo'] = archivo.name
        data['tipo_archivo'] = archivo.content_type
        data['tamano_archivo'] = archivo.size

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )