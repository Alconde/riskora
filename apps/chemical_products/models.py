from django.db import models
from django.conf import settings
from apps.companies.models import Company
from apps.core.mixins import AuditFieldsMixin


class ProductoQuimico(AuditFieldsMixin, models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='productos_quimicos')
    nombre = models.CharField(max_length=200)
    fabricante = models.CharField(max_length=200, blank=True, default='')
    composicion = models.TextField(blank=True, default='')
    uso = models.TextField(blank=True, default='')
    ubicacion = models.CharField(max_length=200, blank=True, default='')
    ficha_seguridad = models.FileField(upload_to='fichas_seguridad/', blank=True)
    imagen_etiqueta = models.ImageField(upload_to='etiquetas_quimicos/', blank=True)
    fecha_caducidad = models.DateField(null=True, blank=True)
    stock = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unidad = models.CharField(max_length=20, blank=True, default='uds')
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'Producto Químico'
        verbose_name_plural = 'Productos Químicos'

    def __str__(self):
        return self.nombre

    @property
    def caducado(self):
        if self.fecha_caducidad:
            from django.utils import timezone
            return self.fecha_caducidad < timezone.now().date()
        return False


class ClasificacionQuimica(AuditFieldsMixin, models.Model):
    PELIGRO_CHOICES = [
        ('GHS01', 'Explosivo'),
        ('GHS02', 'Inflamable'),
        ('GHS03', 'Comburente'),
        ('GHS04', 'Gases a presión'),
        ('GHS05', 'Corrosivo'),
        ('GHS06', 'Tóxico'),
        ('GHS07', 'Irritante / Nocivo'),
        ('GHS08', 'Peligro para la salud'),
        ('GHS09', 'Peligro para el medio ambiente'),
    ]

    producto = models.ForeignKey(ProductoQuimico, on_delete=models.CASCADE, related_name='clasificaciones')
    pictograma = models.CharField(max_length=10, choices=PELIGRO_CHOICES)
    frase_riesgo = models.CharField(max_length=200, blank=True, default='')
    frase_precaucion = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        verbose_name = 'Clasificación Química'
        verbose_name_plural = 'Clasificaciones Químicas'

    def __str__(self):
        return f"{self.producto.nombre} — {self.get_pictograma_display()}"
