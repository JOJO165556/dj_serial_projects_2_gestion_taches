import json
from channels.generic.websocket import AsyncWebsocketConsumer

class KanbanConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope['url_route']['kwargs']['project_id']
        self.group_name = f'kanban_updates_{self.project_id}'

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
        message = event.get('message', '')
        board_data = event.get('board_data', None)

        # Envoyer le message au WebSocket (client)
        payload = {
            'type': 'update_board',
            'message': message,
        }
        if board_data:
            payload['board_data'] = board_data
            
        await self.send(text_data=json.dumps(payload))
