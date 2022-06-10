import contextlib
from datetime import datetime

from kombu.exceptions import EncodeError
from pymongo.errors import InvalidDocument
from celery import states, Task, uuid
from celery.backends.base import get_current_task
from celery.backends.mongodb import MongoBackend as _MongoBackend

from django.core.cache import cache


class LockConflictError(Exception):
    pass


class Lock:
    def __init__(self, key=None, expires=None) -> None:
        self.key = key
        self.expires = expires
    
    def try_lock(self):
        if self.acquire():
            self.release()
            return True
        return False
    
    def acquire(self):
        return cache.add(f"task_lock:{self.key}", self.uid, self.expires)
    
    def release(self):
        cache.delete(f"task_lock:{self.key}")
    
    def __enter__(self):
        if not self.acquire():
            raise LockConflictError(self.key)
    
    def __exit__(self, *args):
        self.release()


class CustomTask(Task):
    lock = None

    def apply_async(self, args=None, kwargs=None, task_id=None, producer=None, link=None, link_error=None, shadow=None, **options):
        task_id = task_id or uuid()
        if self.lock:
            self.lock.uid = task_id
            if not self.lock.key:
                self.lock.key = self.name
            if not self.lock.try_lock():
                raise LockConflictError(self.lock.key)
        return super().apply_async(args, kwargs, task_id, producer, link, link_error, shadow, **options)
    
    def apply(self, args=None, kwargs=None, link=None, link_error=None, task_id=None, retries=None, throw=None, logfile=None, loglevel=None, headers=None, **options):
        task_id = task_id or uuid()
        if self.lock:
            self.lock.uid = task_id
            if not self.lock.key:
                self.lock.key = self.name
            cm = self.lock
        else:
            cm = contextlib.nullcontext()
        with cm:
            return super().apply(args, kwargs, link, link_error, task_id, retries, throw, logfile, loglevel, headers, **options)
    
    def __call__(self, *args, **kwargs):
        if self.lock:
            self.lock.uid = self.request.id
            if not self.lock.key:
                self.lock.key = self.name
            cm = self.lock
        else:
            cm = contextlib.nullcontext()
        with cm:
            return super().__call__(*args, **kwargs)


class MongoBackend(_MongoBackend):
    def _get_result_meta(self, result, state, traceback, request, format_date=False, encode=False):
        meta = super()._get_result_meta(result, state, traceback, request, format_date, encode)
        if state == states.STARTED:
            meta['date_started'] = datetime.utcnow()
        task = get_current_task()
        meta.update(module=task.run.__module__, name=task.name.rsplit('.', 1)[-1])
        return meta

    def _store_result(self, task_id, result, state,
                      traceback=None, request=None, **kwargs):
        """Store return value and state of an executed task."""
        meta = self._get_result_meta(result=self.encode(result), state=state,
                                     traceback=traceback, request=request)
        # Add the _id for mongodb
        meta['_id'] = task_id

        try:
            self.collection.update_one({'_id': task_id}, {'$set': meta}, upsert=True)
        except InvalidDocument as exc:
            raise EncodeError(exc)

        return result
