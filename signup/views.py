# DJANGO
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.core.validators import EmailValidator
from django.core.mail import BadHeaderError, send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.http import Http404

# DJANGO REST
from rest_framework.response import Response
from rest_framework.views import APIView

# STANDARD LIBRARY
import json
import re
import uuid
from datetime import date

# CUSTOM
from signup.models import PotentialUser
from login.models import CustomUser

class signup(APIView):
    """
    Validate names
    """
    def validate_names(self, errors, data):
        pattern = re.compile('^[a-zA-Z]+$')
        if not data['fName']:
            errors['name'].append('You must enter a first name.')
        else:
            if len(data['fName']) > 150:
                errors['name'].append('First name cannot exceed 150 characters.')
            if not re.search(pattern, data['fName']):
                errors['name'].append('First name must contain only letters.')

        if not data['sName']:
            errors['name'].append('You must enter a second name.')
        else:
            if len(data['sName']) > 150:
                errors['name'].append('Second name cannot exceed 150 characters.')
            if not re.search(pattern, data['sName']):
                errors['name'].append('Second name must contain only letters.')

        return errors

    """
    Validate password
    """
    def validate_passwords(self, errors, data):
        if data['password']:
            if data['password'] != data['passwordConf']:
                errors['password'].append('passwords do not match.')
        else:
            errors['password'].append('You must enter a password.')
        if len(data['password']) < 8:
            errors['password'].append('Your password needs to be at least 8 characters.')
        if len(data['password']) > 150:
            errors['password'].append('Your password cannot exceed 150 characters.')
        return errors

    """
    check if email exists
    """
    def email_available(self, email):
        try:
            User = get_user_model()
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            return True
        return False

    """
    Validate emails
    """
    def validate_email(self, errors, data):
        if data['email']:
            try:
                email_validator = EmailValidator()
                email_validator.__call__(data['email'])
            except:
                errors['email'].append('The email entered is not valid')
            if len(data['email']) > 150:
                errors['password'].append('Your email cannot exceed 150 characters.')
            if data['email'] != data['emailConf']:
                errors['email'].append('Emails do not match.')
            if not self.email_available(data['email']):
                errors['email'].append('Email is already in use.')
        else:
            errors['email'].append('You must enter an email.')

        return errors

    """
    Send verifcation email
    """
    def send_verification_email(self, email_to, token, id, name):
        link = settings.SITE_URL + 'verifyemail/' + str(id) + '/' + str(token)
        subject = 'Activate your account'
        email_from = 'noreply@compute-it.org.uk'
        html_content = render_to_string("email_verification_template.html", {'name': name, 'link': link})
        text_content = strip_tags(html_content)
        body = ''
        email = EmailMultiAlternatives(subject, body, email_from, [email_to])
        try:
            email = EmailMultiAlternatives(subject, body, email_from, [email_to])
            email.attach_alternative(html_content, "text/html")
            email.send()
        except BadHeaderError:
            print('Invalid header found.')


    def hello(self):
        print('hello')


    def post(self, request, *args, **kwargs):
        # print(request.data)
        errors = {'name': [], 'email': [], 'password': []}
        # validate passwords
        errors = self.validate_passwords(errors, request.data)

        errors = self.validate_names(errors, request.data)
        errors = self.validate_email(errors, request.data)


        if not errors['email'] and not errors['password'] and not errors['name']:
            user_is_member = True # check email exists on club manager database
            if user_is_member:
                hashed_password = make_password(request.data['password'], salt=None, hasher='default')
                verifcation_token = uuid.uuid4()
                potential_user = PotentialUser.objects.create(
                    first_name=request.data['fName'],
                    last_name=request.data['sName'],
                    email=request.data['email'],
                    password=hashed_password,
                    v_token=verifcation_token,
                    timestamp=date.isoformat(date.today()),
                    locked=False)

                self.send_verification_email(
                    request.data['email'],
                    verifcation_token,
                    potential_user.id,
                    (request.data['fName'] + ' ' + request.data['sName']))
            else:
                errors['email'].append(
                """
                    We were unable to link your email to an active gym membership.
                    Make sure you are using the same email you used to sign up to the gym.
                    If you are not already a member of David Corfields Gymnasium press the menu you icon in the top right and select Gym Membership.
                    From there, follow the signup instructions.
                """
                )
        # validate emails
        return JsonResponse({
            'errors': errors
        })




class verifyemail(View):


    def str_to_date(self, str_date):
        date_split = str.split(str_date, '-')
        y = int(date_split[0])
        m = int(date_split[1])
        d = int(date_split[2])
        return date(y, m, d)


    def get(self, request, token, id):

        print(id)
        print(token)
        new_user = None
        try:
            new_user = PotentialUser.objects.get(id=id, v_token=token)
        except:
            return HttpResponse({"Could not find matching id and token. \nPossibly expired signup. \nTry signing up again."})
        if new_user.locked:
            return HttpResponse({"This signup token has already been used."})
        new_user.locked = True
        new_user.save()
        print(new_user.timestamp)
        current_date = self.str_to_date(date.isoformat(date.today()))
        diff = (current_date - new_user.timestamp).days
        if diff > 7:
            new_user.delete()
            return HttpResponse({'This activation token has expired. Please sign up again to renew it.'})


        user_account = CustomUser.objects.create(
            first_name=new_user.first_name,
            last_name=new_user.last_name,
            email=new_user.email,
            password=new_user.password,
            is_staff=False
        )
        # user_account.password = new_user.password
        user_account.save()

        new_user.delete()
        name = user_account.first_name + ' ' + user_account.last_name
        success_page = render_to_string("email_verified.html", {'name': name})
        return HttpResponse(success_page)










#
