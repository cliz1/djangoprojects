# File: models.py
# Author: Nathaniel Clizbe (clizbe@bu.edu), 12/10/2024
# Description: All the database models for the project
from django.db import models

class Parent(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_intake = models.DateField()
    email_address = models.EmailField()
    home_address = models.TextField()
    phone_number = models.CharField(max_length=15)
    town_village = models.CharField(max_length=100)
    country_of_origin = models.CharField(max_length=100, default="None")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    current_grade = models.IntegerField()
    town_village = models.CharField(max_length=100)
    #school_district = models.CharField(max_length=100)
    country_of_origin = models.CharField(max_length=100)
    date_of_intake = models.DateField()
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name="children")
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class TutoringService(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="tutoring_sessions")
    date_of_contact = models.DateField()
    location_of_contact = models.CharField(max_length=200)
    session_focus = models.CharField(max_length=100)
    activity = models.TextField()
    length_of_session = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return f"Tutoring: {self.student.first_name} on {self.date_of_contact}"

class AdvocacyService(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="advocacy_sessions")
    length_of_contact = models.DecimalField(max_digits=4, decimal_places=2)
    description = models.TextField()
    date_of_contact = models.DateField()
    school_district = models.CharField(max_length=100)

    def __str__(self):
        return f"Advocacy: {self.student.first_name} on {self.date_of_contact}"
