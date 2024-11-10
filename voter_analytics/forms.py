from django import forms
from .models import Voter
from datetime import datetime

PARTY_CHOICES = [
        ('', 'Select Party'),  # Add this if you want an empty choice
        ('Democratic', 'Democratic'),
        ('Republican', 'Republican'),
        ('Constitution Party', 'Constitution Party'),
        ('Unknown', 'Unknown'),
        ('Independent Party', 'Independent Party'),
        ('Freedom Party', 'Freedom Party'),
        ('Libertarian Party', 'Libertarian Party'),
        ('Tea Party', 'Tea Party'),
        ('Green Party', 'Green Party'),
        ('Reform Party', 'Reform Party'),
        ('Other', 'Other'),
    
    ]

# Helper function to get years for date of birth filter
def get_year_choices(start_year=1900, end_year=None):
    end_year = end_year or datetime.now().year
    return [(str(year), str(year)) for year in range(start_year, end_year + 1)]

class VoterFilterForm(forms.Form):
    party_affiliation = forms.ChoiceField(choices=PARTY_CHOICES, required=False)
    min_date_of_birth = forms.ChoiceField(
        choices=[('', 'Any')] + get_year_choices(),
        required=False,
        label="Minimum Date of Birth (Year)"
    )
    max_date_of_birth = forms.ChoiceField(
        choices=[('', 'Any')] + get_year_choices(),
        required=False,
        label="Maximum Date of Birth (Year)"
    )
    voter_score = forms.ChoiceField(
        choices=[('', 'All')] + [(str(score), str(score)) for score in range(6)],
        required=False,
        label="Voter Score"
    )
    elections = forms.MultipleChoiceField(
        choices=[
            ('v20state', '2020 State Election'),
            ('v21town', '2021 Town Election'),
            ('v21primary', '2021 Primary Election'),
            ('v22general', '2022 General Election'),
            ('v23town', '2023 Town Election')
        ],
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Participated in Elections"
    )
