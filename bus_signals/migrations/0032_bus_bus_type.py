# Generated by Django 4.2.6 on 2024-05-30 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0031_alter_bus_lts_isolation'),
    ]

    operations = [
        migrations.AddField(
            model_name='bus',
            name='bus_type',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Type'),
        ),
    ]