from __future__ import absolute_import, unicode_literals
import logging

import os

from celery import Celery, signals, utils
from django.conf import settings

# set the default Django settings module for the 'celery' program.
# 如果没有修改settings文件路径的话 一般就是 根应用.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.local')

app = Celery('meetingroom', task_cls='meetingroom.backends.CustomTask')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
# 规定在settings中以CELERY开头的变量才能被celery读取
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
# 自动从加载的app寻找task.py
app.autodiscover_tasks()
app.loader.override_backends = {'mon': 'meetingroom.backends.MongoBackend'}
app.conf.task_track_started = True


@signals.task_revoked.connect
def on_task_revoked(sender, **kwargs):
    sender.lock.release()


@signals.task_prerun.connect
def on_task_prerun(sender, task_id, **kwargs):
    logger = utils.log.task_logger

    log_handlers = []
    for handler in logger.handlers:
        if getattr(handler, '__pertask__', False):
            handler.close()
        else:
            log_handlers.append(handler)

    this_handler = logging.FileHandler(os.path.join(settings.LOG_ROOT, f"{task_id}.log"))
    this_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s|%(message)s"))
    this_handler.__pertask__ = True
    log_handlers.append(this_handler)
    logger.handlers[:] = log_handlers


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))



#
# 设置定时任务的方式
# 1 django后台添加
# 2 系统启动完后自动注册 setup_periodic_tasks函数
# 3 在代码里直接配置 app.conf.beat_schedule
# 4 动态添加（较多） notes有截图


# !配置文件注册
# this is important to load the celery tasks
# from meetingroom.tasks import add

# app.conf.beat_schedule = {
#     'every-5-seconds': {
#         'task': 'meetingroom.tasks.add',
#         'schedule': 5.0,
#         'args': (16, 4,)
#     },
    # 'add-every-monday-morning': {
    #     'task': 'tasks.add',
    #     'schedule': crontab(hour=7, minute=30, day_of_week=1),
    #     'args': (16, 16),
    # },
    # 'add-at-melbourne-sunset': {
    #     'task': 'tasks.add',
    #     'schedule': solar('sunset', -37.81753, 144.96715),
    #     'args': (16, 16),
    # },
# }

# beat进程启动时注册
# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # Calls test('hello') every 10 seconds.
#     sender.add_periodic_task(10.0, test.s('hello'), name='every-10-seconds')


#     # Calls test('world') every 30 seconds
#     sender.add_periodic_task(30.0, test.s('world'), expires=10)

#     # Executes every Monday morning at 7:30 a.m.
#     sender.add_periodic_task(
#         crontab(hour=7, minute=30, day_of_week=1),
#         test.s('Happy Mondays!'),
#     )

# # 动态添加周期任务 input in python manager.py shell
# import json
# from django_celery_beat.models import PeriodicTask, IntervalSchedule

# scheduler, created = IntervalSchedule.objects.get_or_create(every=10, period=IntervalSchedule.SECONDS,)

# task = PeriodicTask.objects.create(interpythoval=scheduler, name='say hello', task= 'meetingroom.celery.test', args=json.dumps(['welcome']),)


@app.task
def test(arg):
    print(arg)
    print("this is on_after_configure task")

app.conf.timezone = "Asia/Shanghai"
