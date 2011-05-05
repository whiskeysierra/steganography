import struct

def __key_blocks(key):
    return [ (key >> (32 * i)) & 0xffffffff for i in range(3, -1, -1) ]

def encrypt(key, block, n=32):
    """
        Encrypt 64 bit block using the XTEA block cipher
        * key = 128 bit
        * block = 64 bit
        * n = rounds (default 32)
    """
    
    mask = 0xffffffff
    
    v0 = block >> 32
    v1 = block & mask
    k = __key_blocks(key)
    delta = 0x9E3779B9
    sum = 0
    
    for round in range(n):
        v0 += ((v1 << 4 ^ v1 >> 5) + v1) ^ (sum + k[sum & 3])
        v0 &= mask
        sum += delta
        sum &= mask
        v1 += ((v0 << 4 ^ v0 >> 5) + v0) ^ (sum + k[sum >> 11 & 3])
        v1 &= mask

    return v0 << 32 | v1
    
def decrypt(key, block, n=32):
    """
        Decrypt 64 bit block using the XTEA block cipher
        * key = 128 bit 
        * block = 64 bit
        * n = rounds (default 32)
    """
    
    mask = 0xffffffff

    v0 = block >> 32
    v1 = block & mask
    k = __key_blocks(key)
    delta = 0x9E3779B9
    sum = (delta * n) & mask
    
    for round in range(n):
        v1 -= ((v0 << 4 ^ v0 >> 5) + v0) ^ (sum + k[sum >> 11 & 3])
        v1 &= mask
        sum -= delta
        sum &= mask
        v0 -= ((v1 << 4 ^ v1 >> 5) + v1) ^ (sum + k[sum & 3])
        v0 &= mask
    
    return v0 << 32 | v1
