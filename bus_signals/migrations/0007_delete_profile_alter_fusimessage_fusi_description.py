# Generated by Django 5.0.1 on 2024-02-02 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0006_alter_awspathbucket_path_internal_date_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Profile',
        ),
        migrations.AlterField(
            model_name='fusimessage',
            name='fusi_description',
            field=models.CharField(max_length=500, verbose_name='Fusi Description'),
        ),
    ]
