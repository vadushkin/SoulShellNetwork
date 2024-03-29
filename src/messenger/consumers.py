import json

from channels.generic.websocket import AsyncWebsocketConsumer


class MessengerConsumer(AsyncWebsocketConsumer):
    """Consumer to manage WebSocket connections for the Messenger app."""

    async def connect(self):
        """Consumer Connect implementation, to validate user status and prevent
        non-authenticated user to take advantage from the connection."""

        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add(
                f"{self.scope['user'].username}",
                self.channel_name,
            )
            await self.accept()

    async def disconnect(self, close_code):
        """Consumer implementation to leave behind the group at the moment the
        closes the connection."""
        await self.channel_layer.group_discard(
            f"{self.scope['user'].username}",
            self.channel_name,
        )

    async def receive(self, text_data):
        """Receive method implementation to redirect any new message received
        on the websocket to broadcast to all the clients."""
        await self.send(text_data=json.dumps(text_data))
