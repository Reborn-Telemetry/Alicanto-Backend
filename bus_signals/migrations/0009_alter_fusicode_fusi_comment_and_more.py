# Generated by Django 5.0.1 on 2024-02-13 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0008_bus_bus_ecu'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fusicode',
            name='fusi_comment',
            field=models.TextField(blank=True, null=True, verbose_name='Fusi Comment'),
        ),
        migrations.AlterField(
            model_name='fusicode',
            name='fusi_state',
            field=models.CharField(blank=True, choices=[('Abierto', 'Abierto'), ('Cerrado', 'Cerrado')], default='open', max_length=10, null=True, verbose_name='Fusi State'),
        ),
    ]
