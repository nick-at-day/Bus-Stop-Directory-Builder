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
        return [[kw, self.__stopNumber] for kw in self.__keywords]


class Keyword_Entity:
    def __init__(self, label=None, stopsReferencing=None):
        self.__label = label
        self.__stopsReferencing = stopsReferencing if stopsReferencing is not None else []

    def getStopsFromKeyword(self):
        if isinstance(self.__stopsReferencing, str):
            self.__stopsReferencing = [self.__stopsReferencing]
        allStops = []
        for stops in self.__stopsReferencing:
            allStops.append(stops)
        return f"Stops referencing: {self.__label}: {allStops}"
    
    # def addStopsToKeyword(self, kw, stops):
    #     if kw = 

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


# for localKeys in photos:
#     print(localKeys.getAllKeywords()) # Making sure I can get all local keys out of one file

all_keys = set() # note that the set is a built-in method for ensuring uniqueness in a list

for k in photos:
    for keyword in k.getAllKeywords():
        all_keys.add(keyword)


# for keys in all_keys:
#     keyDict.append(Keyword_Entity(keys, "")) # initialize unique keyword entities with empty stop numbers



# print(keyDict[1]) # Making sure I can get Keyword objects out of the key dict

keyDict = [] # list of all keyword entities
all_keyStopPairs = []

for k in photos:
    for i in k.returnStopNumberKeywordPair():
        keyDict.append(Keyword_Entity(i[0],i[1])) # This is currently taking the unique list and pushing one keyword entity for every key / stop pair... There are 14 "fence" objects. Figure out how to check to see if the key already exists, then append, rather than creating new objects each time


for i in keyDict:
    print(i.getStopsFromKeyword()) 

# print(all_keyStopPairs)



# Possible solution to the appending stops problem:

# 1) Initialize all the empty keyword entities based on existing keyword
# 2) In a for each loop for every key/stop pair:
#     3) Iterate through all keyword_entities, calling a function that checks the label of each one
#     4) when the label is found within the keyDict list, call a function that appends the stop to that keyword entity
# 5) if the key/stop pair passes through the whole list of existing labels, create a new keyword entity with the key / stop pair