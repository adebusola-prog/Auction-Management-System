from django.urls import path

from .consumers import BidUpdateConsumer

websocket_urlpatterns =[
    path('ws/<int:pk>/product/', BidUpdateConsumer.as_asgi())
]