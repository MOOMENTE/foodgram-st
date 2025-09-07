import os

from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Recipe


@receiver(pre_save, sender=Recipe)
def delete_old_image(sender, instance, **kwargs):
    """Удаляет старое изображение рецепта при загрузке нового."""
    if not instance.pk:
        return

    try:
        old_instance = Recipe.objects.get(pk=instance.pk)
        old_image = old_instance.image
        new_image = instance.image

        if old_image and old_image != new_image:
            old_image_path = os.path.join(settings.MEDIA_ROOT, str(old_image))
            if os.path.isfile(old_image_path):
                os.remove(old_image_path)
    except Recipe.DoesNotExist:
        pass
