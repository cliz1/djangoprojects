# Generated by Django 5.1.1 on 2024-10-21 05:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mini_fb', '0006_remove_profile_image_file_profile_profile_image_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='image_file',
            field=models.ImageField(upload_to='images/'),
        ),
    ]
