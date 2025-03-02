from django.urls import path
from hospital.consumers import TokenNumberConsumer  # Import consumer class

websocket_urlpatterns = [
    path("ws/token-updates/", TokenNumberConsumer.as_asgi()),  # WebSocket URL
]
