import os
import shutil

from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import User


@receiver(pre_save, sender=User)
def delete_old_avatar(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = User.objects.get(pk=instance.pk)
        old_avatar = old_instance.avatar
        new_avatar = instance.avatar

        if old_avatar and old_avatar != new_avatar:
            old_avatar_path = os.path.join(
                settings.MEDIA_ROOT, str(old_avatar)
            )
            if os.path.isfile(old_avatar_path):
                os.remove(old_avatar_path)
    except User.DoesNotExist:
        pass


@receiver(post_save, sender=User)
def set_default_avatar(sender, instance, created, **kwargs):
    if created and not instance.avatar:
        default_avatar_path = os.path.join(
            settings.BASE_DIR,
            "data",
            "images",
            "test-images",
            f"face{instance.id % 6 + 1}.png",
        )

        if os.path.exists(default_avatar_path):
            avatar_dir = os.path.join(settings.MEDIA_ROOT, "avatars")
            os.makedirs(avatar_dir, exist_ok=True)

            new_avatar_path = os.path.join(
                avatar_dir, f"user_{instance.id}_avatar.png"
            )
            shutil.copy2(default_avatar_path, new_avatar_path)

            instance.avatar = f"avatars/user_{instance.id}_avatar.png"
            instance.save(update_fields=["avatar"])
