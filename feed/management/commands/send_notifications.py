from django.core.management.base import BaseCommand, CommandError
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from feed.models import Post, PostsToNotify
from django.conf import settings
from datetime import datetime
from django.db.models import Q
import logging

prompt = '[' + str(datetime.now()) + '] '

class Command(BaseCommand):

    # Sends notifications of feed
    def handle(self, *args, **options):
        posts_to_notify = PostsToNotify.objects.filter(notification_sent=False)

        count_to_send = len(posts_to_notify)
        count_sent = 0

        for post_to_notify in posts_to_notify:
            success = self.notify_users_of_post(post_to_notify)
            if success:
                count_sent += 1
                post_to_notify.notification_sent = True
                post_to_notify.save()
            
        if count_to_send != count_sent:
            self.stdout.write(prompt + 'Failure:' + str(count_sent) + ' notifications sent out of ' + str(count_to_send))
        PostsToNotify.objects.filter(notification_sent=True).delete()
    

    def notify_users_of_post(self, post_to_notify):
        post = Post.objects.get(id=post_to_notify.post.id)
        
        try:
            image_url = ''
            if post.thumbnail_link:
                image_url = post.thumbnail_link
            elif post.image_name:
                image_url = settings.SITE_URL + 'media/post_images/' + image_url

            message = Message(
                notification=Notification(
                    title="New post from " + post.user.first_name + ' ' + post.user.last_name, 
                    body=post.content, 
                    image=image_url
                ),
                data={'type': 'feed'}
            )
            FCMDevice.objects.filter(~Q(user=post.user)).send_message(message)
            return True
        except Exception as e:
            # logging.exception('NewPost')
            return False