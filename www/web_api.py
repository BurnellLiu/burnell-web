#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json
import base64
import random
import os
import time
import logging

from aiohttp import web, ClientSession

from config import configs
from web_core import get, post
from web_common import *
from db_models import UserAuth, UserInfo, Comment, Blog, Image, generate_id
from web_error import permission_error, data_error
from session_cookie import user_cookie_generate, verify_image_cookie_generate
from verify_image import generate_verify_image


__author__ = 'Burnell Liu'


@post('/api/weibo/login')
async def api_weibo_login(request):
    """
    微博登录API函数
    :param request:
    :return:
    """
    ct = request.content_type.lower()
    if ct.startswith('application/json'):
        params = await request.json()
        if not isinstance(params, dict):
            return data_error()
    else:
        return data_error()

    # 取出用户id和访问令牌
    uid = None
    if 'uid' in params:
        uid = params['uid']
    if not uid:
        return data_error()
    access_token = None
    if 'access_token' in params:
        access_token = params['access_token']
    if not access_token or not access_token.strip():
        return data_error()

    # 获取用户数据
    url = 'https://api.weibo.com/2/users/show.json?access_token='
    url += access_token
    url += '&uid='
    url += str(uid)
    async with ClientSession() as session:
        async with session.get(url) as response:
            user_data = await response.json()
            logging.info(user_data)
            if not isinstance(user_data, dict):
                return data_error()

    user_name = None
    if 'screen_name' in user_data:
        user_name = user_data['screen_name']
    if not user_name:
        return data_error()
    user_image = None
    if 'avatar_hd' in user_data:
        user_image = user_data['avatar_hd']
    if not user_image:
        return data_error()

    # 更新或者保存用户信息
    user = await UserInfo.find(str(uid))
    logging.info(user)
    if not user:
        user = UserInfo(id=uid, name=user_name, image=user_image)
        await user.save()
    else:
        user.name = user_name
        user.image = user_image
        await user.update()

    # 生成用户COOKIE
    cookie_name = configs.user_cookie.name
    cookie_secret = configs.user_cookie.secret
    cookie_str = user_cookie_generate(str(uid), 86400, cookie_secret)
    r = web.Response()
    r.set_cookie(cookie_name, cookie_str, max_age=86400, httponly=True)
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@post('/api/authenticate')
async def api_user_authenticate(request):
    """
    用户登录验证API函数
    :param request: 请求对象
    :return: 回响消息, 并且设置COOKIE
    """
    ct = request.content_type.lower()
    if ct.startswith('application/json'):
        params = await request.json()
        if not isinstance(params, dict):
            return data_error()
    else:
        return data_error()

    email = None
    if 'email' in params:
        email = params['email']
    password = None
    if 'password' in params:
        password = params['password']

    if not email:
        return data_error(u'非法邮箱账号')
    if not password:
        return data_error(u'非法密码')

    users = await UserAuth.find_all(where='email=?', args=[email])
    if len(users) == 0:
        return data_error(u'账号不存在')

    user = users[0]
    sha1_password = generate_sha1_password(user['id'], password)
    if user['password'] != sha1_password:
        return data_error(u'密码有误')

    cookie_name = configs.user_cookie.name
    cookie_secret = configs.user_cookie.secret
    cookie_str = user_cookie_generate(user['id'], 86400, cookie_secret)
    r = web.Response()
    r.set_cookie(cookie_name, cookie_str, max_age=86400, httponly=True)
    user['password'] = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/api/users')
async def api_user_get(request):
    """
    WEB API: 获取用户数据API函数
    :param request: 请求对象
    :return: 用户数据字典
    """
    if not is_admin(request):
        return permission_error()

    page_index = 1
    str_dict = parse_query_string(request.query_string)
    if 'page' in str_dict:
        page_index = int(str_dict['page'])

    num = await UserInfo.find_number('count(id)')
    p = Pagination(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = await UserInfo.find_all(order_by='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, users=users)


@post('/api/users')
async def api_user_register(request):
    """
    用户注册API函数
    :param request: 请求对象
    :return: 注册成功则设置COOKIE，返回响应消息
    """
    _RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
    _RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

    ct = request.content_type.lower()
    if ct.startswith('application/json'):
        params = await request.json()
        if not isinstance(params, dict):
            return data_error()
    else:
        return data_error()

    name = None
    if 'name' in params:
        name = params['name']
    email = None
    if 'email' in params:
        email = params['email']
    password = None
    if 'password' in params:
        password = params['password']
    verify = None
    if 'verify' in params:
        verify = params['verify']

    # 检查验证码是否输入正确
    if not verify or not verify.strip():
        return data_error(u'非法验证码')
    verify_cookie_name = configs.verify_image_cookie.name
    cookie_secret = configs.verify_image_cookie.secret
    cookie_str = request.cookies.get(verify_cookie_name)
    cookie_str_input = verify_image_cookie_generate(verify.upper(), cookie_secret)
    if not cookie_str == cookie_str_input:
        return data_error(u'验证码错误')

    # 检查用户数据是否合法
    if not name or not name.strip():
        return data_error(u'非法用户名')
    if not email or not _RE_EMAIL.match(email):
        return data_error(u'非法邮箱账号')
    if not password or not _RE_SHA1.match(password):
        return data_error(u'非法密码')

    # 检查用户邮箱是否已经被注册
    users = await UserAuth.find_all(where='email=?', args=[email])
    if len(users) > 0:
        return data_error(u'邮箱已经被使用')

    # 生成用户ID, 并且混合用户ID和密码进行SHA1加密
    uid = generate_id()
    sha1_password = generate_sha1_password(uid, password)

    # 将新用户数据保存到数据库中
    user = UserAuth(id=uid, email=email, password=sha1_password)
    await user.save()

    # 生成头像图片URL
    head_img_url = configs.domain_name
    head_img_url += '/static/img/head_%s.jpg' % random.randint(1, 15)
    user_info = UserInfo(id=uid, name=name.strip(), image=head_img_url)
    await user_info.save()

    # 生成COOKIE
    cookie_str = user_cookie_generate(user['id'], 86400, configs.user_cookie.secret)
    cookie_name = configs.user_cookie.name

    # 生成响应消息
    r = web.Response()
    # 删除用于验证验证码的COOKIE
    r.set_cookie(verify_cookie_name, '-deleted-', max_age=0, httponly=True)
    r.set_cookie(cookie_name, cookie_str, max_age=86400, httponly=True)
    user['password'] = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/api/verifyimage')
async def api_verify_image_get(request):
    """
    WEB API: 获取验证码图片API函数
    :param request: 请求对象
    :return: 验证码图片
    """
    num_str, image = generate_verify_image(configs.font_path)

    # 生成验证码图像COOKIE值
    cookie_name = configs.verify_image_cookie.name
    cookie_secret = configs.verify_image_cookie.secret
    cookie_str = verify_image_cookie_generate(num_str, cookie_secret)

    json_data = json.dumps(dict(image=image), ensure_ascii=False, default=lambda o: o.__dict__)

    r = web.Response(body=json_data.encode('utf-8'))
    r.set_cookie(cookie_name, cookie_str, max_age=86400, httponly=True)
    r.content_type = 'application/json;charset=utf-8'
    return r


@get('/api/blogs')
async def api_blog_get(request):
    """
    获取指定页面的博客数据函数
    :param request: 请求对象
    :return: 博客数据
    """

    if not is_admin(request):
        return permission_error()

    page_index = 1
    str_dict = parse_query_string(request.query_string)
    if 'page' in str_dict:
        page_index = int(str_dict['page'])

    num = await Blog.find_number('count(id)')
    p = Pagination(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = await Blog.find_all(order_by='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)


@get('/api/blogs/{blog_id}')
async def api_blog_get_one(request):
    """
    获取指定ID的博客数据函数
    :param request: 请求对象
    :return: 博客数据
    """
    if not is_admin(request):
        return permission_error()

    blog_id = request.match_info['blog_id']
    blog = await Blog.find(blog_id)
    if not blog:
        return data_error(u'非法blog id')

    return blog


@post('/api/blogs')
async def api_blog_create(request):
    """
    创建博客API函数
    :param request: 请求
    :return:
    """
    if not is_admin(request):
        return permission_error()

    ct = request.content_type.lower()
    if ct.startswith('application/json'):
        params = await request.json()
        if not isinstance(params, dict):
            return data_error()
    else:
        return data_error()

    name = None
    if 'name' in params:
        name = params['name']
    summary = None
    if 'summary' in params:
        summary = params['summary']
    content = None
    if 'content' in params:
        content = params['content']
    cover_image = None
    if 'cover_image' in params:
        cover_image = params['cover_image']
    blog_type = None
    if 'type' in params:
        blog_type = params['type']
    if not name or not name.strip():
        return data_error(u'博客名称不能为空')
    if not summary or not summary.strip():
        return data_error(u'博客摘要不能为空')
    if not content or not content.strip():
        return data_error(u'博客内容不能为空')
    if not cover_image or not cover_image.strip():
        return data_error(u'封面图片不能为空')
    if not blog_type or not blog_type.strip():
        return data_error(u'博客类型不能为空')

    blog = Blog(user_id=request.__user__['id'],
                user_name=request.__user__['name'],
                user_image=request.__user__['image'],
                name=name.strip(),
                summary=summary.strip(),
                content=content.strip(),
                cover_image=cover_image.strip(),
                read_times=0,
                type=blog_type)
    await blog.save()
    return blog


@post('/api/blogs/{blog_id}')
async def api_blog_update(request):
    """
    更新博客API函数
    :param request: 请求对象
    :return:
    """
    if not is_admin(request):
        return permission_error()

    ct = request.content_type.lower()
    if ct.startswith('application/json'):
        params = await request.json()
        if not isinstance(params, dict):
            return data_error()
    else:
        return data_error()

    blog_id = request.match_info['blog_id']

    name = None
    if 'name' in params:
        name = params['name']
    summary = None
    if 'summary' in params:
        summary = params['summary']
    content = None
    if 'content' in params:
        content = params['content']
    cover_image = None
    if 'cover_image' in params:
        cover_image = params['cover_image']
    blog_type = None
    if 'type' in params:
        blog_type = params['type']

    if not name or not name.strip():
        return data_error(u'博客名称不能为空')
    if not summary or not summary.strip():
        return data_error(u'博客摘要不能为空')
    if not content or not content.strip():
        return data_error(u'博客内容不能为空')
    if not cover_image or not cover_image.strip():
        return data_error(u'封面图片不能为空')
    if not blog_type or not blog_type.strip():
        return data_error(u'博客类型不能为空')

    blog = await Blog.find(blog_id)
    if not blog:
        return data_error(u'非法blog id')

    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()
    blog.cover_image = cover_image.strip()
    blog.type = blog_type.strip()
    await blog.update()
    return blog


@post('/api/blogs/{blog_id}/delete')
async def api_blog_delete(request):
    """
    删除博客API函数
    :param request: 请求对象
    :return:
    """
    if not is_admin(request):
        return permission_error()

    blog_id = request.match_info['blog_id']

    # 根据博客ID找到博客详细内容
    blog = await Blog.find(blog_id)
    if not blog:
        return data_error(u'非法blog id')

    await blog.remove()

    return dict(id=blog_id)


@get('/api/images')
async def api_image_get(request):
    """
    获取图像API函数
    :param request: 请求对象
    :return: 图像数据
    """
    if not is_admin(request):
        return permission_error()

    page_index = 1
    str_dict = parse_query_string(request.query_string)
    if 'page' in str_dict:
        page_index = int(str_dict['page'])

    num = await Image.find_number('count(id)')
    p = Pagination(num, page_index, page_size=6)
    if num == 0:
        return dict(page=p, images=())
    images = await Image.find_all(order_by='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, images=images)


@post('/api/images')
async def api_image_upload(request):
    """
    上传图片API函数
    :param request: 请求对象
    :return:
    """
    if not is_admin(request):
        return permission_error()

    ct = request.content_type.lower()
    if ct.startswith('application/json'):
        params = await request.json()
        if not isinstance(params, dict):
            return data_error()
    else:
        return data_error()

    image_name = None
    if 'name' in params:
        image_name = params['name']
    image_str = None
    if 'image' in params:
        image_str = params['image']
    if not image_name or not image_name.strip():
        return data_error(u'图片名不能为空')
    if not image_str or not image_str.strip():
        return data_error(u'图片内容不能为空')

    # 取消图片的原始名，只保留后缀名
    loc = image_name.find('.')
    if loc == -1:
        return data_error(u'图片名有误')
    image_name = image_name[loc:]

    # 先在数据库中生成一条图片的记录
    image = Image(url='xx')
    await image.save()

    # 使用图片数据的创建时间做为URL
    image_url = '/static/img/'
    image_url += str(int(image.created_at * 1000))
    image_url += image_name

    image.url = (configs.domain_name + image_url)
    await image.update()

    image_str = image_str.replace('data:image/png;base64,', '')
    image_str = image_str.replace('data:image/jpeg;base64,', '')
    image_data = base64.b64decode(image_str)

    image_path = '.'
    image_path += image_url
    file = open(image_path, 'wb')
    file.write(image_data)
    file.close()
    return image


@post('/api/images/{image_id}/delete')
async def api_image_delete(request):
    """
    删除博客API函数
    :param request: 请求
    :return:
    """
    if not is_admin(request):
        return permission_error()

    image_id = request.match_info['image_id']
    image = await Image.find(image_id)
    if not image:
        return data_error(u'非法image id')

    url = image.url
    await image.remove()

    url = url.replace(configs.domain_name, '')

    filename = '.'
    filename += url
    if os.path.exists(filename):
        os.remove(filename)

    return dict(id=image_id)


@get('/api/comments')
async def api_comment_get(request):
    """
    获取评论API函数
    :param request: 请求对象
    :return: 评论数据
    """
    if not is_admin(request):
        return permission_error()

    page_index = 1
    str_dict = parse_query_string(request.query_string)
    if 'page' in str_dict:
        page_index = int(str_dict['page'])

    num = await Comment.find_number('count(id)')
    p = Pagination(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = await Comment.find_all(order_by='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comments=comments)


@post('/api/blogs/{blog_id}/comments')
async def api_comment_create(request):
    """
    创建评论API函数
    :param request: 请求
    :return: 返回响应消息
    """
    # 只有登录用户才能发表评论
    user = request.__user__
    if user is None:
        return data_error(u'请先登录')

    # 限制每10秒只能发送一条评论
    comments = await Comment.find_all(
        'user_id=? and created_at > ?',
        [user.id, time.time()-10.0])
    if len(comments) > 0:
        return data_error(u'评论过于频繁（10秒后再试）')

    # 获取评论内容
    ct = request.content_type.lower()
    if ct.startswith('application/json'):
        params = await request.json()
        if not isinstance(params, dict):
            return data_error()
    else:
        return data_error()

    # 检查评论内容
    content = None
    if 'content' in params:
        content = params['content']
    if not content or not content.strip():
        return data_error(u'评论内容不能为空')

    blog_id = request.match_info['blog_id']
    blog = await Blog.find(blog_id)
    if blog is None:
        return data_error(u'评论的博客不存在')

    # 检查评论目标人名称，如果为NULL，表示对博客直接评论
    target_user_name = None
    if 'targetName' in params:
        target_user_name = params['targetName']
    if not target_user_name or not target_user_name.strip():
        target_user_name = blog.user_name

    # 检查评论目标人id，如果为NULL，表示对博客直接评论
    target_user_id = None
    if 'targetId' in params:
        target_user_id = params['targetId']
    if not target_user_id or not target_user_id.strip():
        target_user_id = blog.user_id

    comment = Comment(blog_id=blog.id,
                      user_id=user.id,
                      user_name=user.name,
                      user_image=user.image,
                      target_user_id=target_user_id,
                      target_user_name=target_user_name,
                      content=content.strip())
    await comment.save()
    return comment


@post('/api/comments/{id}/delete')
async def api_comment_delete(request):
    """
    删除评论API函数
    :param request: 请求对象
    :return:
    """
    if not is_admin(request):
        return permission_error()

    comment_id = request.match_info['id']

    c = await Comment.find(comment_id)
    if c is None:
        return data_error(u'非法comment id')

    await c.remove()
    return dict(id=comment_id)
