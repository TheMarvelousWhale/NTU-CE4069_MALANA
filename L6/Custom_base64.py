# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 14:21:11 2021

@author: SosigCatto
"""

s = 'xDuebTK0Wjirx2ihWRKCN1l0JAV5NDSeaDirW21eyEaexjRrV29q'

charset = "ZYXABCDEFGHIJKLMNOPQRSTUVWzyxabcdefghijklmnopqrstuvw0123456789+/"

def decode(target,charset):
    bitstream = ""
    for c in target:
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
        

if __name__ == "__main__":
    print(decode(s,charset))