from rest_framework import serializers
from .models import ResumeUpload, ResumeAnalysis, ProcessingStatus
from .forms import ResumeUploadForm

class ResumeUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeUpload
        fields = ['id','job_role','original_file','status','created_at']
        read_only_fields = ['id','status','created_at']
    def validate_original_file(self, value):
        form = ResumeUploadForm(files={'original_file': value}, data={'job_role': self.initial_data.get('job_role')})
        if not form.is_valid(): raise serializers.ValidationError(form.errors.get('original_file', ['Invalid file'])[0])
        return value

class ProcessingStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcessingStatus
        fields = ['stage','progress','message','updated_at']

class AnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeAnalysis
        fields = ['rule_score','ai_score','final_score','ai_output','created_at']
