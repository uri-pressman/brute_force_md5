import base64
import hashlib
import secrets
from Cryptodome.Cipher import AES
from Cryptodome import Random


# --- Your Diffie-Hellman Class ---
class SimpleDH:
    def __init__(self):
        """
        initializing the key object
        """
        #numbers for exchange
        self.p = 997
        self.g = 2
        self.__private_key = secrets.randbelow(self.p - 1) + 1

    def get_public_key(self):
        """
        creates a public key out of the private one
        :return:
        """
        return pow(self.g, self.__private_key, self.p)

    def get_shared_secret(self, remote_public_key):
        """
        creates a shared key with both parties key
        :param remote_public_key:
        :return:
        """
        return pow(remote_public_key, self.__private_key, self.p)


# --- The Class from your Image ---
