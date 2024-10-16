from django.apps import AppConfig



class BusSignalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bus_signals'

    def ready(self):
        from bus_signals.threads.energia_anual import iniciar_calculo_diario
        iniciar_calculo_diario()
