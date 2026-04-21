import json
from channels.generic.websocket import AsyncWebsocketConsumer

class KanbanConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'kanban_updates'

        # Rejoindre le groupe de diffusion
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Quitter le groupe
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Recevoir un message depuis le groupe WebSocket
    async def kanban_update(self, event):
        message = event['message']

        # Envoyer le message au WebSocket (client)
        await self.send(text_data=json.dumps({
            'type': 'update',
            'message': message
        }))
