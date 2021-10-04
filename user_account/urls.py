from django.urls import path
from . import views
from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet



urlpatterns = [
    path('avatar/', views.Avatar.as_view()),
    path('password/change/', views.PassChange.as_view()),
    path('password/reset/', views.PassReset.as_view()),
    path('password/reset/<int:id>/<uuid:token>', views.ConfirmPassReset.as_view()),
    path('search/', views.UserSearch.as_view()),
    path('list_staff/', views.GetStaff.as_view()),
    path('upload_user_data/', views.UploadUserData.as_view()),
    path('devices/', FCMDeviceAuthorizedViewSet.as_view({'post': 'create'}), name='create_fcm_device'),
]
