import json
from channels.generic.websocket import WebsocketConsumer
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from login.models import CustomUser
from messenger.models import ChatUser, Messages, Chat
from django.db.models import Q
from datetime import datetime

class MessengerConsumer(WebsocketConsumer):
    def connect(self):
        print("\n")
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        print(text_data)
        json_message = json.loads(text_data)

        action = json_message['action']
        data = json_message['data']
        if action == 'init':
            self.init(data['token'])

        #try:
        # All other actions go after this point !
        user_id = self.get_user_id(data['token'])
        # if user is not authenticated
        if user_id < 0:
            return

        if action == 'message':
            self.message(data, user_id)
        if action == 'new_chat':
            self.new_chat(data, user_id)
        #except Exception as e:
        #    print(e)


    def new_chat(self, data, user_id):
                #try:
                async_to_sync(self.channel_layer.group_add)(
                    str(data['chat_id']),
                    self.channel_name
                )

                other_user_chat = ChatUser.objects.get(
                    Q(subscribed_chat=data['chat_id'])
                    & ~Q(user=user_id)
                )

                async_to_sync(self.channel_layer.group_send)(
                    str(other_user_chat.user.id),
                    {
                        'type': 'chat_message',
                        'message': 'new_chat',
                        'chat_id': data['chat_id']
                    }
                )
                #except Exception as e:
                #    print("error: " + str(e))


    """
    Initialises channel layer by adding it to a unique group
    """
    def init(self, token):
        user_id = -1
        if token:
            user_id = self.get_user_id(token)
            if user_id < 0:
                return
        else:
            return

        # Create room name
        self.room_group_name = str(user_id)

        users_chats = ChatUser.objects.filter(user=user_id)
        # join the room

        for chat in users_chats:
            async_to_sync(self.channel_layer.group_add)(
                str(chat.subscribed_chat.id),
                self.channel_name
            )

        # Create personal chat
        async_to_sync(self.channel_layer.group_add)(
            str(user_id),
            self.channel_name
        )


    def message(self, data, user_id):
        #try:
        if len(data['message']) > 1000:
            return
        user = CustomUser.objects.get(id=user_id)
        # confirm users are in chat
        current_user_chat = ChatUser.objects.get(subscribed_chat=data['chat_id'], user=user)
        other_user_chat = ChatUser.objects.get(
            Q(subscribed_chat=data['chat_id'])
            & ~Q(user=user)
        )
        other_user_chat.read = False
        other_user_chat.last_updated = str(datetime.now())
        current_user_chat.last_updated = str(datetime.now())
        current_user_chat.save()
        other_user_chat.save()
        other_user = CustomUser.objects.get(id=other_user_chat.user.id)
        chat = Chat.objects.get(id=data['chat_id'])
        Messages.objects.create(
            chat=chat,
            user=user,
            message=data['message'],
        )
        self.notify_chat(chat.id)
        #except Exception as e:
        #    print("error: " + str(e))


    def notify_chat(self, chat_id):
        async_to_sync(self.channel_layer.group_send)(
            str(chat_id),
            {
                'type': 'chat_message',
                'message': 'new_message'
            }
        )

    def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message
        }))

    def get_user_id(self, token):
        try:
            auth_row = Token.objects.get(key=token)
            return auth_row.user_id
        except:
            return -1

    @database_sync_to_async
    def is_authenticated(self, token):
        try:
            Token.objects.get(key=token)
            return True
        except:
            return False
        return False



#
