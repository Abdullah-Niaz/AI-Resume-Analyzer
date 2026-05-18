from django.urls import path
from .api_views import UploadResumeAPIView, ResumeStatusAPIView, ResumeAnalysisAPIView, ResumeDownloadAPIView
urlpatterns=[path('upload-resume/', UploadResumeAPIView.as_view()), path('resume/<int:pk>/status/', ResumeStatusAPIView.as_view()), path('resume/<int:pk>/analysis/', ResumeAnalysisAPIView.as_view()), path('resume/<int:pk>/download/', ResumeDownloadAPIView.as_view())]
