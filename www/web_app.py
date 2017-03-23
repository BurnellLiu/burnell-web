#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import asyncio
import os

from aiohttp import web
from jinja2 import Environment, FileSystemLoader

import db_orm
import web_core

from config import configs
from template_filters import datetime_filter
from web_middlewares import logger_factory, auth_factory, response_factory

__author__ = 'Burnell Liu'


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
        work_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(work_path, 'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)

    # 设置jinja2的过滤器
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f

    # 保存jinja2环境实例
    app['__templating__'] = env


async def init_app(event_loop):
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
    # 最后再返回经过全部拦截器装饰过的函数
    # 这样最终调用url处理函数之前或之后就可以进行一些额外的处理
    middlewares=[logger_factory, auth_factory, response_factory]
    web_app = web.Application(loop=event_loop, middlewares=middlewares)

    # 初始化前端模板, 指定的过滤器函数可以在模板文件中使用
    init_jinja2(web_app, filters=dict(datetime=datetime_filter))

    # 添加路由函数
    web_core.add_routes(web_app, 'web_routes.py')

    # 添加静态文件
    web_core.add_static(web_app)

    # 创建服务器
    server = await event_loop.create_server(
        web_app.make_handler(),
        '127.0.0.1',
        9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return server


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init_app(loop))
    loop.run_forever()
