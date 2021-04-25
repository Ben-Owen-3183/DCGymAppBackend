from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from django.core.validators import EmailValidator
import django.contrib.auth.hashers
import json
import re
from django.core.mail import BadHeaderError, send_mail


class signup(APIView):


    """
    Validate names
    """
    def validate_names(self, errors):
        if not request.data['fName']:
            errors['name'].append('You must enter a first name.')
        if not request.data['sName']:
            errors['name'].append('You must enter a second name.')
        if len(request.data['fName']) > 150:
            errors['name'].append('First name cannot exceed 150 characters.')
        if len(request.data['sName']) > 150:
            errors['name'].append('Second name cannot exceed 150 characters.')
        pattern = re.compile('^[a-zA-Z]+$')
        if re.search(pattern, request.data['fName']):
            errors['name'].append('First name must contain only letters.')
        if re.search(pattern, request.data['sName']):
            errors['name'].append('Second name must contain only letters.')


    """
    Validate password
    """
    def validate_passwords(self, errors):
        if request.data['password']:
            if request.data['password'] != request.data['passwordConf']:
                errors['password'].append('passwords do not match.')
        else:
            errors['password'].append('You must enter a password.')
        if len(request.data['password']) < 8:
            errors['password'].append('Your password needs to be at least 8 characters.')
        if len(request.data['password']) > 150:
            errors['password'].append('Your password cannot exceed 150 characters.')


    """
    Validate emails
    """
    def validate_emails(self):
        if request.data['email']:
            try:
                email_validator = EmailValidator()
                email_validator.__call__(request.data['email'])
            except:
                errors['email'].append('The email entered is no valid')
            if len(request.data['email']) > 150:
                errors['password'].append('Your email cannot exceed 150 characters.')
            if request.data['email'] != request.data['emailConf']:
                errors['email'].append('Emails do not match.')
        else:
            errors['email'].append('You must enter an email.')


    """
    Send verifcation email
    """
    def send_verification_email(self, email_to):
        subject = 'Activate your account'
        email_from = 'noreply@compute-it.org.uk'
        body = 'hello'
        try:
            send_mail(subject, body, email_from, [email_to])
        except BadHeaderError:
            print('Invalid header found.')


    def hello(self):
        print('hello')


    def post(self, request, *args, **kwargs):
        print(request.data)
        self.hello()
        self.send_verification_email('ben.owen@compute-it.org.uk')
        return JsonResponse({})
        errors = {'name': [], 'email': [], 'password': []}
        # validate passwords
        errors = self.validate_passwords(errors)
        errors = self.validate_names(errors)
        errors = self.validate_email(errors)


        if not errors['email'] and not errors['password'] and not errors['name']:
            user_is_member = True # check email exists on club manager database
            if user_is_member:
                hashed_password = make_password(request.data['password'], salt=None, hasher='default')
                potential_user = PotentialUser(
                    first_name=request.data['fName'],
                    last_name=request.data['sName'],
                    email=request.data['email'],
                    password=hashed_password,
                    clubmanager_id='clubmanger id')
                # send verifcation email
                # create potential user
                #  PBKDF2 algorithm with a SHA256 hash



        # validate emails
        return JsonResponse({
            'errors': errors
        })
