#!/usr/bin/env python

import argparse
import binary
import cfb
import hashlib
import image
import os
import random
import struct
import sys
import xtea
import itertools

def main():
    parser = argparse.ArgumentParser(description="Encrypts and hides binary content in the lowest bits of a bitmap")
    parser.add_argument('-k', '--password', type=str, required=True, metavar='<password>', help='The password used for encryption')
    parser.add_argument('-m', '--macpassword', type=str, required=True, metavar='<macpassword>', help='The password used for authenticity and integrity')
    parser.add_argument("content", type=file, metavar='<content>', help="The binary file to hide")
    parser.add_argument('bitmap', type=file, metavar='<bitmap>', help='The bitmap file to hide the binary file in')
    args = parser.parse_args()
        
    password = args.password
    macpassword = args.macpassword
    content = args.content
    bitmap = args.bitmap
    
    binary_size = os.path.getsize(content.name)
    bitmap_size = os.path.getsize(bitmap.name)
    
    if binary_size * 8 > bitmap_size:
        raise Exception("%s is too big to be hidden in %s" % (content.name, bitmap.name))
    
    key = int(hashlib.sha256(password).hexdigest(), 16) >> 128
    size = os.path.getsize(content.name) * 8;
    iv = random.randint(0, 0xffffffffffffffff)
    
    # TODO stream like encryption
    plaintext = bytearray(content.read())
    
    encrypted = cfb.encrypt(xtea.encrypt, key, iv, plaintext)
    
    all = itertools.chain(
        binary.unpack(iv, 8),
        binary.unpack(binary_size, 2),
        encrypted
    )
    
    image.hide(all, bitmap)
    
if __name__ == "__main__":
    main()
        