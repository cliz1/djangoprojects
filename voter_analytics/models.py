from django.db import models
from datetime import datetime
import csv
from django.db import IntegrityError

class Voter(models.Model):
    last_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    street_number = models.CharField(max_length=10)
    street_name = models.CharField(max_length=255)
    apartment_number = models.CharField(max_length=10, blank=True, null=True)
    zip_code = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    date_of_registration = models.DateField()
    party_affiliation = models.CharField(max_length=50)
    precinct_number = models.CharField(max_length=10)
    v20state = models.BooleanField(default=False)
    v21town = models.BooleanField(default=False)
    v21primary = models.BooleanField(default=False)
    v22general = models.BooleanField(default=False)
    v23town = models.BooleanField(default=False)
    voter_score = models.IntegerField()

    def __str__(self):
        return f"{self.first_name} {self.last_name} - Precinct {self.precinct_number}"

# Dictionary to map party abbreviations to full names
PARTY_MAPPING = {
    "D": "Democratic",
    "R": "Republican",
    "CC": "Constitution Party",
    "L": "Libertarian Party",
    "T": "Tea Party",
    "O": "Other",
    "G": "Green Party",
    "J": "Independent Party",
    "Q": "Reform Party",
    "FF": "Freedom Party"
}

def load_data(file_path):
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                party_affiliation = PARTY_MAPPING.get(row['Party Affiliation'].strip(), "Unknown")

                voter = Voter(
                    last_name=row['Last Name'].strip(),
                    first_name=row['First Name'].strip(),
                    street_number=row['Residential Address - Street Number'].strip(),
                    street_name=row['Residential Address - Street Name'].strip(),
                    apartment_number=row.get('Residential Address - Apartment Number', '').strip() or None,
                    zip_code=row['Residential Address - Zip Code'].strip(),
                    date_of_birth=datetime.strptime(row['Date of Birth'].strip(), "%Y-%m-%d").date(),
                    date_of_registration=datetime.strptime(row['Date of Registration'].strip(), "%Y-%m-%d").date(),
                    party_affiliation=party_affiliation,
                    precinct_number=row['Precinct Number'].strip(),
                    v20state=row['v20state'].strip() == 'Y',
                    v21town=row['v21town'].strip() == 'Y',
                    v21primary=row['v21primary'].strip() == 'Y',
                    v22general=row['v22general'].strip() == 'Y',
                    v23town=row['v23town'].strip() == 'Y',
                    voter_score=int(row['voter_score'].strip())
                )
                voter.save()
            except IntegrityError as e:
                print(f"Error saving voter {row['Voter ID Number']}: {e}")
            except Exception as e:
                print(f"Unexpected error with voter {row['Voter ID Number']}: {e}")

