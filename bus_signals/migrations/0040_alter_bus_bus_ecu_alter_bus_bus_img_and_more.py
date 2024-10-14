# Generated by Django 4.2.6 on 2024-10-14 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_signals', '0039_bus_ecu_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bus',
            name='bus_ecu',
            field=models.CharField(blank=True, choices=[('Q1', 'Q1'), ('Q2', 'Q2')], db_index=True, max_length=20, null=True, verbose_name='Bus ECU'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='bus_img',
            field=models.ImageField(blank=True, db_index=True, default='bus.png', null=True, upload_to=''),
        ),
        migrations.AlterField(
            model_name='bus',
            name='bus_name',
            field=models.CharField(db_index=True, max_length=40, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='bus_series',
            field=models.CharField(choices=[('Queltehue', 'Queltehue'), ('Queltehue-Q2', 'Queltehue-Q2'), ('Tricahue', 'Tricahue'), ('Retrofit', 'Retrofit'), ('Prueba', 'Prueba')], db_index=True, max_length=100, verbose_name='Serie'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='bus_type',
            field=models.CharField(blank=True, db_index=True, max_length=20, null=True, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='charging',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True, verbose_name='Charging'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='client',
            field=models.CharField(db_index=True, default='Link', max_length=20, verbose_name='Client'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='ecu_state',
            field=models.IntegerField(blank=True, db_index=True, null=True, verbose_name='ECU State'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='jarvis',
            field=models.CharField(blank=True, db_index=True, default='1.0.0', max_length=20, null=True, verbose_name='Jarvis'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='key_state',
            field=models.ImageField(blank=True, db_index=True, null=True, upload_to='', verbose_name='Key State'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='lts_24_volt',
            field=models.FloatField(blank=True, db_index=True, default=0, null=True, verbose_name='LTS 24 Volt'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='lts_fusi',
            field=models.IntegerField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterField(
            model_name='bus',
            name='lts_isolation',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True, verbose_name='LTS Isolation'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='lts_odometer',
            field=models.IntegerField(blank=True, db_index=True, default=0, null=True, verbose_name='LTS Odometer'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='lts_soc',
            field=models.IntegerField(blank=True, db_index=True, default=None, null=True, verbose_name='LTS SOC'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='lts_update',
            field=models.DateTimeField(blank=True, db_index=True, null=True, verbose_name='LTS Update'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='mark',
            field=models.CharField(blank=True, db_index=True, default='1.0.0', max_length=20, null=True, verbose_name='Mark'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='plate_number',
            field=models.CharField(blank=True, db_index=True, max_length=10, null=True, verbose_name='Plate Number'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='sniffer',
            field=models.CharField(db_index=True, max_length=10, unique=True, verbose_name='Sniffer'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='soh',
            field=models.IntegerField(blank=True, db_index=True, null=True, verbose_name='SOH'),
        ),
        migrations.AlterField(
            model_name='bus',
            name='vision',
            field=models.CharField(blank=True, db_index=True, default='1.0.0', max_length=20, null=True, verbose_name='Vision'),
        ),
    ]