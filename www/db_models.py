#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import uuid
from db_orm import Model, StringField, BooleanField, FloatField, TextField, IntegerField

__author__ = 'Burnell Liu'


def generate_id():
    """
    生成随机id
    """
    return uuid.uuid1().hex


class UserAuth(Model):
    """
    用户验证表类
    create table user_auth (
    `id` varchar(50) not null,
    `email` varchar(50) not null,
    `password` varchar(50) not null,
    unique key `idx_email` (`email`),
    primary key (`id`)
    ) engine=innodb default charset=utf8;
    """
    # 定义表名称
    __table__ = 'user_auth'

    id = StringField(primary_key=True, default=generate_id, ddl='varchar(50)')
    email = StringField(primary_key=False, default=None, ddl='varchar(50)')
    password = StringField(primary_key=False, default=None, ddl='varchar(50)')


class UserInfo(Model):
    """
    用户信息表类
    create table user_info (
    `id` varchar(50) not null,
    `admin` bool not null,
    `name` varchar(50) not null,
    `image` varchar(500) not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
    ) engine=innodb default charset=utf8;
    """
    # 定义表名称
    __table__ = 'user_info'

    id = StringField(primary_key=True, default=generate_id, ddl='varchar(50)')
    admin = BooleanField(default=False)
    name = StringField(primary_key=False, default=None, ddl='varchar(50)')
    image = StringField(primary_key=False, default=None, ddl='varchar(500)')
    created_at = FloatField(primary_key=False, default=time.time)


class Blog(Model):
    """
    博客表
    create table blogs (
    `id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `name` varchar(50) not null,
    `cover_image` varchar(500) NOT NULL DEFAULT '',
    `summary` varchar(200) not null,
    `content` mediumtext not null,
    `read_times` bigint(20) unsigned zerofill NOT NULL DEFAULT '00000000000000000000',
    `type` varchar(50) not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
    ) engine=innodb default charset=utf8;
    """
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=generate_id, ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    name = StringField(ddl='varchar(50)')
    cover_image = StringField(ddl='varchar(500)')
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    read_times = IntegerField()
    type = StringField(ddl='varchar(50)')
    created_at = FloatField(default=time.time)


class Comment(Model):
    """
    评论表
    CREATE TABLE `comments` (
    `id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
    `blog_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
    `user_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
    `user_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
    `user_image` varchar(500) COLLATE utf8mb4_unicode_ci NOT NULL,
    `target_user_id` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
    `target_user_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
    `content` mediumtext COLLATE utf8mb4_unicode_ci,
    `created_at` double NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_created_at` (`created_at`) USING BTREE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
    __table__ = 'comments'

    id = StringField(primary_key=True, default=generate_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    target_user_id = StringField(ddl='varchar(50)')
    target_user_name = StringField(ddl='varchar(50)')
    content = TextField()
    created_at = FloatField(default=time.time)


class Image(Model):
    """
    图片表
    create table images (
    `id` varchar(50) not null,
    `url` varchar(500) not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
    ) engine=innodb default charset=utf8;
    """
    __table__ = 'images'
    id = StringField(primary_key=True, default=generate_id, ddl='varchar(50)')
    url = StringField(ddl='varchar(500)')
    created_at = FloatField(default=time.time)


async def unit_test_model(loop):
    from db_orm import create_pool
    await create_pool(
        loop=loop,
        host='bdm240853593.my3w.com',
        user='bdm240853593',
        password='ttlovelj911',
        db='bdm240853593_db')

    # u = User(name='Test', email='test@example.com', password='1234567890', image='about:blank')
    # await u.save()
    """
    image = Images(url='/static/img/head_1.jpg')
    await  image.save()
    image = Images(url='/static/img/head_2.jpg')
    await  image.save()
    image = Images(url='/static/img/head_3.jpg')
    await  image.save()
    image = Images(url='/static/img/head_4.jpg')
    await  image.save()
    image = Images(url='/static/img/head_5.jpg')
    await  image.save()
    image = Images(url='/static/img/head_6.jpg')
    await  image.save()
    image = Images(url='/static/img/head_7.jpg')
    await  image.save()
    image = Images(url='/static/img/head_8.jpg')
    await  image.save()
    image = Images(url='/static/img/head_9.jpg')
    await  image.save()
    image = Images(url='/static/img/head_10.jpg')
    await  image.save()
    image = Images(url='/static/img/head_12.jpg')
    await  image.save()
    image = Images(url='/static/img/head_13.jpg')
    await  image.save()
    image = Images(url='/static/img/head_14.jpg')
    await  image.save()
    image = Images(url='/static/img/head_15.jpg')
    await  image.save()
    """

if __name__ == '__main__':
    import asyncio
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(unit_test_model(event_loop))
    event_loop.run_forever()
