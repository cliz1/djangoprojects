# File: urls.py
# Author: Nathaniel Clizbe (clizbe@bu.edu), 12/10/2024
# Description: URLS for the final project website (to navigate between pages and perform actions)
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import HomePageView, StudentSearchView, StudentDetailView, ParentSearchView, ParentDetailView, StudentUpdateView, ParentUpdateView, add_advocacy_service, add_tutoring_service, IntakeView, charts_view, DeleteServiceView, DeleteAdvocacyServiceView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path('search/', StudentSearchView.as_view(), name='student_search'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('parent_search/', ParentSearchView.as_view(), name='parent_search'),
    path('parent/<int:pk>/', ParentDetailView.as_view(), name='parent_detail'),
    path('student/<int:pk>/update/', StudentUpdateView.as_view(), name='student_update'),
    path('parent/<int:pk>/update/', ParentUpdateView.as_view(), name='parent_update'),
    path('student/<int:pk>/add_tutoring_service/', add_tutoring_service, name='add_tutoring_service'),
    path('student/<int:pk>/add_advocacy_service/', add_advocacy_service, name='add_advocacy_service'),
    path("login/", auth_views.LoginView.as_view(template_name="project/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path('intake/', IntakeView.as_view(), name='intake'),
    path('charts/', charts_view, name='charts'),
    path('delete_service/<int:pk>/', DeleteServiceView.as_view(), name='delete_service'),
    path('delete_adv_service/<int:pk>/', DeleteAdvocacyServiceView.as_view(), name='delete_adv_service'),

]
