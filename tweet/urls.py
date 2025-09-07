from . import views
from django.urls import path
urlpatterns = [
    path('', views.tweet_list, name="tweet_list"),
    path('create/', views.tweet_create, name="tweet_create"),
    path('<int:tweet_id>/edit/', views.tweet_edit, name="tweet_edit"),
    path('<int:tweet_id>/delete/', views.tweet_delete, name='tweet_delete'),
    path('<int:tweet_id>/comment/', views.add_comment, name="add_comment"),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name="comment_delete"),
    path('comment/<int:comment_id>/edit/', views.comment_edit, name="comment_edit"),
    path('<int:tweet_id>/like/', views.like_tweet, name="like_tweet"),
    path('<int:tweet_id>/dislike/', views.dislike_tweet, name="dislike_tweet"),
    path('register/', views.register, name='register'),
    path('search/', views.search_view, name='search'),
]
