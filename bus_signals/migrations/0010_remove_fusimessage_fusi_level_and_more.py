# Generated by Django 5.0.1 on 2024-01-23 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0009_fusimessage_message_class'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fusimessage',
            name='fusi_level',
        ),
        migrations.RemoveField(
            model_name='fusimessage',
            name='fusi_serie',
        ),
        migrations.AlterField(
            model_name='fusimessage',
            name='message_class',
            field=models.CharField(blank=True, choices=[('Q1', 'Q1'), ('Q2', 'Q2')], max_length=20, null=True, verbose_name='Message Class'),
        ),
    ]