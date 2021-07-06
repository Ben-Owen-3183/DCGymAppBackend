from django.urls import path
from . import views

urlpatterns = [
    path('like_post/', views.LikePost.as_view()),
    path('like_comment/', views.LikeComment.as_view()),
    path('like_reply/', views.LikeReply.as_view()),
    path('new_post/', views.NewPost.as_view()),
    path('new_post_comment/', views.NewPostComment.as_view()),
    path('new_comment_reply/', views.NewCommentReply.as_view()),
    path('get_posts/', views.GetPosts.as_view()),
    path('get_posts_before/', views.GetPostBeforeDateTime.as_view()),
    # path('get_posts_after/', views.GetPostAfterDateTime.as_view()),
    path('delete_post/', views.DeletePost.as_view()),
    path('pin_post/', views.PinPost.as_view()),
]
