#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import asyncio
import os
import json
import time
import hashlib

from aiohttp import web
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

from config import configs
from db_models import User

import db_orm
import web_core

__author__ = 'Burnell Liu'


async def parse_cookie(cookie_str):
    """
    解析COOKIE字符串
    :param cookie_str: COOKIE字符串
    :return: 成功返回user对象, 失败返回None
    """
    if not cookie_str:
        return None
    try:
        str_list = cookie_str.split('-')
        if len(str_list) != 3:
            return None
        uid, expires, sha1 = str_list
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None

        cookie_key = configs.session.secret
        s = '%s-%s-%s-%s' % (uid, user['password'], expires, cookie_key)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('parse cookie fail: invalid sha1')
            return None
        user['password'] = '******'
        return user

    except Exception as e:
        logging.exception(e)
        return None


async def logger_factory(app, handler):
    """
    记录URL日志的中间件, 请求被处理前进行写日志
    :param app: WEB应用对象
    :param handler: 处理请求对象
    :return: 中间件处理对象
    """
    async def logger(request):
        logging.info('request arrived, method: %s, path: %s' % (request.method, request.path))
        return await handler(request)
    return logger


async def auth_factory(app, handler):
    """
    验证登录的中间件, 请求被处理前进行登录验证
    :param app: WEB应用对象
    :param handler: 处理请求对象
    :return: 中间件处理对象
    """
    async def auth(request):
        logging.info('check user: %s %s' % (request.method, request.path))
        request.__user__ = None

        # 从COOKIE中解析出用户对象, 并且保存在请求对象中
        cookie_name = configs.session.cookie_name
        cookie_str = request.cookies.get(cookie_name)
        if cookie_str:
            user = await parse_cookie(cookie_str)
            if user:
                logging.info('set current user: %s' % user['email'])
                request.__user__ = user

        # 针对管理页面, 需要验证是否是管理员
        if request.path.startswith('/manage/') and (request.__user__ is None or not request.__user__['admin']):
            return web.HTTPFound('/signin')
        return await handler(request)
    return auth


async def response_factory(app, handler):
    """
    处理响应的中间件, 请求被处理后需要转换为web.Response对象再返回, 以保证满足aiohttp的要求
    :param app: WEB应用对象
    :param handler: 处理请求对象
    :return: 中间件处理对象
    """
    async def response(request):

        r = await handler(request)

        logging.info('response handler: %s' % r)

        # 如果处理后结果已经是web.Response对象, 则直接返回
        if isinstance(r, web.StreamResponse):
            return r

        # 如果处理后结果是字典对象, 则进行如下处理
        if isinstance(r, dict):
            template_file_name = r.get('__template__')

            # 处理结果字典中不包含__template__则表示直接返回数据，所以需要序列化为json数据
            # 处理结果字典中包含__template__则表示返回HTML页面
            if template_file_name is None:
                json_data = json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__)
                resp = web.Response(body=json_data.encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                # 从请求中取出用户信息
                r['__user__'] = request.__user__
                templating_env = app['__templating__']
                template = templating_env.get_template(template_file_name)
                resp = web.Response(body=template.render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp

    return response


def init_jinja2(app, **kw):
    """
    初始化前端模板库(jinja2)
    :param app: WEB应用对象
    :param kw: 关键字参数
    """
    logging.info('init jinja2...')

    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True)
    )

    # 设置前端模板库路径和其他参数
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)

    # 设置jinja2的过滤器
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f

    # 保存jinja2环境实例
    app['__templating__'] = env


def datetime_filter(t):
    """
    时间过滤器, 格式化日期
    :param t: 日期值, 该值为浮点数
    :return: 格式化后的日期字符串
    """
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


async def app_init(event_loop):
    """
    网站初始化函数
    :param event_loop: 事件循环对象
    :return: 服务器对象
    """
    # 创建数据库连接池
    await db_orm.create_pool(
        loop=event_loop,
        host=configs.db.host,
        user=configs.db.user,
        password=configs.db.password,
        db=configs.db.database)

    # 创建网站应用对象
    # middlewares 接收一个列表，列表的元素就是拦截器函数
    # aiohttp内部循环里以倒序分别将url处理函数用拦截器装饰一遍
    # 最后再返回经过全部拦截器装饰过的函数, 这样最终调用url处理函数之前或之后就可以进行一些额外的处理
    web_app = web.Application(loop=event_loop, middlewares=[logger_factory, auth_factory,response_factory])

    # 初始化前端模板, 指定的过滤器函数可以在模板文件中使用
    init_jinja2(web_app, filters=dict(datetime=datetime_filter))

    # 添加路由函数
    web_core.add_routes(web_app, 'web_routes.py')

    # 添加静态文件
    web_core.add_static(web_app)

    # 创建服务器
    server = await event_loop.create_server(web_app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return server


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(app_init(loop))
    loop.run_forever()
