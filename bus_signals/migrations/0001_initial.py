# Generated by Django 4.2.6 on 2024-01-26 18:46

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Bus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bus_name', models.CharField(max_length=10, unique=True, verbose_name='Name')),
                ('sniffer', models.CharField(max_length=10, unique=True, verbose_name='Sniffer')),
                ('plate_number', models.CharField(blank=True, max_length=10, null=True, verbose_name='Plate Number')),
                ('bus_series', models.CharField(choices=[('Queltehue', 'Queltehue'), ('Tricahue', 'Tricahue'), ('Retrofit', 'Retrofit')], max_length=10, verbose_name='Serie')),
                ('client', models.CharField(default='Link', max_length=20, verbose_name='Client')),
                ('lts_soc', models.FloatField(blank=True, default=None, null=True, verbose_name='LTS SOC')),
                ('lts_odometer', models.FloatField(blank=True, default=0, null=True, verbose_name='LTS Odometer')),
                ('lts_isolation', models.FloatField(blank=True, default=0, null=True, verbose_name='LTS Isolation')),
                ('lts_24_volt', models.FloatField(blank=True, default=0, null=True, verbose_name='LTS 24 Volt')),
                ('lts_fusi', models.FloatField(blank=True, default=0, null=True, verbose_name='LTS FUSI')),
                ('lts_update', models.DateTimeField(blank=True, null=True, verbose_name='LTS Update')),
                ('mark', models.CharField(blank=True, default='1.0.0', max_length=20, null=True, verbose_name='Mark')),
                ('jarvis', models.CharField(blank=True, default='1.0.0', max_length=20, null=True, verbose_name='Jarvis')),
                ('vision', models.CharField(blank=True, default='1.0.0', max_length=20, null=True, verbose_name='Vision')),
                ('bus_img', models.ImageField(blank=True, default='bus.png', null=True, upload_to='')),
            ],
            options={
                'verbose_name': 'Bus',
                'verbose_name_plural': 'Buses',
                'ordering': ['bus_name'],
            },
            managers=[
                ('bus', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='FusiMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fusi_code', models.CharField(max_length=10, unique=True, verbose_name='Fusi Code')),
                ('fusi_description', models.CharField(max_length=200, verbose_name='Fusi Description')),
                ('message_class', models.CharField(blank=True, choices=[('Q1', 'Q1'), ('Q2', 'Q2')], max_length=20, null=True, verbose_name='Message Class')),
            ],
            options={
                'verbose_name': 'Fusi Message',
                'verbose_name_plural': 'Fusi Messages',
                'ordering': ['fusi_code'],
            },
            managers=[
                ('fusi', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Phone')),
                ('hola', models.CharField(blank=True, max_length=20, null=True, verbose_name='Hola')),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
            },
            managers=[
                ('profile', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Technician',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('phone', models.CharField(max_length=20, verbose_name='Phone')),
                ('job', models.CharField(choices=[('1', 'Electro Mecanico'), ('2', 'Electrico'), ('3', 'Electronico')], max_length=100, verbose_name='Job')),
            ],
            options={
                'verbose_name': 'Technician',
                'verbose_name_plural': 'Technicians',
                'ordering': ['name'],
            },
            managers=[
                ('technician', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='SystemPressure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('system_pressure_value', models.FloatField(blank=True, verbose_name='System Pressure Value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'System Pressure',
                'verbose_name_plural': 'System Pressures',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('system_pressure', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Speed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('speed_value', models.FloatField(blank=True, verbose_name='Speed Value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Speed',
                'verbose_name_plural': 'Speeds',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('speed', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Soc',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('soc_value', models.FloatField(blank=True, default=None, null=True, verbose_name='SOC Value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'SOC',
                'verbose_name_plural': 'SOCs',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('soc', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ServiceCompressorStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='Timestamp')),
                ('service_compressor_value', models.FloatField(blank=True, verbose_name='Service Compressor Value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Service Compressor Status',
                'verbose_name_plural': 'Service Compressor Status',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('service_compressor', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='PtcTwoVoltage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('ptc_two_voltage_value', models.FloatField(blank=True, null=True, verbose_name='PTC Two Voltage')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'PTC Two Voltage',
                'verbose_name_plural': 'PTC Two Voltages',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('ptc_two', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='PtcOneVoltage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('ptc_one_voltage_value', models.FloatField(blank=True, null=True, verbose_name='PTC One Voltage')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'PTC One Voltage',
                'verbose_name_plural': 'PTC One Voltages',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('ptc_one', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='PositiveTorque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('positive_torque_value', models.FloatField(blank=True, null=True, verbose_name='Torque')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Positive Torque',
                'verbose_name_plural': 'Positive Torques',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('positive_torque', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='PackTemperature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('pack_temperature_value', models.FloatField(blank=True, null=True, verbose_name='Pack Temperature')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Pack Temperature',
                'verbose_name_plural': 'Pack Temperatures',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('pack_temperature', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Odometer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('odometer_value', models.FloatField(blank=True, verbose_name='Odometer Value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Odometer',
                'verbose_name_plural': 'Odometers',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('odometer', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='NegativeTorque',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('negative_torque_value', models.FloatField(blank=True, null=True, verbose_name='Torque')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Negative Torque',
                'verbose_name_plural': 'Negative Torques',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('negative_torque', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ModemInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imei', models.CharField(max_length=20, verbose_name='IMEI')),
                ('rem_number', models.CharField(max_length=20, verbose_name='REM Number')),
                ('sim_number', models.CharField(max_length=20, verbose_name='SIM Number')),
                ('user', models.CharField(max_length=20, verbose_name='User')),
                ('password', models.CharField(max_length=20, verbose_name='Password')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Modem Info',
                'verbose_name_plural': 'Modem Info',
                'ordering': ['rem_number'],
            },
            managers=[
                ('modem_info', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='MaxTemperaturePack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('max_temperature_pack_value', models.FloatField(blank=True, null=True, verbose_name='Max Temperature Pack')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Max Temperature Pack',
                'verbose_name_plural': 'Max Temperatures Pack',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('max_temperature_pack', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='LenzeEngineSpeed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('lenze_engine_speed_value', models.FloatField(blank=True, null=True, verbose_name='lenze_engine_speed_value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Lenze Engine Speed',
                'verbose_name_plural': 'Lenze Engine Speeds',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('lenze_engine_speed', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='LenzeCurrent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('lenze_current_value', models.FloatField(blank=True, null=True, verbose_name='lenze_current_value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Lenze Current',
                'verbose_name_plural': 'Lenze Currents',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('lenze_current', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Isolation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('isolation_value', models.FloatField(blank=True, null=True, verbose_name='Isolation')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Isolation',
                'verbose_name_plural': 'Isolations',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('isolation', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='GearStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='Timestamp')),
                ('gear_status_value', models.FloatField(blank=True, verbose_name='Gear Status Value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Gear Status',
                'verbose_name_plural': 'Gear Status',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('gear_status', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='FusiCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('fusi_code', models.FloatField(blank=True, verbose_name='Fusi Code')),
                ('fusi_state', models.CharField(blank=True, default='open', max_length=10, null=True, verbose_name='Fusi State')),
                ('fusi_comment', models.CharField(blank=True, max_length=200, verbose_name='Fusi Comment')),
                ('failure_odometer', models.FloatField(blank=True, null=True, verbose_name='Odometer')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Fusi Code',
                'verbose_name_plural': 'Fusi Codes',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('fusi', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='EngineTemperature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('engine_temperature_value', models.FloatField(blank=True, null=True, verbose_name='Temperature')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Engine Temperature',
                'verbose_name_plural': 'Engine Temperatures',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('engine_temperature', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='ChargeStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('charge_status_value', models.FloatField(blank=True, verbose_name='Charge Status Value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Charge Status',
                'verbose_name_plural': 'Charge Status',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('charge_status', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='BusState',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='Timestamp')),
                ('bus_state_value', models.CharField(blank=True, max_length=10, null=True, verbose_name='Bus State Value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Bus State',
                'verbose_name_plural': 'Bus State',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('bus_state', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='BtmsTemperature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('btms_temperature_value', models.FloatField(blank=True, verbose_name='BTMS Temperature Value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'BTMS Temperature',
                'verbose_name_plural': 'BTMS Temperatures',
            },
            managers=[
                ('btms_temperature', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='BtmsStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='Timestamp')),
                ('btms_status_value', models.FloatField(blank=True, verbose_name='BTMS Status Value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'BTMS Status',
                'verbose_name_plural': 'BTMS Status',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('btms_status', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='BrakePedalStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='Timestamp')),
                ('brake_pedal_status_value', models.FloatField(blank=True, verbose_name='Brake Pedal Status Value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Brake Pedal Status',
                'verbose_name_plural': 'Brake Pedal Status',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('brake_pedal_status', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='BatteryPackVoltage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('battery_pack_voltage_value', models.FloatField(blank=True, null=True, verbose_name='Battery Pack Voltage')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Battery Pack Voltage',
                'verbose_name_plural': 'Batteries Pack Voltage',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('battery_pack_voltage', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='BatteryPackCurrent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('battery_pack_current_value', models.FloatField(blank=True, null=True, verbose_name='Battery Pack Current')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Battery Pack Current',
                'verbose_name_plural': 'Batteries Pack Current',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('battery_pack_current', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='BatteryPackCellMinVoltage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('battery_pack_cell_min_voltage_value', models.FloatField(blank=True, null=True, verbose_name='Battery Pack Cell Min Voltage')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Battery Pack Cell Min Voltage',
                'verbose_name_plural': 'Batteries Pack Cell Min Voltage',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('battery_pack_cell_min_voltage', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='BatteryPackCellMaxVoltage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('battery_pack_cell_max_voltage_value', models.FloatField(blank=True, null=True, verbose_name='Battery Pack Cell Max Voltage')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Battery Pack Cell Max Voltage',
                'verbose_name_plural': 'Batteries Pack Cell Max Voltage',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('battery_pack_cell_max_voltage', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='BatteryPackAvgCellVoltage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('battery_pack_avg_cell_voltage_value', models.FloatField(blank=True, null=True, verbose_name='Battery Pack Avg Cell Voltage')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Battery Pack Avg Cell Voltage',
                'verbose_name_plural': 'Batteries Pack Avg Cell Voltage',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('battery_pack_avg_cell_voltage', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='BatteryHealth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('battery_health_value', models.FloatField(blank=True, null=True, verbose_name='Battery Health')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Battery Health',
                'verbose_name_plural': 'Batteries Health',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('battery_health', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='Battery24Volts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='TimeStamp')),
                ('battery_24_volts_value', models.FloatField(blank=True, default=None, null=True, verbose_name='Battery 24 Volts Value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Battery 24 Volts',
                'verbose_name_plural': 'Batteries 24 Volts',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('battery_24_volts', django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name='AirConditionerStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('TimeStamp', models.DateTimeField(blank=True, null=True, verbose_name='Timestamp')),
                ('air_conditioner_status_value', models.FloatField(blank=True, verbose_name='Air Conditioner Status Value')),
                ('bus', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bus_signals.bus')),
            ],
            options={
                'verbose_name': 'Air Conditioner Status',
                'verbose_name_plural': 'Air Conditioner Status',
                'ordering': ['TimeStamp'],
            },
            managers=[
                ('air_conditioner_status', django.db.models.manager.Manager()),
            ],
        ),
    ]
