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


class Keyword_Entity:
    def __init__(self, label=None, stopsReferencing=None):
        self.__label = label
        self.__stopsReferencing = stopsReferencing if stopsReferencing is not None else []

with ExifToolHelper() as et:
    for files in os.listdir("fileInputs/"):
        filePath = os.path.join("fileInputs/" + files)
        for d in et.get_tags([filePath], ["Keywords"]):
            for k, v in d.items():
                print(f"Dict: {k} = {v}")