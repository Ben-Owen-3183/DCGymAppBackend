from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from login.models import CustomUser
from messenger.models import Chat, ChatUser, Messages
from rest_framework.views import APIView
from django.db.models import Q
from datetime import datetime
from user_account.models import UserAvatar
from django.core.paginator import Paginator
from django.db.models import Exists

import logging

def get_messages(chat_id):
    try:
        messages = Messages.objects.filter(
            timestamp__range=["1066-01-01", datetime.now()],
            chat=chat_id
        ).order_by('-timestamp')[:30]

        message_list = []
        for msg in messages:
            message_list.append({
                'id': msg.id,
                'chat_id': msg.chat.id,
                'user_id': msg.user.id,
                'message': msg.message,
                'datetime': msg.timestamp,
            })
        message_list
        return message_list
    except Exception as e:
        return []


def get_messages_after_message_datetime(chat_id, msg_datetime, msg_id):
    try:
        messages = Messages.objects.filter(
            Q(timestamp__range=[msg_datetime, datetime.now()])
            & Q(chat=chat_id)
            & ~Q(id=msg_id)
        ).order_by('-timestamp')[:30]

        message_list = []
        for msg in messages:
            message_list.append({
                'id': msg.id,
                'chat_id': msg.chat.id,
                'user_id': msg.user.id,
                'message': msg.message,
                'datetime': msg.timestamp,
            })
        message_list
        return message_list
    except Exception as e:
        return []


def get_chat_data(user, chat_id):
    try:
        user_chat = ChatUser.objects.get(subscribed_chat=chat_id, user=user)
        other_user_chat = None
        try:
            other_user_chat = ChatUser.objects.get(
                Q(subscribed_chat=chat_id)
                & ~Q(user=user)
            )
        except ChatUser.DoesNotExist:
            # Deletes zombie chat caused by not exist other_user_chat 
            user_chat.delete()
            Chat.objects.get(id=chat_id).delete()
            Messages.objects.filter(chat_id=chat_id).delete()
            return None

        return {
            'id': str(chat_id),
            'read': user_chat.read,
            'messages': get_messages(chat_id),
            'other_user_data': user_row_to_json(other_user_chat.user)
        }
    except:
        return None



def user_row_to_json(user):
    return  {
        'id': str(user.id),
        'fName': user.first_name,
        'sName': user.last_name,
        'isStaff': False if user.hidden else user.is_staff,
        'isStaff': user.is_staff,
        'avatarURL': getUserAvatar(user.id)
    }


def getUserAvatar(user_id):
    try:
        userAvatar = UserAvatar.objects.get(user=user_id)
        return userAvatar.image_name
    except:
        return ''


# Create your views here.
class CreateNewChat(APIView):

    def post(self, request):
        if request.user.id == request.data['otherUser']:
            return Response({'error': ['cannot chat with yourself']})

        chat_id = None
        other_user_data = None
        try:
            chat_id = self.users_already_in_chat(request.user.id, request.data['otherUser'])
            if chat_id > -1:
                print("chat exists. Nothing more to do")
                return Response({'chat_id': chat_id, 'new': False})

            newChat = Chat.objects.create()
            current_user_chat = ChatUser.objects.create(
                subscribed_chat=newChat,
                user=request.user,
                read=True
            )
            chat_id = current_user_chat.subscribed_chat.id
            other_user_data = CustomUser.objects.get(
                id=request.data['otherUser']
            )
            ChatUser.objects.create(
                subscribed_chat=newChat,
                user=other_user_data
            )
        except Exception as e:
            logging.exception('Create New Chat')
            return Response({'errors': ['failed to make new chat. Possible other user does not exist.']})

        print("new chat has been made.")
        return Response({
            'new': True,
            'read': True,
            'chat_id': chat_id,
            'message': [],
            'other_user_data': {
                'id': other_user_data.id,
            }
        })


    """
    checks if a chat between two users exists. Will return the chat
    id if one exists. -1 if nothing
    """
    def users_already_in_chat(self, user1_id, user2_id):
        user1_chats = ChatUser.objects.filter(user=user1_id)
        user2_chats = ChatUser.objects.filter(user=user2_id)
        for user1_row in user1_chats:
            for user2_row in user2_chats:
                if user1_row.subscribed_chat == user2_row.subscribed_chat:
                    return user1_row.subscribed_chat.id
        return -1


class GetChat(APIView):

    def post(self, request):
        try:
            return Response(get_chat_data(request.user, request.data['chat_id']))
        except Exception as e:
            logging.exception('Get Chat')
        return Response({})


class GetChats(APIView):

    def get(self, request):
        chats = []
        try:
            user_chats = ChatUser.objects.filter(user=request.user).order_by('-last_updated')
            for chat in user_chats:
                messages = get_messages(chat.subscribed_chat)
                other_user_chat = ChatUser.objects.get(
                    Q(subscribed_chat=chat.subscribed_chat)
                    & ~Q(user=request.user)
                )
                other_user = CustomUser.objects.get(id=other_user_chat.user.id)
                # only added a chat if it has messages
                if len(messages) > 0:
                    chats.append({
                        'id': str(chat.subscribed_chat.id),
                        'read': chat.read,
                        'messages': messages,
                        'other_user_data': user_row_to_json(other_user)
                    })
        except Exception as e:
            logging.exception('Get Chats')
            return Response({'error': ['something went wrong getting chats']})
        return Response({'chats': chats})



""" call to set a chat to read """
class ChatRead(APIView):

    def post(self, request):
        try:
            chat_user = ChatUser.objects.get(
                Q(subscribed_chat=request.data['chat_id'])
                & Q(user=request.user)
            )
            chat_user.read = True
            chat_user.save()
        except Exception as e:
            logging.exception('Chat Read')
        return Response({})


"""
    responds with all the missing messages and chats of a user
    data = {
        chats_data: [
            {
                chat_id: ...
                last_message_id: ...request
                last_message_time: ...
            },
            {
                ...
            }
        ]
    }
"""
class SyncChats(APIView):

    def match_chat(self, chats, chat_id):
        for chat in chats:
            if str(chat['chat_id']) == str(chat_id):
                return chat
        return None


    def add_msgs_to_response(self, response, matched_chat):
        messages = get_messages_after_message_datetime(
            matched_chat['chat_id'],
            matched_chat['last_message_time'],
            matched_chat['last_message_id'],
        )
        return {
            'chat_id': matched_chat['chat_id'],
            'messages': messages
        }


    def post(self, request):
        try:
            users_chats = ChatUser.objects.filter(user=request.user)
            chats_data = request.data['chats_data']
            response = {
                'new_chats': [],
                'new_chat_messages': []
            }

            for user_chat in users_chats:
                chat_id = user_chat.subscribed_chat.id
                matched_chat = self.match_chat(chats_data, chat_id)
                if matched_chat and matched_chat.get('last_message_time'):
                    new_messages_data = self.add_msgs_to_response(response, matched_chat)
                    if len(new_messages_data['messages']) > 0:
                        response['new_chat_messages'].append(new_messages_data)
                else:
                    new_chat = get_chat_data(request.user, chat_id)
                    if new_chat != None and len(new_chat['messages']) > 0:
                        response['new_chats'].append(new_chat)

            return Response(response)
        except Exception as e:
            logging.exception('Sync Chats')
            return Response({})


""" returns messages of chat after datetime """
class ChatHistory(APIView):

    def post(self, request):
        try:
            chat_id = request.data['chat_id']
            user_is_in_chat = Exists(ChatUser.objects.filter(
                user=request.user, subscribed_chat=chat_id
            ))

            if not user_is_in_chat:
                raise Exception("user not in chat")

            msg_id = request.data['last_message_id']
            msg_datetime = request.data['last_message_time']
            messages = self.get_messages_before_message_datetime(chat_id, msg_datetime, msg_id)
            return Response({'messages': messages})
        except Exception as e:
            logging.exception('Chat History')
            return Response()



    def get_messages_before_message_datetime(self, chat_id, msg_datetime, msg_id):
        try:
            messages = Messages.objects.filter(
                Q(timestamp__range=['1066-01-01', msg_datetime])
                & Q(chat=chat_id)
                & ~Q(id=msg_id)
            ).order_by('-timestamp')[:30]

            message_list = []
            for msg in messages:
                message_list.append({
                    'id': msg.id,
                    'chat_id': msg.chat.id,
                    'user_id': msg.user.id,
                    'message': msg.message,
                    'datetime': msg.timestamp,
                })
            message_list
            return message_list
        except Exception as e:
            return []






#
