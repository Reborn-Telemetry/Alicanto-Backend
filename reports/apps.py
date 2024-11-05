from django.apps import AppConfig
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

            if not DjangoJob.objects.filter(id="daily_recorrido_update").exists():
                self._iniciar_calculo_recorrido_diario()

            if not DjangoJob.objects.filter(id="eliminar_duplicados_diarios").exists():
                self._iniciar_eliminar_duplicados_diarios()

            # Iniciar el scheduler
            self.scheduler.start()

    def _iniciar_calculo_diario(self):
        from bus_signals.threads.energia_anual import calcular_energia_anual_diaria
        from apscheduler.triggers.cron import CronTrigger

        # Configurar el trigger para que se ejecute todos los días a las 14:30 PM hora de Chile
        self.scheduler.add_job(
            calcular_energia_anual_diaria,
            trigger=CronTrigger(hour=16, minute=10, timezone=pytz.timezone('America/Santiago')),
            id="calcular_energia_anual_diaria",
            replace_existing=True,
            misfire_grace_time=300,
            max_instances=1,
        )

    def _iniciar_calculo_historico_diario(self):
        from bus_signals.threads.matriz_energia_historico_flota import scheduled_get_historical_data
        from apscheduler.triggers.cron import CronTrigger

        # Configurar el trigger para los datos históricos
        self.scheduler.add_job(
            scheduled_get_historical_data,
            trigger=CronTrigger(hour=23, minute=51, timezone=pytz.timezone('America/Santiago')),
            id="scheduled_get_historical_data",
            replace_existing=True,
            misfire_grace_time=300,
            max_instances=1,
        )

    def _iniciar_calculo_odometro_diario(self):
        from bus_signals.threads.max_odometer_dayly import daily_max_auto_update
        from apscheduler.triggers.cron import CronTrigger

        # Configurar el trigger para la actualización del odómetro diario
        self.scheduler.add_job(
            daily_max_auto_update,
            trigger=CronTrigger(hour=23, minute=55, timezone=pytz.timezone('America/Santiago')),
            id="daily_max_auto_update",
            replace_existing=True,
            misfire_grace_time=300,
            max_instances=1,
        )

    def _iniciar_calculo_recorrido_diario(self):
        from bus_signals.threads.recorridos import daily_recorrido_update  # Importar la nueva función
        from apscheduler.triggers.cron import CronTrigger

        # Configurar el trigger para la actualización diaria del recorrido
        self.scheduler.add_job(
            daily_recorrido_update,
            trigger=CronTrigger(hour=23, minute=58, timezone=pytz.timezone('America/Santiago')),
            id="daily_recorrido_update",
            replace_existing=True,
            misfire_grace_time=300,
            max_instances=1,
        )

    def _iniciar_eliminar_duplicados_diarios(self):
        from bus_signals.threads.eraser import eliminar_duplicados_diarios  # Importa la función de eliminación de duplicados
        from apscheduler.triggers.cron import CronTrigger

        # Configurar el trigger para ejecutar la eliminación de duplicados todos los días a la medianoche
        self.scheduler.add_job(
            eliminar_duplicados_diarios,
            trigger=CronTrigger(hour=9, minute=40, timezone=pytz.timezone('America/Santiago')),
            id="eliminar_duplicados_diarios",
            replace_existing=True,
            misfire_grace_time=300,
            max_instances=1,
        )
