# Generated by Django 4.2.6 on 2024-04-02 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0021_alter_bus_lts_soc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fusicode',
            name='failure_odometer',
            field=models.IntegerField(blank=True, null=True, verbose_name='Odometer'),
        ),
    ]
