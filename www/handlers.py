#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import re
import hashlib
import json
import logging
import base64
import asyncio
import random

from aiohttp import web

import markdown2

from config import configs
from coreweb import get, post
from models import User, Comment, Blog, Image,generate_id
from apis import Page, APIError, APIValueError, APIResourceNotFoundError, APIPermissionError

__author__ = 'Burnell Liu'


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
                filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


def get_page_index(page_str):
    p = 1
    try:
        p = int(page_str)
    except ValueError as e:
        pass
    if p < 1:
        p = 1
    return p


@get('/')
async def index(*, page='1'):
    """
    WEB APP首页路由函数
    :param page: 博客页索引
    :return:
    """
    page_index = get_page_index(page)
    num = await Blog.find_number('count(id)')
    page = Page(num, page_index)
    if num == 0:
        blogs = []
    else:
        # 以创建时间降序的方式查找指定的博客
        blogs = await Blog.find_all(order_by='created_at desc', limit=(page.offset, page.limit))
    return {
        '__template__': 'index.html',
        'page': page,
        'blogs': blogs
    }


@get('/blog/{blog_id}')
async def blog(blog_id):
    """
    博客详细页面路由函数
    :param blog_id: 博客ID
    :return:
    """
    # 根据博客ID找到博客详细内容
    blog = await Blog.find(blog_id)

    # 找到指定博客ID的博客的评论
    comments = await Comment.find_all('blog_id=?', [blog_id], orderBy='created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    return {
        '__template__': 'blog_detail.html',
        'blog': blog,
        'comments': comments
    }


@get('/register')
def register():
    """
    用户注册页面路由函数
    :return:
    """
    return {
        '__template__': 'register.html'
    }


@get('/signin')
def signin():
    """
    用户登录页面路由函数
    """
    return {
        '__template__': 'signin.html'
    }


@get('/signout')
def signout(request):
    """
    用户登出路由函数
    :param request: 请求对象
    :return:
    """
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    cookie_name = configs.session.cookie_name
    r.set_cookie(cookie_name, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r


@get('/manage/users')
def manage_users(*, page='1'):
    """
    用户管理页面路由函数
    :param page:
    :return:
    """
    return {
        '__template__': 'manage_users.html',
        'page_index': get_page_index(page)
    }


@get('/manage/blogs')
def manage_blogs(*, page='1'):
    """
    管理博客页面路由函数
    :param page:
    :return:
    """
    return {
        '__template__': 'manage_blogs.html',
        'page_index': get_page_index(page)
    }


@get('/manage/images')
def manage_images(request):
    """
    管理图片页面路由函数
    :param request:
    :return:
    """
    return {
        '__template__': 'manage-images.html'
    }


@get('/manage/blogs/create')
def manage_create_blog():
    """
    创建博客页面路由函数
    :return:
    """
    return {
        '__template__': 'manage_blog_edit.html',
        'id': '',
        'action': '/api/blogs'
    }


@get('/manage/blogs/edit')
def manage_edit_blog(*, id):
    """
    编辑博客页面路由函数
    :param id: 博客ID
    :return:
    """
    return {
        '__template__': 'manage_blog_edit.html',
        'id': id,
        'action': '/api/blogs/%s' % id
    }


@get('/manage/comments')
def manage_comments(*, page='1'):
    """
    管理评论页面路由函数
    :param page: 页面索引
    :return:
    """
    return {
        '__template__': 'manage_comments.html',
        'page_index': get_page_index(page)
    }


def check_admin(request):
    """
    检查是否是管理员用户
    :param request: 请求对象
    :return: 如果当前用户不是管理员则抛出异常
    """
    if request.__user__ is None or not request.__user__['admin']:
        raise APIPermissionError()


def generate_user_cookie(user, max_age):
    """
    根据用户信息生成COOKIE
    :param user: 用户
    :param max_age: COOKIE有效时间
    :return: COOKIE字符串
    """
    # 过期时间
    expires = str(int(time.time() + max_age))
    cookie_key = configs.session.secret
    mix_str = '%s-%s-%s-%s' % (user['id'], user['password'], expires, cookie_key)
    items = [user['id'], expires, hashlib.sha1(mix_str.encode('utf-8')).hexdigest()]
    return '-'.join(items)


def generate_sha1_password(user_id, original_password):
    """
    根据用户id和原始密码, 生成一个进过sha1加密的密码
    :param user_id: 用户id
    :param original_password: 原始密码
    :return: 加密密码
    """
    uid_password = '%s:%s' % (user_id, original_password)
    sha1_password = hashlib.sha1(uid_password.encode('utf-8')).hexdigest()
    return sha1_password


@post('/api/authenticate')
async def api_user_authenticate(*, email, password):
    """
    用户登录验证API函数
    :param email: 用户邮箱
    :param password: 用户密码
    :return: 回响消息, 并且设置COOKIE
    """
    if not email:
        raise APIValueError(email, u'非法邮箱账号')
    if not password:
        raise APIValueError(password, u'非法密码')

    users = await User.find_all(where='email=?', args=[email])
    if len(users) == 0:
        # TODO: APIError第二个参数设置为'invalid email'会导致登录按钮处于旋转状态
        # TODO: 原因不明
        raise APIError('authenticate:fail', 'email', u'邮箱账号不存在')

    user = users[0]
    sha1_password = generate_sha1_password(user['id'], password)
    if user['password'] != sha1_password:
        # TODO: APIError第二个参数设置为'invalid password'会导致登录按钮处于旋转状态
        # TODO: 原因不明
        raise APIError('authenticate:fail', 'password', u'密码错误')

    cookie_name = configs.session.cookie_name
    r = web.Response()
    r.set_cookie(cookie_name, generate_user_cookie(user, 86400), max_age=86400, httponly=True)
    user['password'] = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/api/users')
async def api_get_users():
    """
    WEB API: 获取用户数据API函数
    :return: 用户数据字典
    """
    users = await User.find_all(order_by='created_at desc')
    for u in users:
        u['password'] = '******'
    return dict(users=users)


@post('/api/users')
async def api_register_user(*, email, name, password):
    """
    用户注册API函数
    :param email: 用户邮箱
    :param name: 用户名
    :param password: 密码, 传送过来的密码值为: 用户邮箱混合原始密码进行SHA1加密
    :return:
    """
    _RE_EMAIL = re.compile(r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
    _RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')

    # 检查用户数据是否合法
    if not name or not name.strip():
        raise APIValueError(name, u'用户名非法')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError(email, u'邮箱账号非法')
    if not password or not _RE_SHA1.match(password):
        raise APIValueError(password, '密码非法')

    # 检查用户邮箱是否已经被注册
    users = await User.find_all(where='email=?', args=[email])
    if len(users) > 0:
        raise APIError('register:fail', email, u'邮箱已经被使用')

    # 生成用户ID, 并且混合用户ID和密码进行SHA1加密
    uid = generate_id()
    sha1_password = generate_sha1_password(uid, password)

    # 生成头像图片URL
    head_img_url = '/static/img/head_%s.jpg' % random.randint(1, 15)

    # 将新用户数据保存到数据库中
    user = User(id=uid, name=name.strip(), email=email, password=sha1_password, image=head_img_url)
    await user.save()

    # 生成COOKIE
    cookie = generate_user_cookie(user, 86400)
    cookie_name = configs.session.cookie_name

    # 生成响应消息
    r = web.Response()
    r.set_cookie(cookie_name, cookie, max_age=86400, httponly=True)
    user['password'] = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/api/blogs')
async def api_get_blogs(*, page='1'):
    """
    获取指定页面的博客数据函数
    :param page: 页面索引
    :return:
    """
    page_index = get_page_index(page)
    num = await Blog.find_number('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, blogs=())
    blogs = await Blog.find_all(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, blogs=blogs)


@get('/api/blogs/{blog_id}')
async def api_get_blog(*, blog_id):
    """
    获取指定ID的博客数据函数
    :param blog_id: 指定的博客id
    :return: 博客数据
    """
    blog = await Blog.find(blog_id)
    return blog


@post('/api/blogs')
async def api_create_blog(request, *, name, summary, content):
    """
    创建博客API函数
    :param request: 请求
    :param name: 博客名称
    :param summary: 博客摘要
    :param content: 博客内容
    :return:
    """
    check_admin(request)
    if not name or not name.strip():
        raise APIValueError('name', u'博客名不能为空')

    if not summary or not summary.strip():
        raise APIValueError('summary', u'摘要不能为空')

    if not content or not content.strip():
        raise APIValueError('content', u'内容不能为空')

    blog = Blog(user_id=request.__user__['id'],
                user_name=request.__user__['name'],
                user_image=request.__user__['image'],
                name=name.strip(),
                summary=summary.strip(),
                content=content.strip())
    await blog.save()
    return blog


@post('/api/blogs/{blog_id}')
async def api_update_blog(blog_id, request, *, name, summary, content):
    """
    更新博客API函数
    :param blog_id: 博客ID
    :param request: 请求
    :param name: 博客名
    :param summary: 博客摘要
    :param content: 博客内容
    :return:
    """
    check_admin(request)
    blog = await Blog.find(blog_id)
    if not name or not name.strip():
        raise APIValueError('name', u'博客名不能为空')
    if not summary or not summary.strip():
        raise APIValueError('summary', u'博客摘要不能为空')
    if not content or not content.strip():
        raise APIValueError('content', u'博客内容不能为空')

    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()
    await blog.update()
    return blog


@post('/api/blogs/{blog_id}/delete')
async def api_delete_blog(request, *, blog_id):
    """
    删除博客API函数
    :param request: 请求
    :param blog_id: 博客ID
    :return:
    """
    check_admin(request)
    blog = await Blog.find(blog_id)
    await blog.remove()
    return dict(id=blog_id)


@get('/api/images')
async def api_get_images(*, page='1'):
    """
    获取图像API函数
    :param page: 页面索引
    :return:
    """
    page_index = get_page_index(page)
    num = await Image.find_number('count(id)')
    p = Page(num, page_index, page_size=6)
    if num == 0:
        return dict(page=p, images=())
    images = await Image.find_all(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, images=images)


@post('/api/images')
async def api_upload_image(request):
    params = await request.json()

    image = Image(url='xx')
    await image.save()

    image_url = '/static/img/'
    image_url += image.id
    image_url += params['name']
    image.url = image_url
    await image.update()

    image_str = params['image']
    image_str = image_str.replace('data:image/png;base64,', '')
    image_str = image_str.replace('data:image/jpeg;base64,', '')
    image_data = base64.b64decode(image_str)

    image_path = '.'
    image_path += image_url
    file = open(image_path,'wb')
    file.write(image_data)
    file.close()
    return image


@get('/api/comments')
async def api_get_comments(*, page='1'):
    """
    获取评论API函数
    :param page: 页面索引
    :return:
    """
    page_index = get_page_index(page)
    num = await Comment.find_number('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, comments=())
    comments = await Comment.find_all(orderBy='created_at desc', limit=(p.offset, p.limit))
    return dict(page=p, comments=comments)


@post('/api/blogs/{blog_id}/comments')
async def api_create_comment(blog_id, request, *, content):
    """
    创建评论API函数
    :param blog_id: 博客ID
    :param request: 请求
    :param content: 评论内容
    :return:
    """
    user = request.__user__
    if user is None:
        raise APIPermissionError(u'请先登录')

    if not content or not content.strip():
        raise APIValueError('content', u'评论内容不能为空')

    blog = await Blog.find(blog_id)
    if blog is None:
        raise APIResourceNotFoundError('Blog', u'评论的博客不存在')

    comment = Comment(blog_id=blog.id,
                      user_id=user.id,
                      user_name=user.name,
                      user_image=user.image,
                      content=content.strip())
    await comment.save()
    return comment


@post('/api/comments/{id}/delete')
async def api_delete_comment(id, request):
    """
    删除评论API函数
    :param id: 评论ID
    :param request: 请求
    :return:
    """
    check_admin(request)
    c = await Comment.find(id)
    if c is None:
        raise APIResourceNotFoundError('Comment', u'该评论不存在')
    await c.remove()
    return dict(id=id)


