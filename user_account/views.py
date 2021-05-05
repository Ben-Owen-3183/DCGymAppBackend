from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import base64
from user_account.models import UserAvatar
from django.core.files.base import ContentFile

class user_account(APIView):
    """
    Validate names
    """

class Avatar(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        image_file = ContentFile(base64.b64decode(request.data['base64']))

        user_avatar = None
        try:
            user_avatar = UserAvatar.objects.get(user=request.user)
            user_avatar.image = image_file
            user_avatar.save()
        except:
            user_avatar = UserAvatar.objects.create(
                user=request.user,
                type=request.data['type'],
                image=image_file
            )

        # encoded = base64.b64encode(user_avatar.image.read()).decode('utf-8')
        return Response('hello')
