import json
from channels.generic.websocket import AsyncWebsocketConsumer


class BidUpdateConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for updating bid data in real-time.

    Methods:
        connect: Connects to the WebSocket and adds the consumer to the appropriate group.
        disconnect: Disconnects from the WebSocket and removes the consumer from the group.
        send_bid_update: Sends bid update data to the connected clients.
    """
    async def connect(self):
        self.auction_product_id = self.scope['url_route']['kwargs']['pk']
        self.auction_group_name = f"auction_{self.auction_product_id}"

        await self.channel_layer.group_add(
           
            self.auction_group_name,

            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):

        await self.channel_layer.group_discard(

            self.auction_group_name,
            self.channel_name
        )

    async def send_bid_update(self, event):

        bid_data = event['bid_data']
        await self.send(text_data=json.dumps({

            'type': 'bid_update',

            'bid_data': bid_data,
        }))