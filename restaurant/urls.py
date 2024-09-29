from django.urls import path
from . import views

urlpatterns = [
    path('main/', views.main_page, name='main'),
    path('order/', views.order_page, name='order'),
    path('confirmation/', views.confirmation_page, name='confirmation_page')
]

