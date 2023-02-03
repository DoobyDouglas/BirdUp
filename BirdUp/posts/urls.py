from django.urls import path

from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('group/<slug:slug>/', views.GroupPosts.as_view(), name='group_list'),
    path('profile/<str:username>/', views.Profile.as_view(), name='profile'),
    path('posts/<int:post_id>/',
         views.PostDetail.as_view(), name='post_detail'),
    path('create/', views.PostCreate.as_view(), name='create'),
    path('posts/<int:post_id>/edit/', views.PostEdit.as_view(),
         name='post_edit'),
    path('posts/<int:post_id>/comment/',
         views.AddComment.as_view(), name='add_comment'),
    path('follow/', views.FollowIndex.as_view(), name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.ProfileFollow.as_view(),
        name='profile_follow'
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.ProfileUnfollow.as_view(),
        name='profile_unfollow'
    ),
    path('group_create/', views.GroupCreate.as_view(), name='group_create'),
    path('groups/', views.GroupIndex.as_view(), name='group_index'),
    path('group/<slug:slug>/follow/',
         views.GroupFollow.as_view(), name='group_follow'),
    path('group/<slug:slug>/unfollow/',
         views.GroupUnfollow.as_view(), name='group_unfollow'),
    path('group/<slug:slug>/create/',
         views.GroupPostCreate.as_view(), name='group_post'),
    path('group/<slug:slug>/followers/',
         views.GroupFollowers.as_view(), name='group_followers'),
    path('post_search/',
         views.PostSearchView.as_view(), name='post_search'),
    path('user_search/',
         views.UserSearchView.as_view(), name='user_search'),
    path('group_search/',
         views.GroupSearchView.as_view(), name='group_search'),
]
