import re
import os
import json
from pathlib import Path
from exiftool import ExifToolHelper
from pprint import pprint
from itertools import zip_longest
import lorem
import random

sourceFilepath = "/Users/nicholasseitz/Pictures/Update Directory/"

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
    def dumpToJson(cls, photos, filename="stopList.json"):
        allData = [photo.toDict() for photo in photos.values()]
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

    def getLabel(self):
        return self.__label

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

    def toDict(self):
        return {
            "Keyword": self.__label,
            "Stops": self.__stopsReferencing
        }

    @classmethod
    def dumpKeysToJson(cls, keys, filename="keyList.json"):
        allData = [photo.toDict() for photo in keys.values()]
        with open(filename, "w") as o:
            json.dump(allData, o, indent=4)

photos = {}
all_keys = set()
keyDict = {} 

with ExifToolHelper() as et:
    for files in os.listdir(sourceFilepath):
        filePath = os.path.join(sourceFilepath + files)
        fileName = os.path.splitext(files)
        if ".jpg" in files:
            for d in et.get_tags([filePath], ["IPTC:Keywords"]):
                keywords = d.get("IPTC:Keywords", [])
                if isinstance(keywords, str):
                    keywords = [keywords]
                fullKeys = []
                for kw in keywords:
                    if kw in ("onPage", "Edited") or "_" in kw:
                        continue
                    else:
                        fullKeys.append(kw)
                photos[fileName] = (Photo_Entity(fileName[0],fullKeys))
            else:
                continue

for k in photos.values():
    for keyword in k.getAllKeywords():
        all_keys.add(keyword)

for k in photos.values():
    for keyword, stopNum in k.returnKeywordStopNumberPair():
        if keyword not in keyDict:
            keyDict[keyword] = (Keyword_Entity(keyword, stopNum))
            print("New keyword created:", keyword)
            # keyDict[keyword].addStop(stopNum)
        else: 
            keyDict.get(keyword).addStop(stopNum)
            print("Added to existing)")

Photo_Entity.dumpToJson(photos)
Keyword_Entity.dumpKeysToJson(keyDict)

for p in photos.values():
    ceil = random.randint(5,15)
    loremText = []
    while ceil >= 0:
        loremText.append(lorem.sentence()*random.randint(3,12))
        ceil -= 1
    with open(f"{sourceFilepath}Stop Number {p.getStopNumber()}.md", "w") as f:
        f.write(f"# Stop {p.getStopNumber()}\n\n")
        f.write(f"![[{p.getStopNumber()}.jpg]]\n\n")
        f.write(f"## Notes\n\n\n## Keywords\n\n")
        for kw in p.getAllKeywords():
            f.write(f"- [[{kw}]]\n")

for k in keyDict.values():
    ceil = random.randint(5,15)
    loremText = []
    while ceil >= 0:
        loremText.append(lorem.sentence()*random.randint(3,12))
        ceil -= 1
    with open(f"{sourceFilepath}{k.getLabel()}.md", "w") as f:
        f.write(f"# Stops referencing keyword {k.getLabel()}\n\n")
        for a,b in zip_longest(loremText, k.returnStops(), fillvalue=""):
            if a:
                f.write(str(a) + "\n\n")
            if b:
                f.write(f"![[{str(b)}.jpg]]\n[[Stop Number {str(b)}]]\n\n")