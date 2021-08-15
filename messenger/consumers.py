import json
from channels.generic.websocket import WebsocketConsumer
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from asgiref.sync import async_to_sync
from login.models import CustomUser
from messenger.models import ChatUser, Messages, Chat
from user_account.models import UserAvatar
from django.db.models import Q
from datetime import datetime
import logging


def user_row_to_json(user):
    return  {
        'id': str(user.id),
        'fName': user.first_name,
        'sName': user.last_name,
        'isSuperUser': user.is_superuser,
        'isStaff': user.is_staff,
        'avatarURL': getUserAvatar(user.id)
    }


def getUserAvatar(user_id):
    try:
        userAvatar = UserAvatar.objects.get(user=user_id)
        return userAvatar.image_name
    except:
        return ''



class MessengerConsumer(WebsocketConsumer):
    def connect(self):
        print("\n")
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        json_message = json.loads(text_data)

        action = json_message['action']
        data = json_message['data']
        if action == 'init':
            self.init(data['token'])

        try:
            # All other actions go after this point !
            user_id = self.get_user_id(data['token'])
            # if user is not authenticated
            if user_id < 0:
                return

            if action == 'message':
                self.message(data, user_id)
            if action == 'new_chat':
                self.new_chat(data, user_id)
            if action == 'add_new_chat':
                self.add_new_chats(user_id)
            if action == 'chat_read':
                self.set_chat_read(user_id, data['chat_id'])
        except Exception as e:
            logging.exception('Receive')


    def set_chat_read(self, user_id, chat_id):
        other_user_chat = ChatUser.objects.get(
            Q(subscribed_chat=chat_id)
            & Q(user=user_id)
        )
        other_user_chat.read = True
        other_user_chat.save()
        self.notify_chat(
            str(user_id),
            {
                'action': 'SET_CHAT_READ',
                'chat_id': str(chat_id)
            }
        )


    def add_new_chats(self, user_id):
        try:
            users_chats = ChatUser.objects.filter(user=user_id)
            for chat in users_chats:
                async_to_sync(self.channel_layer.group_add)(
                    str(chat.subscribed_chat.id),
                    self.channel_name
                )
        except Exception as e:
            logging.exception('Add New Chat')


    """ Creates a new chat and adds the user"""
    def new_chat(self, data, user_id):
        try:
            async_to_sync(self.channel_layer.group_add)(
                str(data['chat_id']),
                self.channel_name
            )

            other_user_chat = ChatUser.objects.get(
                Q(subscribed_chat=data['chat_id'])
                & ~Q(user=user_id)
            )

            self.notify_chat(
                str(other_user_chat.user.id),
                {
                    'action': 'NEW_CHAT',
                    'chat_id': data['chat_id']
                }
            )
        except Exception as e:
            logging.exception('New Chat')


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

    """Sends a new chat message to group"""
    def message(self, data, user_id):
        try:
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
            data['message'] = data['message'].strip()
            message = Messages.objects.create(
                chat=chat,
                user=user,
                message=data['message'],
            )



            self.notify_chat(
                str(chat.id),
                {
                    'action': 'NEW_CHAT_MESSAGE',
                    'read': {
                        str(user.id): current_user_chat.read,
                        str(other_user.id): other_user_chat.read,
                    },
                    'message': {
                        'id': str(message.id),
                        'chat_id': str(chat.id),
                        'user_id': str(user.id),
                        'message': data['message'],
                        'datetime': str(message.timestamp),
                    },
                    'chat_data': {
                        'id': str(chat.id),
                        'read': current_user_chat.read,
                        'messages': [],
                        'other_user_data': user_row_to_json(other_user_chat.user)
                    }

                }
            )
        except Exception as e:
            logging.exception('New Message')

    def notify_chat(self, group_name, data):
        async_to_sync(self.channel_layer.group_send)(
            group_name,
            {
                'type': 'emit',
                'data': data,
            }
        )

    def emit(self, event):
        data = event['data']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'data': data
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
