# Generated by Django 5.1.2 on 2024-10-29 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0016_recorrido'),
    ]

    operations = [
        migrations.AddField(
            model_name='recorrido',
            name='recorrido',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
