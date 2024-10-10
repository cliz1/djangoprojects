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
    path('profile/<int:pk>/', ProfileView.as_view(), name='show_profile')
]

