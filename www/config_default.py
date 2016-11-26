#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开发环境默认配置
"""

__author__ = 'Burnell Liu'

configs = {
    'db': {
        'host': 'bdm240853593.my3w.com',
        'port': 3306,
        'user': 'bdm240853593',
        'password': 'ttlovelj911',
        'database': 'bdm240853593_db'
    },
    'user_cookie': {
        'secret': 'TEST',
        'name': 'USER_SESSION'
    },
    'verify_image_cookie':{
        'secret': 'happy',
        'name': 'VERIFY_IMAGE_SESSION'
    }
}