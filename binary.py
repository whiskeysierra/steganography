
def pack(bytes):
    l = 0
    for byte in bytes:
        l = l << 8 | byte
    return l

def unpack(l, n):
    for i in range(n - 1, -1, -1):
        yield (l >> 8 * i) & 0xff