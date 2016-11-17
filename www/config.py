#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置文件
"""

import config_default

__author__ = 'Burnell Liu'


class AttributeDict(dict):
    """
    属性字典, 支持以x.y的方式来访问字典数据
    """
    def __init__(self, names=(), values=(), **kw):
        super(AttributeDict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Dict' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


def dict_merge(default, override):
    """
    字典融合
    :param default: 字典
    :param override: 重载字典
    :return: 融合后的字典
    """
    r = {}
    for k, v in default.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = dict_merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r


def to_attribute_dict(d):
    """
    将普通字典转换为属性字典
    :param d: 源字典
    :return: 属性字典
    """
    attribute_dict = AttributeDict()
    for k, v in d.items():
        attribute_dict[k] = to_attribute_dict(v) if isinstance(v, dict) else v
    return attribute_dict

configs = config_default.configs

try:
    import config_override
    configs = dict_merge(config_default.configs, config_override.configs)
except ImportError:
    pass

configs = to_attribute_dict(configs)