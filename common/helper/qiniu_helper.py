import hashlib
import os
import re
import requests
from qiniu import Auth, BucketManager, CdnManager, put_file, build_batch_delete
from qiniu import put_data
from common.libs.aio import run_on_executor
from config.apps.third import QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_BUCKET_NAME, QINIU_CDN_DOMAIN


@run_on_executor()
def fetch(url, key=None, path='', bucket_name=QINIU_BUCKET_NAME):
    return sync_fetch(url, key=key, path=path, bucket_name=bucket_name)


def sync_fetch(url, key=None, path='', bucket_name=QINIU_BUCKET_NAME):
    """
    抓取远程文件上传到七牛服务器
    :param url: 远程文件地址
    :param key: 文件名
    :param path: 上传到的目录
    :param bucket_name: 七牛空间名
    :return:
    """
    if re.match(r'//.+', url):
        url = 'http:' + url

    # 构建鉴权对象
    q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
    # 初始化BucketManager
    bucket = BucketManager(q)
    if key is None:
        m_extension = re.search(r'\/.*(\.[^\.\?]+)(\??.*)$', url)
        if m_extension:
            extension = m_extension.group(1)
        else:
            extension = ""
        key = hashlib.md5(url.encode()).hexdigest()[:10] + extension  # 生成文件名
    ret, info = bucket.fetch(url, bucket_name, os.path.join(path, key))
    return ret


@run_on_executor()
def upload(data, key=None, path=None, bucket_name=QINIU_BUCKET_NAME):
    """
    上传文件
    :param data: 上传的文件
    :param key: 上传后的名字
    :param path: 上传到的地址
    :param bucket_name: 七牛空间名
    :return:
    """
    try:
        # 构建鉴权对象
        q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
        # 生成上传token
        token = q.upload_token(bucket_name)
        if key:
            upload_path = key
        elif path:
            upload_path = path + hashlib.md5(data).hexdigest()
        else:
            return None
        ret, info = put_data(up_token=token, key=upload_path, data=data)
        _key = ret['key']
    except:
        _key = ''
    return _key


def upload_img(data, key=None, path=None, bucket_name=QINIU_BUCKET_NAME):
    """
    上传文件
    :param data: 上传的文件
    :param key: 上传后的名字
    :param path: 上传到的地址
    :param bucket_name: 七牛空间名
    :return:
    """
    try:
        # 构建鉴权对象
        q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
        # 生成上传token
        token = q.upload_token(bucket_name)
        if key:
            upload_path = key
        elif path:
            upload_path = path + hashlib.md5(data).hexdigest()
        else:
            return None
        ret, info = put_data(up_token=token, key=upload_path, data=data)
        _key = ret['key']
    except:
        _key = ''
    return _key


@run_on_executor()
def upload_image(key=None, localfile=None, bucket_name=QINIU_BUCKET_NAME):
    """
    上传图片到七牛服务器，并返回图片宽高及mime type
    :param data: 要上传的本地文件
    :param key: 上传后的文件名
    :param path: 上传地址
    :param bucket_name:  上传的空间名
    :return:
    """
    try:
        # 构建鉴权对象
        q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)

        # 生成上传token
        token = q.upload_token(bucket_name,key)

        # 生成上传文件名
        if key:
            upload_path = key
        elif localfile:
            upload_path = hashlib.md5(localfile).hexdigest()
        else:
            return None

        ret, info = put_file(token, upload_path, localfile, version='v2')
        print("???????",ret,info)
        return ret
    except:
        print("出错了")
        pass


@run_on_executor()
def download(key, path='pic', prefix='', postfix=''):  #
    """
    :param key: 文件名
    :param path: 下载地址
    :param prefix: 前缀 prefix:'basketball'
    :param postfix: 文件规格 postfix:'?imageView2/0/w/300'
    :return:
    """
    if prefix:
        key = f'{prefix}/{key}'  # # basketball/teamflag_s/e6951e359da2218e05122aed5851199d.gif
        file_name = key.split('/')[2]
        dir_name = f'{key.split("/")[0]}_{key.split("/")[1]}'
    else:
        file_name = key.split('/')[1]
        dir_name = key.split('/')[0]
    l_pth = os.path.dirname(f'{path}/{dir_name}/')
    if not os.path.exists(l_pth):
        os.makedirs(l_pth)

    # 构建鉴权对象
    q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
    if postfix:
        base_url = f'{QINIU_CDN_DOMAIN}{key}{postfix}'
    else:
        base_url = f'{QINIU_CDN_DOMAIN}{key}'
    private_url = q.private_download_url(base_url, expires=7200)
    r = requests.get(private_url)
    if r.status_code == 200:
        with open(f'{l_pth}/{file_name}', 'wb') as f:
            f.write(r.content)


@run_on_executor()
def update_file(key, prefix='', postfix='', local_pth='', bucket_name=QINIU_BUCKET_NAME):
    """
    更新文件
    :param key: 文件名
    :param prefix: 前缀目录 prefix:'basketball'
    :param postfix: 图片参数 postfix:'?imageView2/...'
    :param local_pth: 新文件名
    :param bucket_name: 空间名
    :return:
    """

    # 初始化Auth状态
    q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
    # 生成上传token
    token = q.upload_token(bucket_name)
    # 初始化BucketManager
    bucket = BucketManager(q)
    _key = ''

    # 更新文件
    if not key:
        return None
    try:
        #前缀
        if prefix:
            key = f'{prefix}/{key}'
        if postfix:
            base_url = f'{QINIU_CDN_DOMAIN}{key}{postfix}'
        else:
            base_url = f'{QINIU_CDN_DOMAIN}{key}'
        private_url = q.private_download_url(base_url, expires=7200)
        r = requests.get(private_url)
        data = r.content
        # 删除旧文件
        ret, info = bucket.delete(bucket_name, key)
        # 上传文件
        if local_pth:
            ret, info = put_file(up_token=token, key=key, file_path=local_pth)
            _key = ret['key']
        else:
            ret, info = put_data(up_token=token, key=key, data=data)
            _key = ret['key']
    except Exception as e:
        raise e
    return _key


@run_on_executor()
def refresh(paths=None):
    if not paths:
        return None

    try:
        refresh_dirs = list()
        q = Auth(access_key=QINIU_ACCESS_KEY, secret_key=QINIU_SECRET_KEY)
        cdn_manager = CdnManager(q)
        # 需要刷新的目录链接
        for path in paths:
            refresh_dirs.append(f'{QINIU_CDN_DOMAIN}{path}')

        # 刷新链接
        refresh_result = cdn_manager.refresh_dirs(refresh_dirs)
    except Exception as e:
        raise e

    return refresh_result


@run_on_executor()
def refresh_file(key, prefix=''):
    if not key:
        return None
    if prefix:
        key = f'{prefix}/{key}'

    q = Auth(access_key=QINIU_ACCESS_KEY, secret_key=QINIU_SECRET_KEY)
    cdn_manager = CdnManager(q)
    # 需要刷新的文件链接
    urls = [
        f'{QINIU_CDN_DOMAIN}{key}'
    ]
    # 刷新链接
    return cdn_manager.refresh_urls(urls)


@run_on_executor()
def get_upload_token(img_dir, rename=True, size=100):
    """
    获取上传token
    :param img_dir: 保存的文件夹路径
    :param rename: 是否重命名
    :param size: 限制文件大小M
    :return:
    """

    # https://developer.qiniu.com/kodo/1235/vars#xvar

    img_dir = re.sub(r'^(.*)/$', '\g<1>', img_dir)
    q = Auth(access_key=QINIU_ACCESS_KEY, secret_key=QINIU_SECRET_KEY)
    if rename:
        save_key = img_dir + '/${year}/${mon}/${day}/$(etag)$(ext)'
    else:
        save_key = img_dir + '/${year}/${mon}/${day}/${fname}'
    policy = {
        'scope'     : '<bucket>:<key>',
        'saveKey'   : save_key,
        'returnBody': '{"key": $(key), "hash": $(etag), "width": $(imageInfo.width), "height": $(imageInfo.height), '
                      '"mime_type":$(mimeType), "fsize": $(fsize), "fname": $(fname), '
                      '"exif": $(exif), "ext": $(ext), "fprefix": $(fprefix)}',
        'mimeLimit' : 'video/quicktime;video/*;audio/mpeg;image/*;application/octet-stream;application/zip;application/vnd.android.package-archive;application/json',
        'fsizeLimit': 1024 * 1024 * size
    }
    token = q.upload_token(QINIU_BUCKET_NAME, policy=policy, expires=60)
    return token


@run_on_executor()
def delete(key, prefix='', bucket_name=QINIU_BUCKET_NAME):
    """
    删除源图片
    :param key: 文件名
    :param prefix: 文件目录
    :param bucket_name:
    :return:
    """
    # 初始化Auth状态
    q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
    # 初始化BucketManager
    bucket = BucketManager(q)
    try:
        if prefix:
            key = f'{prefix}/{key}'

        # 删除旧文件
        ret, info = bucket.delete(bucket_name, key)
    except Exception as e:
        raise e
    return ret


@run_on_executor()
def batch_delete(keys, bucket_name=QINIU_BUCKET_NAME):
    """
    批量删除文件
    """
    # 初始化Auth状态
    q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
    # 初始化BucketManager
    bucket = BucketManager(q)
    ops = build_batch_delete(bucket_name, keys)
    ret, info = bucket.batch(ops)
    return ret, info


@run_on_executor()
def list_files(prefix, limit, marker=None, delimiter=None, bucket_name=QINIU_BUCKET_NAME):
    """
    获取指定前缀文件列表
    """
    # 初始化Auth状态
    q = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
    # 初始化BucketManager
    bucket = BucketManager(q)
    try:
        ret, eof, info = bucket.list(bucket_name, prefix, marker, limit, delimiter)
    except Exception as e:
        raise e
    return ret


if __name__ == '__main__':
    import asyncio
    import os



    # 刷新图片
    for f in ['card28.png?imageslim', 'card58.png?imageslim', 'card98.png?imageslim']:
        r = asyncio.run(refresh_file(f'coupon/{f}'))
        print(r)

    # 上传图片
    # for f in os.listdir('/opt/app/new/ttmapi/build/tmp/'):
    #     with open(f'/opt/app/new/ttmapi/build/tmp/{f}', 'rb') as file:
    #         content = file.read()
    #         # r = asyncio.run(upload(content, key=f'images/{f}'))
    #         # r = asyncio.run(upload(content, key=f'user/pendant/{f}'))
    #         r = asyncio.run(upload(content, key=f'coupon/{f}'))
    #         # r = asyncio.run(download('user/avatar/banned_v2.png'))
    #         print(r)
    # print(asyncio.run(list_files('image/2022/02/11', 2)))
