from django import forms
from .models import Student, Parent

class StudentSearchForm(forms.Form):
    # Create the fields
    search_name = forms.CharField(max_length=100, required=False, label="Search by Name")
    country_of_origin = forms.ChoiceField(choices=[('', 'All')] + [(country, country) for country in Student.objects.values_list('country_of_origin', flat=True).distinct()], required=False, label="Country of Origin")
    current_grade = forms.ChoiceField(choices=[('', 'All')] + [(grade, grade) for grade in Student.objects.values_list('current_grade', flat=True).distinct()], required=False, label="Grade")
    town_village = forms.ChoiceField(choices=[('', 'All')] + [(town, town) for town in Student.objects.values_list('town_village', flat=True).distinct()], required=False, label="Town/Village")
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

class ParentUpdateForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['first_name', 'last_name', 'email_address', 'home_address', 'phone_number', 'town_village', 'country_of_origin']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
