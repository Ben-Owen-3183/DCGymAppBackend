from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login.as_view()),
    path('user_data/', views.UserData.as_view())
]
