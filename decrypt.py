#!/usr/bin/env python

from itertools import islice as slice
import argparse
import binary
import cfb
import hashlib
import hmac
import image
import sys
import xtea

def main():
    parser = argparse.ArgumentParser(description='Decrypts and authenticates binary content hidden in the lowest bits of a bitmap')
    parser.add_argument('-k', '--password', type=str, required=True, metavar='<password>', help='The password used for decryption')
    parser.add_argument('-m', '--macpassword', type=str, required=True, metavar='<macpassword>', help='The password used for authenticity and integrity')
    parser.add_argument('bitmap', type=file, metavar='<bitmap>', help='The bitmap file to extract the binary file from')
    args = parser.parse_args()
    
    password = args.password
    macpassword = args.macpassword
    bitmap = args.bitmap

    key = int(hashlib.sha256(password).hexdigest(), 16) >> 128
    
    ciphertext = image.show(bitmap)
    
    iv = binary.pack(slice(ciphertext, 8))
    mac = binary.pack(slice(ciphertext, 32))
    binary_size = binary.pack(slice(ciphertext, 2))
    encrypted = slice(ciphertext, binary_size)

    decrypted = bytearray(cfb.decrypt(xtea.encrypt, key, iv, encrypted))
    
    check = int(hmac.new(macpassword, str(decrypted), hashlib.sha256).hexdigest(), 16)

    if mac == check:
        for d in decrypted:
            sys.stdout.write(chr(d))
    else:
        raise Exception('Data has been altered')
    
if __name__ == '__main__':
    main()
        