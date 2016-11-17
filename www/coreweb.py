#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools
import inspect
import asyncio
import logging
import os
from aiohttp import web
from urllib import parse

from apis import APIError


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


def get_required_kw_args(fn):
    """
    获取目标函数的没有默认值的命名关键字参数
    :param fn: 目标函数
    :return: 函数参数元组
    """
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)


def get_named_kw_args(fn):
    """
    获取指定函数的命名关键字参数
    :param fn: 目标函数
    :return: 函数参数元组
    """
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)


def has_named_kw_args(fn):
    """
    检查目标函数是否存在命名关键字参数
    :param fn: 目标函数
    :return: True, False
    """
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True
    return False


def has_var_kw_arg(fn):
    """
    检查目标函数是否存在关键字参数
    :param fn: 目标函数
    :return: True, False
    """
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True
    return False


def has_request_arg(fn):
    """
    检查目标函数是否存在request参数
    :param fn: 目标函数
    :return: True, False
    """
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':
            found = True
            continue
        if found:
            if param.kind != inspect.Parameter.VAR_POSITIONAL and \
               param.kind != inspect.Parameter.KEYWORD_ONLY and \
               param.kind != inspect.Parameter.VAR_KEYWORD:
                raise ValueError('Request parameter must be the last named parameter in function: %s%s'
                                 % (fn.__name__, str(sig)))
    return found


class RequestHandler(object):
    """
    请求处理类
    该类实例为可调用对象（函数）
    该类目的就是从路由函数中分析其需要接收的参数，从request中获取必要的参数，调用路由函数
    """

    def __init__(self, fn):
        """
        构造函数
        :param fn: 路由函数
        """
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call__(self, request):
        kw = None
        # 如果路由函数包含关键字参数或者命名关键字参数或者没有默认值的命名关键字参数
        # 则我们需要组合出参数交给路由函数
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest('Missing Content-Type.')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest('JSON body must be object.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest('Unsupported Content-Type: %s' % request.content_type)
            if request.method == 'GET':
                qs = request.query_string
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]

        if kw is None:
            kw = dict(**request.match_info)
        else:
            # 如果路由函数只包含命名关键字参数, 则我们需要从kw中移除其他参数
            if not self._has_var_kw_arg and self._named_kw_args:
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # check named arg:
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v
        if self._has_request_arg:
            kw['request'] = request

        # 检查是否命名关键字参数都被填充
        if self._required_kw_args:
            for name in self._required_kw_args:
                if not (name in kw):
                    return web.HTTPBadRequest('Missing argument: %s' % name)

        logging.info('call route with args: %s' % str(kw))
        try:
            r = await self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)


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

    app.router.add_route(method, path, RequestHandler(fn))


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

