# fix_sequences.py (Django management command)

from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Reset all sequences to match max id in tables'

    def handle(self, *args, **kwargs):
        with connection.cursor() as cursor:
            tables = [
                'project_parent',
                'project_student',
                # add any other tables in your app here
            ]
            for table in tables:
                self.stdout.write(f"Resetting sequence for: {table}")
                cursor.execute(f"""
                    SELECT setval(
                        pg_get_serial_sequence('"{table}"', 'id'),
                        COALESCE((SELECT MAX(id) FROM "{table}"), 1),
                        true
                    );
                """)
                self.stdout.write(self.style.SUCCESS(f"  ✓ {table}"))
        self.stdout.write(self.style.SUCCESS("All sequences reset."))