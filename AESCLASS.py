import base64
import hashlib
from Cryptodome import Random
from Cryptodome.Cipher import AES


class AESCipher(object):
    def __init__(self, key):
        """
        initializing the key object out of the key string
        :param key: the key created by the two parties
        """
        self.bs = AES.block_size
        self.key = hashlib.sha256(str(key).encode()).digest()

    def encrypt(self, data):
        """
        encrypts the msg to be sent
        :param data: the msg to encrypt
        :return:
        """
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        data_padded = self._pad(data_bytes)

        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        return base64.b64encode(iv + cipher.encrypt(data_padded))

    def decrypt(self, msg):
        """
        decrypt a given msg
        :param msg: the msg to decrypt
        :return:
        """
        enc = base64.b64decode(msg)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        padded_data = cipher.decrypt(enc[AES.block_size:])
        return self._unpad(padded_data).decode('utf-8')

    def _pad(self, s):
        padding_len = self.bs - len(s) % self.bs
        padding = bytes([padding_len] * padding_len)
        return s + padding

    @staticmethod
    def _unpad(s):
        padding_len = s[-1]
        return s[:-padding_len]

    def encrypt_bytes(self, raw_bytes):
        raw_padded = self._pad(raw_bytes)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw_padded))

    def decrypt_bytes(self, msg):
        enc = base64.b64decode(msg)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        padded_data = cipher.decrypt(enc[AES.block_size:])
        return self._unpad(padded_data)