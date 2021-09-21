from django.urls import path
from . import views

urlpatterns = [
    # path('login', views.login, name='login'),
    # path('signup', views.signup, name='signup'),
    path('login/', views.login.as_view()),
    path('user_data/', views.userData.as_view())
]
