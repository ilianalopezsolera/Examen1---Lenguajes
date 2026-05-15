from django.db import models

class EvidenciaProyecto(models.Model):

    CATEGORIAS = [
        ('Documento', 'Documento'),
        ('Imagen', 'Imagen'),
        ('Captura', 'Captura'),
        ('Informe', 'Informe'),
        ('Presentacion', 'Presentacion'),
        ('Otro', 'Otro'),
    ]

    titulo = models.CharField(max_length=255)

    proyecto = models.CharField(max_length=255)

    responsable = models.CharField(max_length=255)

    categoria = models.CharField(
        max_length=50,
        choices=CATEGORIAS
    )

    descripcion = models.TextField()

    archivo_url = models.URLField()

    nombre_archivo = models.CharField(max_length=255)

    tipo_archivo = models.CharField(max_length=100)

    tamano_archivo = models.IntegerField()

    fecha_registro = models.DateTimeField(auto_now_add=True)

    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

# Create your models here.
