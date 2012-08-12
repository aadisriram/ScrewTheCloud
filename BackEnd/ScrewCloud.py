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
        return 'pb'
    
    def upload_data(self, data):
        self.dataStore.append(data)
        return (len(self.dataStore)-1)
    
    def retrieve_data(self, identifier):
        identifier = int(identifier)
        return self.dataStore[identifier]
    
    def get_embeddable_content(self, ident):
        return "google.com"
    
class UploaderB():
    dataStore = []
    
    def upId(self):
        return 'im'
    
    def upload_data(self, data):
        self.dataStore.append(data)
        return (len(self.dataStore)-1)
    
    def retrieve_data(self, identifier):
        identifier = int(identifier)
        return self.dataStore[identifier]
    
    def get_embeddable_content(self, ident):
        return "bing.com"
    
class UploaderB():
    dataStore = []
    
    def upId(self):
        return 'pc'
    
    def upload_data(self, data):
        self.dataStore.append(data)
        return (len(self.dataStore)-1)
    
    def retrieve_data(self, identifier):
        identifier = int(identifier)
        return self.dataStore[identifier]
    
    def get_embeddable_content(self, ident):
        return "yahoo.com"
    
img_uploader = ImageUploader()
pb_uploader = PastebinUploader()
        
#uploaders[img_uploader.upId()] = img_uploader
#uploaders[pb_uploader.upId()] = pb_uploader

uploaders["pb"] = UploaderB()
uploaders["im"] = Uploader()
uploaders["pc"] = Uploader()

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
        chunkList = []
        
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
            chunkList.append((chunk, uploader.upId()))
            
            upload_id = uploader.upload_data(chunk)
            
            identifier += uploader.upId() + str(upload_id) + ";"
            
            splitSummary.append({
                "r": "%.2f" % (float(len(chunk))/float(len(fileData))),
                "s": uploader.upId(),
                "e": uploader.get_embeddable_content(upload_id)
            })
            
            prev_offset += next_split["size"]
            next_split = dss.get_next()
        
        i = 0
        chunkGroups = []
        chunkUploaders = []
        
        while True:
            if i >= len(chunkList):
                break
                
            if i < len(chunkList) - 2 or i == len(chunkList) - 2:
                # There is a group possible
                chunkGroups.append((chunkList[i][0], chunkList[i+1][0], i, i+1))
                chunkUploaders += [(chunkList[i][1], chunkList[i+1][1])]
                i = i + 2
            elif i == len(chunkList) - 1:
                chunkGroups.append((chunkList[i][0], chunkList[0][0], i, 0))
                chunkUploaders += [(chunkList[i][1], chunkList[0][1])]
                i = i + 1
            
        paritySet = []
        identifier += "|"
        
        for chunkGroup in chunkGroups:
            lower = 0
            higher = 1
            
            paritySet.append({"sz": 0, "parity_data": []})
            
            if len(chunkGroup[0]) < len(chunkGroup[1]):
                lower = 0
                higher = 1
            else:
                lower = 1
                higher = 0
                
            paritySet[-1]["size"] = len(chunkGroup[lower])
            paritySet[-1]["parity_for"] = (chunkGroup[2], chunkGroup[3])
                
            for i in range(0, len(chunkGroup[higher][0]) - len(chunkGroup[lower][0])):
                chunkGroup[lower][0] += [chr(0)]
                
            for i in range(0, len(chunkGroup[lower][0])):
                paritySet[-1]["parity_data"].append(ord(chunkGroup[lower][0][i]) ^ ord(chunkGroup[higher][0][i]))
                
        i = 0
        
        for parityChunk in paritySet:
            print '-->'
            usedUploaders = chunkUploaders[i]
            candidates = [upl for upl in uploaders if upl not in usedUploaders]
            
            if len(candidates) is not 0:
                upldr = uploaders[candidates[random.randint(0, len(candidates)-1)]]
                upload_id = uploader.upload_data(parityChunk["parity_data"])
                
                identifier += upldr.upId() + str(upload_id) + ";"
                
                splitSummary.append({
                    "p": True,
                    "sz": parityChunk["size"],
                    "s": upldr.upId(),
                    "e": uploader.get_embeddable_content(upload_id)
                })
        
        # Remove the trailing semi-colon
        
        stash_id = get_random_id()
        self.stash[stash_id] = {"identifier": identifier[0:-1], "type": fileType, "name": fileName}
        return (identifier[0:-1], stash_id, splitSummary)
    
    def unstash(self, stash_id):
        return self.stash[stash_id]
    
    def retrieve(self, identifier):
        global uploaders
        
        print identifier
        identifier = ''.join(identifier.split("|")[0][0:-1])
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
        except:
            print 'IGNORING'
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
            
            return json.dumps({"identifier": identData[0], "stashId": identData[1], "splitSummary": identData[2]})
    
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
