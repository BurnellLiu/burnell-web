#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import hashlib
import json
import logging
import base64
import random
import os
import time

from aiohttp import web
from urllib import parse

import markdown2

from config import configs
from web_core import get, post
from db_models import User, Comment, Blog, Image, generate_id
from web_error import permission_error, data_error
from session_cookie import cookie_generate

__author__ = 'Burnell Liu'


class Pagination(object):
    """
    分页类
    """

    def __init__(self, item_count, page_index=1, page_size=10):
        """
        页面类构造函数
        :param item_count: 项目总数
        :param page_index: 页索引
        :param page_size: 页面大小
        """
        self.item_count = item_count
        self.page_size = page_size

        # 页面数量
        self.page_count = item_count // page_size + (1 if item_count % page_size > 0 else 0)

        if item_count == 0:
            self.offset = 0
            self.limit = 0
            self.page_index = 1
        elif page_index > self.page_count:
            self.page_index = self.page_count
            self.offset = self.page_size * (self.page_index - 1)
            self.limit = self.page_size
        else:
            self.page_index = page_index
            self.offset = self.page_size * (page_index - 1)
            self.limit = self.page_size

        # 标志是否存在下一页
        self.has_next = self.page_index < self.page_count

        # 标志是否存在前一页
        self.has_previous = self.page_index > 1

    def __str__(self):
        return 'item_count: %s, page_count: %s, page_index: %s, page_size: %s, offset: %s, limit: %s' % (self.item_count, self.page_count, self.page_index, self.page_size, self.offset, self.limit)

    __repr__ = __str__


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'),
                filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


def is_admin(request):
    """
    检查是否是管理员用户
    :param request: 请求对象
    :return: 如果当前用户不是管理员则返回False, 否则返回true
    """
    if request.__user__ is None or not request.__user__['admin']:
        return False
    else:
        return True


def parse_query_string(qs):
    """
    解析查询字符串
    :param qs: 需要解析的查询字符串
    :return: 查询字段字典
    """
    kw = dict()
    if not qs:
        return kw

    for k, v in parse.parse_qs(qs, True).items():
        kw[k] = v[0]

    return kw


def generate_sha1_password(user_id, original_password):
    """
    根据用户id和原始密码, 生成一个经过sha1加密的密码
    :param user_id: 用户id
    :param original_password: 原始密码
    :return: 加密密码
    """
    uid_password = '%s:%s' % (user_id, original_password)
    sha1_password = hashlib.sha1(uid_password.encode('utf-8')).hexdigest()
    return sha1_password


@get('/')
async def index(request):
    """
    WEB APP首页路由函数
    :param request: 请求对象
    :return: 首页面
    """
    page_index = 1
    str_dict = parse_query_string(request.query_string)
    if 'page' in str_dict:
        page_index = int(str_dict['page'])

    num = await Blog.find_number('count(id)')
    page = Pagination(num, page_index)

    if num == 0:
        blogs = []
    else:
        # 以创建时间降序的方式查找指定的博客
        blogs = await Blog.find_all(order_by='created_at desc', limit=(page.offset, page.limit))

    return {
        '__template__': 'blog_list.html',
        'page': page,
        'blogs': blogs
    }


@get('/blogs')
async def blog_list(request):
    """
    博客列表路由函数
    :param request: 请求对象
    :return: 博客列表页面
    """
    page_index = 1
    str_dict = parse_query_string(request.query_string)
    if 'page' in str_dict:
        page_index = int(str_dict['page'])

    num = await Blog.find_number('count(id)')
    page = Pagination(num, page_index)

    if num == 0:
        blogs = []
    else:
        # 以创建时间降序的方式查找指定的博客
        blogs = await Blog.find_all(order_by='created_at desc', limit=(page.offset, page.limit))

    return {
        '__template__': 'blog_list.html',
        'page': page,
        'blogs': blogs
    }


@get('/blog/{blog_id}')
async def blog_detail(request):
    """
    博客详细页面路由函数
    :param request: 请求对象
    :return: 博客详细页面
    """

    blog_id = request.match_info['blog_id']

    # 根据博客ID找到博客详细内容
    blog = await Blog.find(blog_id)
    if not blog:
        return data_error(u'非法blog id')

    # 阅读次数增加
    blog.read_times += 1
    await blog.update()

    # 找到指定博客ID的博客的评论
    comments = await Comment.find_all('blog_id=?', [blog_id], order_by='created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content)
    return {
        '__template__': 'blog_detail.html',
        'blog': blog,
        'comments': comments
    }


@get('/register')
def user_register(request):
    """
    用户注册页面路由函数
    :param request: 请求对象
    :return: 用户注册页面
    """
    return {
        '__template__': 'user_register.html'
    }


@get('/signin')
def user_signin(request):
    """
    用户登录页面路由函数
    :param request: 请求对象
    :return: 用户登录
    """
    return {
        '__template__': 'user_signin.html'
    }


@get('/signout')
def user_signout(request):
    """
    用户登出路由函数
    :param request: 请求对象
    :return:
    """
    referer = request.headers.get('Referer')
    r = web.HTTPFound(referer or '/')
    cookie_name = configs.cookie.name
    r.set_cookie(cookie_name, '-deleted-', max_age=0, httponly=True)
    logging.info('user signed out.')
    return r


@get('/manage/users')
def manage_users(request):
    """
    用户管理页面路由函数
    :param request: 请求对象
    :return: 用户管理页面
    """
    return {
        '__template__': 'manage_users.html'
    }


@get('/manage/blogs')
def manage_blogs(request):
    """
    管理博客页面路由函数
    :param request: 请求对象
    :return: 管理博客页面
    """
    return {
        '__template__': 'manage_blogs.html',
    }


@get('/manage/images')
def manage_images(request):
    """
    管理图片页面路由函数
    :param request: 请求对象
    :return: 管理图片页面
    """
    return {
        '__template__': 'manage-images.html'
    }


@get('/manage/blogs/create')
def manage_create_blog(request):
    """
    创建博客页面路由函数
    :param request: 请求对象
    :return: 创建博客页面
    """
    return {
        '__template__': 'manage_blog_edit.html'
    }


@get('/manage/blogs/edit')
def manage_edit_blog(request):
    """
    编辑博客页面路由函数
    :param request: 请求对象
    :return: 编辑博客页面
    """
    return {
        '__template__': 'manage_blog_edit.html'
    }


@get('/manage/comments')
def manage_comments(request):
    """
    管理评论页面路由函数
    :param request: 请求对象
    :return: 评论管理页面
    """
    return {
        '__template__': 'manage_comments.html'
    }


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

    users = await User.find_all(where='email=?', args=[email])
    if len(users) == 0:
        return data_error(u'账号不存在')

    user = users[0]
    sha1_password = generate_sha1_password(user['id'], password)
    if user['password'] != sha1_password:
        return data_error(u'密码有误')

    cookie_name = configs.cookie.name
    cookie_secret = configs.cookie.secret
    cookie_str = cookie_generate(user, 86400, cookie_secret)
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

    users = await User.find_all(order_by='created_at desc')
    for u in users:
        u['password'] = '******'
    return dict(users=users)


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

    # 检查用户数据是否合法
    if not name or not name.strip():
        return data_error(u'非法用户名')
    if not email or not _RE_EMAIL.match(email):
        return data_error(u'非法邮箱账号')
    if not password or not _RE_SHA1.match(password):
        return data_error(u'非法密码')

    # 检查用户邮箱是否已经被注册
    users = await User.find_all(where='email=?', args=[email])
    if len(users) > 0:
        return data_error(u'邮箱已经被使用')

    # 生成用户ID, 并且混合用户ID和密码进行SHA1加密
    uid = generate_id()
    sha1_password = generate_sha1_password(uid, password)

    # 生成头像图片URL
    head_img_url = '/static/img/head_%s.jpg' % random.randint(1, 15)

    # 将新用户数据保存到数据库中
    user = User(id=uid, name=name.strip(), email=email, password=sha1_password, image=head_img_url)
    await user.save()

    # 生成COOKIE
    cookie_str = cookie_generate(user, 86400, configs.cookie.secret)
    cookie_name = configs.cookie.name

    # 生成响应消息
    r = web.Response()
    r.set_cookie(cookie_name, cookie_str, max_age=86400, httponly=True)
    user['password'] = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
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

    if not name or not name.strip():
        return data_error(u'博客名称不能为空')

    if not summary or not summary.strip():
        return data_error(u'博客摘要不能为空')

    if not content or not content.strip():
        return data_error(u'博客内容不能为空')

    if not cover_image or not cover_image.strip():
        return data_error(u'封面图片不能为空')

    blog = Blog(user_id=request.__user__['id'],
                user_name=request.__user__['name'],
                user_image=request.__user__['image'],
                name=name.strip(),
                summary=summary.strip(),
                content=content.strip(),
                cover_image=cover_image.strip(),
                read_times=0)
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

    name = params['name']
    summary = params['summary']
    content = params['content']
    cover_image = params['cover_image']

    if not name or not name.strip():
        return data_error(u'博客名称不能为空')
    if not summary or not summary.strip():
        return data_error(u'博客摘要不能为空')
    if not content or not content.strip():
        return data_error(u'博客内容不能为空')
    if not cover_image or not cover_image.strip():
        return data_error(u'封面图片不能为空')

    blog = await Blog.find(blog_id)
    if not blog:
        return data_error(u'非法blog id')

    blog.name = name.strip()
    blog.summary = summary.strip()
    blog.content = content.strip()
    blog.cover_image = cover_image.strip()
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

    image = Image(url='xx')
    await image.save()

    # 使用图片数据的创建时间做为URL
    image_url = '/static/img/'
    image_url += str(int(image.created_at * 1000))
    image_url += image_name

    image.url = image_url
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

    comment = Comment(blog_id=blog.id,
                      user_id=user.id,
                      user_name=user.name,
                      user_image=user.image,
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


