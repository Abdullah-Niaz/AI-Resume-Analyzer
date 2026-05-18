from django.conf import settings
from django.db import models
from django.utils import timezone

class JobRole(models.Model):
    name = models.CharField(max_length=80, unique=True)
    keywords = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return self.name

class ResumeUpload(models.Model):
    class Status(models.TextChoices):
        PENDING='pending','Pending'; PROCESSING='processing','Processing'; COMPLETED='completed','Completed'; FAILED='failed','Failed'
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    job_role = models.ForeignKey(JobRole, on_delete=models.SET_NULL, null=True)
    original_file = models.FileField(upload_to='resumes/originals/%Y/%m/')
    generated_pdf = models.FileField(upload_to='resumes/generated/%Y/%m/', blank=True, null=True)
    extracted_text = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f'{self.user} - {self.original_file.name}'

class ProcessingStatus(models.Model):
    resume = models.OneToOneField(ResumeUpload, on_delete=models.CASCADE, related_name='processing')
    stage = models.CharField(max_length=80, default='Queued')
    progress = models.PositiveSmallIntegerField(default=0)
    message = models.CharField(max_length=255, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

class ResumeAnalysis(models.Model):
    resume = models.OneToOneField(ResumeUpload, on_delete=models.CASCADE, related_name='analysis')
    rule_score = models.PositiveSmallIntegerField(default=0)
    ai_score = models.PositiveSmallIntegerField(default=0)
    final_score = models.PositiveSmallIntegerField(default=0)
    ai_output = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

class ImprovementResult(models.Model):
    resume = models.OneToOneField(ResumeUpload, on_delete=models.CASCADE, related_name='improvement')
    rewritten_sections = models.JSONField(default=dict)
    improved_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
