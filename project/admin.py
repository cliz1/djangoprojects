# File: admin.py
# Author: Nathaniel Clizbe (clizbe@bu.edu), 12/10/2024
# Description: Admin stuff for the project project


from django.contrib import admin

# Register your models here.

# Register your models here.
from .models import Student, Parent, TutoringService, AdvocacyService
admin.site.register(Student)
admin.site.register(Parent)
admin.site.register(TutoringService)
admin.site.register(AdvocacyService)