from django.urls import path
from . import views

urlpatterns = [
    # path('login', views.login, name='login'),
    # path('signup', views.signup, name='signup'),
    path('privacy_policy/', views.privacy_policy.as_view()),
    path('terms_and_conditions/', views.terms_and_conditions.as_view())
]
