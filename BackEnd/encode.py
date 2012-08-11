import sys
import os
import png
import math

def encode_to_image(filename):
    filesize = os.path.getsize(filename)
    print "filename",filename,"filesize",filesize    
    w = int(math.sqrt(filesize))
    f = open(filename,"rb")
    byte = f.read(1)
    pixelarray = []
    rowarray = []
    row,col = 0,0
    while byte != "":
        byte = f.read(1)        
        print byte
        r,g,b = (byte & 0b11000000),(byte & 0b00111000),(byte & 0b00000111)
        rowarray.append(r)
        col += 1
        if (col == width -1):
            col = 0
            rowarray=[]



def main(argv):
    filename = argv[1]
    encode_to_image(filename)

if __name__=="__main__":
    print "calling main"
    main(sys.argv)
