# Create your views here.

#from django.shortcuts import render
from django.shortcuts import render
from django.urls import reverse
from typing import Any
from .models import Profile
from django.views.generic import ListView, DetailView, CreateView
from .forms import CreateProfileForm, CreateStatusMessageForm

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

class CreateProfileView(CreateView):
    ''' View for a page to create a new profile '''
    form_class = CreateProfileForm 
    template_name = 'mini_fb/create_profile_form.html' 

    def form_valid(self, form):
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('show_all_profiles')

class CreateStatusMessageView(CreateView):
    '''
    A view to create a Status Message for a Profile.
    On GET: send back the form to display.
    On POST: read/process the form and save the new StatusMessage to the database.
    '''
    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"

    def get_context_data(self, **kwargs):
        # get the context data from the superclass
        context = super().get_context_data(**kwargs)

        # find the Profile identified by the PK from the URL pattern
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        
        # add the Profile to the context
        context['profile'] = profile
        return context

    def get_success_url(self):
        '''Return the URL to redirect to on success.'''
        # find the Profile identified by the PK from the URL pattern
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        return reverse('show_profile', kwargs={'pk': profile.pk})

    def form_valid(self, form):
        '''This method is called after the form is validated, 
        before saving data to the database.'''

        # find the Profile identified by the PK from the URL pattern
        profile = Profile.objects.get(pk=self.kwargs['pk'])

        # attach this Profile to the instance of the StatusMessage to set its FK
        form.instance.profile = profile  # like: status_message.profile = profile

        # delegate work to superclass version of this method
        return super().form_valid(form)