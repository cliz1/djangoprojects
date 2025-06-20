import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cs412.settings_demo')
django.setup()

from django.conf import settings
import random
from datetime import timedelta, date
from faker import Faker

assert 'sqlite3' in settings.DATABASES['default']['ENGINE'], "ERROR: Not using SQLite!"

from project_demo.models import Parent, Student, TutoringService, AdvocacyService

fake = Faker()
Faker.seed(0)
random.seed(0)

NUM_PARENTS = 15
MAX_STUDENTS_PER_PARENT = 3
MAX_TUTORING_SESSIONS = 5
MAX_ADVOCACY_SESSIONS = 3

# Fixed pools of categories for consistent overlap
COUNTRIES = ["USA", "Canada", "Mexico", "India", "Nigeria", "Brazil", "China", "France", "Germany", "Kenya"]
TOWNS = ["Springfield", "Rivertown", "Laketown", "Hillview", "Maplewood", "Cedarville", "Fairview", "Greenville", "Oakland", "Brookfield"]
SCHOOL_DISTRICTS = ["District A", "District B", "District C", "District D", "District E", "District F", "District G", "District H", "District I", "District J"]

def random_date(start_year=2010, end_year=2023):
    start_date = date(start_year, 1, 1)
    end_date = date(end_year, 12, 31)
    return start_date + timedelta(days=random.randint(0, (end_date - start_date).days))

def generate_data():
    Parent.objects.all().delete()
    Student.objects.all().delete()
    TutoringService.objects.all().delete()
    AdvocacyService.objects.all().delete()

    for _ in range(NUM_PARENTS):
        parent_country = random.choice(COUNTRIES)
        parent_town = random.choice(TOWNS)

        parent = Parent.objects.create(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            date_of_intake=random_date(),
            email_address=fake.email(),
            home_address=fake.address(),
            phone_number=fake.phone_number(),
            town_village=parent_town,
            country_of_origin=parent_country
        )

        for _ in range(random.randint(1, MAX_STUDENTS_PER_PARENT)):
            student_school_district = random.choice(SCHOOL_DISTRICTS)

            student = Student.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                date_of_birth=fake.date_of_birth(minimum_age=5, maximum_age=18),
                current_grade=random.randint(1, 12),
                town_village=parent_town,  # same as parent for overlap
                email_address=fake.email(),
                phone_number=fake.phone_number(),
                country_of_origin=parent_country,  # same as parent for overlap
                date_of_intake=random_date(),
                parent=parent
            )

            # Add tutoring sessions
            for _ in range(random.randint(0, MAX_TUTORING_SESSIONS)):
                TutoringService.objects.create(
                    student=student,
                    date_of_contact=random_date(2020, 2024),
                    location_of_contact=fake.address(),
                    session_focus=random.choice(['Math', 'Reading', 'Science', 'Writing']),
                    activity=fake.paragraph(),
                    length_of_session=round(random.uniform(0.5, 2.0), 2)
                )

            # Add advocacy sessions
            for _ in range(random.randint(0, MAX_ADVOCACY_SESSIONS)):
                AdvocacyService.objects.create(
                    student=student,
                    date_of_contact=random_date(2020, 2024),
                    school_district=student_school_district,
                    description=fake.text(),
                    length_of_contact=round(random.uniform(0.25, 1.5), 2)
                )

if __name__ == '__main__':
    print("Generating demo data...")
    generate_data()
    print("Done.")
