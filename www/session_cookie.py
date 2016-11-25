#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
import hashlib

from db_models import User

__author__ = 'Burnell Liu'


async def cookie_parse(cookie_str, cookie_secret=''):
    """
    解析COOKIE字符串
    :param cookie_str: COOKIE字符串
    :param cookie_secret: 加密COOKIE的字符串
    :return: 成功返回user对象, 失败返回None
    """
    if not cookie_str:
        return None
    try:
        str_list = cookie_str.split('-')
        if len(str_list) != 3:
            return None
        uid, expires, sha1 = str_list
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None

        s = '%s-%s-%s-%s' % (uid, user['password'], expires, cookie_secret)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('parse cookie fail: invalid sha1')
            return None
        user['password'] = '******'
        return user

    except Exception as e:
        logging.exception(e)
        return None


def cookie_generate(user, max_age, cookie_secret=''):
    """
    根据用户信息生成COOKIE
    :param user: 用户
    :param max_age: COOKIE有效时间
    :param cookie_secret: 加密COOKIE的字符串
    :return: COOKIE字符串
    """
    # 过期时间
    expires = str(int(time.time() + max_age))
    mix_str = '%s-%s-%s-%s' % (user['id'], user['password'], expires, cookie_secret)
    items = [user['id'], expires, hashlib.sha1(mix_str.encode('utf-8')).hexdigest()]
    return '-'.join(items)