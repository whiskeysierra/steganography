#!/usr/bin/env python

import argparse
import Image
import os
import sys
import sha
import hashlib

""" 
XTEA Block Encryption Algorithm

Original Code: http://code.activestate.com/recipes/496737/
Algorithm:     http://www.cix.co.uk/~klockstone/xtea.pdf 

    >>> import os
    >>> x = xtea.xtea()
    >>> iv = 'ABCDEFGH'
    >>> z = x.crypt('0123456789012345','Hello There',iv)
    >>> z.encode('hex')
    'fe196d0a40d6c222b9eff3'
    >>> x.crypt('0123456789012345',z,iv)
    'Hello There'

Modified to use CBC - Steve K:
    >>> import xtea
    >>> x = xtea.xtea()
    >>> #set up your key and IV then...
    >>> x.xtea_cbc_decrypt(key, iv, data, n=32, endian="!")

""" 
import struct

TEA_BLOCK_SIZE = 8
TEA_KEY_SIZE = 16

class xtea:

    def crypt(self, key,data,iv='\00\00\00\00\00\00\00\00',n=32):
        """
            Encrypt/decrypt variable length string using XTEA cypher as
            key generator (OFB mode)
            * key = 128 bit (16 char) 
            * iv = 64 bit (8 char)
            * data = string (any length)

            >>> import os
            >>> key = os.urandom(16)
            >>> iv = os.urandom(8)
            >>> data = os.urandom(10000)
            >>> z = crypt(key,data,iv)
            >>> crypt(key,z,iv) == data
            True

        """
        def keygen(self, key,iv,n):
            while True:
                iv = self.xtea_encrypt(key,iv,n)
                for k in iv:
                    yield ord(k)
        xor = [ chr(x^y) for (x,y) in zip(map(ord,data),keygen(self, key,iv,n)) ]
        return "".join(xor)

    def xtea_encrypt(self, key,block,n=32,endian="!"):
        """
            Encrypt 64 bit data block using XTEA block cypher
            * key = 128 bit (16 char) 
            * block = 64 bit (8 char)
            * n = rounds (default 32)
            * endian = byte order (see 'struct' doc - default big/network) 

            >>> z = xtea_encrypt('0123456789012345','ABCDEFGH')
            >>> z.encode('hex')
            'b67c01662ff6964a'

            Only need to change byte order if sending/receiving from 
            alternative endian implementation 

            >>> z = xtea_encrypt('0123456789012345','ABCDEFGH',endian="<")
            >>> z.encode('hex')
            'ea0c3d7c1c22557f'

        """
        v0,v1 = struct.unpack(endian+"2L",block)
        k = struct.unpack(endian+"4L",key)
        sum,delta,mask = 0L,0x9e3779b9L,0xffffffffL
        for round in range(n):
            v0 = (v0 + (((v1<<4 ^ v1>>5) + v1) ^ (sum + k[sum & 3]))) & mask
            sum = (sum + delta) & mask
            v1 = (v1 + (((v0<<4 ^ v0>>5) + v0) ^ (sum + k[sum>>11 & 3]))) & mask
        return struct.pack(endian+"2L",v0,v1)

    def xtea_decrypt(self, key,block,n=32,endian="!"):
        """
            Decrypt 64 bit data block using XTEA block cypher
            * key = 128 bit (16 char) 
            * block = 64 bit (8 char)
            * n = rounds (default 32)
            * endian = byte order (see 'struct' doc - default big/network) 

            >>> z = 'b67c01662ff6964a'.decode('hex')
            >>> xtea_decrypt('0123456789012345',z)
            'ABCDEFGH'

            Only need to change byte order if sending/receiving from 
            alternative endian implementation 

            >>> z = 'ea0c3d7c1c22557f'.decode('hex')
            >>> xtea_decrypt('0123456789012345',z,endian="<")
            'ABCDEFGH'
        """
        v0,v1 = struct.unpack(endian+"2L",block)
        k = struct.unpack(endian+"4L",key)
        delta,mask = 0x9e3779b9L,0xffffffffL
        sum = (delta * n) & mask
        for round in range(n):
            v1 = (v1 - (((v0<<4 ^ v0>>5) + v0) ^ (sum + k[sum>>11 & 3]))) & mask
            sum = (sum - delta) & mask
            v0 = (v0 - (((v1<<4 ^ v1>>5) + v1) ^ (sum + k[sum & 3]))) & mask
        return struct.pack(endian+"2L",v0,v1)

    def xtea_cbc_decrypt(self, key, iv, data, n=32, endian="!"):
        """
            Decrypt a data buffer using cipher block chaining mode
            Written by Steve K
        """
        global TEA_BLOCK_SIZE
        size = len(data)
        if (size % TEA_BLOCK_SIZE != 0):
            raise Exception("Size of data is not a multiple of TEA \
                            block size (%d)" % (TEA_BLOCK_SIZE))
        decrypted = ""
        i = 0
        while (i < size):
            result = self.xtea_decrypt(key,
                                  data[i:i + TEA_BLOCK_SIZE],
                                  n, endian)

            j = 0
            while (j < TEA_BLOCK_SIZE):
                decrypted += chr(ord(result[j]) ^ ord(iv[j]))
                j += 1

            iv = data[i:i + TEA_BLOCK_SIZE]
        i += TEA_BLOCK_SIZE

        return decrypted

def main():
    parser = argparse.ArgumentParser(description="Hides a binary file in a bitmap.")
    parser.add_argument("-b", "--bits", required=True, metavar='B', type=int, help="the number of least significant bits to use")
    parser.add_argument("-k", "--password", required=True, type=str, help="The password used for encryption")
    parser.add_argument("binary", type=file, help="the binary file to hide")
    parser.add_argument("image", type=file, help="the image file to hide the binary file in")
    args = parser.parse_args()
    
    bits = args.bits
    password = args.password
    binary = args.binary
    image = args.image

    sha256 = hashlib.new("sha256");
    sha256.update(password)
    password_sha256 = sha256.hexdigest()
    full = 2 ** 256 - 1
    print int(password_sha256, 16)
    sys.exit(1)
    
    binary_size = os.path.getsize(binary.name)
    image_size = os.path.getsize(image.name)
    
    if (binary_size * 8) / bits > image_size:
        print "%s does not fit into %s" % (binary.name, image.name)
        sys.exit(1)
    
    with open(image.name + ".b%02d" % bits, "wb") as target:
        try:
            bitmap = Image.open(image)
            
            class Encoder:
                
                # the index in the file
                byte_index = 0
                # the current byte, stored to save disk access
                current_byte = None
                # index in the current byte (0-7)
                bit_index = 0
                
                def next_byte(self):
                    return int(ord(binary.read(1)))
                
                def encode(self, pixel):
                    if self.current_byte is None:
                        # first byte
                        self.current_byte = self.next_byte()
                    elif self.current_byte == "":
                        # last byte
                        raise EOFError
                    elif self.bit_index == 8:
                        # all bits of current byte read
                        self.current_byte = self.next_byte()
                        self.byte_index += 1
                        self.bit_index = 0
                    
                    r = pixel
                    for n in xrange(bits):
                        byte = (1 << n)
                        if (self.current_byte & byte) == 0:
                            # set byte to 0
                            r &= ~byte
                        else:
                            # set bit to 1
                            r |= byte
                    
                    return r
            
            encoder = Encoder()
            bitmap.point(encoder.encode).save("target.bmp", "BMP")
            bitmap.point(encoder.encode).save(target, "BMP")
        finally:
            binary.close()
            image.close()
        
if __name__ == "__main__":
    main()
        