# Generated by Django 4.2.6 on 2024-04-01 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0017_alter_fusicode_fusi_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='lts_fusi',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
