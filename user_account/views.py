from rest_framework.views import APIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from user_account.models import UserAvatar, PasswordResets, MembershipStatus, AwaitingActivation
from login.models import CustomUser
from django.core.files.storage import FileSystemStorage
from PIL import Image
from django.contrib.auth.hashers import make_password, check_password
import uuid
from datetime import date
from django.conf import settings
from django.utils.html import strip_tags
from django.core.mail import BadHeaderError, send_mail, EmailMultiAlternatives
from django.http import HttpResponse, HttpResponseRedirect
from django.views import View
from django.template.loader import render_to_string
from django.contrib.postgres.search import TrigramSimilarity, SearchVector, SearchQuery, SearchRank
import csv
import io
from django.db import transaction
from django.shortcuts import redirect
from firebase_admin.messaging import Message, Notification
from fcm_django.models import FCMDevice

def getUserAvatar(user_id):
    try:
        userAvatar = UserAvatar.objects.get(user=user_id)
        return userAvatar.image_name
    except:
        return ''


def user_to_json(user):
    return  {
        'id': user.id,
        'fName': user.first_name,
        'sName': user.last_name,
        'isSuperUser': user.is_superuser,
        'isStaff': False if user.hidden else user.is_staff,
        'avatarURL': getUserAvatar(user.id)
    }



class GetStaff(APIView):

    def get(self, request):
        staff = CustomUser.objects.filter(is_staff=True).order_by('-is_superuser')
        staff_list = []
        for s in staff:
            if not s.hidden:
                staff_list.append(user_to_json(s))
        return Response({'staff_list' : staff_list})


class UserSearch(APIView):

    def post(self, request):
        name = request.data['text']

        results = CustomUser.objects.annotate(
            similarity=TrigramSimilarity('first_name', name) + TrigramSimilarity('last_name', name),
        ).filter(similarity__gt=0.2).order_by('-similarity')[:20]


        response = []
        for user in results:
            if not user.hidden and request.user.id != user.id:
                response.append(user_to_json(user))
        return Response(response)


class PassChange(APIView):

    def validate_passwords(self, data):
        errors = [];
        if data['newPassword']:
            if data['newPassword'] != data['newPasswordConf']:
                errors.append('passwords do not match.')
        else:
            errors.append('You must enter a new password.')
        if len(data['newPassword']) < 8:
            errors.append('Your new password needs to be at least 8 characters.')
        if len(data['newPassword']) > 150:
            errors.append('Your new password cannot exceed 150 characters.')
        return errors

    def post(self, request):
        if request.user.check_password(request.data['currentPassword']) == False:
            return Response({'errors': ['Incorrect password. Please try again.']})

        errors = self.validate_passwords(request.data)
        if(errors):
            return Response({'errors': errors})

        try:
            new_password = make_password(request.data['newPassword'], salt=None, hasher='default')
            request.user.password = new_password
            request.user.save()
            return Response({'success': errors})
        except:
            return Response({'errors': ['Something went wrong changing your password. Your password has not been changed']})


class ConfirmPassReset(View):
    permission_classes = [AllowAny]

    def str_to_date(self, str_date):
        date_split = str.split(str_date, '-')
        y = int(date_split[0])
        m = int(date_split[1])
        d = int(date_split[2])
        return date(y, m, d)


    """
    Send verifcation email
    """
    def send_email(self, email_to, name, password):
        subject = 'New Password'
        email_from = 'dcgymapp@gmail.com'
        html_content = f"""
            <p>Hello {name},</p>
            <p>Your password has been reset to {password}</p>
            <p>After you login with your new password press the menu icon in the top right to
            open the app menu. From there press "settings" and choose "change password".
            You will then be able to set a new memorable password. You will need this generated password
            to perform this action so don't loose it.</p>
        """
        text_content = strip_tags(html_content)
        body = ''
        try:
            email = EmailMultiAlternatives(subject, body, email_from, [email_to])
            email.attach_alternative(html_content, "text/html")
            email.send()
        except BadHeaderError:
            print('Invalid header found.')


    def get(self, request, token, id):
        password_reset = None
        try:
            password_reset = PasswordResets.objects.get(user=id, v_token=token)
        except:
            return HttpResponse({"Could not find matching id and token. \nPossibly expired password reset.\nPlease try again"})

        if password_reset.locked:
            return HttpResponse({"This password reset token has already been used."})
        #password_reset.locked = True
        password_reset.save()
        current_date = self.str_to_date(date.isoformat(date.today()))
        diff = (current_date - password_reset.timestamp).days
        if diff > 7:
            password_reset.delete()
            return HttpResponse({'This password reset token has expired. Please make a new request to reset password'})

        user_account = None
        try:
            user_account = CustomUser.objects.get(id=password_reset.user)
        except:
            return HttpResponse({"This user account does not exist"})

        plain_text_password = ''
        try:
            plain_text_password = CustomUser.objects.make_random_password()
            hashed_password = make_password(plain_text_password, salt=None, hasher='default')
            user_account.password = hashed_password
            user_account.save()
        except:
            return HttpResponse({'errors': ['Something went wrong changing your password. Your password has not been changed']})

        user_account.save()
        password_reset.delete()
        name = user_account.first_name + ' ' + user_account.last_name

        self.send_email(user_account.email, name, plain_text_password)

        success_page = render_to_string("password_reset.html", {'name': name})
        return HttpResponse(success_page)


class PassReset(APIView):
    permission_classes = [AllowAny]

    """
    Send verifcation email
    """
    def send_verification_email(self, email_to, token, id, name):
        link = settings.SITE_URL + 'user/password/reset/' + str(id) + '/' + str(token)
        subject = 'Reset Password'
        email_from = 'dcgymapp@gmail.com'
        html_content = """
            <p>Hello """ + name + """,</p>
            <p>A password reset has been requested for this account</p>
            <p>If this is correct, click the link below to reset your password.</p>
            <a href=\"""" + link + """\">Reset Password</a>
        """
        text_content = strip_tags(html_content)
        body = ''
        email = EmailMultiAlternatives(subject, body, email_from, [email_to])
        try:
            email = EmailMultiAlternatives(subject, body, email_from, [email_to])
            email.attach_alternative(html_content, "text/html")
            email.send()
        except BadHeaderError:
            print('Invalid header found.')


    def post(self, request):
        email = request.data['email']
        user = None
        try:
            user = CustomUser.objects.get(email=email)
        except:
            return Response({'errors': ['The email entered is not recognised']})

        verifcation_token = uuid.uuid4()
        PasswordResets.objects.create(
            user=user.id,
            email=email,
            v_token=verifcation_token,
            timestamp=date.isoformat(date.today()),
            locked=False
        )
        name = user.first_name + ' ' + user.last_name
        self.send_verification_email(
            email, verifcation_token, user.id, name
        )
        return Response({'success'})


class Avatar(APIView):

    def is_image_file(self, extension):
        extension = '.' + extension
        extension_list = Image.registered_extensions()
        for el in extension_list:
            if extension == el:
                return True
        return False


    def post(self, request):
        content_type = request.FILES['image'].content_type
        file_extension = content_type.split('/')[1]

        if not self.is_image_file(file_extension):
            return Response({'errors': 'Uploaded file is not a recognised as a valid image format'})

        file_name = 'av_' + str(request.user.id) + '.' + file_extension
        fs = FileSystemStorage('media/avatars')
        # fs.delete(file_name)
        file = fs.save(file_name, request.FILES['image'])

        userAvatar = None
        try:
            userAvatar = UserAvatar.objects.get(user=request.user)
        except:
            userAvatar = UserAvatar.objects.create(user=request.user)

        userAvatar.image_name = file
        userAvatar.save()

        return Response({'url': userAvatar.image_name})


class ActivateAccount_Allow(View):

    def get(self, request, activation_request_id):
        if request.user.is_superuser == False:
            return HttpResponse({'you do not have permission for this action'}) 


        membership_status = None
        activation_request = None

        try:
            activation_request = AwaitingActivation.objects.get(id=activation_request_id)
        except:
            return HttpResponse({'This activation request no longer exists.'}) 

        try:
            membership_status = MembershipStatus.objects.filter(email=activation_request.email)[0]
            if membership_status == None:
                raise 'no member status object found'
        except:
            return HttpResponse({'membership status does not exist. You need to create one to activate this user.'}) 

        user = CustomUser.objects.get(email=membership_status.email)
        try:
            message = Message(
                notification=Notification(
                    title="Account Activation", 
                    body="Hi " + user.first_name + ", your account has been activated and you can now login!", 
                ),
            )
            devices = FCMDevice.objects.filter(user=user)
            devices.send_message(message)
        except:
            pass

        subject = 'Account Activation'
        email_from = 'dcgymapp@gmail.com'
        html_content = render_to_string("user_activated.html", {'name': user.first_name})
        text_content = strip_tags(html_content)
        body = ''
        try:
            email = EmailMultiAlternatives(subject, body, email_from, [user.email])
            email.attach_alternative(html_content, "text/html")
            email.send()
        except BadHeaderError:
            print('Invalid header found.')

        membership_status.active = True
        membership_status.save()
        activation_request.delete()

   
        
        return HttpResponseRedirect(settings.SITE_URL + 'admin/user_account/awaitingactivation/')
        

class ActivateAccount_Deny(View):
    def get(self, request, activation_request_id):
        if request.user.is_superuser == False:
            return HttpResponse({'you do not have permission for this action'}) 
            
        try:
            activation_request = AwaitingActivation.objects.get(id=activation_request_id)
            activation_request.delete()
        except:
            return HttpResponse({'This activation request no longer exists.'}) 

        return HttpResponseRedirect(settings.SITE_URL + 'admin/user_account/awaitingactivation/')