# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 11:32:41 2021

@author: hoang
"""

charset = "abcdefghijklmnopqrstuvwxyz"

def insert(input_str,output):
    for c in charset:
        for insertion_index in range(len(input_str)+1):
            inserted = input_str[:insertion_index] + c + input_str[insertion_index:]
            print(f"{inserted} - {output}")
            if inserted == output:
                return True
    return False

def delete(input,output):
    for deletion_index in range(len(input)):
        deleted = input[:deletion_index] +input[deletion_index+1:]
        if deleted == output:
            return True
    return False

def replace(input,output):
    for c in charset:
        for replace_index in range(len(output)):
            replaced = input[:]
            replaced[replace_index] = c
            if replaced == output:
                return True
    return False

def main(input_str,output_str):
    if insert(input_str,output_str) == True or delete(input_str,output_str) == True or replace(input_str,output_str) == True:
        return True
    else:
        return False

if __name__ == "__main__":
    #main()
    pass