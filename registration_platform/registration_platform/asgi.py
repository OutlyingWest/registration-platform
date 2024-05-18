"""
ASGI config for registration_platform project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/asgi/
"""

import os

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from verification.consumers import DocumentStatusConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'registration_platform.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/document_status/", DocumentStatusConsumer.as_asgi()),
        ])
    ),
})
