# -*- coding: utf-8 -*-
from __future__ import absolute_import

import string
import random
from flask import Flask

from custom_cache import CustomCache

SECRET_KEY = '\xfb\x12\xdf\xa1@i\xd6>V\xc0\xbb\x8fp\x16#Z\x0b\x81\xeb\x16'
DEBUG = True
CACHE_TYPE = 'memcached'
CACHE_DEFAULT_TIMEOUT = 60  # 默认缓存1分钟
CACHE_KEY_PREFIX = 'test_'  # 所有key之前添加前缀
CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']


app = Flask(__name__)
app.config.from_object(__name__)
cache = CustomCache(app)

strings = string.ascii_lowercase


class User():
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.name)

    def __init__(self, name):
        self.name = name

    @classmethod
    @cache.memoize()
    def get(cls, a):
        print 'class not from cache {0}'.format(a)
        return 'cls ' + strings[a] + random.choice(strings)

    @cache.memoize()
    def get_2(self, a):
        return 'self-' + self.name + strings[a] + random.choice(strings)


#: This is an example of a memoized function
@cache.memoize()
def hello(a):
    print 'not from cache {0}'.format(a)
    return strings[a] + random.choice(strings)


@app.route('/func')
def func_page():
    cache.delete_memoized(hello)
    print hello(1)
    print hello(3)
    print cache.get_item_dict(hello, [1, 2, 3])
    return 'OK'


@app.route('/cls')
def cls_page():
    cache.delete_memoized(User.get)
    print User.get(1)
    print User.get(3)
    print cache.get_item_dict(User.get, [1, 2, 3])
    return 'OK'


@app.route('/self')
def self_page():
    user = User('abc')
    cache.delete_memoized(user.get)
    print user.get_2(1)
    print user.get_2(3)
    print cache.get_item_dict(user.get_2, [1, 2, 3])
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
