import time
from celery import shared_task
from celery.utils.log import get_task_logger

from meetingroom.backends import Lock


logger = get_task_logger(__name__)
INTERVAL = 10


@shared_task
def add(a, b):
    return a + b



@shared_task(bind=True, lock=Lock())
def long_running(self, duration=10):
    for i in range(duration):
        # self.update_state(state="PROGRESS", meta={'progress': (i + 1) * 10})
        time.sleep(1)
    return 55


@shared_task(bind=True)
def periodic_task(self):
    logger.info("Scheduling the next run at %d seconds later", INTERVAL)
    self.apply_async(countdown=INTERVAL)  # Round to the interval
    # Pretend it takes 20 seconds to finish
    time.sleep(20)
    return 42



@shared_task()
def enable_periodic_task(task_id):
    # This task can be a crontab or interval scheduled task.
    from django_celery_beat.models import PeriodicTask, PeriodicTasks

    PeriodicTask.objects.filter(pk=task_id).update(enabled=True)
    PeriodicTasks.update_changed()

# To kickstart a periodic task:
# enable_periodic_task.apply_async(eta=start_time - 10s)
