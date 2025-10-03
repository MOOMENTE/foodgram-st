import os

from django.conf import settings
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "foodgram.settings")

application = get_wsgi_application()
application = WhiteNoise(application, root=str(settings.STATIC_ROOT))
application.add_files(str(settings.MEDIA_ROOT), prefix="media/")
