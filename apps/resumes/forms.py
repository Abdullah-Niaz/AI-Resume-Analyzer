from django import forms
from django.conf import settings
from .models import ResumeUpload

class ResumeUploadForm(forms.ModelForm):
    class Meta:
        model = ResumeUpload
        fields = ['job_role','original_file']
    def clean_original_file(self):
        f = self.cleaned_data['original_file']
        allowed = ['.pdf', '.docx']
        name = f.name.lower()
        if not any(name.endswith(ext) for ext in allowed):
            raise forms.ValidationError('Only PDF and DOCX files are allowed.')
        if f.size > settings.MAX_UPLOAD_MB * 1024 * 1024:
            raise forms.ValidationError(f'Maximum file size is {settings.MAX_UPLOAD_MB} MB.')
        return f
