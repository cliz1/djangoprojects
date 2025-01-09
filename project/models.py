# File: models.py
# Author: Nathaniel Clizbe (clizbe@bu.edu), 12/10/2024
# Description: All the database models for the project
from django.db import models
import csv
from datetime import datetime
#from .models import Parent, Student, TutoringService, AdvocacyService

class Parent(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_intake = models.DateField(null=True, blank=True)
    email_address = models.EmailField(null=True, blank=True)
    home_address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    town_village = models.CharField(max_length=100, null=True, blank=True)
    country_of_origin = models.CharField(max_length=100, default="None", null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Student(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField(null=True, blank=True)
    current_grade = models.IntegerField(null=True, blank=True)
    town_village = models.CharField(max_length=100, null=True, blank=True)
    #school_district = models.CharField(max_length=100)
    country_of_origin = models.CharField(max_length=100, null=True, blank=True)
    date_of_intake = models.DateField(null=True, blank=True)
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


def load_data(file_path):
    """
    Load data from a CSV file and populate the database.

    Args:
        file_path (str): Path to the CSV file.
    """
    count = 0
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            print(count)
            form_type = row.get('Choose Form Type', '').strip()

            if form_type == 'Intake':
                handle_intake(row)
            elif form_type == 'Advocacy contact':
                handle_advocacy_contact(row)
            elif form_type == 'Tutoring contact':
                handle_tutoring_contact(row)
            count+=1

def handle_intake(row):
    """Handle intake rows by creating parents and students."""
    parent = Parent.objects.create(
        date_of_intake = datetime.strptime(row["Timestamp"], "%m/%d/%Y %H:%M:%S").date(),
        first_name=row['Parent first name'],
        last_name=row['Parent last name'],
        phone_number=row['Phone number'],
        email_address=row.get('Email', ''),
        home_address=row['Address'],
        town_village=row['Town/ Village'],
        country_of_origin=row['Country of origin'],
    )

    create_student(
        date_of_intake = datetime.strptime(row["Timestamp"], "%m/%d/%Y %H:%M:%S").date(),
        parent=parent,
        first_name=row['Student first name'],
        last_name=row['Student last name'],
        date_of_birth=row['Date of birth'],
        grade=row['Current grade'],
        town_village=row['Town/ Village'],
        country_of_origin=row['Country of origin'],
    )

    for i in range(2, 4):  # Handles Student #2 and Student #3
        first_name_key = f'Student #{i} first name'
        if row.get(first_name_key):
            create_student(
                date_of_intake = datetime.strptime(row["Timestamp"], "%m/%d/%Y %H:%M:%S").date(),
                parent=parent,
                first_name=row[first_name_key],
                last_name=row[f'Student #{i} last name'],
                date_of_birth=row[f'Student #{i} date of birth'],
                grade=row[f'Student #{i} current grade'],
                town_village=row['Town/ Village'],
                country_of_origin=row['Country of origin']
            )


def create_student(date_of_intake, parent, first_name, last_name, date_of_birth, grade, town_village, country_of_origin):
    """Create a student and associate with the parent."""
    if grade=='K':
        grade = 0
    if grade =='OS':
        grade = 13
    if grade =='':
        grade = 13
    Student.objects.create(
        date_of_intake=date_of_intake,
        parent=parent,
        first_name=first_name,
        last_name=last_name,
        date_of_birth=parse_date(date_of_birth),
        current_grade=grade,
        town_village = '',
        country_of_origin = country_of_origin
    )


def handle_advocacy_contact(row):
    """Handle advocacy contact rows by adding services to existing students."""
    try:
        student = Student.objects.get(
            first_name=row['Student first nameC'],
            last_name=row['Student last nameC']
        )
    except Student.DoesNotExist:
        print(f"Student not found: {row['Student first name']} {row['Student last name']}")
        return

    if student.town_village=='':
        student.town_village = row['School districtC']
        student.save()

    AdvocacyService.objects.create(
        student=student,
        date_of_contact=parse_date(row['Date of contactC']),
        school_district=row['School districtC'],
        length_of_contact=row['Length of contactC'],
        description=row['Description of advocacy'],
    )


def handle_tutoring_contact(row):
    """Handle tutoring contact rows by adding services to existing students."""
    try:
        student = Student.objects.get(
            first_name=row['Student first nameB'],
            last_name=row['Student last nameB']
        )
    except Student.DoesNotExist:
        print(f"Student not found: {row['Student first name']} {row['Student last name']}")
        return

    if student.town_village=='':
        student.town_village = row['School districtB']
        student.save()

    TutoringService.objects.create(
        student=student,
        date_of_contact=parse_date(row['Date of contactB']),
        location_of_contact=row['Location of contact'],
        length_of_session=row['Length of session'],
        session_focus=row['Focus'],
        activity=row['Activity'],
    )


def parse_date(date_str):
    """Parse a date string into a datetime object."""
    try:
        return datetime.strptime(date_str, '%m/%d/%Y').date()
    except (ValueError, TypeError):
        return None

