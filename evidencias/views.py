from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from urllib3 import request
from .models import EvidenciaProyecto
from .serializers import EvidenciaSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

import cloudinary.uploader


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
        archivo = request.FILES['archivo']
        resultado = cloudinary.uploader.upload(archivo)
        url = resultado['secure_url']
        return super().create(request, *args, **kwargs)