# Generated by Django 5.0.1 on 2024-01-23 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0005_alter_bus_client_alter_bus_plate_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='plate_number',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Plate Number'),
        ),
    ]
