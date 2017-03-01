#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开发环境默认配置
"""

__author__ = 'Burnell Liu'

configs = {
    'db': {
        'host': '1.1.1.1',
        'port': 3306,
        'user': 'user',
        'password': 'pwd',
        'database': 'db'
    },
    'user_cookie': {
        'secret': 'TEST',
        'name': 'USER_SESSION'
    },
    'verify_image_cookie': {
        'secret': 'happy',
        'name': 'VERIFY_IMAGE_SESSION'
    },
    'font_path': 'C:/Windows/Fonts/Arial.ttf',
    'domain_name': 'http://127.0.0.1:9000'
}