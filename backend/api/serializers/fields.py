from rest_framework import serializers


class AbsoluteURLImageField(serializers.ImageField):

    def to_representation(self, value):                          
        url = super().to_representation(value)
        if not url:
            return url
        request = self.context.get("request")
        if request is None:
            return url
        return request.build_absolute_uri(url)
