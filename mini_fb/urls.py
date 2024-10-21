## mini_fb/urls.py
## description: URL patterns for the mini_fb app

from django.urls import path
from django.conf import settings
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
    path('profile/<int:pk>/create_status/', CreateStatusMessageView.as_view(), name='create_status'),
    #url pattern for updating a profile 
    path("profile/<int:pk>/update/", UpdateProfileView.as_view(), name='update_profile'),  
    #url pattern for deleting a statusmessage 
    path("status/<int:pk>/delete/", DeleteStatusMessageView.as_view(), name='delete_status_message'), 
    #url pattern for updating a statusmessage 
    path("status/<int:pk>/update/", UpdateStatusMessageView.as_view(), name='update_status')

]