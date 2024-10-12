from django.db import models
import uuid
from datetime import datetime, timedelta
from django.utils import timezone


series_choices = (
    ('Queltehue', 'Queltehue'),
    ('Queltehue-Q2', 'Queltehue-Q2'),
    ('Tricahue', 'Tricahue'),
    ('Retrofit', 'Retrofit'),
    ('Prueba', 'Prueba'),
)
job_choices = (
    ('Electro Mecanico', 'Electro Mecanico'),
    ('Electrico', 'Electrico'),
    ('Electronico', 'Electronico'),
)

message_class_choices = (
    ('Q1', 'Q1'),
    ('Q2', 'Q2'),
)
fusi_code_options = (
  ('Abierto', 'Abierto'),
  ('Cerrado', 'Cerrado'),
)



class Bus(models.Model):
    bus_name = models.CharField('Name', max_length=40, unique=True, blank=False, null=False)
    sniffer = models.CharField('Sniffer', max_length=10, unique=True, blank=False, null=False)
    plate_number = models.CharField('Plate Number', max_length=10, unique=False, blank=True, null=True)
    bus_series = models.CharField('Serie', max_length=100, choices=series_choices, blank=False, null=False)
    client = models.CharField('Client', max_length=20, blank=False, null=False, default='Link')
    lts_soc = models.IntegerField('LTS SOC', default=None, blank=True, null=True)
    lts_odometer = models.IntegerField('LTS Odometer', default=0, blank=True, null=True)
    lts_isolation = models.IntegerField('LTS Isolation', default=0, blank=True, null=True)
    lts_24_volt = models.FloatField('LTS 24 Volt', default=0, blank=True, null=True)
    lts_fusi = models.IntegerField(blank=True, null=True)
    charging = models.IntegerField('Charging', default=0, blank=True, null=True)
    lts_update = models.DateTimeField('LTS Update', auto_now=False, blank=True, null=True)
    mark = models.CharField('Mark', max_length=20, blank=True, null=True, default='1.0.0')
    jarvis = models.CharField('Jarvis', max_length=20, blank=True, null=True, default='1.0.0')
    vision = models.CharField('Vision', max_length=20, blank=True, null=True, default='1.0.0')
    bus_img = models.ImageField(null=True, blank=True, default='bus.png')
    bus_ecu = models.CharField('Bus ECU', max_length=20, blank=True, null=True, choices=message_class_choices)
    soh = models.IntegerField('SOH', blank=True, null=True)
    bus_type = models.CharField('Type', max_length=20, blank=True, null=True)
    key_state = models.ImageField('Key State', null=True, blank=True)
    ecu_state = models.IntegerField('ECU State', blank=True, null=True)
 
    bus = models.Manager()

    def __str__(self):
        return f'{self.bus_name}'
    
    def delay_data(self):
        ahora = timezone.now()
        fecha_limite = ahora - timedelta(days=3)
        
        # Filtramos directamente en una sola consulta
        registros = Bus.bus.filter(
            lts_update__lt=fecha_limite
        )

        return registros


    class Meta:
        verbose_name = 'Bus'
        verbose_name_plural = 'Buses'
        ordering = ['bus_name']

class Odometer(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    odometer_value = models.IntegerField('Odometer Value', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    odometer = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.odometer_value} - {self.bus}'

    class Meta:
        verbose_name = 'Odometer'
        verbose_name_plural = 'Odometers'
        ordering = ['TimeStamp']


class Soc(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    soc_value = models.IntegerField('SOC Value', default=None, blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, blank=True, null=True)

    soc = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.soc_value} - {self.bus}'

    class Meta:
        verbose_name = 'SOC'
        verbose_name_plural = 'SOCs'
        ordering = ['TimeStamp']


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


class BatteryHealth(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    battery_health_value = models.IntegerField('Battery Health', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    battery_health = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.battery_health_value} - {self.bus}'

    class Meta:
        verbose_name = 'Battery Health'
        verbose_name_plural = 'Batteries Health'
        ordering = ['TimeStamp']


class FusiCode(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    fusi_code = models.IntegerField()
    fusi_state = models.CharField('Fusi State', max_length=10, blank=True, null=True, default='open', choices=fusi_code_options)
    fusi_comment = models.TextField('Fusi Comment', blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)
    failure_odometer = models.IntegerField('Odometer', blank=True, null=True)

    fusi = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.fusi_code} - {self.fusi_state} - {self.fusi_comment} - ' \
               f'{self.failure_odometer} - {self.bus}'

    class Meta:
        verbose_name = 'Fusi Code'
        verbose_name_plural = 'Fusi Codes'
        ordering = ['TimeStamp']


class FusiMessage(models.Model):
    fusi_code = models.IntegerField()
    fusi_description = models.CharField('Fusi Description', max_length=500)
    message_class = models.CharField('Message Class', choices=message_class_choices, max_length=20, blank=True,
                                     null=True)

    fusi = models.Manager()

    def __str__(self):
        return f'{self.message_class}- {self.fusi_code} - {self.fusi_description}'

    class Meta:
        verbose_name = 'Fusi Message'
        verbose_name_plural = 'Fusi Messages'
        ordering = ['fusi_code']


class Isolation(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    isolation_value = models.FloatField('Isolation', blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    isolation = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.isolation_value} - {self.bus}'

    class Meta:
        verbose_name = 'Isolation'
        verbose_name_plural = 'Isolations'
        ordering = ['TimeStamp']

class ChargeStatus(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    charge_status_value = models.FloatField('Charge Status Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)
    soc_level = models.IntegerField('SOC Level', blank=True, null=True)

    charge_status = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.charge_status_value} - {self.bus}'

    class Meta:
        verbose_name = 'Charge Status'
        verbose_name_plural = 'Charge Status'
        ordering = ['TimeStamp']

class HvilStatus(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    hvil_status_value = models.IntegerField('HVIL Status Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    hvil_status = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.hvil_status_value} - {self.bus}'

    class Meta:
        verbose_name = 'HVIL Status'
        verbose_name_plural = 'HVIL Status'
        ordering = ['TimeStamp']


class PackTemperature(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    pack_temperature_value = models.FloatField('Pack Temperature', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    pack_temperature = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.pack_temperature_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.max_temperature_pack_value} - {self.bus}'

    class Meta:
        verbose_name = 'Max Temperature Pack'
        verbose_name_plural = 'Max Temperatures Pack'
        ordering = ['TimeStamp']


class BatteryPackCurrent(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    battery_pack_current_value = models.FloatField('Battery Pack Current', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    battery_pack_current = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.battery_pack_current_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.battery_pack_voltage_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.battery_pack_cell_max_voltage_value} - {self.bus}'

    class Meta:
        verbose_name = 'Battery Pack Cell Max Voltage'
        verbose_name_plural = 'Batteries Pack Cell Max Voltage'
        ordering = ['TimeStamp']

class CellsVoltage(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    max_v = models.FloatField('Max', null=True, blank=True)
    min_v = models.FloatField('Min', null=True, blank=True)
    avg = models.FloatField('Avg', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)
    diff_min_max = models.FloatField('Diff Min Max', null=True, blank=True) 
    diff_min_avg = models.FloatField('Diff Min Avg', null=True, blank=True)
    diff_max_avg = models.FloatField('Diff Max Avg', null=True, blank=True)


    cells_voltage = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.max_v} - {self.min_v} - {self.avg} - {self.diff_max_avg} - {self.diff_min_avg} - {self.diff_min_max} - {self.bus}'
    
    class Meta:
        verbose_name = 'Cells Voltage'
        verbose_name_plural = 'Cells Voltage'
        

class BatteryPackCellMinVoltage(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', null=True, blank=True)
    battery_pack_cell_min_voltage_value = models.FloatField('Battery Pack Cell Min Voltage', null=True, blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    battery_pack_cell_min_voltage = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.battery_pack_cell_min_voltage_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.battery_pack_avg_cell_voltage_value} - {self.bus}'

    class Meta:
        verbose_name = 'Battery Pack Avg Cell Voltage'
        verbose_name_plural = 'Batteries Pack Avg Cell Voltage'
        ordering = ['TimeStamp']


class PtcOneVoltage(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    ptc_one_voltage_value = models.FloatField('PTC One Voltage', blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    ptc_one = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.ptc_one_voltage_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.ptc_two_voltage_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.positive_torque_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.negative_torque_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.engine_temperature_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.lenze_current_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.lenze_engine_speed_value} - {self.bus}'

    class Meta:
        verbose_name = 'Lenze Engine Speed'
        verbose_name_plural = 'Lenze Engine Speeds'
        ordering = ['TimeStamp']


class Speed(models.Model):
    TimeStamp = models.DateTimeField('TimeStamp', blank=True, null=True)
    speed_value = models.FloatField('Speed Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    speed = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.speed_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.system_pressure_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.btms_temperature_value} - {self.bus}'

    class Meta:
        verbose_name = 'BTMS Temperature'
        verbose_name_plural = 'BTMS Temperatures'




class GearStatus(models.Model):
    TimeStamp = models.DateTimeField('Timestamp', blank=True, null=True)
    gear_status_value = models.FloatField('Gear Status Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    gear_status = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.gear_status_value} - {self.bus}'

    class Meta:
        verbose_name = 'Gear Status'
        verbose_name_plural = 'Gear Status'
        ordering = ['TimeStamp']


class BrakePedalStatus(models.Model):
    TimeStamp = models.DateTimeField('Timestamp', blank=True, null=True)
    brake_pedal_status_value = models.FloatField('Brake Pedal Status Value', blank=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    brake_pedal_status = models.Manager()

    def __str__(self):
        return f'{self.TimeStamp} - {self.brake_pedal_status_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.air_conditioner_status_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.service_compressor_value} - {self.bus}'

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
        return f'{self.TimeStamp} - {self.btms_status_value} - {self.bus}'

    class Meta:
        verbose_name = 'BTMS Status'
        verbose_name_plural = 'BTMS Status'
        ordering = ['TimeStamp']


class ModemInfo(models.Model):
    imei = models.CharField('IMEI', max_length=20)
    rem_number = models.CharField('REM Number', max_length=20)
    sim_number = models.CharField('SIM Number', max_length=20)
    user = models.CharField('User', max_length=20)
    password = models.CharField('Password', max_length=20)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    modem_info = models.Manager()

    def __str__(self):
        return f'{self.imei} - {self.rem_number} - {self.sim_number} - {self.user} - {self.password} - {self.bus}'

    class Meta:
        verbose_name = 'Modem Info'
        verbose_name_plural = 'Modem Info'
        ordering = ['rem_number']


class AwsPathBucket(models.Model):
    path_sniffer = models.CharField('Path Sniffer', max_length=100)
    path_name = models.CharField('Path Name', max_length=100)
    path_internal_date = models.CharField('Path Internal Date', blank=True, null=True, max_length=100)
    path_reveal_date = models.CharField('Path Reveal Date', blank=True, null=True, max_length=100)
    path_status = models.BooleanField('Path Status', default=False)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return (f'{self.path_sniffer} - {self.path_name} - {self.path_internal_date} - {self.path_reveal_date} - '
                f'{self.path_status}')

    class Meta:
        verbose_name = 'Aws Path Bucket'
        verbose_name_plural = 'Aws Path Buckets'
        ordering = ['path_sniffer']

class EcuState(models.Model):
    TimeStamp = models.DateTimeField('Timestamp', blank=True, null=True)
    sleep_state = models.IntegerField(blank=True, null=True)
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, null=True, blank=True)
    lts_kms = models.IntegerField('LTS Kms', blank=True, null=True)

    ecu_state = models.Manager()

    def __str__(self):
        return f'{self.sleep_state} - {self.bus} - {self.TimeStamp}'

    class Meta:
        verbose_name = 'ECU State'
        verbose_name_plural = 'ECU States'
        
