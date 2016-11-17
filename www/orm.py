#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import aiomysql

__author__ = 'Burnell Liu'


async def create_pool(loop, **kw):
    """
    创建连接池
    :param loop: 事件循环对象
    """
    logging.info('create database connection pool...')
    # 创建一个全局的连接池，每个HTTP请求都可以从连接池中直接获取数据库连接。
    # 使用连接池的好处是不必频繁地打开和关闭数据库连接，而是能复用就尽量复用。
    # 连接池由全局变量__pool存储，缺省情况下将编码设置为utf8，自动提交事务
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop
    )


async def select(sql, args, size=None):
    """
    执行SELECT语句
    :param sql: SQL语句
    :param args: SQL参数
    :param size: 获取指定数量的记录
    :return: 条目
    """
    logging.info('Sql: %s Args: %s Size:%s' % (sql, args, size))
    global __pool
    async with __pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # SQL语句的占位符是?，而MySQL的占位符是%s，所以需要替换
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        return rs


async def execute(sql, args, autocommit=True):
    """
    通用执行语句
    :param sql: SQL语句
    :param args: SQL参数
    :param autocommit: 是否自动提交
    :return: 受影响的行数
    """
    logging.info('Sql: %s Args: %s Autocommit:%s' % (sql, args, autocommit))
    async with __pool.get() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected


def create_args_string(num):
    array = []
    for n in range(num):
        array.append('?')
    return ', '.join(array)


class Field(object):
    """
    数据库表字段基类
    """
    def __init__(self, column_type, primary_key, default):
        """
        表字段构造函数
        :param column_type: 字段类型
        :param primary_key: 标记是否为主键
        :param default: 默认值
        """
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default


class StringField(Field):
    """
    字符串字段类
    """
    def __init__(self, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(ddl, primary_key, default)


class BooleanField(Field):
    """
    布尔字段类
    """
    def __init__(self, default=False):
        super().__init__('boolean', False, default)


class IntegerField(Field):
    """
    整数字段类
    """
    def __init__(self, primary_key=False, default=0):
        super().__init__('bigint', primary_key, default)


class FloatField(Field):
    """
    浮点数字段类
    """
    def __init__(self, primary_key=False, default=0.0):
        super().__init__('real', primary_key, default)


class TextField(Field):
    """
    文本字段类
    """
    def __init__(self, default=None):
        super().__init__('text', False, default)


class ModelMetaclass(type):
    """
    数据表模型元类
    """
    def __new__(mcs, name, bases, attrs):
        """
        创建类
        :param mcs: 准备创建的类对象
        :param name: 类的名字
        :param bases: 类继承的父类集合
        :param attrs: 类的属性集合(包括方法)
        """
        if name == 'Model':
            return type.__new__(mcs, name, bases, attrs)

        table_name = attrs.get('__table__', None) or name

        field_dict = dict()
        field_key_list = []
        field_primary_key = None
        for k, v in attrs.items():
            # 找出类中的所有字段属性
            if isinstance(v, Field):
                field_dict[k] = v
                if v.primary_key:
                    # 找到主键:
                    if field_primary_key:
                        raise BaseException('Duplicate primary key for field: %s' % k)
                    field_primary_key = k
                else:
                    field_key_list.append(k)

        if not field_primary_key:
            raise BaseException('Primary key not found.')

        for k in field_dict.keys():
            attrs.pop(k)

        escaped_fields = list(map(lambda f: '`%s`' % f, field_key_list))

        # 字段名和列的映射关系
        attrs['__mappings__'] = field_dict

        # 数据库表名称
        attrs['__table__'] = table_name

        # 主键属性名
        attrs['__primary_key__'] = field_primary_key

        # 除主键外的字段名
        attrs['__fields__'] = field_key_list
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (field_primary_key, ', '.join(escaped_fields), table_name)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % \
                              (table_name, ', '.join(escaped_fields),
                               field_primary_key, create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % \
                              (table_name, ', '.join(map(lambda f: '`%s`=?' % f, field_key_list)), field_primary_key)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (table_name, field_primary_key)
        return type.__new__(mcs, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    """
    数据表模型类
    """
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def get_value(self, key):
        """
        获取指定键对象的属性值, 如果不存在则返回None
        :param key: 键名称
        :return: 属性值
        """
        return getattr(self, key, None)

    def get_value_or_default(self, key):
        """
        获取指定键对应的属性值, 当没有设置该属性值时, 则使用默认值
        :param key: 键名称
        :return: 属性值
        """
        value = getattr(self, key, None)

        # 未指定则使用默认值
        if value is None:
            field = self.__mappings__[key]
            # 如果默认值为函数对象, 则调用函数生成默认值
            # 该机制在生成默认ID时很有用, 可使用函数生成不同的ID
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                setattr(self, key, value)
        return value

    @classmethod
    async def find_all(cls, where=None, args=None, **kw):
        """
        查找所有对象
        :param where: 条件限制
        :param args: 参数值
        :param kw: 关键字参数, 可以指定order_by和limit
        :return: 对象字典数组
        """
        sql = [cls.__select__]

        # 如果存在条件限制，则添加添加限制到SQL语句中
        if where:
            sql.append('where')
            sql.append(where)

        if args is None:
            args = []

        # 如果存在排序限制，则添加排序限制到SQL语句中
        order_by = kw.get('order_by', None)
        if order_by:
            sql.append('order by')
            sql.append(order_by)

        limit = kw.get('limit', None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' % str(limit))

        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    @classmethod
    async def find_number(cls, select_field, where=None, args=None):
        """
        查找对象数目
        :param select_field: 查找的字段
        :param where: 查找条件
        :param args: 查找参数
        :return: 数目
        """
        sql = ['select %s _num_ from `%s`' % (select_field, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    async def find(cls, pk):
        """
        通过主键查找对象
        :param pk: 主键
        :return: 属性对象字典
        """
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    async def save(self):
        """
        保存数据到数据库中
        """
        # 获取当前实例的属性值或默认属性值
        args = list(map(self.get_value_or_default, self.__fields__))
        args.append(self.get_value_or_default(self.__primary_key__))

        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warning('failed to insert record: affected rows: %s' % rows)

    async def update(self):
        args = list(map(self.get_value, self.__fields__))
        args.append(self.get_value(self.__primary_key__))
        rows = await execute(self.__update__, args)
        if rows != 1:
            logging.warning('failed to update by primary key: affected rows: %s' % rows)

    async def remove(self):
        args = [self.get_value(self.__primary_key__)]
        rows = await execute(self.__delete__, args)
        if rows != 1:
            logging.warning('failed to remove by primary key: affected rows: %s' % rows)


def unit_test_connection_pool():
    event_loop = asyncio.get_event_loop()
    event_loop.run_until_complete(create_pool(event_loop,
                                              host='bdm240853593.my3w.com',
                                              user='bdm240853593',
                                              password='ttlovelj911',
                                              db='bdm240853593_db'))
    event_loop.run_forever()


def unit_test_model():
    class User(Model):
        # 表名称
        # 如果不定义__table__, 则__table__默认被定义为类名
        __table__ = 'users'

        # 表字段名id, 整形, 主键, 默认值为0
        id = IntegerField(primary_key=True)

        # 表字段名name, 字符串, 默认值为None
        name = StringField()

        # 表字段名age, 整形. 默认值为0
        age = IntegerField()

    print(User.__mappings__['id'])
    print(User.__mappings__['name'])
    print('Table name: %s' % User.__table__)
    print('Primary key: %s' % User.__primary_key__)
    print('Fields: %s' % User.__fields__)
    print('Select: %s' % User.__select__)
    print('Insert: %s' % User.__insert__)
    print('Update: %s' % User.__update__)
    print('Delete: %s' % User.__delete__)

    user = User(id=123, name='Michael')
    print('Test user id: %s' % user['id'])
    print('Test user name: %s' % user['name'])
    print(user.get_value('id'))
    print(user.get_value('name'))
    print(user.get_value_or_default('age'))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unit_test_model()


