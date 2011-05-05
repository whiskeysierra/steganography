#!/usr/bin/env python

import argparse
import sys
import cfb

def main():
    parser = argparse.ArgumentParser(description='Decrypts and authenticates binary content hidden in the lowest bits of a bitmap')
    parser.add_argument('-p', '--passphrase', type=str, metavar='<passphrase>', help='The passphrase used for decryption')
    parser.add_argument('-k', '--key', type=str, metavar='<key>', help='The key used for authenticity and integrity')
    parser.add_argument('bitmap', type=file, metavar='<bitmap>', help='The bitmap file to extract the binary file from')
    args = parser.parse_args()
    
    passphrase = args.passphrase
    key = args.key
    bitmap = args.bitmap
    
    print 'Decrypt? Really?'
    cfb.decrypt()

if __name__ == '__main__':
    main()
        