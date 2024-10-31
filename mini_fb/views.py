# Create your views here.

#from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from typing import Any
from .models import Profile, Image, StatusMessage
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .forms import CreateProfileForm, CreateStatusMessageForm, UpdateProfileForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User

class UpdateProfileView(LoginRequiredMixin, UpdateView):
    '''A view to update a Profile.'''
    
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'mini_fb/update_profile_form.html'

    def get_login_url(self):
        return reverse_lazy('login')

    def get_success_url(self):
        '''Return the URL to redirect to after successfully updating the profile.'''
        # Redirect back to the updated profile's page
        profile = self.get_object()
        return reverse('show_profile', kwargs={'pk': profile.pk})
    
    def get_object(self):
        ''' querying for the Profile object related to the logged-in user'''
        return get_object_or_404(Profile, user=self.request.user)


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
        # Reconstruct the UserCreationForm with POST data
        user_form = UserCreationForm(self.request.POST)

        if user_form.is_valid():
            user = user_form.save()

            # Attach the user to the Profile instance
            profile = form.save(commit=False)  
            profile.user = user  # Associate the new user with the profile
            profile.save()  

            return super().form_valid(form)

        # If the UserCreationForm is invalid, re-render the form with errors
        context = self.get_context_data(form=form)
        context['user_form'] = user_form  
        return self.render_to_response(context)
    
    def get_success_url(self):
        return reverse('show_all_profiles')
    
    def get_context_data(self, **kwargs):
        # Call the superclass version to get the context
        context = super().get_context_data(**kwargs)
        
        # Create an instance of UserCreationForm and add it to the context
        context['user_form'] = UserCreationForm()
        
        return context

class CreateStatusMessageView(LoginRequiredMixin, CreateView):
    '''
    A view to create a Status Message for a Profile.
    On GET: send back the form to display.
    On POST: read/process the form and save the new StatusMessage to the database.
    '''
    form_class = CreateStatusMessageForm
    template_name = "mini_fb/create_status_form.html"

    def get_login_url(self):
        return reverse_lazy('login')

    def get_context_data(self, **kwargs):
        # get the context data from the superclass
        context = super().get_context_data(**kwargs)

        # find the Profile identified by the PK from the URL pattern
        profile = self.get_object()
        
        # add the Profile to the context
        context['profile'] = profile
        return context

    def get_success_url(self):
        '''Return the URL to redirect to on success.'''
        # find the Profile identified by the PK from the URL pattern
        profile = self.get_object()
        return reverse('show_profile', kwargs={'pk': profile.pk})

    def form_valid(self, form):
        '''This method is called after the form is validated, 
        before saving data to the database.'''

        # find the Profile identified by the PK from the URL pattern
        profile = self.get_object()

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
    
    def get_object(self):
        ''' querying for the Profile object related to the logged-in user'''
        return get_object_or_404(Profile, user=self.request.user)

class DeleteStatusMessageView(LoginRequiredMixin, DeleteView):
    '''A view to delete a Status Message for a Profile.'''

    model = StatusMessage
    template_name = "mini_fb/delete_status_form.html"
    context_object_name = 'status_message'

    def get_login_url(self):
        return reverse_lazy('login')

    def get_success_url(self):
        '''Return the URL to redirect to on success.'''
        # find the Profile identified by the PK from the URL pattern
        #profile = self.get_object()
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})
    
class UpdateStatusMessageView(LoginRequiredMixin, UpdateView):
    model = StatusMessage
    template_name = "mini_fb/update_status_form.html"
    context_object_name = 'status_message'
    fields = ['message']  # Specify the fields to be updated

    def get_login_url(self):
        return reverse_lazy('login')

    def get_success_url(self):
        '''Return the URL to redirect to on success.'''
        # Redirect to the profile page related to the status message being updated
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})
    
  

class CreateFriendView(LoginRequiredMixin, View):
    def get_login_url(self):
        return reverse_lazy('login')
    def dispatch(self, request, *args, **kwargs):
        # get the primary keys from the URL parameters
        other_pk = self.kwargs['other_pk']

         # retrieve the profiles
        profile = self.get_object()
        other_profile = get_object_or_404(Profile, pk=other_pk)

        # add the friend if they aren’t already friends
        profile.add_friend(other_profile)

        # redirect back to the profile page
        return redirect('show_profile', pk=profile.pk)
    
    def get_object(self):
        ''' querying for the Profile object related to the logged-in user'''
        return get_object_or_404(Profile, user=self.request.user)

class ShowFriendSuggestionsView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'mini_fb/friend_suggestions.html'
    context_object_name = 'profile'

    def get_login_url(self):
        return reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_object()
        context['suggestions'] = profile.get_friend_suggestions() 
        return context
    
    def get_object(self):
        ''' querying for the Profile object related to the logged-in user'''
        return get_object_or_404(Profile, user=self.request.user)
    
class ShowNewsFeedView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'mini_fb/news_feed.html'
    context_object_name = 'profile'

    def get_login_url(self):
        return reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_messages'] = self.object.get_news_feed()  # call the get_news_feed method
        return context
    
    def get_object(self):
        ''' querying for the Profile object related to the logged-in user'''
        return get_object_or_404(Profile, user=self.request.user)
    
