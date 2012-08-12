from flask import Flask, request, redirect, url_for, send_file
from werkzeug import secure_filename

from uploaders.Uploader import ImageUploader
from uploaders.Uploader import PastebinUploader

import os
import math
import random
import json
import uuid
import StringIO

import urllib

UPLOAD_FOLDER = '/home/thirtyseven/projects/ScrewTheCloud/BackEnd/store'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

uploaders = {}

class Uploader():
    dataStore = []
    
    def upId(self):
        return 'ua'
    
    def upload_data(self, data):
        self.dataStore.append(data)
        return (len(self.dataStore)-1)
    
    def retrieve_data(self, identifier):
        identifier = int(identifier)
        return self.dataStore[identifier]
    
    def getEmbeddableContent(self):
        return "google.com"
    
class UploaderB():
    dataStore = []
    
    def upId(self):
        return 'ub'
    
    def upload_data(self, data):
        self.dataStore.append(data)
        return (len(self.dataStore)-1)
    
    def retrieve_data(self, identifier):
        identifier = int(identifier)
        return self.dataStore[identifier]
    
    def getEmbeddableContent(self):
        return "bing.com"
    
img_uploader = ImageUploader()
pb_uploader = PastebinUploader()
        
uploaders[img_uploader.upId()] = img_uploader
uploaders[pb_uploader.upId()] = pb_uploader

#uploaders["ub"] = UploaderB()
#uploaders["ua"] = Uploader()

class DefaultSplitStrategy():
    _numSplits = 0
    _services = []
    _size = 0
    _total_size = 0
    
    def __init__(self, number_of_splits, services, total_size):
        self._numSplits = number_of_splits
        self._services = services
        self._size = total_size
        self._total_size = total_size
        
    # Return data in the format:
    # { "size": XXX // Number of bytes of the next split
    #   "service: XXX // Which service to use
    # }
    def get_next(self):
        if self._size <= 0:
            return None
            
        ret = {}
        
        if self._size < self._total_size/self._numSplits:
            ret["size"] = self._size
            self._size = 0
        else:
            proc_size = min(self._size, math.ceil(self._total_size/self._numSplits))
            next_size = random.randint(int(proc_size/2), int(proc_size))
            ret["size"] = next_size
        
            self._size -= next_size
        
        service = self._services[random.randint(0, len(self._services)-1)]
        ret["service"] = service
        return ret
        
'''
dss = DefaultSplitStrategy(5, ["sa", "sb", "sc"], 4391)

ssize = dss.get_next()
recomp_size = 0

while ssize is not None:
    recomp_size += ssize["size"]
    print str(ssize["size"]) + "//" + str(ssize["service"])
    ssize = dss.get_next()
    
print "Recomp Size: " + str(recomp_size)
'''

def list_to_array(inpList):
    retArr = []
    
    for inpKey in inpList:
        retArr.append(inpList[inpKey])
        
    return retArr

def get_random_id():
    return ''.join([x for x in str(uuid.uuid4()) if x is not '-'])

class ScrewCloud():
    stash = {}
    
    def encode(self, fileData):
        return fileData
    
    def upload(self, fileData, fileName, fileType):
        global uploaders
        splitSummary = []
        
        identifier = ""
            
        # Now we essentially have a list of bytes, we need to split and save
        fileData = screwCloud.encode(fileData)
          
        dss = DefaultSplitStrategy(2, list_to_array(uploaders), len(fileData))
        
        prev_offset = 0
        next_split = dss.get_next()
            
        while next_split is not None:
            uploader = next_split["service"]
            #print prev_offset, prev_offset + next_split["size"]
            
            chunk = fileData[prev_offset:prev_offset + next_split["size"]]
            upload_id = uploader.upload_data(chunk)
            
            identifier += uploader.upId() + str(upload_id) + ";"
            
            splitSummary.append({
                "ratio": float(len(chunk))/float(len(fileData)),
                "service": uploader.upId(),
                "embeddable": uploader.getEmbeddableContent()
            })
            
            prev_offset += next_split["size"]
            next_split = dss.get_next()
            
        # Remove the trailing semi-colon
        
        stash_id = get_random_id()
        self.stash[stash_id] = {"identifier": identifier[0:-1], "type": fileType, "name": fileName}
        return (identifier[0:-1], stash_id, splitSummary)
    
    def unstash(self, stash_id):
        return self.stash[stash_id]
    
    def retrieve(self, identifier):
        global uploaders
        
        print identifier
        parts = identifier.split(";")
        fileData = []
        
        for part in parts:
            uploader_id = part[0:2]
            part_id = part[2:]
            
            uploader = uploaders[uploader_id]
            fileDatum = uploader.retrieve_data(part_id)
            fileData += fileDatum
            
        return fileData
    
screwCloud = ScrewCloud()

def file_to_byte_array(fileName):
    fileHandle = open(fileName, "rb")
    fileData = []
            
    try:
        byte = fileHandle.read(1)
                
        while byte != "":
            fileData.append(byte)
            byte = fileHandle.read(1)
    finally:
        fileHandle.close()
        
    return fileData

'''
fileData = file_to_byte_array("/home/thirtyseven/dump_file")
ident = screwCloud.upload(fileData, "something", "app/binary")
screwCloud.retrieve(ident)
'''

@app.route("/upload", methods=['GET', 'POST'])
def upload():    
    if request.method == 'POST':
        file = request.files['file']
        redir_request = None
        
        try:
            redir_request = request.args['redirect']
        finally:
            print 'HERE'
        
        if file:
            filePath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            fileUpHeaders = file.headers._list
            contentType = ''
            
            for fileUpHeader in fileUpHeaders:
                if fileUpHeader[0] == 'Content-Type':
                    contentType = fileUpHeader[1]
                    
            file.save(filePath)
            
            fileData = file_to_byte_array(filePath)
            identData = screwCloud.upload(fileData, file.filename, contentType)
            
            if redir_request is not None:
                payload = json.dumps({"identifier": identData[0], "stashId": identData[1], "splitSummary": identData[2]})
                payload = urllib.quote(payload)
                
                redir_request += "?payload=" + payload
                return redirect(redir_request)
            
            return json.dumps({"identifier": identData[0], "stashId": identData[1]})
    
    return '''
    <!doctype html>
    <title>Upload new file</title>
    <h1>Upload new file</h1>
    
    <form action="" method=post enctype=multipart/form-data>
    <p>
     <input type=file name=file />
     <input type=submit value=Upload />
    </p>
    </form>
    '''
    
@app.route("/retrieve", methods=['GET'])
def retrieve():
    stash_id = None
    identifier = None
    headers = {}
    
    fileType = ""
    fileName = ""
    
    try:
        stash_id = request.args['stash_id']
    except:
        None
        
    try:
        identifier = request.args['identifier']
    except:
        None
    
    if stash_id is not None:
        stashSet = screwCloud.unstash(str(stash_id))
        identifier = stashSet["identifier"]
        fileType = stashSet["type"]
        fileName = stashSet["name"]
        
    fileData = screwCloud.retrieve(identifier)
    fileResponse = StringIO.StringIO()
    
    byteCount = 0
    
    for fileDatum in fileData:
        fileResponse.write(fileDatum)
        
    fileResponse.seek(0)
    
    return send_file(fileResponse, attachment_filename=fileName, as_attachment=True)
    
if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
