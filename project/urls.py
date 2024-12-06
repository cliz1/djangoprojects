from django.urls import path
from .views import HomePageView, StudentSearchView, StudentDetailView, ParentSearchView, ParentDetailView, StudentUpdateView, ParentUpdateView, add_advocacy_service, add_tutoring_service

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
]
