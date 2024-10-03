from django.db import models

# Create your models here.

class Article(models.Model):
    '''Idea of one article by some author'''
    title = models.TextField(blank=False)
    author = models.TextField(blank=False)
    text = models.TextField(blank=False)
    published = models.DateTimeField(auto_now=True)

    def __str__(self):
        '''Return str representation of the object'''
        return f'{self.title} by {self.author}'