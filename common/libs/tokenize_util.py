import ujson
import base64
import urllib.parse
from base64 import b64decode
from functools import lru_cache
from Crypto.Cipher import AES, DES3
from Crypto.Hash import HMAC
from Crypto.Random import get_random_bytes


def encrypt_app_token(data):
    """
    使用DES3-CBC模式加密App token
    data = {'uid': uid, 'time': 0}
    将 [版本] + [偏移量] + [密文] 拼接后的字节做base64编码
    :param data:
    :return:
    """
    key = bytes.fromhex('4b0ebc8c6eb0a7a93d75d4082946385f')
    iv = get_random_bytes(8)
    cipher = DES3.new(key, DES3.MODE_CBC, iv)

    plaintext = ujson.dumps(data)[::-1]
    plaintext = base64.b64encode(plaintext.encode()).decode()
    size = DES3.block_size
    count = len(plaintext)
    add = size - (count % size)
    plaintext = plaintext + (chr(add) * add)
    ct = cipher.encrypt(plaintext.encode())
    return base64.b64encode(b'\x02' + iv + ct).decode()


@lru_cache(maxsize=1024 * 1024)
def decrypt_app_token(token):
    """
    token解密
    采用lru_cache缓存1K数据
    采用AES-GCM-128算法，加密KEY为7c6e0b2c4ab564fe4789036afb0c34f5，
    把【Token版本】+【12位向量】+【TAG】+【密文】拼接得到Token
    :param token:
    :return:
    """
    try:
        key = bytes.fromhex('4b0ebc8c6eb0a7a93d75d4082946385f')
        decoded_token = b64decode(token)

        v = decoded_token[0]  # Token算法版本
        iv = decoded_token[1:9]  # 8位随机字节向量
        ct = decoded_token[9:]  # 密文
        cipher = DES3.new(key, DES3.MODE_CBC, iv=iv)

        data = cipher.decrypt(ct)
        data = data.decode('utf-8')
        data = data[0: -ord(data[-1])]
        plain = ujson.loads(base64.b64decode(data).decode()[::-1])
        return {
            'uid' : plain['uid'],
            'time': plain['time'],
            'v'   : v
        }
    except Exception as e:
        return None


def encrypt_mobile_token(data):
    """
    使用DES3-CBC模式加密App token
    data = {'uid': uid, 'time': 0}
    将 [版本] + [偏移量] + [密文] 拼接后的字节做base64编码
    :param data:
    :return:
    """
    key = bytes.fromhex('8546516079a7ed845cdbe27dd094a3a4')
    iv = get_random_bytes(8)
    cipher = DES3.new(key, DES3.MODE_CBC, iv)

    plaintext = ujson.dumps(data)[::-1]
    plaintext = base64.b64encode(plaintext.encode()).decode()
    size = DES3.block_size
    count = len(plaintext)
    add = size - (count % size)
    plaintext = plaintext + (chr(add) * add)
    ct = cipher.encrypt(plaintext.encode())
    return base64.b64encode(b'\x02' + iv + ct).decode()


@lru_cache(maxsize=1024 * 1024)
def decrypt_mobile_token(token):
    """
    token解密
    采用lru_cache缓存1K数据
    采用AES-GCM-128算法，加密KEY为7c6e0b2c4ab564fe4789036afb0c34f5，
    把【Token版本】+【12位向量】+【TAG】+【密文】拼接得到Token
    :param token:
    :return:
    """
    try:
        key = bytes.fromhex('8546516079a7ed845cdbe27dd094a3a4')
        decoded_token = b64decode(token)

        v = decoded_token[0]  # Token算法版本
        iv = decoded_token[1:9]  # 8位随机字节向量
        ct = decoded_token[9:]  # 密文
        cipher = DES3.new(key, DES3.MODE_CBC, iv=iv)

        data = cipher.decrypt(ct)
        data = data.decode('utf-8')
        data = data[0: -ord(data[-1])]
        plain = ujson.loads(base64.b64decode(data).decode()[::-1])
        return {
            'uid' : plain['uid'],
            'time': plain['time'],
            'v'   : v
        }
    except Exception as e:
        return None


# 加密web端token
def encrypt_web_token(data):
    key = bytes.fromhex('6a28e3b4d8d899cf70b74075ac63fbc8')
    size = DES3.block_size
    iv = get_random_bytes(size)
    cipher = DES3.new(key, DES3.MODE_CBC, iv)

    plaintext = ujson.dumps(data)[::-1]
    plaintext = base64.b64encode(plaintext.encode()).decode()
    count = len(plaintext)
    add = size - (count % size)
    plaintext = plaintext + (chr(add) * add)
    ct = cipher.encrypt(plaintext.encode())
    h = HMAC.new(key)
    hmac = h.update(ct).digest()
    token = base64.b64encode(b'\x02' + iv + hmac + ct).decode()
    return urllib.parse.quote_plus(token)


# 解密web端token
@lru_cache(maxsize=1000000)
def decrypt_web_token(token):
    print(token)
    try:
        key = bytes.fromhex('6a28e3b4d8d899cf70b74075ac63fbc8')
        token = urllib.parse.unquote_plus(token)
        decoded_token = b64decode(token)

        v = decoded_token[0]  # Token算法版本
        iv = decoded_token[1:9]  # 8位随机字节向量
        hmac = decoded_token[9:25]  # 8位随机字节向量
        ct = decoded_token[25:]  # 密文
        h = HMAC.new(key)
        h.update(ct)
        h.verify(hmac)
        cipher = DES3.new(key, DES3.MODE_CBC, iv=iv)
        data = cipher.decrypt(ct)
        data = data.decode("utf-8")
        data = data[0: -ord(data[-1])]
        plain = ujson.loads(base64.b64decode(data).decode()[::-1])
        return {
            'uid' : plain['uid'],
            'time': plain['time'],
            'v'   : v
        }
    except Exception as e:
        return None


# 加密管理后台token
def encrypt_admin_token(data):
    # 采用AES-GCM-128算法，ce6f3dc422e63bf076a5c680f64df704，
    plaintext = ujson.dumps(data)
    key = bytes.fromhex('ce6f3dc422e63bf076a5c680f64df704')
    nonce = iv = get_random_bytes(12)  # 12位tag
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce, mac_len=16)
    ct, tag = cipher.encrypt_and_digest(plaintext.encode())
    bins = iv + tag + ct
    token = base64.b64encode(bins).decode()
    token = urllib.parse.quote_plus(token)
    return token


# 解密管理后台token
@lru_cache(maxsize=1000000)
def decrypt_admin_token(token):
    try:
        token = urllib.parse.unquote_plus(token)
        key = bytes.fromhex('ce6f3dc422e63bf076a5c680f64df704')
        bins = base64.b64decode(token)
        iv = bins[:12]  # 12位向量
        tag = bins[12:28]  # 签名所得tag
        ct = bins[28:]  # 密文
        cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
        plaintext = cipher.decrypt_and_verify(ct, tag)
        data = ujson.loads(plaintext)
        return data
    except Exception:
        return None


if __name__ == '__main__':

    # 'AjV7c4dAy0KZeFh1p7Z%2BKZEVvUsxnO8iqNDvRU8GHeJB7ZuooC2Ruk3deg626dzw3Jhhoe0Z74CQ%2FYFxaWrH0mK8De110IA5vA%3D%3D'
    # 'AoiibfTsTmc4xBKZFlieKmhfWUY94Do147JX0qcy7Q%252F7l%252Fy9xtJZjFp3CR2xL5dNjEfTnYBaLRtJ7wCoHR00ZrOf2Avc2ceoNg%253D%253D'
    # 'AjV7c4dAy0KZeFh1p7Z%2BKZEVvUsxnO8iqNDvRU8GHeJB7ZuooC2Ruk3deg626dzw3Jhhoe0Z74CQ%2FYFxaWrH0mK8De110IA5vA%3D%3D'
    'AgWQfG8tBk3A3AhquTtlmboZMXBfobwKsbzBVpOMZq8LFprjGA39KMPV55THs8NS6sJd3CDbH1tHXz7hnUsoZxds32E51EM0JA%253D%253D'
    'AgWQfG8tBk3A3AhquTtlmboZMXBfobwKsbzBVpOMZq8LFprjGA39KMPV55THs8NS6sJd3CDbH1tHXz7hnUsoZxds32E51EM0JA%3D%3D'

    r = decrypt_web_token('AgWQfG8tBk3A3AhquTtlmboZMXBfobwKsbzBVpOMZq8LFprjGA39KMPV55THs8NS6sJd3CDbH1tHXz7hnUsoZxds32E51EM0JA%3D%3D')
    print(r)
    # r = decrypt_v1('AS+Gj0W\\/sAiyXkiRHd9jINNDQz11uq0w0TKSz1Iu0P7yij9uw70CbFqYwLvtt7o+3kk\\/T1Um+9fuuDcTD\\/8=')
    # print(r)
    # t = encrypt_app_token({'uid': 3995418, 'time': 1635494783, 'v': 2})
    # print(t)
    # d = decrypt_v1(t)
    # print(d)
    # d = decrypt_v2(t)
    # print(d)
    # t = encrypt_web_token({'uid': 3535476, 'time': 1606449909})
    # print(t)
    # d = decrypt_web_token('Alkw73BgSaxWksAM9TFqcY4eylDf0HVIdpqz7lr%2BtVkTvwC3g0Ii0E5iZTJoJ0wbb0GSB3uwylm477EcVzbVuT4%3D')
    # print(d)
