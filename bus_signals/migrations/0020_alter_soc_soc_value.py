# Generated by Django 4.2.6 on 2024-04-01 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0019_alter_bus_lts_odometer_alter_odometer_odometer_value'),
    ]

    operations = [
        migrations.AlterField(
            model_name='soc',
            name='soc_value',
            field=models.IntegerField(blank=True, default=None, null=True, verbose_name='SOC Value'),
        ),
    ]
