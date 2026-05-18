from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ResumeUploadForm
from .models import ResumeUpload, JobRole
from .tasks import start_resume_pipeline


def _analysis_context(latest_resume):
    if not latest_resume or not hasattr(latest_resume, 'analysis'):
        return {
            'latest_score': 82,
            'matched_keywords': ['Python', 'Django', 'DRF', 'PostgreSQL'],
            'missing_keywords': ['Kubernetes', 'GraphQL', 'AWS'],
            'suggestions': [
                'Tailor your resume to the job description',
                'Include relevant keywords and skills',
                'Use a clear and concise format',
            ],
        }

    ai_output = latest_resume.analysis.ai_output or {}
    matched = ai_output.get('matched_keywords') or []
    missing = ai_output.get('missing_keywords') or []
    weak_points = ai_output.get('weak_points') or []

    return {
        'latest_score': latest_resume.analysis.final_score,
        'matched_keywords': matched[:6] or ['Python', 'Django', 'DRF'],
        'missing_keywords': missing[:6] or ['Keywords pending'],
        'suggestions': weak_points[:4] or ['Improve bullet impact', 'Add measurable outcomes'],
    }


@login_required
def dashboard(request):
    form = ResumeUploadForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        resume = form.save(commit=False)
        resume.user = request.user
        resume.save()
        start_resume_pipeline(resume.id)
        return redirect('resume_detail', pk=resume.id)

    resumes = (
        ResumeUpload.objects
        .filter(user=request.user)
        .select_related('job_role')
        .order_by('-created_at')
    )
    latest_resume = resumes.first()
    context = {
        'form': form,
        'resumes': resumes,
        'job_roles': JobRole.objects.all().order_by('name'),
    }
    context.update(_analysis_context(latest_resume))
    return render(request, 'resumes/dashboard.html', context)


@login_required
def resume_detail(request, pk):
    resume = get_object_or_404(
        ResumeUpload.objects.select_related('job_role'),
        pk=pk,
        user=request.user,
    )
    return render(request, 'resumes/detail.html', {'resume': resume})


@login_required
def download_resume(request, pk):
    resume = get_object_or_404(ResumeUpload, pk=pk, user=request.user)
    if not resume.generated_pdf:
        raise Http404('PDF not ready')
    return FileResponse(
        open(resume.generated_pdf.path, 'rb'),
        as_attachment=True,
        filename='improved_resume.pdf',
    )
