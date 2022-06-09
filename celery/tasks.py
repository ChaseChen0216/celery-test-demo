from celery import Celery
import time
app = Celery('tasks', backend='redis://127.0.0.1', broker='redis://127.0.0.1')
# backend负责任务完成结果的存储  broker负责任务(注册)的存储

@app.task
def add(x, y):
    print("===========add================")
    time.sleep(3)
    return x - y

@app.task
def fib(n):
    print("============fib===============")
    a,b = 1,1
    for i in range(n-1):
        a,b = b,a+b
    return a
