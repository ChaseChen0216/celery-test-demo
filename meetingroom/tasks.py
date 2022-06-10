import time
from celery import shared_task
from celery.utils.log import get_task_logger

from meetingroom.backends import Lock


logger = get_task_logger(__name__)


@shared_task
def add(a, b):
    return a + b



@shared_task(bind=True, lock=Lock())
def long_running(self):
    logger.info("%s - %s - %s -%s", self.run.__module__, self.name, self, self.lock)
    for i in range(10):
        # self.update_state(state="PROGRESS", meta={'progress': (i + 1) * 10})
        time.sleep(1)
    return 55
