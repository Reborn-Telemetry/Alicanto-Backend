from typing import Any
from django.db import models
import uuid

series_choices = (
    ('1', 'Queltehue'),
    ('2', 'Tricahue'),
    ('3', 'Retrofit'),
)
job_choices = (
    ('1', 'Electro Mecanico'),
    ('2', 'Electrico'),
    ('3', 'Electronico'),
)

message_class_choices = (
    ('Q1', 'Q1'),
    ('Q2', 'Q2'),
)


class Bus(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    bus_name = models.CharField('Name', max_length=10, unique=True, blank=False, null=False)
    sniffer = models.CharField('Sniffer', max_length=10, unique=True, blank=False, null=False)
    plate_number = models.CharField('Plate Number', max_length=10, unique=False, blank=True, null=True)
    bus_series = models.CharField('Serie', max_length=10, choices=series_choices, blank=False, null=False)
    client = models.CharField('Client', max_length=20, blank=False, null=False, default='Link')
    lts_soc = models.FloatField('LTS SOC', default=None, blank=True, null=True)
    lts_odometer = models.FloatField('LTS Odometer', default=0, blank=True, null=True)
    lts_isolation = models.FloatField('LTS Isolation', default=0, blank=True, null=True)
    lts_24_volt = models.FloatField('LTS 24 Volt', default=0, blank=True, null=True)
    lts_fusi = models.FloatField('LTS FUSI', default=0, blank=True, null=True)
    lts_update = models.DateTimeField('LTS Update', auto_now=False, blank=True, null=True)
    mark = models.CharField('Mark', max_length=20, blank=True, null=True, default='1.0.0')
    jarvis = models.CharField('Jarvis', max_length=20, blank=True, null=True, default='1.0.0')
    vision = models.CharField('Vision', max_length=20, blank=True, null=True, default='1.0.0')

    bus = models.Manager()

    def __str__(self):
        return (f'{self.bus_name} - {self.sniffer} - {self.plate_number} - {self.bus_series} - {self.client} -'
                f' {self.lts_soc} - {self.lts_odometer} - {self.lts_isolation} - {self.lts_24_volt} - '
                f'{self.lts_fusi} - {self.lts_update}')

    class Meta:
        verbose_name = 'Bus'
        verbose_name_plural = 'Buses'
        ordering = ['bus_name']


class Battery24Volts(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    battery_24_volts_value = models.FloatField('Battery 24 Volts Value', default=None, blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, blank=True, null=True)

    battery_24_volts = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.battery_24_volts_value} - {self.bus}'

    class Meta:
        verbose_name = 'Battery 24 Volts'
        verbose_name_plural = 'Batteries 24 Volts'
        ordering = ['TimeStamp']


class Soc(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    soc_value = models.FloatField('SOC Value', default=None, blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, blank=True, null=True)

    soc = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.soc_value} - {self.bus}'

    class Meta:
        verbose_name = 'SOC'
        verbose_name_plural = 'SOCs'
        ordering = ['TimeStamp']


class PackTemperature(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    pack_temperature_value = models.FloatField('Pack Temperature', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    pack_temperature = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.pack_temperature_value} - {self.bus}'

    class Meta:
        verbose_name = 'Pack Temperature'
        verbose_name_plural = 'Pack Temperatures'
        ordering = ['TimeStamp']


class MaxTemperaturePack(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    max_temperature_pack_value = models.FloatField('Max Temperature Pack', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    max_temperature_pack = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.max_temperature_pack_value} - {self.bus}'

    class Meta:
        verbose_name = 'Max Temperature Pack'
        verbose_name_plural = 'Max Temperatures Pack'
        ordering = ['TimeStamp']


class BatteryHealth(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    battery_health_value = models.FloatField('Battery Health', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    battery_health = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.battery_health_value} - {self.bus}'

    class Meta:
        verbose_name = 'Battery Health'
        verbose_name_plural = 'Batteries Health'
        ordering = ['TimeStamp']


class BatteryPackCurrent(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    battery_pack_current_value = models.FloatField('Battery Pack Current', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    battery_pack_current = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.battery_pack_current_value} - {self.bus}'

    class Meta:
        verbose_name = 'Battery Pack Current'
        verbose_name_plural = 'Batteries Pack Current'
        ordering = ['TimeStamp']


class BatteryPackVoltage(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    battery_pack_voltage_value = models.FloatField('Battery Pack Voltage', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    battery_pack_voltage = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.battery_pack_voltage_value} - {self.bus}'

    class Meta:
        verbose_name = 'Battery Pack Voltage'
        verbose_name_plural = 'Batteries Pack Voltage'
        ordering = ['TimeStamp']


class BatteryPackCellMaxVoltage(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    battery_pack_cell_max_voltage_value = models.FloatField('Battery Pack Cell Max Voltage', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    battery_pack_cell_max_voltage = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.battery_pack_cell_max_voltage_value} - {self.bus}'

    class Meta:
        verbose_name = 'Battery Pack Cell Max Voltage'
        verbose_name_plural = 'Batteries Pack Cell Max Voltage'
        ordering = ['TimeStamp']


class BatteryPackCellMinVoltage(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    battery_pack_cell_min_voltage_value = models.FloatField('Battery Pack Cell Min Voltage', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    battery_pack_cell_min_voltage = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.battery_pack_cell_min_voltage_value} - {self.bus}'

    class Meta:
        verbose_name = 'Battery Pack Cell Min Voltage'
        verbose_name_plural = 'Batteries Pack Cell Min Voltage'
        ordering = ['TimeStamp']


class BatteryPackAvgCellVoltage(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    battery_pack_avg_cell_voltage_value = models.FloatField('Battery Pack Avg Cell Voltage', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    battery_pack_avg_cell_voltage = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.battery_pack_avg_cell_voltage_value} - {self.bus}'

    class Meta:
        verbose_name = 'Battery Pack Avg Cell Voltage'
        verbose_name_plural = 'Batteries Pack Avg Cell Voltage'
        ordering = ['TimeStamp']


class Isolation(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    isolation_value = models.FloatField('Isolation', blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    isolation = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.isolation_value} - {self.bus}'

    class Meta:
        verbose_name = 'Isolation'
        verbose_name_plural = 'Isolations'
        ordering = ['TimeStamp']


class PtcOneVoltage(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    ptc_one_voltage_value = models.FloatField('PTC One Voltage', blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    ptc_one = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.ptc_one_voltage_value} - {self.bus}'

    class Meta:
        verbose_name = 'PTC One Voltage'
        verbose_name_plural = 'PTC One Voltages'
        ordering = ['TimeStamp']


class PtcTwoVoltage(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    ptc_two_voltage_value = models.FloatField('PTC Two Voltage', blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    ptc_two = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.ptc_two_voltage_value} - {self.bus}'

    class Meta:
        verbose_name = 'PTC Two Voltage'
        verbose_name_plural = 'PTC Two Voltages'
        ordering = ['TimeStamp']


class PositiveTorque(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    positive_torque_value = models.FloatField('Torque', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    positive_torque = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.positive_torque_value} - {self.bus}'

    class Meta:
        verbose_name = 'Positive Torque'
        verbose_name_plural = 'Positive Torques'
        ordering = ['TimeStamp']


class NegativeTorque(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    negative_torque_value = models.FloatField('Torque', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    negative_torque = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.negative_torque_value} - {self.bus}'

    class Meta:
        verbose_name = 'Negative Torque'
        verbose_name_plural = 'Negative Torques'
        ordering = ['TimeStamp']


class EngineTemperature(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    engine_temperature_value = models.FloatField('Temperature', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    engine_temperature = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.engine_temperature_value} - {self.bus}'

    class Meta:
        verbose_name = 'Engine Temperature'
        verbose_name_plural = 'Engine Temperatures'
        ordering = ['TimeStamp']


class LenzeCurrent(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    lenze_current_value = models.FloatField('lenze_current_value', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    lenze_current = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.lenze_current_value}'

    class Meta:
        verbose_name = 'Lenze Current'
        verbose_name_plural = 'Lenze Currents'
        ordering = ['TimeStamp']


class LenzeEngineSpeed(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    lenze_engine_speed_value = models.FloatField('lenze_engine_speed_value', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    lenze_engine_speed = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.lenze_engine_speed_value}'

    class Meta:
        verbose_name = 'Lenze Engine Speed'
        verbose_name_plural = 'Lenze Engine Speeds'
        ordering = ['TimeStamp']


class Odometer(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    odometer_value = models.FloatField('Odometer Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    odometer = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.odometer_value} - {self.bus}'

    class Meta:
        verbose_name = 'Odometer'
        verbose_name_plural = 'Odometers'
        ordering = ['TimeStamp']


class Speed(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    speed_value = models.FloatField('Speed Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    speed = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.speed_value} - {self.bus}'

    class Meta:
        verbose_name = 'Speed'
        verbose_name_plural = 'Speeds'
        ordering = ['TimeStamp']


class SystemPressure(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    system_pressure_value = models.FloatField('System Pressure Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    system_pressure = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.system_pressure_value} - {self.bus}'

    class Meta:
        verbose_name = 'System Pressure'
        verbose_name_plural = 'System Pressures'
        ordering = ['TimeStamp']


class BtmsTemperature(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    btms_temperature_value = models.FloatField('BTMS Temperature Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    btms_temperature = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.btms_temperature_value}'

    class Meta:
        verbose_name = 'BTMS Temperature'
        verbose_name_plural = 'BTMS Temperatures'


class FusiCode(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    fusi_code = models.FloatField('Fusi Code', blank=True)
    fusi_state = models.CharField('Fusi State', max_length=10, blank=True, null=True, default='open')
    fusi_comment = models.CharField('Fusi Comment', max_length=200, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)
    failure_odometer = models.FloatField('Odometer', blank=True, null=True)

    fusi = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.fusi_code} - {self.fusi_state} - {self.fusi_comment} - ' \
               f'{self.failure_odometer} - {self.bus}'

    class Meta:
        verbose_name = 'Fusi Code'
        verbose_name_plural = 'Fusi Codes'
        ordering = ['TimeStamp']


class ChargeStatus(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    charge_status_value = models.FloatField('Charge Status Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    charge_status = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.charge_status_value} - {self.bus}'

    class Meta:
        verbose_name = 'Charge Status'
        verbose_name_plural = 'Charge Status'
        ordering = ['TimeStamp']


class GearStatus(models.Model):
    TimeStamp = models.DateTimeField('Timestamp', blank=True, null=True)
    gear_status_value = models.FloatField('Gear Status Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    gear_status = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.gear_status_value} - {self.bus}'

    class Meta:
        verbose_name = 'Gear Status'
        verbose_name_plural = 'Gear Status'
        ordering = ['TimeStamp']


class BusState(models.Model):
    TimeStamp = models.DateTimeField('Timestamp', blank=True, null=True)
    bus_state_value = models.CharField('Bus State Value', max_length=10, blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    bus_state = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.bus_state_value} - {self.bus}'

    class Meta:
        verbose_name = 'Bus State'
        verbose_name_plural = 'Bus State'
        ordering = ['TimeStamp']


class BrakePedalStatus(models.Model):
    TimeStamp = models.DateTimeField('Timestamp', blank=True, null=True)
    brake_pedal_status_value = models.FloatField('Brake Pedal Status Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    brake_pedal_status = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.brake_pedal_status_value} - {self.bus}'

    class Meta:
        verbose_name = 'Brake Pedal Status'
        verbose_name_plural = 'Brake Pedal Status'
        ordering = ['TimeStamp']


class AirConditionerStatus(models.Model):
    TimeStamp = models.DateTimeField('Timestamp', blank=True, null=True)
    air_conditioner_status_value = models.FloatField('Air Conditioner Status Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    air_conditioner_status = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.air_conditioner_status_value} - {self.bus}'

    class Meta:
        verbose_name = 'Air Conditioner Status'
        verbose_name_plural = 'Air Conditioner Status'
        ordering = ['TimeStamp']


class ServiceCompressorStatus(models.Model):
    TimeStamp = models.DateTimeField('Timestamp', blank=True, null=True)
    service_compressor_value = models.FloatField('Service Compressor Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    service_compressor = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.service_compressor_value} - {self.bus}'

    class Meta:
        verbose_name = 'Service Compressor Status'
        verbose_name_plural = 'Service Compressor Status'
        ordering = ['TimeStamp']


class BtmsStatus(models.Model):
    TimeStamp = models.DateTimeField('Timestamp', blank=True, null=True)
    btms_status_value = models.FloatField('BTMS Status Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    btms_status = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.TimeStamp} - {self.btms_status_value} - {self.bus}'

    class Meta:
        verbose_name = 'BTMS Status'
        verbose_name_plural = 'BTMS Status'
        ordering = ['TimeStamp']


class FusiMessage(models.Model):
    fusi_code = models.CharField('Fusi Code', max_length=10, unique=True)
    fusi_description = models.CharField('Fusi Description', max_length=200)
    message_class = models.CharField('Message Class', choices=message_class_choices, max_length=20, blank=True, null=True)

    fusi = models.Manager()

    def __str__(self):
        return f'{self.message_class}- {self.fusi_code} - {self.fusi_description}'

    class Meta:
        verbose_name = 'Fusi Message'
        verbose_name_plural = 'Fusi Messages'
        ordering = ['fusi_code']


class ModemInfo(models.Model):
    imei = models.CharField('IMEI', max_length=20)
    rem_number = models.CharField('REM Number', max_length=20)
    sim_number = models.CharField('SIM Number', max_length=20)
    user = models.CharField('User', max_length=20)
    password = models.CharField('Password', max_length=20)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    modem_info = models.Manager()

    def __str__(self):
        return f'{self.id} - {self.imei} - {self.rem_number} - {self.sim_number} - {self.user} - {self.password} -' \
               f' {self.bus}'

    class Meta:
        verbose_name = 'Modem Info'
        verbose_name_plural = 'Modem Info'
        ordering = ['rem_number']


class Technician(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField('Name', max_length=100)
    phone = models.CharField('Phone', max_length=20)
    job = models.CharField('Job', max_length=100, choices=job_choices)

    technician = models.Manager()

    def __str__(self):
        return f'{self.name} - {self.phone} - {self.job}'

    class Meta:
        verbose_name = 'Technician'
        verbose_name_plural = 'Technicians'
        ordering = ['name']

