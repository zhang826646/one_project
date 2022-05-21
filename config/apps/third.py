
# 七牛云
QINIU_CDN_DOMAIN = 'https://cdn.leisu.com/'
QINIU_ACCESS_KEY = '4oPmt-gbFg0aVs6WWly_X17rI_jWx3uGcDbM1T2l'
QINIU_SECRET_KEY = 'RslOODyhed5pfjlfUH3UAuyz5wAapVT3r4FZMSgB'
QINIU_BUCKET_NAME = 'ttmimg'

class CDNDir:
    UPLOAD = 'upload/'  # 通用路径（30天过期）
    IMAGE = 'image/'  # 通用路径 图片


class CDNUrl:
    UPLOAD = QINIU_CDN_DOMAIN + CDNDir.UPLOAD
    IMAGE = QINIU_CDN_DOMAIN + CDNDir.IMAGE

