from django.db import models
from apps.companies.models import Company


def upload_cae_path(instance, filename):
    return f'cae/{instance.empresa_subcontrata.empresa_id}/{instance.empresa_subcontrata.id}/{filename}'


def upload_procedimiento_path(instance, filename):
    return f'cae/{instance.empresa_id}/procedimiento/{filename}'


def upload_carta_path(instance, filename):
    return f'cae/{instance.empresa_id}/carta/{filename}'


def upload_riesgos_path(instance, filename):
    return f'cae/{instance.empresa_id}/riesgos/{filename}'


class EmpresaSubcontrata(models.Model):
    empresa = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='empresas_subcontrata',
        verbose_name='Empresa principal',
    )
    nombre_empresa = models.CharField('Nombre de la empresa', max_length=255)
    trabajo_realizar = models.TextField('Trabajo a realizar')
    persona_contacto = models.CharField('Persona de contacto', max_length=200)
    telefono = models.CharField('Telefono', max_length=20, blank=True)
    email = models.EmailField('Correo electronico', blank=True)
    activa = models.BooleanField('Activa', default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Empresa subcontratada'
        verbose_name_plural = 'Empresas subcontratadas'
        ordering = ['nombre_empresa']

    def __str__(self):
        return self.nombre_empresa

    @property
    def total_documentos(self):
        return self.documentos_cae.count()

    @property
    def documentos_subidos(self):
        return self.documentos_cae.exclude(documento='').count()

    @property
    def documentos_actualizados(self):
        from django.utils import timezone
        today = timezone.localdate()
        return self.documentos_cae.exclude(documento='').filter(
            models.Q(fecha_caducidad__isnull=True) | models.Q(fecha_caducidad__gte=today)
        ).count()

    @property
    def habilitada(self):
        total = self.total_documentos
        if total == 0:
            return False
        return self.documentos_subidos == total and self.documentos_actualizados == total

    @property
    def porcentaje_documentacion(self):
        total = self.total_documentos
        if total == 0:
            return 0
        return round((self.documentos_subidos / total) * 100)


class DocumentoCAETipo(models.Model):
    nombre = models.CharField('Nombre del documento', max_length=200)
    descripcion = models.TextField('Descripcion', blank=True)
    obligatorio = models.BooleanField('Obligatorio', default=True)
    orden = models.PositiveIntegerField('Orden', default=0)
    activo = models.BooleanField('Activo', default=True)

    class Meta:
        verbose_name = 'Tipo de documento CAE'
        verbose_name_plural = 'Tipos de documentos CAE'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return self.nombre


class DocumentoCAE(models.Model):
    empresa_subcontrata = models.ForeignKey(
        EmpresaSubcontrata,
        on_delete=models.CASCADE,
        related_name='documentos_cae',
        verbose_name='Empresa subcontratada',
    )
    tipo_documento = models.ForeignKey(
        DocumentoCAETipo,
        on_delete=models.CASCADE,
        related_name='documentos',
        verbose_name='Tipo de documento',
    )
    documento = models.FileField(
        upload_to=upload_cae_path,
        blank=True,
        null=True,
        verbose_name='Documento',
    )
    fecha_subida = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de subida',
    )
    fecha_caducidad = models.DateField(
        blank=True,
        null=True,
        verbose_name='Fecha de caducidad',
    )

    class Meta:
        verbose_name = 'Documento CAE'
        verbose_name_plural = 'Documentos CAE'
        unique_together = ['empresa_subcontrata', 'tipo_documento']
        ordering = ['tipo_documento__orden', 'tipo_documento__nombre']

    def __str__(self):
        return f'{self.empresa_subcontrata} - {self.tipo_documento}'

    @property
    def subido(self):
        return bool(self.documento)

    @property
    def actualizado(self):
        if not self.documento:
            return False
        if not self.fecha_caducidad:
            return True
        from django.utils import timezone
        return self.fecha_caducidad >= timezone.localdate()


class ProcedimientoCAE(models.Model):
    empresa = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='procedimiento_cae',
        verbose_name='Empresa',
    )
    documento = models.FileField(
        upload_to=upload_procedimiento_path,
        blank=True,
        null=True,
        verbose_name='Procedimiento de coordinacion',
    )
    version = models.CharField('Version', max_length=20, default='1.0')
    fecha = models.DateField('Fecha del procedimiento', blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Procedimiento CAE'
        verbose_name_plural = 'Procedimientos CAE'

    def __str__(self):
        return f'Procedimiento CAE - {self.empresa}'


class CartaCAE(models.Model):
    empresa = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='carta_cae',
        verbose_name='Empresa',
    )
    documento = models.FileField(
        upload_to=upload_carta_path,
        blank=True,
        null=True,
        verbose_name='Carta de empresas',
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carta CAE'
        verbose_name_plural = 'Cartas CAE'

    def __str__(self):
        return f'Carta CAE - {self.empresa}'


class DocumentoRiesgosCAE(models.Model):
    empresa = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='documento_riesgos_cae',
        verbose_name='Empresa',
    )
    documento = models.FileField(
        upload_to=upload_riesgos_path,
        blank=True,
        null=True,
        verbose_name='Documento de riesgos, medidas preventivas y emergencia',
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Documento de Riesgos CAE'
        verbose_name_plural = 'Documentos de Riesgos CAE'

    def __str__(self):
        return f'Documento Riesgos CAE - {self.empresa}'
