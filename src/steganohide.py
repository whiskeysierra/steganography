#!/usr/bin/env python

import argparse
import Image
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Hides a binary file in a bitmap.")
    parser.add_argument("-b", "--bits", required=True, metavar='B', type=int, help="the number of least significant bits to use")
    parser.add_argument("binary", type=file, help="the binary file to hide")
    parser.add_argument("image", type=file, help="the image file to hide the binary file in")
    args = parser.parse_args()
    
    bits = args.bits;
    binary = args.binary;
    image = args.image;
    
    binary_size = os.path.getsize(binary.name);
    image_size = os.path.getsize(image.name);
    
    if (binary_size * 8) / bits > image_size:
        print "%s does not fit into %s" % (binary.name, image.name)
        sys.exit(1)
    
    with open(image.name + ".b%02d" % bits, "wb") as target:
        try:
            bitmap = Image.open(image)
            
            class Encoder:
                
                # the current byte, stored to save disk access
                current_byte = None
                
                # index in the current byte (0-7)
                bit_index = 0
                
                def read_byte(self):
                    read = binary.read(1)
                    print "Read %s" % read
                    if read == "":
                        return ""
                    else:
                        return int(ord(read))
                
                def next_bit(self):
                    if self.current_byte is None:
                        self.current_byte = self.read_byte()
                        
                    if self.current_byte == "":
                        # last byte
                        return 
                    
                    try:
                        bit = (self.current_byte & (1 << self.bit_index)) >> self.bit_index
                        self.bit_index = self.bit_index + 1
                        return bit
                    finally:
                        if self.bit_index is 7:
                            self.bit_index = 0
                            self.current_byte = self.read_byte()
                
                def encode(self, pixel):
                    if self.current_byte == "":
                        # last byte
                        return pixel
                    
                    #print "Input byte: %d" % pixel
                    for n in xrange(bits):
                        # set n-th bit to 0
                        pixel &= ~(1 << n)
                        bit = self.next_bit()
                        if bit is None:
                            return pixel
                        # set n-th bit to 1 if needed
                        pixel |= bit << n
                    
                    #print "Output byte: %d" % pixel
                    return pixel

            encoder = Encoder()
            out = Image.new(bitmap.mode, bitmap.size, None)
            width, height = bitmap.size
            for x in xrange(width):
                for y in xrange(height):
                    r, g, b = bitmap.getpixel((x, y))
                    r = encoder.encode(r)
                    g = encoder.encode(g)
                    b = encoder.encode(b)
                    out.putpixel((x, y), (r, g, b))
                    
            out.save(target, "BMP")            
        finally:
            binary.close()
            image.close()
        
if __name__ == "__main__":
    main()
        