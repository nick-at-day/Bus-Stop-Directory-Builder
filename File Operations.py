import re
import os
import json
from pathlib import Path
from exiftool import ExifToolHelper
from pprint import pprint

class Photo_Entity:
    def __init__(self, stopNumber=None, stopKeywords=None, index=None):
        self.__stopNumber = stopNumber
        self.__keywords = stopKeywords if stopKeywords is not None else []
        self.__index = index

    def getStopNumber(self):
        return self.__stopNumber

    def addKeywords(self, keyword):
        if keyword not in self.__keywords:
            self.__keywords.append(keyword)

    def getKeywordAtIndex(self, index):
        return self.__keywords[index]
    
    def getAllKeywords(self): 
        return self.__keywords
    
    def getNumberOfKeys(self):
        return len(self.__keywords)
    
    def returnKeywordStopNumberPair(self):
        return [[kw, self.__stopNumber] for kw in self.__keywords]
    
    def toDict(self):
        return {
            "Stop Number": self.__stopNumber,
            "keywords": self.__keywords             
        }
    @classmethod
    def dumpToJson(cls, photos, filename="keyList.json"):
        allData = [photo.toDict() for photo in photos]
        with open(filename, "w") as o:
            json.dump(allData, o, indent=4)



class Keyword_Entity:
    def __init__(self, label=None, stopsReferencing=None):
        self.__label = label
        if stopsReferencing is None: 
            self.__stopsReferencing = []
        elif isinstance(stopsReferencing,list):
            self.__stopsReferencing = stopsReferencing
        else:
            self.__stopsReferencing = [stopsReferencing]

    def returnStops(self):
        return self.__stopsReferencing

    def getStopsFromKeyword(self):
        if isinstance(self.__stopsReferencing, str):
            self.__stopsReferencing = [self.__stopsReferencing]
        allStops = []
        for stops in self.__stopsReferencing:
            allStops.append(stops)
        return f"Stops referencing {self.__label}: {allStops}"
    
    def addStop(self, stop):
        if stop not in self.__stopsReferencing:
            self.__stopsReferencing.append(stop)

photos = []

with ExifToolHelper() as et:
    for files in os.listdir("fileInputs/"):
        filePath = os.path.join("fileInputs/" + files)
        fileName = os.path.splitext(files)
        for d in et.get_tags([filePath], ["IPTC:Keywords"]):
            keywords = d.get("IPTC:Keywords", [])
            if isinstance(keywords, str):
                keywords = [keywords]
            fileName = fileName[0]
            kw_clean = []
            for kw in keywords:
                if kw=="onPage":
                    break
                if kw == "edited":
                    break
                kw_clean.append(kw.replace("_",""))
            photos.append(Photo_Entity(fileName,kw_clean))

Photo_Entity.dumpToJson(photos)

# for localKeys in photos:
#     print(localKeys.getAllKeywords()) # Making sure I can get all local keys out of one file

all_keys = set() # note that the set is a built-in method for ensuring uniqueness in a list

for k in photos:
    for keyword in k.getAllKeywords():
        all_keys.add(keyword)

keyDict = {} 


for k in photos:
    for keyword, stopNum in k.returnKeywordStopNumberPair():
        if keyword not in keyDict:
            keyDict[keyword] = (Keyword_Entity(keyword, stopNum))
            print("New keyword created:", keyword)
            keyDict[keyword].addStop(stopNum)
        else: 
            keyDict.get(keyword).addStop([stopNum])
            print("Added to existing)")


for keys in keyDict:
    print(keyDict[keys].getStopsFromKeyword())