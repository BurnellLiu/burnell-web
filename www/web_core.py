#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools
import inspect
import asyncio
import logging
import os


__author__ = 'Burnell Liu'


def get(path):
    """
    定义装饰器 @get('/path')
    :param path: URL路径
    """
    def decorator(func):
        # 设置被装饰的函数签名为原始的签名
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator


def post(path):
    """
    定义装饰器 @post('/path')
    :param path: URL路径
    """
    def decorator(func):
        # 设置被装饰的函数签名为原始的签名
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator


def add_static(app):
    """
    添加静态资源到WEB APP对象中
    :param app: WEB APP对象
    """
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    logging.info('add static: prefix=%s, path=%s' % ('/static/', path))


def add_route(app, fn):
    """
    将指定的路由函数添加到WEB APP对象中
    :param app: WEB APP对象
    :param fn: 路由函数
    """
    # 路由函数必须包含指定的属性
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))

    # 将非协程的函数转换为协程
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)

    logging.info('add route function: %s(%s), method(%s), path(%s)' %
                 (fn.__name__, ', '.join(inspect.signature(fn).parameters.keys()), method, path, ))

    # app.router.add_route(method, path, RequestHandler(fn))
    app.router.add_route(method, path, fn)


def add_routes(app, module_name):
    """
    将指定模块中的所有路由函数添加到WEB APP对象中
    :param app: WEB APP对象
    :param module_name: 模块名称
    """
    n = module_name.find('.')
    if n == (-1):
        mod = __import__(module_name, globals(), locals())
    else:
        mod = __import__(module_name[:n], globals(), locals())

    # 路由函数包含属性__method__和__route__
    # 这连个属性由get和post装饰器生成
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            method = getattr(fn, '__method__', None)
            path = getattr(fn, '__route__', None)
            if method and path:
                add_route(app, fn)


if __name__ == '__main__':
    pass

