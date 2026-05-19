from rest_framework import serializers
from .models import EvidenciaProyecto

TIPOS_ARCHIVO_VALIDOS = ['image/jpeg', 'image/png', 'application/pdf']
TAMANO_MAXIMO_BYTES = 5 * 1024 * 1024  # 5 MB


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

    def validate_titulo(self, value):
        if not value.strip():
            raise serializers.ValidationError("El título no puede estar vacío.")
        return value.strip()

    def validate_proyecto(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre del proyecto no puede estar vacío.")
        return value.strip()

    def validate_responsable(self, value):
        if not value.strip():
            raise serializers.ValidationError("El responsable no puede estar vacío.")
        return value.strip()

    def validate_categoria(self, value):
        categorias_validas = [c[0] for c in EvidenciaProyecto.CATEGORIAS]
        if value not in categorias_validas:
            raise serializers.ValidationError(
                f"Categoría inválida. Opciones válidas: {', '.join(categorias_validas)}"
            )
        return value

    def validate_descripcion(self, value):
        if not value.strip():
            raise serializers.ValidationError("La descripción no puede estar vacía.")
        if len(value) > 500:
            raise serializers.ValidationError(
                "La descripción no puede superar los 500 caracteres."
            )
        return value.strip()

    def validate_archivo(self, archivo):
        if archivo.content_type not in TIPOS_ARCHIVO_VALIDOS:
            raise serializers.ValidationError(
                f"Tipo no permitido: '{archivo.content_type}'. "
                f"Aceptados: {', '.join(TIPOS_ARCHIVO_VALIDOS)}"
            )
        if archivo.size > TAMANO_MAXIMO_BYTES:
            mb = round(archivo.size / 1024 / 1024, 2)
            raise serializers.ValidationError(
                f"El archivo pesa {mb} MB y supera el límite de 5 MB."
            )
        return archivo

    def create(self, validated_data):
        validated_data.pop('archivo', None)  # ← adentro de la clase
        return super().create(validated_data)