import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatRoom, Message
from users.models import CustomUser

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data['message']
            sender_id = data['sender_id']
            
            # Save message to database
            message_obj = await self.save_message(sender_id, message)
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender_id': sender_id,
                    'sender_username': await self.get_username(sender_id),
                    'timestamp': message_obj.timestamp.isoformat()
                }
            )
        except Exception as e:
            print(f"Error in receive: {e}")
    
    # Receive message from room group
    async def chat_message(self, event):
        try:
            message = event['message']
            sender_id = event['sender_id']
            sender_username = event['sender_username']
            timestamp = event['timestamp']
            
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'message': message,
                'sender_id': sender_id,
                'sender_username': sender_username,
                'timestamp': timestamp
            }))
        except Exception as e:
            print(f"Error in chat_message: {e}")
    
    @database_sync_to_async
    def save_message(self, sender_id, message):
        try:
            sender = CustomUser.objects.get(id=sender_id)
            room = ChatRoom.objects.get(id=self.room_id)
            message_obj = Message.objects.create(
                room=room, 
                sender=sender, 
                content=message,
                timestamp=timezone.now()
            )
            return message_obj
        except Exception as e:
            print(f"Error saving message: {e}")
            raise
    
    @database_sync_to_async
    def get_username(self, user_id):
        try:
            return CustomUser.objects.get(id=user_id).username
        except Exception as e:
            print(f"Error getting username: {e}")
            return "Unknown User"
