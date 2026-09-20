from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AgentProfile

@receiver(post_save, sender=User)
def ensure_profile(sender, instance, created, **kwargs):
    if created:
        AgentProfile.objects.get_or_create(
            user=instance,
            defaults={'role': 'admin' if instance.is_superuser else 'agent', 'display_name': instance.get_full_name() or instance.username},
        )
