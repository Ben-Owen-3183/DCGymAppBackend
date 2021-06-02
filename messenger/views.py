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


# Create your views here.
class CreateNewChat(APIView):
    permission_classes = [IsAuthenticated]

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
            print(e)
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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        #try:
        chat_id = request.data['chat_id']
        user_chat = ChatUser.objects.get(subscribed_chat=chat_id, user=request.user)
        other_user_chat = ChatUser.objects.get(
            Q(subscribed_chat=chat_id)
            & ~Q(user=request.user)
        )
        return Response({
            'id': str(chat_id),
            'read': user_chat.read,
            'messages': get_messages(chat_id),
            'other_user_data': user_row_to_json(other_user_chat.user)
        })
        #except Exception as e:
        #    print(str(e))
        #return Response({})


class GetChats(APIView):
    permission_classes = [IsAuthenticated]

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
            print(e);
            return Response({'error': ['something went wrong getting chats']})
        return Response({'chats': chats})


class GetPagedMessages(APIView):
    permission_classes = [IsAuthenticated]

    # https://docs.djangoproject.com/en/3.2/topics/pagination/#paginating-a-listview
    def post(self, request):
                #try:
                page_num = request.data['page']

                messages = Messages.objects.filter(
                    timestamp__range=["1066-01-01", datetime.now()],
                     chat=chat_id
                ).order_by('-timestamp')[:30]

                Paginator()

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
                #except:
                return []


""" call to set a chat to read """
class ChatRead(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            chat_user = ChatUser.objects.get(
                Q(subscribed_chat=request.data['chat_id'])
                & Q(user=request.user)
            )
            chat_user.read = True
            chat_user.save()
        except Exception as e:
            print(e)

        return Response({})





#
