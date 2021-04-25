from django.urls import path
from . import views

urlpatterns = [
    # path('login', views.login, name='login'),
    # path('signup', views.signup, name='signup'),
    path('signup/', views.signup.as_view())
]
