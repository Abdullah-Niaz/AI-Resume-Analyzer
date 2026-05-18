from django.core.management.base import BaseCommand
from apps.resumes.models import JobRole
ROLES = {
 'Frontend Developer':['HTML','CSS','JavaScript','TypeScript','React','accessibility','responsive design','UI','performance'],
 'Backend Developer':['Python','Django','REST API','PostgreSQL','Redis','Celery','Docker','authentication','scalability'],
 'Full Stack Developer':['Django','JavaScript','REST API','PostgreSQL','frontend','backend','Docker','deployment'],
 'Data Analyst':['SQL','Excel','Python','Power BI','Tableau','statistics','dashboard','data cleaning'],
 'Data Scientist':['Python','machine learning','pandas','NumPy','scikit-learn','statistics','modeling','visualization'],
 'DevOps Engineer':['Docker','CI/CD','Linux','Nginx','AWS','monitoring','Kubernetes','automation']
}
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for name, keywords in ROLES.items(): JobRole.objects.update_or_create(name=name, defaults={'keywords': keywords})
        self.stdout.write(self.style.SUCCESS('Job roles seeded'))
