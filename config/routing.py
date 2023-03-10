from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.urls import re_path

from src.messenger.consumers import MessengerConsumer
from src.notifications.consumers import NotificationsConsumer

application = ProtocolTypeRouter(
    {
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    [
                        re_path(r"^notifications/$", NotificationsConsumer),
                        re_path(r"^(?P<username>[^/]+)/$", MessengerConsumer),
                    ]
                )
            )
        )
    }
)
