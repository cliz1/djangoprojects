## mini_fb/urls.py
## description: URL patterns for the mini_fb app

from django.urls import path
from django.conf import settings
from django.contrib.auth import views as auth_views
from . import views
from .views import * # our view class definition 
urlpatterns = [
    # map the URL (empty string) to the view
    path('', ShowAllProfilesView.as_view(), name='show_all_profiles'), # generic class-based view
    # URL pattern to show a specific profile by primary key (pk)
    path('profile/<int:pk>/', ProfileView.as_view(), name='show_profile'),
    #url pattern for creating a profile
    path('create_profile/', CreateProfileView.as_view(), name='create_profile'),
    #url pattern for creating a status
    path('profile/create_status/', CreateStatusMessageView.as_view(), name='create_status'),
    #url pattern for updating a profile 
    path("profile/update/", UpdateProfileView.as_view(), name='update_profile'),  
    #url pattern for deleting a statusmessage 
    path("status/<int:pk>/delete/", DeleteStatusMessageView.as_view(), name='delete_status_message'), 
    #url pattern for updating a statusmessage 
    path("status/<int:pk>/update/", UpdateStatusMessageView.as_view(), name='update_status'),
    #url pattern for adding a friendship
    path('profile/add_friend/<int:other_pk>/', CreateFriendView.as_view(), name='add_friend'),
    #url pattern for showing friend suggestions
    path('profile/friend_suggestions/', ShowFriendSuggestionsView.as_view(), name='friend_suggestions'),
    #url pattern for showing a profile's news feed
    path('profile/news_feed/', ShowNewsFeedView.as_view(), name='show_news_feed'),
    #url for login
    path('login/', auth_views.LoginView.as_view(template_name='mini_fb/login.html'), name='login'),
    #url for logout
    path('logout/', auth_views.LogoutView.as_view(template_name='mini_fb/logged_out.html'), name='logout')

]