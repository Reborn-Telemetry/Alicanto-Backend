# Generated by Django 4.2.6 on 2024-03-26 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='job_title',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
