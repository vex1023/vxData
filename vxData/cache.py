# encoding = utf-8
'''
缓存，减少网络下载的次数
'''

import time
import hashlib

from datetime import datetime, timedelta
from multiprocessing import Lock
from functools import wraps

try:
    import cPickle as pickle
except:
    import pickle


class CacheExpiredException(Exception):
    pass


class NotCacheException(Exception):
    pass


class MemoryStorage():
    def __init__(self):
        self._data = {}
        self._lock = Lock()

    def set(self, key, value, expire_at):
        with self._lock:
            now = time.time()
            if expire_at > now or expire_at < 0:
                self._data[key] = {'expire_at': expire_at, 'value': value}

    def get(self, key):
        with self._lock:
            data = self._data.get(key, None)
            if data:
                now = time.time()
                if data['expire_at'] < 0 or now < data['expire_at']:
                    return data['value']
                else:
                    self._data.pop(key)
                    raise CacheExpiredException('now: %s, data: %s' % (now, data))

            raise NotCacheException('key: %s, data: %s' % (key, data))

    def flush(self):
        del self._data
        self._data = {}


# 定义计时器
class Timer():
    def expire_at(self):
        return


# 永不超时的计时器
class EndlessTimer(Timer):
    def expire_at(self):
        return -1


# 按照时间间隔确定的计时器
class TTLTimer(Timer):
    def __init__(self, seconds=0, minutes=0, hours=0, days=0, weeks=0):
        self._ttl = timedelta(seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks)

    def expire_at(self):
        return (datetime.now() + self._ttl).timestamp()


# 缓存修饰器
class cache():
    storage = MemoryStorage()

    def __init__(self, timer=EndlessTimer()):
        self._timer = timer

    @classmethod
    def set_storage(cls, storage):
        cls.storage = storage

    def __call__(self, func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            # TODO pickle 不支持多线程，需要找个替代方案
            # cache_key = hashlib.md5(pickle.dumps((func.__name__, args, kwargs))).hexdigest()
            cache_string = '%s_%s_%s' % ((func.__name__, args, kwargs))
            cache_key = hashlib.md5(cache_string.encode('utf-8')).hexdigest()
            try:
                ret_val = cache.storage.get(cache_key)
                return ret_val
            except (NotCacheException, CacheExpiredException) as err:
                ret_val = func(*args, **kwargs)
                expire_at = self._timer.expire_at()
                cache.storage.set(cache_key, ret_val, expire_at)

            return ret_val

        return wrapped

    @classmethod
    def flush(cls):
        cls.storage.flush()
