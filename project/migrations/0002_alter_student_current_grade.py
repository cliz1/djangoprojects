# Generated by Django 5.1.1 on 2024-12-05 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='current_grade',
            field=models.IntegerField(),
        ),
    ]