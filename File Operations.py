import os
import json
from pathlib import Path
from exiftool import ExifToolHelper
from itertools import zip_longest
import datetime
import shutil

sourceFilepath = "/Users/nicholasseitz/Pictures/Update Directory/"
backupDir = "/Users/nicholasseitz/Documents/BusStopDirectoryBackup/"

class Photo_Entity:
    def __init__(self, stopNumber=None, stopKeywords=None, photoWriting=None, index=None, dateCreated=None, photoFootnotes=None):
        self.stopNumber = stopNumber
        self.__keywords = stopKeywords if stopKeywords is not None else []
        self.__photoWriting = photoWriting if photoWriting is not None else []
        self.__dateCreated = dateCreated
        self.__photoFootnotes = photoFootnotes if photoFootnotes is not None else []
        self.index = index

    def getStopNumber(self):
        return self.stopNumber

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
        return [[kw, self.stopNumber] for kw in self.__keywords]
    
    def toDict(self):
        return {
            "Stop Number": self.stopNumber,
            "keywords": self.__keywords,
            "writing": self.__photoWriting,
            "Date Created": str(self.__dateCreated),
            "Index": self.index,
            "Footnotes": self.__photoFootnotes
        }
    
    def getFootnotes(self):
        return self.__photoFootnotes
    
    def ingestWriting(self, writing, footnoteText):
        self.__photoWriting = writing
        self.__photoFootnotes = footnoteText
    
    def getPhotoWriting(self):
        return self.__photoWriting
    
    @classmethod
    def dumpToJson(cls, photos, filename="stopList.json"):
        allData = [photo.toDict() for photo in photos.values()]
        with open(filename, "w") as o:
            json.dump(allData, o, indent=4)

    @classmethod
    def createIndexValues(cls, photos):
        pass

class Keyword_Entity:
    def __init__(self, label=None, stopsReferencing=None, kwWriting=None, kwFootnote=None):
        self.__kwWriting = kwWriting if kwWriting is not None else []
        self.__kwFootnote = kwFootnote if kwFootnote is not None else []
        self.keywordLabel = label
        if stopsReferencing is None: 
            self.__stopsReferencing = []
        elif isinstance(stopsReferencing,list):
            self.__stopsReferencing = stopsReferencing
        else:
            self.__stopsReferencing = [stopsReferencing]

    def returnStops(self):
        return self.__stopsReferencing

    def getLabel(self):
        return self.keywordLabel

    def getStopsFromKeyword(self):
        if isinstance(self.__stopsReferencing, str):
            self.__stopsReferencing = [self.__stopsReferencing]
        allStops = []
        for stops in self.__stopsReferencing:
            allStops.append(stops)
        return f"Stops referencing {self.keywordLabel}: {allStops}"
    
    def addStop(self, stop):
        if stop not in self.__stopsReferencing:
            self.__stopsReferencing.append(stop)

    def toDict(self):
        return {
            "Keyword": self.keywordLabel,
            "Stops": self.__stopsReferencing,
            "Writing": self.__kwWriting,
            "Footnotes": self.__kwFootnote
        }
    
    def ingestWriting(self, writing, footnoteText):
        self.__kwWriting = writing
        self.__kwFootnote = footnoteText
    
    def getFootnotes(self):
        return self.__kwFootnote
    
    def getKeywordWriting(self):
        return self.__kwWriting
 
    @classmethod
    def dumpKeysToJson(cls, keys, filename="keyList.json"):
        allData = [kw.toDict() for kw in keys.values()]
        with open(filename, "w") as o:
            json.dump(allData, o, indent=4)

def main():
    photos = {} # Dictionary with format "Stop name: <stop object>"
    all_keys = set() # All existing keywords
    keyDict = {} # Dictionary with format "Keyword: <keyword object>"
    existingFileDict = {}

    now = datetime.datetime.now()  
    nowString = now.strftime("%Y-%m-%d_%H%M%S")

    backupSubdir = os.path.join(backupDir, f"{nowString}_Backup")
    os.makedirs(backupSubdir, exist_ok=True)

    for filename in os.listdir(sourceFilepath):
        if filename.lower().endswith(".md"):
            src = os.path.join(sourceFilepath, filename)
            dst = os.path.join(backupSubdir, filename)
            with open(src, "r", encoding="utf-8") as f:
                existingFileDict[filename] = f.read()
            shutil.copy2(src, dst)   # copy2 preserves metadata

    print(f"Backup complete: {backupSubdir}")

    with ExifToolHelper() as et: # Metadata parsing function
        for files in os.listdir(sourceFilepath):
            filePath = os.path.join(sourceFilepath + files)
            fileName = os.path.splitext(files)
            if ".jpg" in files:
                for d in et.get_tags([filePath], ["IPTC:Keywords", "IPTC:Caption-Abstract", "EXIF:DateTimeOriginal"]):
                    keywords = d.get("IPTC:Keywords", [])
                    dateTime = d.get("EXIF:DateTimeOriginal", "")
                    index = int(d.get("IPTC:Caption-Abstract", ""))
                    fullDate =  datetime.datetime.strptime(dateTime, "%Y:%m:%d %H:%M:%S")
                    if isinstance(keywords, str):
                        keywords = [keywords]
                    fullKeys = []
                    for kw in keywords:
                        if kw in ("onPage", "Edited") or "_" in kw:
                            continue
                        else:
                            fullKeys.append(kw)
                    photos[fileName[0]] = (Photo_Entity(stopNumber=fileName[0],stopKeywords=fullKeys, dateCreated=fullDate, index=index))
                else:
                    continue

    for k in photos.values(): # Create list of all keywords in photos
        for keyword in k.getAllKeywords():
            all_keys.add(keyword)

    for k in photos.values(): # Create keyword objects dictionary or append keywords to existing objeect
            for keyword, stopNum in k.returnKeywordStopNumberPair():
                if keyword not in keyDict:
                    keyDict[keyword] = (Keyword_Entity(keyword, stopNum))
                else: 
                    keyDict.get(keyword).addStop(stopNum)


    for files in os.listdir(sourceFilepath): # Ingest existing writing for stop files
        filepath = os.path.join(sourceFilepath + files)
        if "Stop Number" in files: # Stop number ingest
            baseStop = files[12:]
            baseStop = baseStop[:-3]
            with open(filepath, "r") as f:
                noteText = []
                footnoteText = []
                appendText = 0
                in_section = False
                for lines in f.read().splitlines():
                    if lines.strip().startswith("## Notes"):
                        in_section = True
                        appendText = 1
                        continue 
                    if lines.strip().startswith("## Keywords"):
                        in_section = False
                        continue
                    if lines.strip().startswith("## Footnotes"):
                        in_section = True
                        appendText = 2
                        continue
                    if lines.strip() and in_section == True:
                        if appendText == 2:
                            footnoteText.append(lines)
                        elif appendText == 1:
                            noteText.append(lines)
                        else:
                            continue
                try:
                    photos[baseStop].ingestWriting(noteText, footnoteText)
                except:
                    print(f"Stop number: {baseStop} is not in collection")
        elif ".md" in files: # Keyword file ingest
            baseKW = files[:-3]
            with open(filepath, "r") as f:
                noteText = []
                footnoteText = []
                for lines in f.read().splitlines():
                    if lines.strip().startswith(("[[", "![", "#")):
                        continue 
                    if lines.strip():
                        if lines.strip().startswith("[^"):
                            footnoteText.append(lines)
                        else:
                            noteText.append(lines)
                try: 
                    keyDict[baseKW].ingestWriting(noteText, footnoteText)
                except:
                    keyDict[baseKW] = (Keyword_Entity(label=baseKW))
                    print (f"Keyword: {baseKW} does not appear in collection, creating empty keyword") # update this to be a bit safer... create a new keyword entity with the name and no stops, then add exception handling to the file writing class to add a "No stops referenced" message if there's nothing there.

            
    Photo_Entity.dumpToJson(photos)
    Keyword_Entity.dumpKeysToJson(keyDict)


    def get_neighbors(photos: dict, stop: str):
        ordered = sorted(photos.values(), key=lambda p: p.index)
        for i, photo in enumerate(ordered):
            if photo.stopNumber == stop:
                prev_photo = ordered[i - 1].stopNumber if i > 0 else None
                next_photo = ordered[i + 1].stopNumber if i < len(ordered) - 1 else None
                return [prev_photo, next_photo]
        return [None, None]

    for p in photos.values(): # Write photo files
        with open(f"{sourceFilepath}Stop Number {p.getStopNumber()}.md", "w") as f:
            f.write(f"# Stop {p.getStopNumber()}\n\n")
            adjStops = get_neighbors(photos, p.stopNumber)
            newLine = 0
            if adjStops[0]:
                f.write(f"Previous stop: [[Stop Number {adjStops[0]}]]")
                newLine = 1
                if adjStops[1]:
                    f.write("\n")
            if adjStops[1]:
                f.write(f"Next stop: [[Stop Number {adjStops[1]}]]")
                newLine = 1
            if newLine == 1:
                f.write("\n\n")
            f.write(f"![[{p.getStopNumber()}.jpg]]\n\n")
            f.write(f"## Notes\n\n")
            for ps in p.getPhotoWriting():
                f.write(f"{ps}\n\n")
            f.write(f"## Keywords\n\n")
            for kw in p.getAllKeywords():
                f.write(f"- [[{kw}]]\n")
            if p.getFootnotes():
                f.write("\n## Footnotes and Miscellany\n\n")
                for fn in p.getFootnotes():
                    f.write(f"{fn}\n\n")

    for k in keyDict.values(): # Write keyword files
        with open(f"{sourceFilepath}{k.getLabel()}.md", "w") as f:
            f.write(f"# Stops referencing keyword {k.getLabel()}\n\n")
            if not k.returnStops():
                f.write("*No stops currently reference this keyword*\n\n")
            for a,b in zip_longest(k.getKeywordWriting(), k.returnStops(), fillvalue=""):
                if a:
                    f.write(str(a) + "\n\n")
                if b:
                    f.write(f"![[{str(b)}.jpg]]\n[[Stop Number {str(b)}]]\n\n")
            if k.getFootnotes():
                f.write("\n## Footnotes and Miscellany\n\n")
                for fn in k.getFootnotes():
                    f.write(f"{fn}\n\n")

    newFileDict = {}

    for filename in os.listdir(sourceFilepath):
        if filename.endswith(".md"):
            filepath = os.path.join(sourceFilepath, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                contents = f.read()
            new_contents = contents.rstrip("\n")
            with open(filepath, "w") as f:
                f.write(new_contents)
            newFileDict[filename] = new_contents
    
    # File comparator cleanup:
        # Iterate through markdown files in backup directory to list
        # Itereate through now existing files in live directory to list
        # compare differences using import difflib 
        # collect lines changed, added, unchanged, and new files

if __name__ == "__main__":
    main()