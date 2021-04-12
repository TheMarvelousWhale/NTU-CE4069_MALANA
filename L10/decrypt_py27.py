# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 01:16:20 2021

@author: hoang
"""

import hashlib
from Crypto.Cipher import AES

def derive_key(key):
    # SHA-1 hash algorithm 
    key_sha1 = hashlib.sha1(key).digest()
    b0 = ""
    for x in key_sha1:
        b0 += chr( ord(x)^ 0x36)
    b1 = ""
    for x in key_sha1:
        b1 += chr(ord(x)^ 0x5c)
    # pad remaining bytes with the appropriate value
    b0 += "\x36"*(64 -len(b0))
    b1 += "\x5c"*(64 -len(b1))
    b0_sha1 = hashlib.sha1(b0).digest()
    b1_sha1 = hashlib.sha1(b1).digest()
    return b0_sha1 + b1_sha1

unpad = lambda s: s[0:ord(s[-1])]  
# remove pkcs5 padding
fname = "Urgent.doc"
with open(fname, 'rb+') as f:
    encrypted_data = f.read()
    key = "thosefilesreallytiedthefoldertogether"
    # 256-bit key / 8 = 32 bytes
    aes_key = derive_key(key)[:32]
    
    iv = hashlib.md5(fname.lower()).digest()
    decryptor = AES.new(aes_key, AES.MODE_CBC, iv)
    decrypted_data = decryptor.decrypt(encrypted_data)
    fe = open("nani10.jpg", "wb+")
    fe.write(decrypted_data)
    fe.close()
    #f.truncate(len(decrypted_data))