# Generated by Django 4.2.6 on 2024-03-20 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0013_alter_odometer_odometer_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='odometer',
            name='odometer_value',
            field=models.FloatField(blank=True, null=True, verbose_name='Odometer Value'),
        ),
    ]
