from django.urls import path
from . import views
urlpatterns=[path('', views.dashboard, name='dashboard'), path('resume/<int:pk>/', views.resume_detail, name='resume_detail'), path('resume/<int:pk>/download/', views.download_resume, name='download_resume')]
