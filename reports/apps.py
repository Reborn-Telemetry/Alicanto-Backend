from django.apps import AppConfig
from django.db.models.signals import post_migrate
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJob

class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'
    scheduler = None  # Variable de clase para controlar el scheduler

    def ready(self):
        # Conectar la señal post_migrate para iniciar el scheduler después de las migraciones
        post_migrate.connect(self.start_scheduler, sender=self)

    def start_scheduler(self, **kwargs):
        # Evitar inicializar el scheduler más de una vez
        if not self.scheduler:
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

        # Configurar el trigger para que se ejecute todos los días a las 12:55 PM hora de Chile
        self.scheduler.add_job(
            calcular_energia_anual_diaria,
            trigger=CronTrigger(hour=13, minute=30, timezone=timezone("America/Santiago")),
            id="calcular_energia_anual_diaria",
            replace_existing=True,
        )

    def _iniciar_calculo_historico_diario(self):
        from bus_signals.threads.matriz_energia_historico_flota import scheduled_get_historical_data
        from apscheduler.triggers.cron import CronTrigger
        from pytz import timezone

        # Configurar el trigger para los datos históricos
        self.scheduler.add_job(
            scheduled_get_historical_data,
            trigger=CronTrigger(hour=23, minute=57, timezone=timezone("America/Santiago")),
            id="scheduled_get_historical_data",
            replace_existing=True,
        )

    def _iniciar_calculo_odometro_diario(self):
        from bus_signals.threads.max_odometer_dayly import daily_max_auto_update
        from apscheduler.triggers.cron import CronTrigger
        from pytz import timezone

        # Configurar el trigger para la actualización del odómetro diario
        self.scheduler.add_job(
            daily_max_auto_update,
            trigger=CronTrigger(hour=23, minute=30, timezone=timezone("America/Santiago")),
            id="daily_max_auto_update",
            replace_existing=True,
        )
