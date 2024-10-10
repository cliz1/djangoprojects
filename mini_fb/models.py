from django.db import models

# Create your models here.

class Profile(models.Model):
    '''models the data atrributes of the mini FB profiles'''
    first_name = models.TextField(blank=False)
    last_name = models.TextField(blank=False)
    city = models.TextField(blank=False)
    email_address = models.TextField(blank=False)
    profile_image_url = models.URLField(blank=True)

    def __str__(self):
        '''Return a string representation of this object.'''

        return f'{self.first_name} , {self.last_name}'
    
    def get_status_messages(self):
        # Assuming StatusMessage has a ForeignKey to Profile
        return StatusMessage.objects.filter(profile=self).order_by('-timestamp')

class StatusMessage(models.Model):
    '''Encapsulate the idea of a Status Message.'''
    
    # data attributes of a Status Message:
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    message = models.TextField(blank=False)
    timestamp = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        '''Return a string representation of this Status Message object.'''
        return f'{self.message}'
       
