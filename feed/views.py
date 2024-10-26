from rest_framework.views import APIView
from feed.models import Post, PostsToNotify, ReplyReplyLikes, CommentReplies, PostCommentLikes, PostComment, PostLikes
import logging
from user_account.models import UserAvatar
from login.models import CustomUser
from datetime import datetime
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from login.member_permission import IsActiveMember
from rest_framework.response import Response
from PIL import Image
from django.core.files.storage import FileSystemStorage
from datetime import date
from django.conf import settings
import vimeo
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice
from django.utils import timezone

# number of posts to be returned by default
POST_AMOUNT = 5


def post_to_json(post):
    return {
        'id': post.id,
        'user': user_to_json(post.user),
        'content': post.content,
        'image_url': '/media/post_images/' + post.image_name if post.image_name else '',
        'like_count': PostLikes.objects.filter(post=post).count(),  #post.like_count,
        'timestamp': post.timestamp,
        'pinned': post.pinned,
        'comments': comments_to_json(post),
        'video_id': post.video_id,
        'thumbnail_link': post.thumbnail_link
    }


def getUserAvatar(user_id):
    try:
        userAvatar = UserAvatar.objects.get(user=user_id)
        return userAvatar.image_name
    except:
        return ''


def str_to_date(str_date):
    date_split = str.split(str_date, '-')
    y = int(date_split[0])
    m = int(date_split[1])
    d = int(date_split[2])
    return date(y, m, d)


def should_be_pinned(post):
    current_date = str_to_date(date.isoformat(date.today()))
    diff = (current_date - post.timestamp).days
    if diff > post.pinned_time_days:
        return False
    return True


# unpins old pins and returns active pinned posts
def validate_pinned_posts(posts):
    valid_posts = []
    for post in posts:
        if post.pinned_timed and should_be_pinned(post):
            post.pinned = False
            post.save()
        else:
            valid_posts.append(post)
    return valid_posts


def user_to_json(user):
    return  {
        'id': str(user.id),
        'fName': user.first_name,
        'sName': user.last_name,
        'isSuperUser': user.is_superuser,
        'isStaff': False if user.hidden else user.is_staff,
        'avatarURL': getUserAvatar(user.id)
    }


def comment_to_json(comment):
    return {
        'id': comment.id,
        'user': user_to_json(comment.user),
        'post_id': comment.post.id,
        'text': comment.text,
        'like_count': PostCommentLikes.objects.filter(post_comment=comment).count(), # comment.like_count,
        'timestamp': comment.timestamp,
        'replies': replies_to_json(comment)
    }


def comments_to_json(post):
    try:
        comments = PostComment.objects.filter(post=post).order_by('like_count')
        comments_json = []
        for comment in comments:
            comments_json.append(comment_to_json(comment))
        return comments_json
    except Exception as e:
        return []


def reply_to_json(reply):
    return {
        'id': reply.id,
        'user': user_to_json(reply.user),
        'post_id': reply.post.id,
        'comment_id': reply.post_comment.id,
        'text': reply.text,
        'like_count': ReplyReplyLikes.objects.filter(comment_reply=reply).count(), # reply.like_count,
        'timestamp': reply.timestamp,
    }


def replies_to_json(comment):
    try:
        replies = CommentReplies.objects.filter(post_comment=comment).order_by('timestamp')
        replies_json = []
        for reply in replies:
            replies_json.append(reply_to_json(reply))
        return replies_json
    except Exception as e:
        logging.exception('replies_to_json')
        return []


def posts_to_json(posts):
    posts_json = []
    for post in posts:
        posts_json.append(post_to_json(post))
    return posts_json


class LikePost(APIView):

    def post(self, request):
        try:
            id = request.data['id']
            post = Post.objects.filter(id=id)[0]
            try:
                post_like = PostLikes.objects.filter(user=request.user, post=post)[0]
                post_like.delete()
            except Exception as e:
                PostLikes.objects.create(user=request.user, post=post)
            return Response({'post': post_to_json(post)})
        except Exception as e:
            logging.exception('LikePost')
            return Response({'errors': 'request failed'})


class LikeComment(APIView):

    def post(self, request):
        try:
            id = request.data['id']
            comment = PostComment.objects.filter(id=id)[0]
            try:
                comment_like = PostCommentLikes.objects.filter(user=request.user, post_comment=comment)[0]
                comment_like.delete()
            except Exception as e:
                PostCommentLikes.objects.create(user=request.user, post_comment=comment)
            return Response({'comment': comment_to_json(comment)})
        except Exception as e:
            logging.exception('LikeComment')
            return Response({'errors': 'request failed'})


class LikeReply(APIView):

    def post(self, request):
        try:
            id = request.data['id']
            reply = CommentReplies.objects.filter(id=id)[0]
            try:
                reply_like = ReplyReplyLikes.objects.filter(user=request.user, comment_reply=reply)[0]
                reply_like.delete()
            except Exception as e:
                ReplyReplyLikes.objects.create(user=request.user, comment_reply=reply)
            return Response({'reply': reply_to_json(reply)})
        except Exception as e:
            logging.exception('LikeReply')
            return Response({'errors': 'request failed'})


# Post
class NewPost(APIView):

    def is_image_file(self, extension):
        extension = '.' + extension
        extension_list = Image.registered_extensions()
        for el in extension_list:
            if extension == el:
                return True
        return False


    def store_post_image(self, request):
        content_type = request.FILES['image'].content_type
        file_extension = content_type.split('/')[1]

        if not self.is_image_file(file_extension):
            return Response({'errors': ['Uploaded file is not a recognised as a valid image format']})

        file_name = 'p_' + str(request.user.id) + '.' + file_extension
        fs = FileSystemStorage('media/post_images')
        # fs.delete(file_name)
        return fs.save(file_name, request.FILES['image'])


    def get_thumbnail(self, video_id):
        v = vimeo.VimeoClient(
            settings.VIMEO_KEYS['token'],
            settings.VIMEO_KEYS['key'],
            settings.VIMEO_KEYS['secret']
        )
        response = v.get('https://api.vimeo.com/videos/' + video_id + '/pictures')
        decoded_response = response.json()
        data = decoded_response['data']
        thumbnail_data = self.get_active_thumbnail_data(data)
        last = len(thumbnail_data['sizes']) - 1
        return thumbnail_data['sizes'][last]['link']


    def get_active_thumbnail_data(self, data):
        for el in data:
            if el['active']:
                return el
        raise Exception('no active thumbnail found...')


    def post(self, request):
        try:
            content = request.data['post_text']
            content = content.strip()
            if content == "":
                return Response({'errors': 'no post text entered'})
            file_name = ''
            thumbnail_link = ''
            video_id = ''
            if 'video_link' in request.data and request.data['video_link'] != '':
                video_link = request.data['video_link']
                split_str = video_link.split('/')
                video_id = split_str[3]
                try:
                    thumbnail_link = self.get_thumbnail(video_id)
                except Exception as e:
                    logging.exception('link')
                    return Response({'errors': 'Something went wrong adding the Vimeo video. Ensure you uploaded the correct link.'})
            elif 'image' in request.FILES:
                file_name = self.store_post_image(request)

            newPost = Post.objects.create(
                user=request.user,
                image_name=file_name,
                content=content,
                like_count=1,
                video_id=video_id,
                thumbnail_link=thumbnail_link,
                time_posted=datetime.now(),
                timestamp = datetime.now(tz=timezone.utc)
            )

            PostLikes.objects.create(user=request.user, post=newPost)

            admin_options = {
                'notify': True if request.data['notify'] == 'true' else False,
                'pin_post': True if request.data['pin_post'] == 'true' else False,
                'pin_post_time_limit': True if request.data['pin_post_time_limit'] == 'true' else False,
                'pin_post_days': request.data['pin_post_days'],
            }

            if  request.user.is_staff or request.user.is_superuser:
                newPost.pinned = admin_options['pin_post']
                if admin_options['notify']:
                    newPost.save()
                    PostsToNotify.objects.create(post=newPost)
                if admin_options['pin_post_time_limit']:
                    newPost.pinned_time_days = True
                    newPost.pinned_time_days = admin_options['pin_post_days']

            newPost.save()
            return Response({'success': 'true'})
        except Exception as e:
            logging.exception('NewPost')
            return Response({'errors': 'Something went wrong while uploading post. Please try again.'})


class NewPostComment(APIView):

    def post(self, request):
        try:
            text = request.data['text'].strip()
            post_id = request.data['post_id']
            post = Post.objects.get(id=post_id)
            comment = PostComment.objects.create(
                user=request.user,
                post=post,
                text=text,
                like_count=0,
            )
            return Response({'comment': comment_to_json(comment)})
        except Exception as e:
            logging.exception('NewPostComment')
            return Response({'error': ['something went wrong']})


class NewCommentReply(APIView):

    def post(self, request):
        try:
            text = request.data['text'].strip()
            post_id = request.data['post_id']
            comment_id = request.data['comment_id']
            post = Post.objects.get(id=post_id)
            comment = PostComment.objects.get(id=comment_id)
            reply = CommentReplies.objects.create(
                user=request.user,
                post=post,
                post_comment=comment,
                text=text,
                like_count=0,
            )
            return Response({'reply': reply_to_json(reply)})
        except Exception as e:
            logging.exception('NewPostReply')
            return Response({'error': ['something went wrong']})

# Get
class GetPosts(APIView):

    def post(self, request):

        try:
            user_posts_only = request.data['user_posts_only']
            pinned_posts = None
            if user_posts_only:
                pinned_posts = Post.objects.filter(
                    Q(pinned=True)
                    & Q(user=request.user)
                ).order_by('-timestamp')
            else:
                pinned_posts = Post.objects.filter(pinned=True).order_by('-timestamp')

            pinned_posts = validate_pinned_posts(pinned_posts)
            json_pinned_posts = posts_to_json(pinned_posts)
            new_page_length = (POST_AMOUNT - len(pinned_posts))
            posts = None
            if new_page_length > 0:
                if user_posts_only:
                    posts = Post.objects.filter(
                        Q(pinned=False)
                        & Q(user=request.user)
                    ).order_by('-timestamp')[:new_page_length]
                else:
                    posts = Post.objects.filter(pinned=False).order_by('-timestamp')[:new_page_length]

                json_posts = posts_to_json(posts)
                return Response({'posts': json_pinned_posts + json_posts})
            return Response({'posts': json_pinned_posts})
        except Exception as e:
            logging.exception('GetPosts')
            return Response({'errors': 'request failed'})


class GetPostBeforeDateTime(APIView):

    def post(self, request):
        try:
            user_posts_only = request.data['user_posts_only']
            datetime = request.data['datetime']
            post_id = request.data['post_id']

            posts = None

            if user_posts_only:
                posts = Post.objects.filter(
                    Q(timestamp__range=['1066-01-01', datetime])
                    & ~Q(id=post_id)
                    & Q(pinned=False)
                    & Q(user=request.user)
                ).order_by('-timestamp')[:POST_AMOUNT]
            else:
                posts = Post.objects.filter(
                    Q(timestamp__range=['1066-01-01', datetime])
                    & ~Q(id=post_id)
                    & Q(pinned=False)
                ).order_by('-timestamp')[:POST_AMOUNT]

            json_posts = posts_to_json(posts)
            return Response({'posts': json_posts})
        except Exception as e:
            logging.exception('GetPostBeforeDateTime')
            return Response({'errors': 'request failed'})


class DeletePost(APIView):

    def post(self, request):

        try:
            if request.user.is_staff or request.user.is_superuser:
                post_id = request.data['post_id']
                post = Post.objects.get(id=post_id)
                post.delete()
                return Response({'success': 'post deleted'})
            else:
                return Response({'errors': 'you do not have permission to perform this action'})
        except Exception as e:
            logging.exception('DeletePost')
            return Response({'errors': 'request failed'})


class PinPost(APIView):

    def post(self, request):

        try:
            if request.user.is_staff or request.user.is_superuser:
                post_id = request.data['post_id']
                post = Post.objects.get(id=post_id)
                if post.pinned:
                    post.pinned = False
                else:
                    post.pinned = True
                post.save()
                return Response({'post': post_to_json(post)})
            else:
                return Response({'errors': 'you do not have permission to perform this action'})
        except Exception as e:
            logging.exception('PinPost')
            return Response({'errors': 'request failed'})









#
