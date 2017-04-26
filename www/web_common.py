#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
from urllib import parse


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


class QueryStringParser(object):
    """
    查询字符串解析类
    """
    def __init__(self, qs):
        """
        构造函数
        :param qs: 查询字符串
        """
        self.__kw = dict()
        for k, v in parse.parse_qs(qs, True).items():
            self.__kw[k] = v[0]

    def has_attr(self, key):
        """
        判断是否有某个属性
        :param key: 属性名称
        :return: 属性值
        """
        return key in self.__kw

    def __getattr__(self, key):
        """
        属性获取
        :param key: 属性名称
        :return: 属性值(字符串)，如果不存在该属性则返回None
        """
        if key in self.__kw:
            return self.__kw[key]
        else:
            return None


class RequestData(object):
    """
    请求数据解析类
    """
    def __init__(self, request):
        """
        构造函数
        :param request: 请求对象
        """
        self.__request = request
        self.__kw = {}

    async def json_load(self):
        """
        加载JSON数据
        :return: 成功返回True, 失败返回False
        """
        ct = self.__request.content_type.lower()
        if not ct.startswith('application/json'):
            return False

        params = await self.__request.json()
        if not isinstance(params, dict):
            return False

        self.__kw = params
        return True

    def __getattr__(self, key):
        """
        属性获取
        :param key: 属性名称
        :return: 属性值(字符串)，如果不存在该属性则返回None
        """
        if key in self.__kw:
            return self.__kw[key]
        else:
            return None


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

