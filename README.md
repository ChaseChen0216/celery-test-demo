
##  1. Make sure Redis is running 

## 2. Run Django
```shell
pip install -r requirements.txt
python manager.py migrate
python manager.py createsuperuser
python manager.py runserver
```

## 3. Run Celery

### run worker
```shell
celery -A meetingroom worker -l=info
```

### run beat
```shell
celery -A meetingroom beat --scheduler django_celery_beat.schedulers:DatabaseScheduler -l=info
```

### run celery monitor
```shell
celery -A meetingroom flower --broker=redis://127.0.0.1:6379/0
```

## 4. FrameWork
![](./framework.png)



