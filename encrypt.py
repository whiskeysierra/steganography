#!/usr/bin/env python

import argparse
import cfb
import hashlib
import random
import struct
import sys
import xtea
import os

def random_iv():
    return random.randint(0, 2 ** 64)

def byte_str(byte):
    return bin(byte)[2:].rjust(8, "0")

def main():
    parser = argparse.ArgumentParser(description="Encrypts and hides binary content in the lowest bits of a bitmap")
    parser.add_argument('-p', '--passphrase', type=str, metavar='<passphrase>', help='The passphrase used for decryption')
    parser.add_argument('-k', '--key', type=str, metavar='<key>', help='The key used for authenticity and integrity')
    parser.add_argument("binary", type=file, metavar='<binary>', help="The binary file to hide")
    parser.add_argument('bitmap', type=file, metavar='<bitmap>', help='The bitmap file to hide the binary file in')
    args = parser.parse_args()
        
    passphrase = args.passphrase
    key = args.key
    binary = args.binary
    bitmap = args.bitmap
    
    xtea_key = int(hashlib.sha256(passphrase).hexdigest(), 16) >> 128
    size = os.path.getsize(binary.name) * 8;
    iv = random_iv()
    
    plaintext = bytearray(binary.read())
    
    print "Passphrase: %s" % passphrase
    print "Key: %s" % key
    print "Initial vector: %d" % iv
    print "Content consists of %d bits" % size 
    print "XTEA block size is 64 bits"
    print "Last Block is of size %d bit(s)" % (size % 64)

    print "XTEA key is %d" % xtea_key
    block = random.randint(0, 2 ** 64)
    print "Block is: %d" % block
    
    encrypted = xtea.encrypt(xtea_key, block)
    print "Encrypted block is: %d" % encrypted
    
    decrypted = xtea.decrypt(xtea_key, encrypted)
    print "Decrypted block is: %d" % decrypted
    
    print
    print "Match?"
    print block == decrypted
    
    
if __name__ == "__main__":
    main()
        