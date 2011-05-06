#!/usr/bin/env python

from itertools import chain
import argparse
import binary
import cfb
import hashlib
import hmac
import image
import os
import random
import xtea

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
    
    p = content.read()
    plaintext = bytearray(p)
    
    mac = int(hmac.new(macpassword, p, hashlib.sha256).hexdigest(), 16)
    encrypted = cfb.encrypt(xtea.encrypt, key, iv, chain(binary.unpack(mac, 32), plaintext))
    
    all = chain(
        binary.unpack(iv, 8),
        binary.unpack(binary_size + 32, 2),
        encrypted
    )
    
    image.hide(all, bitmap)
    
if __name__ == "__main__":
    main()
        