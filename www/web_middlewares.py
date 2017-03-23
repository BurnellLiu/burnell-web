#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from aiohttp import web
from config import configs
from session_cookie import user_cookie_parse

__author__ = 'Burnell Liu'


async def logger_factory(app, handler):
    """
    记录URL日志的中间件, 请求被处理前进行写日志
    :param app: WEB应用对象
    :param handler: 处理请求对象
    :return: 中间件处理对象
    """
    async def logger(request):
        # logging.info('request arrived, method: %s, path: %s' % (request.method, request.path))
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
        request.__user__ = None

        # 从COOKIE中解析出用户对象, 并且保存在请求对象中
        cookie_name = configs.user_cookie.name
        cookie_str = request.cookies.get(cookie_name)
        if cookie_str:
            user = await user_cookie_parse(cookie_str, configs.user_cookie.secret)
            if user:
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
                # 设置配置信息
                r['domain_name'] = configs.domain_name
                r['website_name'] = configs.website_name
                r['ICP_NO'] = configs.ICP_NO
                r['weibo'] = configs.weibo

                templating_env = app['__templating__']
                template = templating_env.get_template(template_file_name)
                resp = web.Response(body=template.render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp

    return response
