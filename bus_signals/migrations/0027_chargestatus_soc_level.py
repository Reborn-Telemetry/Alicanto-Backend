# Generated by Django 4.2.6 on 2024-04-08 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0026_alter_batteryhealth_battery_health_value'),
    ]

    operations = [
        migrations.AddField(
            model_name='chargestatus',
            name='soc_level',
            field=models.IntegerField(blank=True, null=True, verbose_name='SOC Level'),
        ),
    ]
