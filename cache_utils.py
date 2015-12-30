# -*- coding: utf-8 -*-
"""flask-cache的工具类"""
from __future__ import absolute_import

import functools
# 导入项目对应的flask-cache对象
from cache import cache


def get_dict(func, ids):
    """
    id为key, value为func返回值的dict
    :param func: 有cache.memoize装饰的方法, 只支持一个参数
    :params ids: id列表
    :return: dict
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
