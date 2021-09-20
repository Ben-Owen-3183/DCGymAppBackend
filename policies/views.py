from django.shortcuts import render
from django.template.loader import render_to_string
from django.views import View
from django.http import HttpResponse
# Create your views here.



class terms_and_conditions(View):
    def get(self, request):
        success_page = render_to_string("terms_and_conditions.html")
        return HttpResponse(success_page)


class privacy_policy(View):
    def get(self, request):
        success_page = render_to_string("privacy_policy.html")
        return HttpResponse(success_page)
