# File: views.py
# Author: Nathaniel Clizbe (clizbe@bu.edu), 12/10/2024
# Description: A bunch of forms to be used by the views

from django import forms
from .models import Student, Parent
from django.utils import timezone

class StudentSearchForm(forms.Form):
    # Create the fields
    search_name = forms.CharField(max_length=100, required=False, label="Search by Name")
    country_of_origin = forms.ChoiceField(choices=[('', 'All')] + [(country, country) for country in Student.objects.values_list('country_of_origin', flat=True).distinct()], required=False, label="Country of Origin")
    current_grade = forms.ChoiceField(choices=[('', 'All')] + [(grade, grade) for grade in Student.objects.values_list('current_grade', flat=True).distinct()], required=False, label="Grade")
    town_village = forms.ChoiceField(choices=[('', 'All')] + [(town, town) for town in Student.objects.values_list('town_village', flat=True).distinct()], required=False, label="School District")
    #school_district = forms.ChoiceField(choices=[('', 'All')] + [(district, district) for district in Student.objects.values_list('school_district', flat=True).distinct()], required=False, label="School District")
    time_period = forms.ChoiceField(
        choices=[
            ('', 'Any Time'),
            ('2_weeks', 'Last 2 Weeks'),
            ('6_months', 'Last 6 Months'),
            ('1_year', 'Last 1 Year')
        ],
        required=False,
        label="Time Period"
    )

class ParentSearchForm(forms.Form):
    search_name = forms.CharField(max_length=100, required=False, label="Search by Name")
    town_village = forms.ChoiceField(
        choices=[('', 'All')] + [(town, town) for town in Parent.objects.values_list('town_village', flat=True).distinct()],
        required=False,
        label="Town/Village"
    )

class StudentUpdateForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'date_of_birth', 'current_grade', 'town_village', 'country_of_origin', 'parent']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['town_village'].label = 'School District'

class ParentUpdateForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['first_name', 'last_name', 'email_address', 'home_address', 'phone_number', 'town_village', 'country_of_origin']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['first_name', 'last_name', 'date_of_intake', 'email_address', 'home_address', 'phone_number', 'town_village']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_of_intake'].required = False
        self.fields['email_address'].required = False
        self.fields['home_address'].required = False
        self.fields['phone_number'].required = False
        self.fields['town_village'].required = False
        self.fields['date_of_intake'].initial = timezone.now().date()
    

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['date_of_intake', 'first_name', 'last_name', 'date_of_birth', 'current_grade', 'town_village', 'country_of_origin', 'parent']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['date_of_intake'].required = False
        self.fields['date_of_birth'].required = False
        self.fields['current_grade'].required = False
        self.fields['town_village'].required = False
        self.fields['country_of_origin'].required = False
        self.fields['date_of_intake'].initial = timezone.now().date()

        # Set custom labels for the fields
        self.fields['date_of_intake'].label = 'Date of Intake'
        self.fields['first_name'].label = 'First Name'
        self.fields['last_name'].label = 'Last Name'
        self.fields['date_of_birth'].label = 'Date of Birth'
        self.fields['current_grade'].label = 'Current Grade'
        self.fields['town_village'].label = 'School District'
        self.fields['country_of_origin'].label = 'Country of Origin'
        self.fields['parent'].label = 'Parent'

class ChartsFilterForm(forms.Form):
    town_village = forms.ModelMultipleChoiceField(
        queryset=Student.objects.values_list('town_village', flat=True).distinct(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Student School District"
    )
    school_level = forms.MultipleChoiceField(
        choices=[
            ('High School', 'High School'),
            ('Middle School', 'Middle School'),
            ('Elementary', 'Elementary')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Student School Level"
    )

    time_range = forms.ChoiceField(
        choices=[
            ('2weeks', 'Last 2 Weeks'),
            ('6months', 'Last 6 Months'),
            ('1year', 'Last 1 Year'),
        ],
        required=False,
        label="Time Range"
    )