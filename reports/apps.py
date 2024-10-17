from django.apps import AppConfig


class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'

    def ready(self):
        from bus_signals.threads.matriz_km_flota_history import start
        start()

        # Importar e iniciar el scheduler
        from bus_signals.threads.matriz_energia_historico_flota import begin
        begin()