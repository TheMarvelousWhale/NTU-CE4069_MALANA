# -*- coding: utf-8 -*-
"""

@Date: 9th April 2021
@author: SosigCatto, Pei Pei and Giraffe

@PostScript: 
    It was a fun ride in malware. 
    지금 까지, 소시지 카트더 ~^0^~
"""


from scapy.all import *

newchar = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/"
encrypt_key = 'malwareanalyst'

def b64_decode(target,charset):
    bitstream = ""
    for c in target:
        if c in charset:               #ignore padding
            i = charset.index(c)       #get the ordinal
            b = format(i,'06b')        #get the binary, size of 6 bit 
            bitstream += b             #since 'format' return a string, append it to result
    result = ""
    for j in range(0,len(bitstream)-8,8):            #truncate any leftover if > multiple of 8 bits
                                                     # it's like counting from 0 to n-1, but in 8 so n-8
        k = int(bitstream[j:j+8],2)                  #grab 8 bit, translate to decimal
        result += chr(k)                             #chr get the ascii text for an ordinal number
    return result

        
def sausage_decrypt(stra):
    key = ""
    for i, b in enumerate(stra):
        index = ord(b) - ord(encrypt_key[i % len(encrypt_key)])      #since encrypt do +, we simply - here
        key = key + chr(index)
    return key


def pry_the_pcap(pcap_path):
    #thankyou fireeye, again
    key = ''
    pkts = rdpcap(pcap_path)
    for pkt in pkts:
        if TCP in pkt and Raw in pkt and bytes('Mozilla/5.0 (Windows NT 6.1; WOW64) KEY','utf-8') in pkt[Raw].load:
            headers, body = pkt[Raw].load.split(bytes("\r\n\r\n",'utf-8'),1)
            key += body.decode('utf-8')
    return key

if __name__ == "__main__":
    target = pry_the_pcap("traffic.pcap")
    print(f"[+] From PCAP: {target}")
    decoded_key = b64_decode(target,newchar)
    print(f"[+] After b64: {decoded_key}")
    decrypted_key = sausage_decrypt(decoded_key)
    print(f"[+] After decryption: {decrypted_key}")


    