from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Role, User


@receiver(post_save, sender=User)
def assign_default_role(sender, instance, created, **kwargs):
    if not created or instance.role_id:
        return
    if instance.is_superuser:
        role, _ = Role.objects.get_or_create(
            slug="admin",
            defaults={"name": "Admin", "description": "Platform administrator"},
        )
    else:
        role, _ = Role.objects.get_or_create(
            slug="customer",
            defaults={"name": "Customer", "description": "Campus customer"},
        )
    User.objects.filter(pk=instance.pk).update(role_id=role.id)
