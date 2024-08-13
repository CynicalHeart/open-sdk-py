import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from gmssl import sm2


def load_rsa_public_key(file_path):
    """
    从文件中读取RSA公钥
    ---

    @param file_path: 公钥文件路径
    """
    with open(file_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(), backend=default_backend())
    return public_key


def load_sm2_public_key(file_path):
    """
    从文件中读取SM2公钥
    ---

    @param file_path: 公钥文件路径
    """
    with open(file_path, "r") as f:
        public_key = f.read().strip()

    return public_key


def rsa_encrypt(key, data):
    """
    使用RSA加密数据
    ---

    @param key: RSA公钥
    @param data: 待加密数据
    """
    key_size = (key.key_size + 7) // 8
    # 计算每个块的最大大小（对于PKCS1v15，通常需要预留11字节）
    max_chunk_size = key_size - 11

    # 将数据编码为UTF-8字节
    data_bytes = data.encode('utf-8')
    encrypted_chunks = []

    # 分块加密
    for i in range(0, len(data_bytes), max_chunk_size):
        chunk = data_bytes[i:i + max_chunk_size]
        encrypted_chunk = key.encrypt(chunk, padding.PKCS1v15())
        encrypted_chunks.append(encrypted_chunk)

    # 将所有加密的块连接起来
    encrypted_data = b''.join(encrypted_chunks)

    # 使用Base64编码并返回
    return base64.b64encode(encrypted_data).decode('utf-8')


def sm2_encrypt(key, data):
    """
    使用sm2加密数据

    ---

    @param key:  SM2公钥
    @param data: 待加密数据
    """
    # 初始化SM2加密对象
    sm2_crypt = sm2.CryptSM2(public_key=key, private_key=None, asn1=True)
    # 加密数据
    encrypted_data = sm2_crypt.encrypt(data.encode('utf-8'))

    return base64.b64encode(encrypted_data).decode('utf-8')
