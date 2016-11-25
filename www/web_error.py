#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Burnell Liu'


def data_error(message=''):
    return {'error': u'数据有误', 'message': message}


def permission_error():
    return {'error': u'权限错误', 'message': u'你没有权限执行这个操作'}
