# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 14:21:11 2021

@author: SosigCatto
"""

s = 'xDuebTK0Wjirx2ihWRKCN1l0JAV5NDSeaDirW21eyEaexjRrV29q'

charset = "ZYXABCDEFGHIJKLMNOPQRSTUVWzyxabcdefghijklmnopqrstuvw0123456789+/"
newchar = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/"
def decode(target,charset):
    bitstream = ""
    for c in target:
        #print(c)
        i = charset.index(c)       #get the ordinal
        b = format(i,'06b')        #get the binary, size of 6 bit 
        bitstream += b             #since format return a string, append it to result

    #now result is a bit stream, just convert it back to ascii (one char - 2bytes)
    #print(result)
        
    result = ""
    for j in range(0,len(bitstream),8):
        k = int(bitstream[j:j+8],2)  #grab 8 bit, translate to decimal
        result += chr(k)             #chr get the ascii text for an ordinal number
    return result

def encode(target,charset):
    #Convert string to bit stream
    bitstream = ""
    for c in target:
        bitstream += format(ord(c),'08b')
    print(bitstream)
    result = ""
    for j in range(0,len(bitstream),6):
        k = int(bitstream[j:j+6],2)  #grab 6 bit, translate to charset
        result += charset[k]
    return result
        
def decrypt(stra):
    encrypt_key = 'malwareanalyst'
    key = ""
    print(stra)
    for i, b in enumerate(stra):
        index = ord(b) - ord(encrypt_key[i % len(encrypt_key)])
        if index > 0:
            key = key + chr(index)
        else:
            pass
        #print(key)
    return key

target = "1DxG59sSLjdEWT/T2nBwZ5RA0n+uYRM3RU+727O"

print(decrypt(decode(target,newchar)))
    #print(target[i:i+2],chr((int(target[i:i+2],16)^int("41",16))-10))
    