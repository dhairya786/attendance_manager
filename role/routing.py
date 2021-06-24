from django.urls import path

from .consumers import ChatConsumer

websocket_urlpatterns = [
    path(r'ws/dashboard/course<int:pk>/room', ChatConsumer.as_asgi()),
]