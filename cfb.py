
def byte_sequence(block, n=8):
    for i in range(n - 1, -1, -1):
        yield block >> i * 8 & 0xff

def mask(n):
    return 1 << max(0, (n * 8) - 1)

def encrypt(cipher, key, iv, plain):
    """
        Encrypts the given plaintext using the specified cipher, key and initial vector.
        * cipher = function (key, block) => block
        * key = 128 bit key
        * iv = 64 bit initial vector
        * plain = variable length byte sequence
    """
    feedback = iv
    i, block = 0, 0
    for p in plain:
        block = block << 8 | p
        i += 1
        if i == 8:
            feedback = block ^ cipher(key, feedback)
            for c in byte_sequence(feedback):
                yield c
            i, block = 0, 0
            
    for c in byte_sequence(block ^ (cipher(key, feedback) & mask(i)), i):
        yield c
    
def decrypt(cipher, key, iv, crypt):
    """
        Decrypts the given ciphertext using the specified cipher, key and initial vector.
        * cipher = function (key, block) => block
        * key = 128 bit key
        * iv = 64 bit initial vector
        * crypt = variable length byte sequence
    """
    feedback = iv
    i, block = 0, 0
    for c in crypt:
        block = block << 8 | c
        i += 1
        if i == 8:
            for p in byte_sequence(block ^ cipher(key, feedback)):
                yield p
            feedback = block
            i, block = 0, 0
    
    for p in byte_sequence(block ^ (cipher(key, feedback) & mask(i)), i):
        yield p
    