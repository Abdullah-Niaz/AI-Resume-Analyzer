from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, views
from rest_framework.response import Response
from .models import ResumeUpload
from .serializers import ResumeUploadSerializer, ProcessingStatusSerializer, AnalysisSerializer
from .tasks import start_resume_pipeline

class UploadResumeAPIView(generics.CreateAPIView):
    serializer_class = ResumeUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    def perform_create(self, serializer):
        resume = serializer.save(user=self.request.user)
        start_resume_pipeline(resume.id)

class ResumeStatusAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        resume = get_object_or_404(ResumeUpload, pk=pk, user=request.user)
        data = {'resume_status': resume.status}
        if hasattr(resume, 'processing'):
            data.update(ProcessingStatusSerializer(resume.processing).data)
        return Response(data)

class ResumeAnalysisAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        resume = get_object_or_404(ResumeUpload, pk=pk, user=request.user)
        if not hasattr(resume, 'analysis'):
            return Response({'detail':'Analysis not ready'}, status=202)
        return Response(AnalysisSerializer(resume.analysis).data)

class ResumeDownloadAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, pk):
        resume = get_object_or_404(ResumeUpload, pk=pk, user=request.user)
        if not resume.generated_pdf:
            return Response({'detail':'PDF not ready'}, status=202)
        return FileResponse(open(resume.generated_pdf.path, 'rb'), as_attachment=True, filename='improved_resume.pdf')
