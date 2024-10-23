# Generated by Django 5.1.2 on 2024-10-16 19:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0042_alter_anualenergy_options'),
        ('reports', '0011_matrizkmflotahistorico'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatrizEnergiaFlotaHistorico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia', models.IntegerField(blank=True, null=True)),
                ('mes', models.IntegerField(blank=True, null=True)),
                ('año', models.IntegerField(blank=True, null=True)),
                ('energia', models.IntegerField(blank=True, null=True)),
                ('bus', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Informe Historico Energia Flota',
                'verbose_name_plural': 'Informes Historico Energia Flota',
            },
        ),
    ]