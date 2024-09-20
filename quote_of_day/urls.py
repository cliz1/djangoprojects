## hw/urls.py
## description: URL pattenrs for the hw app

from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.main_page, name='main'),
    path('quote/', views.main_page, name='quote'),
    path('show_all/', views.show_all, name='show_all'),
    path('about/', views.about_page, name='about'),
]