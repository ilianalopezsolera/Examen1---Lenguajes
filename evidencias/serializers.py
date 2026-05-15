from rest_framework import serializers
from .models import EvidenciaProyecto

class EvidenciaSerializer(serializers.ModelSerializer):

    class Meta:
        model = EvidenciaProyecto
        fields = '__all__'