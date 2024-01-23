# Generated by Django 5.0.1 on 2024-01-23 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0003_mark_alter_jarvisversion_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='client',
            field=models.CharField(blank=True, choices=[(1, 'Link'), (2, 'Reborn'), (3, 'Otro')], max_length=20, null=True, verbose_name='Client'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='plate_number',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Plate Number'),
        ),
    ]
