from rest_framework import serializers

from api.serializers.fields import AbsoluteURLImageField
from recipes.models import Recipe


class RecipeCompactSerializer(serializers.ModelSerializer):

    image = AbsoluteURLImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
        read_only_fields = fields
