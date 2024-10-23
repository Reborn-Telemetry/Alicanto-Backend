from django.apps import AppConfig


class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'

    def ready(self):

        from bus_signals.threads.energia_anual import iniciar_calculo_diario
        iniciar_calculo_diario()

        from bus_signals.threads.matriz_energia_historico_flota import begin
        begin()

        from bus_signals.threads.max_odometer_dayly import daily_max_auto_update
        daily_max_auto_update()