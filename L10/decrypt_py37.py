# -*- coding: utf-8 -*-
"""
Created on Sun Apr 11 01:16:20 2021

@author: hoang

@Changes: incorporate bytestream processing for the key derivation due to .encode('utf-8') cannot work on b0 and b1 string due to its character set
            As such I treat b0 and b1 as bytestream to begin with and append byte to them instead of building a string and use .encode('utf-8')
            which for some reason resulted in a lot of chr(194) and chr(195) irrelevant chars in the resulting byte stream. Probably cos encoding
"""

import hashlib
from Crypto.Cipher import AES

def derive_key(key):
    # SHA-1 hash algorithm 
    key_sha1 = hashlib.sha1(key).digest()
    b0 = b''
    for x in key_sha1:
        b0 += bytes([x^ 0x36])
    b1 = b''
    for x in key_sha1:
        b1 += bytes([x^ 0x5c])
    # pad remaining bytes with the appropriate value
    b0 += bytes([0x36 for _ in range(64 -len(b0))])
    b1 += bytes([0x5c for _ in range(64 -len(b1))])
    b0_sha1 = hashlib.sha1(b0).digest()
    b1_sha1 = hashlib.sha1(b1).digest()
    return b0_sha1 + b1_sha1

fname = "Urgent.doc"
with open(fname, 'rb+') as f:
    encrypted_data = f.read()
    key = "thosefilesreallytiedthefoldertogether".encode('utf-8')
    # 256-bit key / 8 = 32 bytes
    aes_key = derive_key(key)[:32]
    
    iv = hashlib.md5(fname.lower().encode('utf-8')).digest()
    decryptor = AES.new(aes_key, AES.MODE_CBC, iv)
    decrypted_data = decryptor.decrypt(encrypted_data)
    fe = open("nani12.jpg", "wb+")
    fe.write(decrypted_data)
    fe.close()
