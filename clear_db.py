from project.models import Student, Parent, TutoringService, AdvocacyService

Student.objects.all().delete()
Parent.objects.all().delete()
TutoringService.objects.all().delete()
AdvocacyService.objects.all().delete()
