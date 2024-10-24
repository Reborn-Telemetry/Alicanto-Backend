from django.apps import AppConfig
import os
import logging

class ReportsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reports'
    scheduler = None  # Variable de clase para controlar el scheduler

    def ready(self):
        # Verificar que estamos en el proceso principal (no en un proceso worker)
        if os.environ.get('RUN_MAIN') == 'true':
            print("RUN_MAIN is true, starting scheduler...")
            logging.info("RUN_MAIN is true, starting scheduler...")
            self.start_scheduler()

    def start_scheduler(self):
        # Evitar inicializar el scheduler más de una vez
        if not self.scheduler:
            from apscheduler.schedulers.background import BackgroundScheduler
            from django_apscheduler.jobstores import DjangoJobStore
            from django_apscheduler.models import DjangoJob  # Importar aquí

            logging.info("Creando el scheduler y añadiendo los trabajos programados...")
            self.scheduler = BackgroundScheduler()
            self.scheduler.add_jobstore(DjangoJobStore(), "default")

            # Evitar registrar trabajos duplicados
            if not DjangoJob.objects.filter(id="calcular_energia_anual_diaria").exists():
                logging.info("Registrando el trabajo 'calcular_energia_anual_diaria'...")
                self._iniciar_calculo_diario()

            if not DjangoJob.objects.filter(id="scheduled_get_historical_data").exists():
                logging.info("Registrando el trabajo 'scheduled_get_historical_data'...")
                self._iniciar_calculo_historico_diario()

            if not DjangoJob.objects.filter(id="daily_max_auto_update").exists():
                logging.info("Registrando el trabajo 'daily_max_auto_update'...")
                self._iniciar_calculo_odometro_diario()

            # Iniciar el scheduler
            self.scheduler.start()
            logging.info("Scheduler iniciado correctamente.")

    def _iniciar_calculo_diario(self):
        from bus_signals.threads.energia_anual import calcular_energia_anual_diaria
        from apscheduler.triggers.cron import CronTrigger
        from pytz import timezone

        # Configurar el trigger para que se ejecute todos los días a las 15:20 PM hora de Chile
        logging.info("Programando el trabajo diario de cálculo de energía anual.")
        self.scheduler.add_job(
            calcular_energia_anual_diaria,
            trigger=CronTrigger(hour=15, minute=20, timezone=timezone("America/Santiago")),
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
        logging.info("Programando el trabajo diario de cálculo de datos históricos.")
        self.scheduler.add_job(
            scheduled_get_historical_data,
            trigger=CronTrigger(hour=23, minute=57, timezone=timezone("America/Santiago")),
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
        logging.info("Programando el trabajo diario de actualización del odómetro.")
        self.scheduler.add_job(
            daily_max_auto_update,
            trigger=CronTrigger(hour=23, minute=30, timezone=timezone("America/Santiago")),
            id="daily_max_auto_update",
            replace_existing=True,
            misfire_grace_time=300,
            max_instances=1,
        )
