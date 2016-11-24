#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Burnell Liu'


class Page(object):
    """
    显示页面的页面类
    """

    def __init__(self, item_count, page_index=1, page_size=10):
        """
        页面类构造函数
        :param item_count: 项目总数
        :param page_index: 页索引
        :param page_size: 页面大小

        >>> p1 = Page(100, 1)
        >>> p1.page_count
        10
        >>> p1.offset
        0
        >>> p1.limit
        10
        >>> p2 = Page(90, 9, 10)
        >>> p2.page_count
        9
        >>> p2.offset
        80
        >>> p2.limit
        10
        >>> p3 = Page(91, 10, 10)
        >>> p3.page_count
        10
        >>> p3.offset
        90
        >>> p3.limit
        10
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


def data_error(message=''):
    return {'error': u'数据有误', 'message': message}


def permission_error():
    return {'error': u'权限错误', 'message': u'你没有权限执行这个操作'}
