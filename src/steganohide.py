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
                
                index = 0
                
                def read_byte(self):
                    read = binary.read(1)
                    print "Read %s" % read
                    if read is "":
                        print "End of file"
                        return ""
                    else:
                        return int(ord(read))
                
                def next_bit(self):
                    if self.current_byte is None:
                        self.current_byte = self.read_byte()
                    try:
                        bit = (self.current_byte & (1 << self.bit_index)) >> self.bit_index
                        self.bit_index = self.bit_index + 1
                        return bit
                    finally:
                        if self.bit_index is 7:
                            self.bit_index = 0
                            self.current_byte = self.read_byte()
                
                def encode(self, pixel):
                    if self.current_byte is "":
                        # last byte
                        print "End of content"
                        return pixel
                    
                    print "Pixel #%s" % self.index
                    self.index = self.index + 1

                    #print "Input byte: %d" % pixel
                    for n in xrange(bits):
                        # set n-th bit to 0
                        pixel &= ~(1 << n)
                        # set n-th bit to 1 if needed
                        pixel |= self.next_bit() << n
                    
                    #print "Output byte: %d" % pixel
                    return pixel
            
            encoder = Encoder()
            pix = bitmap.load()
            for x in xrange(bitmap.size[0]):
                for y in xrange(bitmap.size[1]):
                    pix[x][y] = encoder.encode(pix[x][y])
            
            #bitmap.point(encoder.encode).save("target.bmp", "BMP")
            #bitmap.point(encoder.encode).save(target, "BMP")
        finally:
            binary.close()
            image.close()
        
if __name__ == "__main__":
    main()
        