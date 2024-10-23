# Generated by Django 5.1.2 on 2024-10-16 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reports', '0007_disponibilidadflota_bus_disponibilidadflota_dias_fs_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MatrizKmFlotaHistorico',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bus', models.CharField(blank=True, max_length=50, null=True)),
                ('dia', models.CharField(blank=True, max_length=50, null=True)),
                ('mes', models.CharField(blank=True, max_length=50, null=True)),
                ('año', models.CharField(blank=True, max_length=50, null=True)),
                ('km_value', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Informe Historico KM Flota',
                'verbose_name_plural': 'Informes Historico KM Flota',
            },
        ),
    ]