# Generated scaffold migration
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name='JobRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True)),
                ('keywords', models.JSONField(default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ResumeUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_file', models.FileField(upload_to='resumes/originals/%Y/%m/')),
                ('generated_pdf', models.FileField(blank=True, null=True, upload_to='resumes/generated/%Y/%m/')),
                ('extracted_text', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('error_message', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('job_role', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='resumes.jobrole')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='resumes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ImprovementResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rewritten_sections', models.JSONField(default=dict)),
                ('improved_text', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resume', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='improvement', to='resumes.resumeupload')),
            ],
        ),
        migrations.CreateModel(
            name='ProcessingStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stage', models.CharField(default='Queued', max_length=80)),
                ('progress', models.PositiveSmallIntegerField(default=0)),
                ('message', models.CharField(blank=True, max_length=255)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resume', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='processing', to='resumes.resumeupload')),
            ],
        ),
        migrations.CreateModel(
            name='ResumeAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rule_score', models.PositiveSmallIntegerField(default=0)),
                ('ai_score', models.PositiveSmallIntegerField(default=0)),
                ('final_score', models.PositiveSmallIntegerField(default=0)),
                ('ai_output', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resume', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='analysis', to='resumes.resumeupload')),
            ],
        ),
    ]
