import rsa
from django.core import cache
import threading
from setting.models.system import SystemSetting, SettingType
import base64

lock = threading.Lock()
rsa_cache = cache.caches['default']
rsa_cache_key = 'rsa_key'

def generate():
    """
    生成 私钥秘钥对
    :return:{key:'公钥',value:'私钥'}
    """
    # 生成一个 2048 位的密钥
    (public_key, private_key) = rsa.newkeys(2048)

    #将私钥转换为字符串形式
    privkey_str = private_key.save_pkcs1().decode()

    #将公钥转换为字符串形式
    pubkey_str = public_key.save_pkcs1().decode()

    return {'public_key': pubkey_str, 'private_key': privkey_str}

def get_key_pair():
    """
    获取公钥私钥
    """
    key_pair = rsa_cache.get(rsa_cache_key)
    if key_pair is None:
        with lock:
            key_pair = rsa_cache.get(rsa_cache_key)
            if key_pair is not None:
                return key_pair
            key_pair = get_key_pair_from_db()
            rsa_cache.set(rsa_cache_key, key_pair)
    return key_pair

def get_key_pair_from_db():
    """
    从数据库获取公钥私钥
    """
    system_setting = SystemSetting.objects.filter(type=SettingType.RSA.value).first()
    if system_setting is None:
        key_pair = generate()
        system_setting = SystemSetting(type=SettingType.RSA.value,
                                       meta={'public_key': key_pair.get('public_key'), 'private_key': key_pair.get('private_key')})
        system_setting.save()
    return system_setting.meta

def encrypt(data: str) -> str:
    """
    加密,返回base64编码后的字符串
    """
    key_pair = get_key_pair()
    public_key_str = key_pair.get('public_key')
    public_key = rsa.PublicKey.load_pkcs1(public_key_str.encode())
    encrypt_data = rsa.encrypt(data.encode(), public_key)
    return base64.b64encode(encrypt_data).decode()

def decrypt(data: str) -> str:
    """
    解密,返回解密后的字符串s
    """
    key_pair = get_key_pair()
    private_key_str = key_pair.get('private_key')
    private_key = rsa.PrivateKey.load_pkcs1(private_key_str.encode())
    return rsa.decrypt(base64.b64decode(data), private_key).decode()

