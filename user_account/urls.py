from django.urls import path
from . import views

urlpatterns = [
    path('avatar/', views.Avatar.as_view()),
    path('password/change/', views.PassChange.as_view()),
    path('password/reset/', views.PassReset.as_view()),
    path('password/reset/<int:id>/<uuid:token>', views.ConfirmPassReset.as_view()),
    path('search/', views.UserSearch.as_view()),
    path('list_staff/', views.GetStaff.as_view()),
    path('upload_user_data/', views.UploadUserData.as_view()),
]
