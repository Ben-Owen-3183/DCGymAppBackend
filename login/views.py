from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from user_account.models import UserAvatar
from .membership_status import member_status_checker
from rest_framework.views import APIView
from login.models import CustomUser
import logging

class userData(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            token = request.data['token']
            user_id = Token.objects.get(key=token).user_id
            user = CustomUser.objects.get(id=user_id)

            avatarName = None
            try:
                avatar = UserAvatar.objects.get(user=user.pk)
                avatarName = avatar.image_name
            except:
                avatarName = ''

            return Response({'user_data' : {
                'token': token,
                'user_id': user.pk,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'avatarURL': avatarName,
            }})
        except Exception as e:
            logging.exception('Get Chat')
            return Response({'error': 'failed request'})


class login(ObtainAuthToken):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        request.data['username'] = request.data['username'].lower()
        serializer = self.serializer_class(data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)

        if not member_status_checker.user_is_active_member(user.email):
            return Response({'membership': 'not active member'})

        avatarName = None
        try:
            avatar = UserAvatar.objects.get(user=user.pk)
            avatarName = avatar.image_name
        except:
            avatarName = ''

        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'avatarURL': avatarName,
        })
