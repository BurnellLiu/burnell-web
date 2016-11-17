#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import uuid
from orm import Model, StringField, BooleanField, FloatField, TextField

__author__ = 'Burnell Liu'


def generate_id():
    """
    生成随机id
    """
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(Model):
    """
    用户表类
    create table users (
    `id` varchar(50) not null,
    `email` varchar(50) not null,
    `password` varchar(50) not null,
    `admin` bool not null,
    `name` varchar(50) not null,
    `image` varchar(500) not null,
    `created_at` real not null,
    unique key `idx_email` (`email`),
    key `idx_created_at` (`created_at`),
    primary key (`id`)
    ) engine=innodb default charset=utf8;
    """
    # 定义表名称
    __table__ = 'users'

    id = StringField(primary_key=True, default=generate_id, ddl='varchar(50)')
    email = StringField(primary_key=False, default=None, ddl='varchar(50)')
    password = StringField(primary_key=False, default=None, ddl='varchar(50)')
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
    `summary` varchar(200) not null,
    `content` mediumtext not null,
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
    summary = StringField(ddl='varchar(200)')
    content = TextField()
    created_at = FloatField(default=time.time)


class Comment(Model):
    """
    评论表
    create table comments (
    `id` varchar(50) not null,
    `blog_id` varchar(50) not null,
    `user_id` varchar(50) not null,
    `user_name` varchar(50) not null,
    `user_image` varchar(500) not null,
    `content` mediumtext not null,
    `created_at` real not null,
    key `idx_created_at` (`created_at`),
    primary key (`id`)
    ) engine=innodb default charset=utf8;
    """
    __table__ = 'comments'

    id = StringField(primary_key=True, default=generate_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_image = StringField(ddl='varchar(500)')
    content = TextField()
    created_at = FloatField(default=time.time)


async def unit_test_model(loop):
    from orm import create_pool
    await create_pool(
        loop=loop,
        host='bdm240853593.my3w.com',
        user='bdm240853593',
        password='ttlovelj911',
        db='bdm240853593_db')

    u = User(name='Test', email='test@example.com', password='1234567890', image='about:blank')

    await u.save()

if __name__ == '__main__':
    import asyncio
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(unit_test_model(event_loop))
    event_loop.run_forever()
