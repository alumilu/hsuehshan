"""
WSGI config for hsuehshan project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hsuehshan.settings")

##
from its.its import TisvcloudChecker
from its.its import HerePlatform

tis = TisvcloudChecker()
tis.start()

here = HerePlatform()
here.start()
##

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
