from django.urls import path
from . import views

urlpatterns = [
    path('create_new_chat/', views.CreateNewChat.as_view()),
    path('get_chats/', views.GetChats.as_view()),
    path('set_chat_read/', views.ChatRead.as_view()),
    path('get_chat/', views.GetChat.as_view()),
    path('sync_chat/', views.SyncChats.as_view()),
]
