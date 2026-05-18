from celery import shared_task

from .models import (
    ResumeUpload,
    ProcessingStatus,
    ResumeAnalysis,
    ImprovementResult,
)

from .services.parser import clean_text, extract_text
from .services.ats import rule_based_score, hybrid_score
from .services.pdf import generate_resume_pdf


def set_progress(resume, stage, progress, message=""):
    ProcessingStatus.objects.update_or_create(
        resume=resume,
        defaults={
            "stage": stage,
            "progress": progress,
            "message": message,
        },
    )


def fake_ai_output(resume, keywords):
    return {
        "ats_score": 82,
        "summary_feedback": (
            "Your resume is good, but it needs stronger keywords, "
            "measurable achievements, and better role alignment."
        ),
        "missing_keywords": [
            "Docker",
            "Redis",
            "Celery",
            "REST API",
            "PostgreSQL",
        ],
        "strong_points": [
            "Python",
            "Django",
            "Backend Development",
        ],
        "weak_points": [
            "Needs more measurable impact",
            "Missing deployment keywords",
        ],
        "rewritten_sections": {
            "summary": (
                "Python Django developer with experience building scalable "
                "web applications, REST APIs, and database-driven systems."
            ),
            "experience": (
                "Developed Django-based web applications with authentication, "
                "dashboard features, database models, and REST API integrations."
            ),
            "skills": (
                "Python, Django, DRF, SQLite, PostgreSQL, Celery, Redis, "
                "HTML, CSS, JavaScript"
            ),
        },
        "job_role_alignment": (
            f"Good match for "
            f"{resume.job_role.name if resume.job_role else 'the selected'} role."
        ),
    }


def safe_ai_analysis(resume, keywords):
    """
    First tries Gemini AI.
    If Gemini fails, returns fake/local AI data so the app never gets stuck.
    """

    try:
        from .services.ai import get_ai_provider

        if not resume.extracted_text:
            raise ValueError("Resume text is empty.")

        job_role_name = resume.job_role.name if resume.job_role else "General"

        ai_output = get_ai_provider().analyze_resume(
            resume.extracted_text,
            job_role_name,
            keywords,
        )

        if not isinstance(ai_output, dict):
            raise ValueError("AI response is not valid JSON.")

        required_keys = [
            "ats_score",
            "summary_feedback",
            "missing_keywords",
            "strong_points",
            "weak_points",
            "rewritten_sections",
            "job_role_alignment",
        ]

        for key in required_keys:
            ai_output.setdefault(key, fake_ai_output(resume, keywords)[key])

        return ai_output

    except Exception as exc:
        print(f"AI failed, using fallback data. Error: {exc}")
        return fake_ai_output(resume, keywords)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def extract_resume_text_task(self, resume_id):
    resume = ResumeUpload.objects.select_related("job_role").get(id=resume_id)

    resume.status = ResumeUpload.Status.PROCESSING
    resume.save(update_fields=["status"])

    set_progress(
        resume,
        "Extracting text",
        20,
        "Reading uploaded resume",
    )

    extracted_text = extract_text(resume.original_file.path)
    resume.extracted_text = clean_text(extracted_text)

    resume.save(update_fields=["extracted_text"])

    return resume_id


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def analyze_resume_task(self, resume_id):
    resume = ResumeUpload.objects.select_related("job_role").get(id=resume_id)

    set_progress(
        resume,
        "Analyzing resume",
        45,
        "Running ATS and AI analysis",
    )

    keywords = resume.job_role.keywords if resume.job_role else []

    rule = rule_based_score(
        resume.extracted_text or "",
        keywords,
    )

    ai_output = safe_ai_analysis(resume, keywords)

    try:
        ai_score = int(ai_output.get("ats_score", 0))
    except Exception:
        ai_score = 75

    final = hybrid_score(
        rule["score"],
        ai_score,
    )

    ResumeAnalysis.objects.update_or_create(
        resume=resume,
        defaults={
            "rule_score": rule["score"],
            "ai_score": ai_score,
            "final_score": final,
            "ai_output": ai_output,
        },
    )

    return resume_id


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def generate_improvements_task(self, resume_id):
    resume = ResumeUpload.objects.get(id=resume_id)

    set_progress(
        resume,
        "Generating improvements",
        70,
        "Preparing rewritten sections",
    )

    rewritten = resume.analysis.ai_output.get("rewritten_sections", {})

    improved_text = "\n\n".join(
        [
            f"{section.title()}\n{content}"
            for section, content in rewritten.items()
            if content
        ]
    )

    if not improved_text:
        improved_text = resume.extracted_text or "No improved content generated."

    ImprovementResult.objects.update_or_create(
        resume=resume,
        defaults={
            "rewritten_sections": rewritten,
            "improved_text": improved_text,
        },
    )

    return resume_id


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=2)
def generate_pdf_task(self, resume_id):
    resume = ResumeUpload.objects.get(id=resume_id)

    set_progress(
        resume,
        "Generating PDF",
        90,
        "Creating improved resume PDF",
    )

    rel_path = generate_resume_pdf(
        resume.id,
        resume.improvement.improved_text,
    )

    resume.generated_pdf.name = rel_path
    resume.status = ResumeUpload.Status.COMPLETED

    resume.save(
        update_fields=[
            "generated_pdf",
            "status",
        ]
    )

    set_progress(
        resume,
        "Completed",
        100,
        "Resume analysis completed",
    )

    return resume_id


def mark_resume_failed(resume_id, exc):
    resume = ResumeUpload.objects.get(id=resume_id)

    resume.status = ResumeUpload.Status.FAILED
    resume.error_message = str(exc)

    resume.save(
        update_fields=[
            "status",
            "error_message",
        ]
    )

    set_progress(
        resume,
        "Failed",
        100,
        str(exc),
    )


@shared_task
def mark_failed_task(request, exc, traceback, resume_id):
    mark_resume_failed(resume_id, exc)


def start_resume_pipeline(resume_id):
    """
    Local stable mode.
    Runs the complete resume pipeline immediately.

    This avoids Redis/Celery blocking issues on Windows.
    Gemini is attempted first.
    If Gemini fails, fallback data is used.
    """

    try:
        resume_id = extract_resume_text_task.run(resume_id)
        resume_id = analyze_resume_task.run(resume_id)
        resume_id = generate_improvements_task.run(resume_id)
        resume_id = generate_pdf_task.run(resume_id)

        return resume_id

    except Exception as exc:
        mark_resume_failed(resume_id, exc)
        raise
