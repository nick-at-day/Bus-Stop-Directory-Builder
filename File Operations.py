import re
import os
from pathlib import Path
from exiftool import ExifToolHelper


class Photo_Entity:
    def __init__(self, stopNumber=None, stopKeywords=None, index=None):
        self.__stopNumber = stopNumber
        self.__keywords = stopKeywords if stopKeywords is not None else []
        self.__index = index

    def addKeywords(self, keyword):
        if keyword not in self.__keywords:
            self.__keywords.append(keyword)

    def getKeywordAtIndex(self, index):
        return self.__keywords[index]
    
    def getAllKeywords(self):
        return self.__keywords
    
    def getNumberOfKeys(self):
        return len(self.__keywords)
    
    def returnStopNumberKeywordPair(self):
        return [[self.__stopNumber, kw] for kw in self.__keywords]


class Keyword_Entity:
    def __init__(self, label=None, stopsReferencing=None):
        self.__label = label
        self.__stopsReferencing = stopsReferencing if stopsReferencing is not None else []

    def getStopsFromKeyword(self):
        return self.__stopsReferencing

photos = []

with ExifToolHelper() as et:
    for files in os.listdir("fileInputs/"):
        filePath = os.path.join("fileInputs/" + files)
        for d in et.get_tags([filePath], ["IPTC:Keywords"]):
            keywords = d.get("IPTC:Keywords", [])
            if isinstance(keywords, str):
                keywords = [keywords]
            fileName = d["SourceFile"]
            kw_clean = []
            for kw in keywords:
                if kw=="onPage":
                    break
                if kw == "edited":
                    break
                kw_clean.append(kw.replace("_",""))
            photos.append(Photo_Entity(fileName,kw_clean))


# for localKeys in photos:
#     print(localKeys.getAllKeywords())

all_keys = set()

for k in photos:
    for keyword in k.getAllKeywords():
        all_keys.add(keyword)

keyDict = []

for keys in all_keys:
    keyDict.append(Keyword_Entity(keys, ""))

print(keyDict[1])

# for k in photos:
#     print(k.getAllKeywords())