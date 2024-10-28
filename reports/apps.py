from django.apps import AppConfig
import os
import pytz

class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'
    scheduler = None  # Variable de clase para controlar el scheduler

    def ready(self):
        # Iniciar el scheduler directamente cuando la aplicación esté lista
        self.start_scheduler()

    def start_scheduler(self):
        # Evitar inicializar el scheduler más de una vez
        if not self.scheduler:
            from apscheduler.schedulers.background import BackgroundScheduler
            from django_apscheduler.jobstores import DjangoJobStore
            from django_apscheduler.models import DjangoJob  # Importar aquí

            self.scheduler = BackgroundScheduler()
            self.scheduler.add_jobstore(DjangoJobStore(), "default")

            # Evitar registrar trabajos duplicados
            if not DjangoJob.objects.filter(id="calcular_energia_anual_diaria").exists():
                self._iniciar_calculo_diario()

            if not DjangoJob.objects.filter(id="scheduled_get_historical_data").exists():
                self._iniciar_calculo_historico_diario()

            if not DjangoJob.objects.filter(id="daily_max_auto_update").exists():
                self._iniciar_calculo_odometro_diario()

            # Iniciar el scheduler
            self.scheduler.start()

    def _iniciar_calculo_diario(self):
        from bus_signals.threads.energia_anual import calcular_energia_anual_diaria
        from apscheduler.triggers.cron import CronTrigger
        from pytz import timezone

        # Configurar el trigger para que se ejecute todos los días a las 14:30 PM hora de Chile
        self.scheduler.add_job(
            calcular_energia_anual_diaria,
            trigger=CronTrigger(hour=16, minute=10, timezone=pytz.timezone('America/santiago')),
            id="calcular_energia_anual_diaria",
            replace_existing=True,
            misfire_grace_time=300,
            max_instances=1,
        )

    def _iniciar_calculo_historico_diario(self):
        from bus_signals.threads.matriz_energia_historico_flota import scheduled_get_historical_data
        from apscheduler.triggers.cron import CronTrigger
        from pytz import timezone

        # Configurar el trigger para los datos históricos
        self.scheduler.add_job(
            scheduled_get_historical_data,
            trigger=CronTrigger(hour=23, minute=57, timezone=pytz.timezone('America/santiago')),
            id="scheduled_get_historical_data",
            replace_existing=True,
            misfire_grace_time=300,
            max_instances=1,
        )

    def _iniciar_calculo_odometro_diario(self):
        from bus_signals.threads.max_odometer_dayly import daily_max_auto_update
        from apscheduler.triggers.cron import CronTrigger
        from pytz import timezone

        # Configurar el trigger para la actualización del odómetro diario
        self.scheduler.add_job(
            daily_max_auto_update,
            trigger=CronTrigger(hour=10, minute=1, timezone=pytz.timezone('America/santiago')),
            id="daily_max_auto_update",
            replace_existing=True,
            misfire_grace_time=300,
            max_instances=1,
        )
