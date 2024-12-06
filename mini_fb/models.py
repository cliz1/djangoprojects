from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone

# Create your models here.


class Profile(models.Model):
    '''models the data atrributes of the mini FB profiles'''
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    city = models.TextField(blank=False)
    email_address = models.TextField(blank=False)
    profile_image_url = models.URLField(blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #image_file = models.ImageField(blank=True) # an actual image

    def __str__(self):
        '''Return a string representation of this object.'''

        return f'{self.first_name} , {self.last_name}'
    
    def get_status_messages(self):
        # Assuming StatusMessage has a ForeignKey to Profile
        return StatusMessage.objects.filter(profile=self).order_by('-timestamp')
    
    def get_absolute_url(self):
        return reverse('show_profile', kwargs={'pk': self.pk})
    
    def get_friends(self):
        '''Return a list of Profile instances that are friends with this profile.'''
        friends_as_profile1 = Friend.objects.filter(profile1=self).values_list('profile2', flat=True)
        friends_as_profile2 = Friend.objects.filter(profile2=self).values_list('profile1', flat=True)
        friend_ids = list(friends_as_profile1) + list(friends_as_profile2)
        friends = Profile.objects.filter(id__in=friend_ids)
        return list(friends)
    
    def add_friend(self, other):
        '''method for adding a friend'''
        if self == other:
            return
        # check if a Friend relationship already exists in either direction
        friendship_exists = Friend.objects.filter(
            (Q(profile1=self) & Q(profile2=other)) | (Q(profile1=other) & Q(profile2=self))
        ).exists()

        if not friendship_exists:
            Friend.objects.create(profile1=self, profile2 = other, timestamp = timezone.now())
    
    def get_friend_suggestions(self):
         # get all profiles except the current profile
        profiles = Profile.objects.exclude(pk=self.pk)

        # get profiles that are friends with this profile
        friends = Friend.objects.filter(
            Q(profile1=self) | Q(profile2=self)
        ).values_list('profile1', 'profile2')

        # flatten the list of friends into a single list of Profile IDs
        friend_ids = set()
        for profile1, profile2 in friends:
            friend_ids.add(profile1)
            friend_ids.add(profile2)

        # exclude the friends from the profiles queryset
        suggestions = profiles.exclude(pk__in=friend_ids)

        return suggestions
    
    def get_news_feed(self):
        # get the list of friends
        friend_ids = Friend.objects.filter(
            Q(profile1=self) | Q(profile2=self)
        ).values_list('profile1', 'profile2')

        # flatten the list of friend IDs into a single list
        friends = set()
        for profile1, profile2 in friend_ids:
            if profile1 != self.pk:
                friends.add(profile1)
            if profile2 != self.pk:
                friends.add(profile2)

        # Add self to the list of profiles to fetch messages from
        friends.add(self.pk)

        # Get all status messages for the profile and its friends
        status_messages = StatusMessage.objects.filter(
            profile__in=friends
        ).order_by('-timestamp')  # Most recent first

        return status_messages


class StatusMessage(models.Model):
    '''Encapsulate the idea of a Status Message.'''
    
    # data attributes of a Status Message:
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    message = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        '''Return a string representation of this Status Message object.'''
        return f'{self.message}'
    
    def get_images(self):
        '''Return all Images associated with this StatusMessage.'''
        return Image.objects.filter(status_message=self)

class Image(models.Model):
    '''Encapsulate the idea of an Image related to a Status Message.'''
    
    status_message = models.ForeignKey(StatusMessage, on_delete=models.CASCADE)
    image_file = models.ImageField(upload_to='images/')
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        '''Return a string representation of this Image object.'''
        return f'Image for StatusMessage {self.status_message.id}'


class Friend(models.Model):
    '''Encapsulates the idea of a Friend or and edge between two Profile nodes'''
    profile1 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile1")
    profile2 = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="profile2")
    timestamp = models.DateTimeField(auto_now=True)

    def __str__(self):
        '''Return a string representation of this Friend relationship.'''
        return f'{self.profile1} & {self.profile2}'
