from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Administrador'
        TECHNICIAN = 'technician', 'Técnico PRL'
        CLIENT = 'client', 'Cliente'
        AUDITOR = 'auditor', 'Auditor'
        VIEWER = 'viewer', 'Solo lectura'

    email = models.EmailField('correo electrónico', unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.VIEWER,
        verbose_name='rol'
    )
    phone = models.CharField('teléfono', max_length=20, blank=True)
    job_title = models.CharField('cargo', max_length=150, blank=True)
    is_verified = models.BooleanField('verificado', default=False)

    def __str__(self):
        return self.get_full_name() or self.username
