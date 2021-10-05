from django.core.management.base import BaseCommand, CommandError
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice


class Command(BaseCommand):

    def handle(self, *args, **options):
        print('\n\n')

        message = Message(
            notification=Notification(title="title", body="text", image="https://pixy.org/src/21/219269.jpg"),
        )
        devices = FCMDevice.objects.all().first()
        response = devices.send_message(message)

        try:
            pass
            # print('success')
        except Exception as e:
            pass
            # print('failure')

        print('\n\n')




#
