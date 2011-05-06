import Image

def to_pixels(image):
    width, height = image.size
    for x in xrange(width):
        for y in xrange(height):
            yield x, y, image.getpixel((x, y))
        
def to_bits(bytes):
    for byte in bytes:
        for i in range(7, -1, -1):
            yield byte >> i & 1

def move(i, finished=False):
    if finished:
        return None, True
    else:
        try:
            return i.next(), False
        except StopIteration:
            return None, True
    

def hide(bytes, bitmap, ext='ste'):
    """
        Hides the given bytes in the supplied bitmap.
        * bytes variable length byte sequence
        * bitmap bitmap file
    """
    
    image = Image.open(bitmap)
    out = Image.new(image.mode, image.size, None)
    
    pixels = to_pixels(image)
    bits = to_bits(bytes)
    
    finished = False
    
    for x, y, pixel in pixels:
        r, g, b = pixel
        
        bit, finished = move(bits, finished)
        r = r if bit is None else (r & ~1) | bit  
        
        bit, finished = move(bits, finished)
        g = g if bit is None else (g & ~1) | bit
        
        bit, finished = move(bits, finished)
        b = b if bit is None else (b & ~1) | bit

        out.putpixel((x, y), (r, g, b))
        
    name = bitmap.name + '.' + ext
    name = "image.enc.bmp"
    with open(name, "wb") as target:
        out.save(target, "BMP")

def to_bytes(bits):
    i, byte = 0, 0
    for bit in bits:
        byte = byte << 1 | bit
        i += 1
        if i == 8:
            yield byte
            i, byte = 0, 0
    if i > 0:
        yield byte

def show(bitmap):
    
    image = Image.open(bitmap)
    width, height = image.size
    
    def bits():
        for x in xrange(width):
            for y in xrange(height):
                r, g, b = image.getpixel((x, y))
                yield r & 1
                yield g & 1
                yield b & 1
    
    for byte in to_bytes(bits()):
        yield byte
            