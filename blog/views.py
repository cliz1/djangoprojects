from django.shortcuts import render
from django.views.generic import ListView
from .models import *

# Create your views here.

class ShowAllView(ListView):
    '''view to show all articles '''
    model = Article
    template_name = 'blog/show_all.html'
    context_object_name = 'articles'
    