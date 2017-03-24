#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
from aiohttp import web

import markdown2

from config import configs
from web_core import get
from web_common import *
from db_models import Comment, Blog
from web_error import data_error


__author__ = 'Burnell Liu'


@get('/')
async def index(request):
    """
    WEB APP首页路由函数
    :param request: 请求对象
    :return: 首页面
    """

    # 以创建时间降序的方式查找指定的博客
    blogs = await Blog.find_all(order_by='created_at desc', limit=(0, 4))
    hot_blogs = await Blog.find_all(order_by='read_times desc', limit=(0, 10))
    new_blog = None
    if len(blogs) > 0:
        new_blog = blogs[0]
    return {
        '__template__': 'index.html',
        'new_blog': new_blog,
        'blogs': blogs[1:],
        'hot_blogs': hot_blogs
    }


@get('/blogs')
async def blog_all(request):
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
        'blogs': blogs,
        'type': 'blogs'
    }


@get('/essay')
async def blog_essay(request):
    """
    随笔博客列表路由函数
    :param request: 请求对象
    :return: 博客列表页面
    """
    page_index = 1
    str_dict = parse_query_string(request.query_string)
    if 'page' in str_dict:
        page_index = int(str_dict['page'])

    num = await Blog.find_number('count(id)', 'type=?', [u'随笔'])
    page = Pagination(num, page_index, 5)

    if num == 0:
        blogs = []
        hot_blogs = []
    else:
        # 以创建时间降序的方式查找指定的博客
        blogs = await Blog.find_all('type=?', [u'随笔'], order_by='created_at desc', limit=(page.offset, page.limit))
        hot_blogs = await Blog.find_all('type=?', [u'随笔'], order_by='read_times desc', limit=(0, 10))

    return {
        '__template__': 'blog_list.html',
        'page': page,
        'blogs': blogs,
        'hot_blogs': hot_blogs,
        'type': 'essay'
    }


@get('/windows')
async def blog_windows(request):
    """
    Windows博客列表路由函数
    :param request: 请求对象
    :return: 博客列表页面
    """
    page_index = 1
    str_dict = parse_query_string(request.query_string)
    if 'page' in str_dict:
        page_index = int(str_dict['page'])

    num = await Blog.find_number('count(id)', 'type=?', [u'Windows开发'])
    page = Pagination(num, page_index, 5)

    if num == 0:
        blogs = []
        hot_blogs= []
    else:
        # 以创建时间降序的方式查找指定的博客
        blogs = await Blog.find_all('type=?', [u'Windows开发'], order_by='created_at desc', limit=(page.offset, page.limit))
        hot_blogs = await Blog.find_all('type=?', [u'Windows开发'], order_by='read_times desc', limit=(0, 10))

    return {
        '__template__': 'blog_list.html',
        'page': page,
        'blogs': blogs,
        'hot_blogs': hot_blogs,
        'type': 'windows'
    }


@get('/ml')
async def blog_ml(request):
    """
    机器学习博客列表路由函数
    :param request: 请求对象
    :return: 博客列表页面
    """
    page_index = 1
    str_dict = parse_query_string(request.query_string)
    if 'page' in str_dict:
        page_index = int(str_dict['page'])

    num = await Blog.find_number('count(id)', 'type=?', [u'机器学习'])
    page = Pagination(num, page_index, 5)

    if num == 0:
        blogs = []
        hot_blogs = []
    else:
        # 以创建时间降序的方式查找指定的博客
        blogs = await Blog.find_all('type=?', [u'机器学习'], order_by='created_at desc', limit=(page.offset, page.limit))
        hot_blogs = await Blog.find_all('type=?', [u'机器学习'], order_by='read_times desc', limit=(0, 10))

    return {
        '__template__': 'blog_list.html',
        'page': page,
        'blogs': blogs,
        'hot_blogs': hot_blogs,
        'type': 'ml'
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
    comments = await Comment.find_all('blog_id=?', [blog_id], order_by='created_at asc')
    for c in comments:
        c.html_content = text2html(c.content)
    blog.html_content = markdown2.markdown(blog.content, extras=["fenced-code-blocks"])
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
    cookie_name = configs.user_cookie.name
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
