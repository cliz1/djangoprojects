from django.contrib import admin

# Register your models here.

# Register your models here.
from .models import Student, Parent, TutoringService, AdvocacyService
admin.site.register(Student)
admin.site.register(Parent)
admin.site.register(TutoringService)
admin.site.register(AdvocacyService)