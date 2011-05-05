
def encrypt(cipher, key, iv, plaintext):
    return cipher(key, plaintext[0:8])

def decrypt(cipher, key, iv, ciphertext):
    return cipher(key, ciphertext[0:8])