import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from channels.layers import get_channel_layer
from .models import Patient

class TokenNumberConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handles WebSocket connection"""
        self.channel_layer = get_channel_layer()  # Ensure channel layer is defined
        await self.channel_layer.group_add("token_updates", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Handles WebSocket disconnection"""
        await self.channel_layer.group_discard("token_updates", self.channel_name)

    async def receive(self, text_data):
        """Handles incoming messages and sends updates to the group"""
        await self.channel_layer.group_send(
            "token_updates",
            {"type": "send_token_update"}
        )

    async def send_token_update(self, event):
        """Sends the latest patient token number"""
        last_patient = await self.get_latest_patient()
        if last_patient:
            await self.send(text_data=json.dumps({"token": last_patient.token_number}))
        else:
            await self.send(text_data=json.dumps({"error": "No patient records found"}))

    @sync_to_async
    def get_latest_patient(self):
        """Fetch the latest patient safely"""
        return Patient.objects.order_by("-id").first()  # Avoid .latest() to prevent errors
