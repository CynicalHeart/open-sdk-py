import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


def load_rsa_public_key(file_path):
    with open(file_path, "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(), backend=default_backend())
    return public_key


def rsa_encrypt(key, data):
    key_size = (key.key_size + 7) // 8
    max_chunk_size = key_size - 11

    data_bytes = data.encode('utf-8')
    encrypted_chunks = []

    for i in range(0, len(data_bytes), max_chunk_size):
        chunk = data_bytes[i:i + max_chunk_size]
        encrypted_chunk = key.encrypt(chunk, padding.PKCS1v15())
        encrypted_chunks.append(encrypted_chunk)

    encrypted_data = b''.join(encrypted_chunks)

    return base64.b64encode(encrypted_data).decode('utf-8')
