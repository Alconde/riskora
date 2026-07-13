from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.companies.models import Company
from .models import PlanPrevention


@receiver(post_save, sender=Company)
def create_prevention_plan(sender, instance, created, **kwargs):
    if created:
        PlanPrevention.objects.get_or_create(company=instance)
