from django.contrib import admin
from .models import JobRole, ResumeUpload, ProcessingStatus, ResumeAnalysis, ImprovementResult
admin.site.register(JobRole)
admin.site.register(ResumeUpload)
admin.site.register(ProcessingStatus)
admin.site.register(ResumeAnalysis)
admin.site.register(ImprovementResult)
