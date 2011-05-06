
def key_blocks(key):
    return [ (key >> (32 * i)) & 0xffffffff for i in range(3, -1, -1) ]

def uint32(i):
    return i & 0xffffffff

def encrypt(key, block, n=32):
    """
        Encrypts a 64 bit block using the xtea block cipher
        * key = 128 bit
        * block = 64 bit
        * n = rounds (default 32)
    """
    
    v0 = block >> 32
    v1 = uint32(block)
    k = key_blocks(key)
    delta = 0x9E3779B9
    sum = 0
    
    for round in range(n):
        v0 = uint32(v0 + (((v1 << 4 ^ v1 >> 5) + v1) ^ (sum + k[sum & 3])))
        sum = uint32(sum + delta)
        v1 = uint32(v1 + (((v0 << 4 ^ v0 >> 5) + v0) ^ (sum + k[sum >> 11 & 3])))

    return v0 << 32 | v1
    
def decrypt(key, block, n=32):
    """
        Decrypts a 64 bit block using the xtea block cipher
        * key = 128 bit 
        * block = 64 bit
        * n = rounds (default 32)
    """
    
    v0 = block >> 32
    v1 = uint32(block)
    k = key_blocks(key)
    delta = 0x9E3779B9
    sum = uint32(delta * n)
    
    for round in range(n):
        v1 = uint32(v1 - (((v0 << 4 ^ v0 >> 5) + v0) ^ (sum + k[sum >> 11 & 3])))
        sum = uint32(sum - delta)
        v0 = uint32(v0 - (((v1 << 4 ^ v1 >> 5) + v1) ^ (sum + k[sum & 3])))
    
    return v0 << 32 | v1
