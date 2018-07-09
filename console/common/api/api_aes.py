# coding=utf-8
import base64

from Crypto.Cipher import AES
from Crypto import Random


class AESCipher(object):
    """
    对称加密解密:
    aes = AESCipher(key)
    r = aes.encrypt("test")
    print r

    """
    def __init__(self, key, block_size=32):
        self.key = key
        self.bs = block_size
        self.pad = lambda s: s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
        self.unpad = lambda s: s[:-ord(s[len(s)-1:])]

    def encrypt(self, raw):
        """
        对称加密
        :param raw:
        :return:
        """
        raw = self.pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        """
        对称解密
        :param enc:
        :return:
        """
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc[16:]))


aes_api = AESCipher(key="498f2940ead775715e7a662eca1d3d9c")
