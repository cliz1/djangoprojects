from django.shortcuts import render

# Create your views here.

#from django.shortcuts import render
from django.shortcuts import render
from .models import Profile
from django.views.generic import ListView, DetailView

class ShowAllProfilesView(ListView):
    '''Create a subclass of ListView to display all mini_fb Profiles.'''
    model = Profile # retrieve objects of type Article from the database
    template_name = 'mini_fb/show_all_profiles.html'
    context_object_name = 'profiles' # how to find the data in the template file


class ProfileView(DetailView):
    '''Display one Profile selected by PK'''
    model = Profile # the model to display
    template_name = "mini_fb/show_profile.html"
    context_object_name = "profile"