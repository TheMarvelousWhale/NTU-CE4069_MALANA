# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 16:46:47 2021

@author: Sosig
"""


encrypted = "96B4A9A08AA7AB87A8 A2 8B 87 85 B4 A3 B186 85 83 85 9C F2 F6 F0  FF E8 A5 A9 AB"

def helper(a,b):
    _tmp =(((a & 255) * 555 ) //16 ) % 256
    result = chr(_tmp ^ b) 
    return result

def decrypt(target):
    key = ""
    for c in range(0,len(target),2):
        key += helper(50,int(target[c:c+2],16))
    print(key)

def main():
    decrypt(encrypted.replace(' ',''))
    return

if __name__ == "__main__":
    main()
    