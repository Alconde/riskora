from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TrainingRecord
from .services import refresh_training_alerts_for_record


@receiver(post_save, sender=TrainingRecord)
def training_record_post_save(sender, instance, **kwargs):
    refresh_training_alerts_for_record(instance)