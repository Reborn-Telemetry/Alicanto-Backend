# Generated by Django 5.1.2 on 2024-10-15 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0040_alter_bus_bus_ecu_alter_bus_bus_img_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnualEnergy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('energia', models.FloatField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
