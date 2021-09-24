import datetime
from cachetools.func import ttl_cache
from aioredis import Redis
import hashlib
import time
import socket
import struct

from sqlalchemy import func

from common.libs.aio import run_sqlalchemy


def to_int(key, default=None):
    try:
        return int(key)
    except (ValueError, TypeError):
        return default


def to_str(key, default=None):
    if key:
        return str(key)
    else:
        return default


def to_float(s, n=0, default=None):
    try:
        s = float(s)
        if n:
            s = round(s, n)
        return s
    except (ValueError, TypeError):
        return default


def now():
    return int(time.time())


def today():
    return int(time.mktime(datetime.date.today().timetuple()))


def md5(content):
    return hashlib.md5(str(content).encode("utf8")).hexdigest()


def ip2long(ipstr):
    try:
        return struct.unpack("!I", socket.inet_aton(ipstr))[0]
    except Exception as e:
        return 0


def long2ip(ip):
    try:
        return socket.inet_ntoa(struct.pack("!I", ip))
    except Exception as e:
        return ''


@run_sqlalchemy()
@ttl_cache(maxsize=1000, ttl=120)
def total_number(db_session, count_type, filter_cond=True):
    return db_session.query(func.count(count_type)).filter(filter_cond).scalar()


def get_ipaddr(request):
    return request.headers.get('X-Real-Ip') or request.ip


async def inc_count(app, name, ttl=60, amount=1, reset_ttl=True):
    """
    inc计数器
    :param app:
    :param name:
    :param ttl:
    :param amount:
    :param reset_ttl:
    :return:
    """
    redis_normal_0 = await app.leisu.get_redis('normal', db=0)
    pipe = redis_normal_0.pipeline()
    key = f's:counter:{name}'
    pipe.incrby(key, amount)
    if reset_ttl:
        pipe.expire(key, ttl)
    else:
        if not await has_count(app, name):
            pipe.expire(key, ttl)
        else:
            if await redis_normal_0.ttl(key) < 0:
                pipe.expire(key, ttl)
    ret = await pipe.execute()
    return ret[0]


async def set_count(app, name, ttl, amount):
    """
    设置计数器
    :param app:
    :param name:
    :param ttl:
    :param amount:
    :return:
    """
    redis_normal_0 = await app.leisu.get_redis('normal', db=0)
    key = f's:counter:{name}'
    await redis_normal_0.setex(key, ttl, amount)


async def reset_count(app, name):
    """
    重置计数器
    :param app:
    :param name:
    :return:
    """
    redis_normal_0 = await app.leisu.get_redis('normal', db=0)
    key = f's:counter:{name}'
    await redis_normal_0.delete(key)


async def get_count(app, name):
    key = f's:counter:{name}'
    redis_normal_0: Redis = await app.leisu.get_redis('normal', db=0)
    count = await redis_normal_0.get(key, encoding='utf8') or 0
    return int(count)


async def has_count(app, name):
    """
    是否有计数器
    :param app:
    :param name:
    :return:
    """
    key = "s:counter:%s" % name
    redis_normal_0 = await app.leisu.get_redis('normal', db=0)
    return await redis_normal_0.exists(key)


def obj2dict(obj):
    """
    对象转字典
    :param obj:
    :return:
    :rtype: dict
    """
    if isinstance(obj, dict):
        return obj

    data = {}
    for k, v in obj.__dict__.items():
        if k[0] == '_':
            continue
        data[k] = v
    return data


def dic2list(dic):
    """
    字典转数组 字典{key1:value1,key2:value2} 转换后[value1,key1,value2,key2]
    :param dic:
    :return:
    """
    lt = []
    for key, value in dic.items():
        try:
            lt.append(float(value))
            lt.append(key)
        except Exception:
            pass
    return lt


def dic2list2(dic):
    """
    字典转数组2 字典{key1:value1,key2:value2} 转换后[key1,value1,ke2,value2]
    :param dic:
    :return:
    """
    lt = []
    for key, value in dic.items():
        try:
            lt.append(key)
            lt.append(value)
        except Exception:
            pass
    return lt


def clear_cookie(response, name):
    response.cookies[name] = ''
    response.cookies[name]['path'] = '/'
    response.cookies[name]['max-age'] = 0
    response.cookies[name]['domain'] = '.leisu.com'
    response.cookies[name]['httponly'] = True
    response.cookies[name]['secure'] = True
    response.cookies[name]['samesite'] = None
    return response
