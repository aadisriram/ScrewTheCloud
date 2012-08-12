import sys
import struct
import os
import png
import math
import binascii
import cStringIO
import pycurl
import urllib
import base64
from pastebin import PastebinAPI

class Uploader:        
    def upload_data(self,data):
        """
        data is an array of bytes
        """
        return None

    def retrieve_data(self,identifier):
        return None

    def upId(self):
        return None

    def get_embeddable_content(self,identifier):
        return None

class ImageUploader(Uploader):
    def upId(self):
        return "im"

    def upload_data(self,data):                        
        width = int(math.sqrt(len(data)))
        pixelarray = []
        rowarray = []
        row,col = 0,0               
        for byte in data:
            byte = int(binascii.hexlify(byte), 16)            
            # convert each byte to pixels
            pixel = [(byte & 0b11000000) >> 6,(byte & 0b00111000) >> 3,(byte & 0b00000111)]        
            rowarray.extend(pixel)        
            col += 1
            if (col == width):
                col = 0                        
                pixelarray.append(rowarray)
                rowarray=[]                
        while (col < width):
            # pad the rest of the last row with black
            rowarray.extend([0,0,0])
            col +=1
        pixelarray.append(rowarray)
        png.from_array(pixelarray,'RGB;3').save("tmp.png")        
        identifier = self.upload_to_imgur("tmp.png")        
        return identifier+':'+str(len(data))

    def upload_to_imgur(self,image_file):
        import pycurl
        response = cStringIO.StringIO()
        c = pycurl.Curl()
        values = [
            ("key", "e14dbae25d7a3475a9df7ddb7a803210"),
            ("image", (c.FORM_FILE, image_file))]
        c.setopt(c.URL, "http://api.imgur.com/2/upload.xml")
        c.setopt(c.HTTPPOST, values)   
        c.setopt(c.WRITEFUNCTION, response.write)
        c.perform()
        c.close()
        xml_str = response.getvalue()    
        link = xml_str[xml_str.find("<original>")+10:xml_str.find("</original>")]        
        return link[19:-4]

    def retrieve_data(self,identifier):
        filename = "./tmp2.png"
        img_id = identifier[:identifier.find(':')]        
        filesize = int(identifier[identifier.find(':')+1:])                        
        url = "http://i.imgur.com/"+img_id+".png"
        urllib.urlretrieve(url, filename)
        f = open("./tmp2.png","rb")         
        image_info =  png.Reader(filename).asRGB()        
        print image_info
        byte_array = []
        pixeldata = png.Reader(filename).asRGB()[2]
        print " in retrieve, filesize is",filesize
        exitflag = False
        for row in pixeldata:        
            if exitflag:
                break
            for i in range(image_info[0]):                        
                byte = (row[i*3] << 6) + (row[i*3 + 1] << 3) +row[i*3 + 2]                            
                byte_array.append(chr(byte))            
                if len(byte_array) == filesize:                    
                    exitflag = True
                    break
        f.close()
        print "in retrieve data, length of byte array",len(byte_array)
        return byte_array
    
    def get_embeddable_content(self,identifier):
        img_id = identifier[:identifier.find(':')]
        return "http://i.imgur.com/"+img_id+".png"

class PastebinUploader(Uploader):
    def upId(self):
        return "pb"

    def upload_data(self,data):
        string = ""
        for byte in data:
            string = string + str(byte)
        encoded = base64.b64encode(string)    
        return self.upload_to_pastebin(encoded)

    def upload_to_pastebin(self,text):
        api_dev_key =  '2a3df06fe524ed88d15b660ccdca21dc'
        api_paste_code = text
        paste_name = 'OpenHack2012'        
        pastebinObj = PastebinAPI()
        api_user_key = pastebinObj.generate_user_key(api_dev_key, "openhack2012", "yahoo")
        ret = pastebinObj.paste(api_dev_key, api_paste_code, api_user_key = api_user_key, paste_name = paste_name,
                                paste_format = None, paste_private = None,
                                paste_expire_date = None)        
        print ret,ret[20:]        
        return ret[20:]

    def retrieve_data(self,identifier):
        url = "http://pastebin.com/raw.php?i="+identifier        
        encoded_data= urllib.urlopen(url).read()
        return base64.b64decode(encoded_data)
    
    def get_embeddable_content(self,identifier):
        return "http://pastebin.com/raw.php?i="+identifier

        
def test_image_upload(filename):
    myImageUploader = ImageUploader()
    f = open(filename,"rb")    
    print "filesize",os.path.getsize(filename)
    byte = f.read(1)
    byte_array = []
    while byte!="":
        byte_array.append(byte)
        byte = f.read(1)
    print "length of byte array",len(byte_array)
    identifier = myImageUploader.upload_data(byte_array)    
    print "identifier",identifier
    byte_array = myImageUploader.retrieve_data(identifier)    
    print "retrieved byte array length",len(byte_array)
    f = open("./decoded.txt","wb")    
    for byte in byte_array:
        f.write(byte)
    f.close()
    
def test_pastebin_upload(filename):
    myPastebinUploader = PastebinUploader()
    f = open(filename,"rb")
    byte = f.read(1)
    byte_array = []
    while byte!="":
        byte_array.append(byte)
        byte = f.read(1)
    identifier = myPastebinUploader.upload_data(byte_array)
    print "identifier",identifier
    print myPastebinUploader.retrieve_data(identifier)

if __name__=="__main__":
    test_image_upload(sys.argv[1])
    
    
    
