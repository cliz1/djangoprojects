## hw/urls.py
## description: URL pattenrs for the hw app

from django.urls import path
from django.conf import settings
from . import views

urlpatterns = [
    path(r'', views.home, name="home"),
    path(r'about', views.about, name = "about")
]