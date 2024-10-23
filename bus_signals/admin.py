from django.contrib import admin
from . import models

admin.site.register(models.Bus)
admin.site.register(models.Battery24Volts)
admin.site.register(models.Soc)
admin.site.register(models.PackTemperature)
admin.site.register(models.MaxTemperaturePack)
admin.site.register(models.BatteryHealth)
admin.site.register(models.BatteryPackCurrent)
admin.site.register(models.BatteryPackVoltage)
admin.site.register(models.BatteryPackCellMaxVoltage)
admin.site.register(models.BatteryPackCellMinVoltage)
admin.site.register(models.BatteryPackAvgCellVoltage)
admin.site.register(models.Isolation)
admin.site.register(models.PtcOneVoltage)
admin.site.register(models.PtcTwoVoltage)
admin.site.register(models.PositiveTorque)
admin.site.register(models.NegativeTorque)
admin.site.register(models.EngineTemperature)
admin.site.register(models.LenzeCurrent)
admin.site.register(models.LenzeEngineSpeed)
admin.site.register(models.Odometer)
admin.site.register(models.Speed)
admin.site.register(models.SystemPressure)
admin.site.register(models.BtmsTemperature)
admin.site.register(models.FusiCode)
admin.site.register(models.ChargeStatus)
admin.site.register(models.GearStatus)

admin.site.register(models.BrakePedalStatus)
admin.site.register(models.AirConditionerStatus)
admin.site.register(models.ServiceCompressorStatus)
admin.site.register(models.BtmsStatus)
admin.site.register(models.FusiMessage)
admin.site.register(models.ModemInfo)

admin.site.register(models.AnualEnergy)



