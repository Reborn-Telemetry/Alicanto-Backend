from django.apps import AppConfig
from django.db.models.signals import post_migrate

class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'

    def ready(self):
        # Conectar la señal post_migrate para iniciar el scheduler después de las migraciones
        post_migrate.connect(self.start_scheduler, sender=self)

    def start_scheduler(self, **kwargs):
        from apscheduler.schedulers.background import BackgroundScheduler
        from django_apscheduler.jobstores import DjangoJobStore

        from bus_signals.threads.energia_anual import iniciar_calculo_diario
        from bus_signals.threads.matriz_energia_historico_flota import iniciar_calculo_historico_diario
        from bus_signals.threads.max_odometer_dayly import iniciar_calculo_odometro_diario

        # Inicializar el scheduler una sola vez dentro de la señal post_migrate
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Registrar las tareas programadas
        iniciar_calculo_diario(scheduler)  # Energía anual
        iniciar_calculo_historico_diario(scheduler)  # Datos históricos de energía
        iniciar_calculo_odometro_diario(scheduler)  # Actualización del odómetro diario

        # Iniciar el scheduler
        scheduler.start()
