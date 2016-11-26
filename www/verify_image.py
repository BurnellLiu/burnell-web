#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import time
import base64
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter


def rand_char():
    """
    随机产生验证码的字符
    :return: 字母
    """
    char_list = 'ABCDEFGHJKMNPQRSTUVWXY3456789'
    index = random.randint(0, len(char_list)-1)
    return char_list[index]


# 随机颜色1:
def rand_background_color():
    """
    随机产生验证码背景使用的颜色
    :return: 颜色(r, g, b)
    :return:
    """
    r = random.randint(64, 255)
    g = random.randint(64, 255)
    b = random.randint(64, 255)
    return r, g, b


# 随机颜色2:
def rand_text_color():
    """
    随机产生验证码文本使用的颜色
    :return: 颜色(r, g, b)
    """
    r = random.randint(32, 127)
    g = random.randint(32, 127)
    b = random.randint(32, 127)
    return r, g, b


def generate_verify_image():
    """
    生成验证码图片
    :return: （图片字符，图片base64编码数据）
    """
    width = 60 * 4
    height = 60
    image = Image.new('RGB', (width, height), (255, 255, 255))
    # 创建Font对象:
    font = ImageFont.truetype('C:/Windows/Fonts/Arial.ttf', 36)
    # 创建Draw对象:
    draw = ImageDraw.Draw(image)
    # 填充每个像素:
    for x in range(width):
        for y in range(height):
            draw.point((x, y), fill=rand_background_color())

    # 输出文字:
    rand_str = rand_char()
    rand_str += rand_char()
    rand_str += rand_char()
    rand_str += rand_char()
    for t in range(4):
        draw.text((60 * t + 10, 10), rand_str[t], font=font, fill=rand_text_color())

    # 模糊:
    image = image.filter(ImageFilter.BLUR)

    file_name = str(time.time())
    file_name += '.jpg'
    image.save(file_name, 'jpeg')

    f = open(file_name, 'rb')
    str_image = b'data:image/jpeg;base64,'
    str_image += base64.b64encode(f.read())
    f.close()
    os.remove(file_name)

    return rand_str, bytes.decode(str_image)


