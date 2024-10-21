# Create your views here.

#from django.shortcuts import render
from django.shortcuts import render
from django.urls import reverse
from typing import Any
from .models import Profile, Image, StatusMessage
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm

class UpdateProfileView(UpdateView):
    '''A view to update a Profile.'''
    
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_success_url(self):
        '''Return the URL to redirect to after successfully updating the profile.'''
        # Redirect back to the updated profile's page
        return reverse('show_profile', kwargs={'pk': self.object.pk})

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
        form.instance.profile = profile

        sm = form.save()

        # handle image file uploads
        files = self.request.FILES.getlist('files')  # get the uploaded files from the form
        for file in files:
            # create a new Image object for each uploaded file
            image = Image(status_message=sm, image_file=file)
            image.save()  # save the Image object to the database

        # delegate work to superclass version of this method
        return super().form_valid(form)

class DeleteStatusMessageView(DeleteView):
    '''A view to delete a Status Message for a Profile.'''

    model = StatusMessage
    template_name = "mini_fb/delete_status_form.html"
    context_object_name = 'status_message'

    def get_success_url(self):
        '''Return the URL to redirect to on success.'''
        # Get the profile related to the status message being deleted
        #profile = Profile.objects.get(pk=self.kwargs['pk'])
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})
    
class UpdateStatusMessageView(UpdateView):
    model = StatusMessage
    template_name = "mini_fb/update_status_form.html"
    context_object_name = 'status_message'
    fields = ['message']  # Specify the fields to be updated

    def get_success_url(self):
        '''Return the URL to redirect to on success.'''
        # Redirect to the profile page related to the status message being updated
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})

