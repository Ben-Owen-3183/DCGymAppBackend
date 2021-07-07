from django.urls import path
from . import views

urlpatterns = [
    path('get/', views.GetTimeTable.as_view()),
]
