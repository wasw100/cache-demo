# -*- coding: utf-8 -*-
import string
import random
import functools
from flask import Flask
from flask.ext.cache import Cache

SECRET_KEY = '\xfb\x12\xdf\xa1@i\xd6>V\xc0\xbb\x8fp\x16#Z\x0b\x81\xeb\x16'
DEBUG = True
CACHE_TYPE = 'memcached'
CACHE_DEFAULT_TIMEOUT = 60  # 默认缓存1个小时
CACHE_KEY_PREFIX = 'test_'  # 所有key之前添加前缀
CACHE_MEMCACHED_SERVERS = ['127.0.0.1:11211']


app = Flask(__name__)
app.config.from_object(__name__)
cache = Cache(app)

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


def get_dict_by_ids(func, ids):
    """
    :param func: 有cache.memoize装饰的方法
    :params ids: id列表
    :return: id为key, func返回值位value的dict
    """
    if not ids:
        return dict()

    instance_self = getattr(func, '__self__', None)
    if instance_self:
        make_cache_key_func = functools.partial(func.make_cache_key,
                                                func.uncached,
                                                instance_self)
        uncached_func = functools.partial(func.uncached, instance_self)
    else:
        make_cache_key_func = functools.partial(func.make_cache_key,
                                                func.uncached)
        uncached_func = func.uncached

    # cache_key列表
    cache_key_list = []
    for item_id in ids:
        cache_key = make_cache_key_func(item_id)
        cache_key_list.append(cache_key)

    # 批量获取缓存
    items = cache.get_many(*cache_key_list)

    uncached_dict = {}
    # 单独获取缓存中没有的数据, 应该使用set_many设置缓存
    for (index, item) in enumerate(items):
        if item is None:
            item_id = ids[index]
            cache_key = cache_key_list[index]

            value = uncached_func(item_id)
            items[index] = value
            uncached_dict[cache_key] = value
    if uncached_dict:
        cache.set_many(uncached_dict, timeout=func.cache_timeout)

    return dict(zip(ids, items))


@app.route('/func')
def func_page():
    cache.delete_memoized(hello)
    print hello(1)
    print hello(3)
    print get_dict_by_ids(hello, [1, 2, 3])
    return 'OK'

@app.route('/cls')
def cls_page():
    cache.delete_memoized(User.get)
    print User.get(1)
    print User.get(3)
    print get_dict_by_ids(User.get, [1, 2, 3])
    return 'OK'

@app.route('/self')
def self_page():
    user = User('abc')
    cache.delete_memoized(user.get)
    print user.get_2(1)
    print user.get_2(3)
    print get_dict_by_ids(user.get_2, [1, 2, 3])
    return 'OK'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
