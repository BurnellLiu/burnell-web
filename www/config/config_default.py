#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
开发环境默认配置
在config_override.py文件中重写配置项即可覆盖配置信息
"""

__author__ = 'Burnell Liu'

configs = {
    # 数据库配置信息
    'db': {
        'host': '1.1.1.1',
        'port': 3306,
        'user': 'user',
        'password': 'pwd',
        'database': 'db'
    },

    # 用户COOKIE配置信息
    'user_cookie': {
        # 加密字段
        'secret': 'TEST',
        # COOKIE名
        'name': 'USER_SESSION'
    },

    # 验证码图片COOKIE配置信息
    'verify_image_cookie': {
        # 加密字段
        'secret': 'happy',
        # COOKIE名
        'name': 'VERIFY_IMAGE_SESSION'
    },

    # GitHub配置信息
    'github': {
        # GitHub申请的客户端ID
        'client_id': 'xxxxxx',
        # GitHub申请的客户端密钥
        'client_secret': 'xxxxxx',
        # 重定向URI
        'redirect_uri': 'xxxxxx'
    },

    # 字体路径，linux下需要填写为'/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
    # 生成验证码需要用到字体
    'font_path': 'C:/Windows/Fonts/Arial.ttf',

    # 域名信息
    'domain_name': 'http://127.0.0.1:9000',

    # 网站名称
    'website_name': 'XXX的个人网站',

    # ICP备案号
    'ICP_NO': 'XICP备XXXXXXXX号'
}