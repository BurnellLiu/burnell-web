#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from datetime import datetime

__author__ = 'Burnell Liu'


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

