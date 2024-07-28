from apscheduler.schedulers.background import BackgroundScheduler

from flask.helpers import get_debug_flag
import werkzeug

import queue
import logging
from logging.handlers import QueueHandler, QueueListener

class FlaskSchedulerManager(BackgroundScheduler):
    # =========================================================================
    # Class functions
    # =========================================================================
    def __init__(self, scheduler=None, app=None):
        BackgroundScheduler.__init__(self)
        self.app = None
        self.scheduler = None
        self._listener = None
        self.logger = None

        if app:
            self.init_app(app)

    # =========================================================================
    # Initialize the APScheduler with a Flask application instance.
    # =========================================================================
    def init_app(self, app, logger_name="thread_logger", console_handler=True):
        State = True
        self.app = app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['scheduler'] = self
        self.scheduler = self

        self.logging_queue = queue.Queue(-1)
        self.logger = logging.getLogger(logger_name)

        queue_handler = QueueHandler(self.logging_queue)
        self.logger.addHandler(queue_handler)
        self.logger.setLevel(logging.DEBUG)

        if console_handler:
            console_handler = logging.StreamHandler()
            formatter = logging.Formatter(
                            '%(asctime)s %(levelname)-8s %(threadName)s: %(message)s')
            console_handler.setFormatter(formatter)
            self._listener = QueueListener(self.logging_queue, console_handler,
                                           respect_handler_level=True)
            self._listener.start()

        self._load_config()
        self._load_jobs()
        return State

    # =========================================================================
    # Re-create the QueueListener with the given handlers
    # =========================================================================
    def queuelistener(self, *args):
        if self._listener:
            self._listener.stop()
        self._listener = QueueListener(self.logging_queue, *args, respect_handler_level=True)
        self._listener.start()
        return

    def getLogger(self):
        return self.logger

    # ==========================================================================
    # Overload start to cope with Flask debugging
    # ==========================================================================
    def start(self, paused=False):
        # Flask in debug mode spawns a child process so that it can restart
        # the process each time your code changes,
        # the new child process initializes and starts a new APScheduler
        # causing the jobs to run twice.
        if get_debug_flag() and not werkzeug.serving.is_running_from_reloader():
            return
        super().start(paused=paused)

    # ==============================================================================
    # Load the configuration from the Flask configuration.
    # ==============================================================================
    def _load_config(self):
        options = {}

        if job_stores := self.app.config.get("SCHEDULER_JOBSTORES"):
            options["jobstores"] = job_stores

        if executors := self.app.config.get("SCHEDULER_EXECUTORS"):
            options["executors"] = executors

        if job_defaults := self.app.config.get("SCHEDULER_JOB_DEFAULTS"):
            options["job_defaults"] = job_defaults

        if timezone := self.app.config.get("SCHEDULER_TIMEZONE"):
            options["timezone"] = timezone

        super().configure(**options)
        return

    # ==============================================================================
    # Load the job definitions from the Flask configuration.
    # ==============================================================================
    def _load_jobs(self):
        if jobs := self.app.config.get("SCHEDULER_JOBS"):
            for job in jobs:
                if 'kwargs' in job:
                    job['kwargs']['logger'] = self.logger
                else:
                    job['kwargs'] = {}
                    job['kwargs']['logger'] = self.logger

                super().add_job(**job)
