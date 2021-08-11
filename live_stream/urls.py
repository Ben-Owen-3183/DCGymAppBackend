from django.urls import path
from . import views

urlpatterns = [
    path('live_streams/', views.GetLiveStream.as_view()),
    path('videos/', views.GetVideos.as_view()),
]
