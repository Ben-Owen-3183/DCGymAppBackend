from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginV1.as_view()),

    # GET THIS FROM USER ACCOUNT OR SOMETHING...
    # path('user_data/', views.UserData.as_view())
]
