"""
ASGI config for DCGymAppBackend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/asgi/
"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DCGymAppBackend.settings')
django.setup()

# from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.http import AsgiHandler

import messenger.routing



# application = get_asgi_application()

application = ProtocolTypeRouter({
    "http": AsgiHandler(),
     "websocket": URLRouter(
         messenger.routing.websocket_urlpatterns
     ),
})
