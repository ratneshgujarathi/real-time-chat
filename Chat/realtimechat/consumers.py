#
#

from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Thread, NewMessage

User = get_user_model()


# class ChatConsumer(AsyncConsumer):
#     async def websocket_connect(self, event):
#         print('connected', event)
#         user = self.scope['user']
#         chat_room = f'user_chatroom_{user.id}'
#         self.chat_room = chat_room
#         await self.channel_layer.group_add(
#             chat_room,
#             self.channel_name
#         )
#         await self.send({
#             'type': 'websocket.accept'
#         })

#     async def websocket_receive(self, event):
#         print('receive', event)
#         received_data = json.loads(event['text'])
#         msg = received_data.get('message')
#         sent_by_id = received_data.get('sent_by')
#         send_to_id = received_data.get('send_to')
#         thread_id = received_data.get('thread_id')

#         if not msg:
#             print('Error:: empty message')
#             return False

#         sent_by_user = await self.get_user_object(sent_by_id)
#         send_to_user = await self.get_user_object(send_to_id)
#         thread_obj = await self.get_thread(thread_id)
#         if not sent_by_user:
#             print('Error:: sent by user is incorrect')
#         if not send_to_user:
#             print('Error:: send to user is incorrect')
#         if not thread_obj:
#             print('Error:: Thread id is incorrect')

#         await self.create_chat_message(thread_obj, sent_by_user, msg)

#         other_user_chat_room = f'user_chatroom_{send_to_id}'
#         self_user = self.scope['user']
#         response = {
#             'message': msg,
#             'sent_by': self_user.id,
#             'thread_id': thread_id
#         }

#         await self.channel_layer.group_send(
#             other_user_chat_room,
#             {
#                 'type': 'chat_message',
#                 'text': json.dumps(response)
#             }
#         )

#         await self.channel_layer.group_send(
#             self.chat_room,
#             {
#                 'type': 'chat_message',
#                 'text': json.dumps(response)
#             }
#         )

#     async def websocket_disconnect(self, event):
#         print('disconnect', event)

#     async def chat_message(self, event):
#         print('chat_message', event)
#         await self.send({
#             'type': 'websocket.send',
#             'text': event['text']
#         })

#     @database_sync_to_async
#     def get_user_object(self, user_id):
#         qs = User.objects.filter(id=user_id)
#         if qs.exists():
#             obj = qs.first()
#         else:
#             obj = None
#         return obj

#     @database_sync_to_async
#     def get_thread(self, thread_id):
#         qs = Thread.objects.filter(id=thread_id)
#         if qs.exists():
#             obj = qs.first()
#         else:
#             obj = None
#         return obj

#     @database_sync_to_async
#     def create_chat_message(self, thread, user, msg):
#         ChatMessage.objects.create(thread=thread, user=user, message=msg)


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        self.chat_room = 'user_chat_room_%s' % self.user

        # Join room group
        await self.channel_layer.group_add(
            self.chat_room,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.chat_room,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        msg = text_data_json['message']
        user_id = text_data_json['sent_by']
        thread_id = text_data_json['thread_id']
        sent_to = text_data_json['sent_to']

        if not msg:
            print('Error:: empty message')
            return False

        sent_by = await self.get_user_object(user_id)
        sent_to_id = await self.get_user_object(sent_to)
        thread_obj = await self.get_thread(thread_id)
        new_msg = await self.create_chat(thread_obj, sent_by, msg)

        self.other_user_chat_room = f'user_chatroom_{sent_to_id}'
        # Send message to room group
        await self.channel_layer.group_send(
            self.chat_room,
            {
                'type': 'chat_message',
                'message': msg,
                'sent_by': user_id,
                'thread_id': thread_id,
                'sent_to': sent_to
            }
        )
        await self.channel_layer.group_send(
            self.other_user_chat_room,
            {
                'type': 'chat_message',
                'message': msg,
                'sent_by': user_id,
                'thread_id': thread_id,
                'sent_to': sent_to
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        msg = event['message']
        user_id = event['sent_by']
        sent_to = event['sent_to']
        thread_id = event['thread_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': msg,
            'sent_by': user_id,
            'sent_to': sent_to,
            'thread_id': thread_id
        }))

    @database_sync_to_async
    def get_user_object(self, user_id):
        qs = User.objects.filter(id=user_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def get_thread(self, thread_id):
        qs = Thread.objects.filter(id=thread_id)
        if qs.exists():
            obj = qs.first()
        else:
            obj = None
        return obj

    @database_sync_to_async
    def create_chat(self, thread_id, sent_by, msg):
        new_msg = NewMessage.objects.create(
            thread_id=thread_id, sent_by=sent_by, msg=msg)
        new_msg.save()
        return new_msg
