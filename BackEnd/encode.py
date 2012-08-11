import sys
import struct
import os
import png
import math
import binascii
import cStringIO
import pycurl
import urllib

def encode_to_image(filename):        
    filesize = os.path.getsize(filename)
    print "filename",filename,"filesize",filesize    
    width = int(math.sqrt(filesize)) # try to keep the image almost square
    f = open(filename,"rb")
    byte = f.read(1)
    pixelarray = []
    rowarray = []
    row,col = 0,0
    while byte != "":        
        byte = int(binascii.hexlify(byte), 16)            
        # convert each byte to pixels, using 3 bits for B and G, and 2 bits for R
        pixel = [(byte & 0b11000000) >> 6,(byte & 0b00111000) >> 3,(byte & 0b00000111)]
        rowarray.extend(pixel)        
        col += 1
        if (col == width):
            col = 0                        
            pixelarray.append(rowarray)
            rowarray=[]
        byte = f.read(1)
    while (col < width):
        # pad the rest of the last row with black
        rowarray.extend([0,0,0])
        col +=1
    pixelarray.append(rowarray)
    png.from_array(pixelarray,'RGB').save(filename[:-4]+".png")
    f.close()
        
def decode_from_image(image,filename):
    f = open(filename,"wb")
    print "trying to open",image
    image_info =  png.Reader(image).asRGB()
    print image_info      
    pixeldata = png.Reader(image).asRGB()[2]
    for row in pixeldata:        
        for i in range(image_info[0]):                        
            byte = (row[i*3] << 6) + (row[i*3 + 1] << 3) +row[i*3 + 2]                                  
            f.write(chr(byte))            
    f.close()

def upload_to_imgur(image):
    import pycurl
    response = cStringIO.StringIO()
    c = pycurl.Curl()
    values = [
        ("key", "e14dbae25d7a3475a9df7ddb7a803210"),
        ("image", (c.FORM_FILE, image))]        
    c.setopt(c.URL, "http://api.imgur.com/2/upload.xml")
    c.setopt(c.HTTPPOST, values)   
    c.setopt(c.WRITEFUNCTION, response.write)
    c.perform()
    c.close()
    xml_str = response.getvalue()    
    link = xml_str[xml_str.find("<original>")+10:xml_str.find("</original>")]
    return link

def download_from_imgur(url):
    fname = "./downloaded_image.png"
    urllib.urlretrieve( url, fname )

def main(argv):
    filename = argv[1]
    encode_to_image(filename)
    decode_from_image(filename[:-4]+".png","result.txt")
    link = upload_to_imgur(filename[:-4]+".png")
    download_from_imgur(link)

if __name__=="__main__":
    print "calling main"
    main(sys.argv)

