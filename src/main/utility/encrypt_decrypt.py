# python script for encrypting and decrypting passwords

import base64
from Cryptodome.Cipher import AES                                   # encryption
from Cryptodome.Protocol.KDF import PBKDF2                          # For hashing and which mode
import os, sys
sys.path.append(os.path.abspath("/Users/prashant-newway/Documents/Data Engineering/Projects/Etl-data-pipeline-pyspark-aws"))
from resources.dev import config
# from logging_config import logger

try:
    key = config.key
    iv = config.iv
    salt = config.salt                      # hashing to create a combination from these three

    if not (key and iv and salt):
        raise Exception(F"Error while fetching details for key/iv/salt")
except Exception as e:
    print(f"Error occured. Details : {e}")
    # logger.error("Error occurred. Details: %s", e)
    sys.exit(0)

                                            # padding and unpadding
BS = 16
pad = lambda s: bytes(s + (BS - len(s) % BS) * chr(BS - len(s) % BS), 'utf-8')
unpad = lambda s: s[0:-ord(s[-1:])]

def get_private_key():
    Salt = salt.encode('utf-8')
    kdf = PBKDF2(key, Salt, 64, 1000)
    key32 = kdf[:32]
    return key32


def encrypt(raw):
    raw = pad(raw)
    cipher = AES.new(get_private_key(), AES.MODE_CBC, iv.encode('utf-8'))
    return base64.b64encode(cipher.encrypt(raw))


def decrypt(enc):
    cipher = AES.new(get_private_key(), AES.MODE_CBC, iv.encode('utf-8'))
    return unpad(cipher.decrypt(base64.b64decode(enc))).decode('utf8')


