# Generated by Django 4.2.6 on 2024-04-02 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0022_alter_fusicode_failure_odometer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fusimessage',
            name='fusi_code',
            field=models.IntegerField(),
        ),
    ]