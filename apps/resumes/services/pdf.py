from pathlib import Path
from django.conf import settings
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch

def generate_resume_pdf(resume_id: int, content: str) -> str:
    out_dir = Path(settings.MEDIA_ROOT) / 'resumes' / 'generated'
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f'improved_resume_{resume_id}.pdf'
    c = canvas.Canvas(str(file_path), pagesize=letter)
    width, height = letter
    x, y = inch, height - inch
    c.setFont('Helvetica-Bold', 16); c.drawString(x, y, 'Improved Resume'); y -= 28
    c.setFont('Helvetica', 10)
    for paragraph in content.split('\n'):
        words = paragraph.split(); line=''
        for word in words:
            if len(line + ' ' + word) > 95:
                c.drawString(x, y, line); y -= 14; line = word
                if y < inch: c.showPage(); c.setFont('Helvetica', 10); y = height - inch
            else: line = (line + ' ' + word).strip()
        if line: c.drawString(x, y, line); y -= 16
        if y < inch: c.showPage(); c.setFont('Helvetica', 10); y = height - inch
    c.save()
    return str(file_path.relative_to(settings.MEDIA_ROOT))
