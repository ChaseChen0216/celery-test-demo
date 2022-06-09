from .base import *

ALLOWED_HOSTS = ["*", '127.0.0.1', "host.docker.internal"]

DEBUG = True

STATIC_URL = '/static/'
STATIC_ROOT = 'static'

# # 使得html文件能够读取静态的CSS\JS文件
# HERE = os.path.dirname(os.path.abspath(__file__))
# print("使得html文件能够读取静态的CSS\JS文件")
# print(HERE)
# HERE = os.path.join(HERE, '../')
# print(HERE)
# STATICFILES_DIRS = (
#     os.path.join(HERE, 'static/'),
# )
# print(STATICFILES_DIRS)

# 显示服务器信息
SIMPLEUI_HOME_INFO = True

# 隐藏最近动作
SIMPLEUI_HOME_ACTION = False


CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/1'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERYD_MAX_TASKS_PER_CHILD = 10
CELERYD_LOG_FILE = os.path.join(BASE_DIR, "logs", "celery_work.log")
CELERYBEAT_LOG_FILE = os.path.join(BASE_DIR, "logs", "celery_beat.log")

# import sentry_sdk
# from sentry_sdk.integrations.django import DjangoIntegration

# sentry_sdk.init(
#     dsn="http://xxx@recruit.ihopeit.com:9000/2",
#     integrations=[DjangoIntegration()],
#     # performance tracing sample rate, 采样率, 生产环境访问量过大时，建议调小（不用每一个URL请求都记录性能）
#     traces_sample_rate=1.0, #
#
#     # If you wish to associate users to errors (assuming you are using
#     # django.contrib.auth) you may enable sending PII data.
#     # 聚类分析 可以上传它的浏览器 版本 操作系统
#     send_default_pii=True
# )
