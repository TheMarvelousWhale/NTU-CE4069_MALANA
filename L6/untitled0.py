# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 16:03:36 2021

@author: hoang
"""

d = int("0x44",16)
a = int("0x24",16)
c = int("0x84",16)
s = int("0x21",16)
print(chr((d^a)-s+c))