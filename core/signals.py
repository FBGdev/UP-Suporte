from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Funcionario


@receiver(post_save, sender=User)
def criar_funcionario(sender, instance, created, **kwargs):
    if created:
        Funcionario.objects.get_or_create(
            usuario=instance,
            defaults={"cargo": "Técnico", "telefone": ""}
        )
