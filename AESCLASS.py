import base64
import hashlib
from random import Random
from Cryptodome import Random
from Cryptodome.Cipher import AES


class AESCipher(object):
    def __init__(self, key):
        """
        initializing the key object out of the key string
        :param key: the key created by the two parties
        """
        self.bs = AES.block_size
        # Ensure key is hashed to exactly 32 bytes
        self.key = hashlib.sha256(str(key).encode()).digest()

    def encrypt(self, data):
        """
        encrypts the msg to be sent
        :param raw: the msg to encrypt
        :return:
        """
        #encodes the msg and adds padding to it
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        else:
            data_bytes = data
        data_padded = self._pad(data_bytes)

        #encrypts the msg
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        # Encrypt the PADDED BYTES directly
        return base64.b64encode(iv + cipher.encrypt(data_padded))

    def decrypt(self, msg):
        """
        decrypt a given msg
        :param msg: the msg to decrypt
        :return:
        """
        #decodes the msg and decrypts it
        enc = base64.b64decode(msg)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        # Decrypt gives us PADDED BYTES
        padded_data = cipher.decrypt(enc[AES.block_size:])

        # removes the padding added by the sender
        return self._unpad(padded_data).decode('utf-8')

    def _pad(self, s):
        """
        adds padding to the msg before sending
        :param s: the msg
        :return: the padded msg
        """
        # len of padding to add
        padding_len = self.bs - len(s) % self.bs
        # Create padding bytes (e.g., b'\x05\x05\x05\x05\x05')
        padding = bytes([padding_len] * padding_len)
        return s + padding





    @staticmethod
    def _unpad(s):
        """
        unpaddes the padded msg to give only the msg without extra bytes
        :param s: the msg to unpad
        :return:
        """
        #removes the padding bytes
        padding_len = s[-1]
        return s[:-padding_len]

    def encrypt_bytes(self, raw_bytes):
        """
        Encrypts raw bytes (like an image) without encoding.
        """
        # 1. Pad the raw bytes
        raw_padded = self._pad(raw_bytes)

        # 2. Generate IV and Encrypt
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        # 3. Return base64 encoded bytes
        return base64.b64encode(iv + cipher.encrypt(raw_padded))

    def decrypt_bytes(self, msg):
        """
        Decrypts into raw bytes (like an image) without decoding to string.
        """
        enc = base64.b64decode(msg)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)

        padded_data = cipher.decrypt(enc[AES.block_size:])

        # Return unpadded BYTES (do not .decode() here!)
        return self._unpad(padded_data)

