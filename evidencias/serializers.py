from rest_framework import serializers

from .models import EvidenciaProyecto


class EvidenciaSerializer(serializers.ModelSerializer):
    archivo = serializers.FileField(
        write_only=True,
        required=False
    )

    class Meta:
        model = EvidenciaProyecto
        fields = [
            'id',
            'titulo',
            'proyecto',
            'responsable',
            'categoria',
            'descripcion',
            'archivo',
            'archivo_url',
            'nombre_archivo',
            'tipo_archivo',
            'tamano_archivo',
            'fecha_registro',
            'fecha_actualizacion',
        ]
        read_only_fields = [  
            'archivo_url',
            'nombre_archivo',
            'tipo_archivo',
            'tamano_archivo',
            'fecha_registro',
            'fecha_actualizacion',
        ]