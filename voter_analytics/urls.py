from django.urls import path
from .views import VoterListView
from . import views

urlpatterns = [
    path('', VoterListView.as_view(), name='voters'),
    path('voter/<int:pk>/', views.VoterDetailView.as_view(), name='voter'),
    path('graphs/', views.VoterGraphsView.as_view(), name='graphs')
]