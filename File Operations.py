import os
import json
from pathlib import Path
from exiftool import ExifToolHelper
from itertools import zip_longest
import datetime
import shutil
from pprint import pprint

sourceFilepath = "/Users/nicholasseitz/Documents/Nicholas Seitz Vault/🚏 RVA Bus Stops/Stops, Photos, and Keywords/"
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
    nowString = now.strftime("%Y-%m-%d %H %M %S")

    backupSubdir = os.path.join(backupDir, f"{nowString}_Backup")
    os.makedirs(backupSubdir, exist_ok=True)

    for filename in os.listdir(sourceFilepath):
        if filename.lower().endswith(".md"):
            src = os.path.join(sourceFilepath, filename)
            dst = os.path.join(backupSubdir, filename)
            with open(src, "r", encoding="utf-8") as f:
                existingFileDict[filename.lower()] = f.read()
            shutil.copy2(src, dst)   # copy2 preserves metadata

    print(f"Backup complete: {backupSubdir}")

    with ExifToolHelper() as et: # Metadata parsing function
        for files in os.listdir(sourceFilepath):
            filePath = os.path.join(sourceFilepath, files)
            fileName = os.path.splitext(files)
            if ".jpg" in files:
                for d in et.get_tags([filePath], ["IPTC:Keywords", "IPTC:Caption-Abstract", "EXIF:DateTimeOriginal"]):
                    keywords = d.get("IPTC:Keywords", [])
                    dateTime = d.get("EXIF:DateTimeOriginal", "")
                    index = int(d.get("IPTC:Caption-Abstract", ""))
                    fullDate =  datetime.datetime.strptime(dateTime, "%Y:%m:%d %H:%M:%S")
                    if isinstance(keywords, str):
                            if keywords.lower().startswith("onpage"):
                                keywords = []
                            else:
                                keywords = [keywords.title()]
                    fullKeys = []
                    for kw in keywords:
                        if kw in ("onPage", "Edited", "") or "_" in kw:
                            continue
                        else:
                            fullKeys.append(kw.title())
                    photos[fileName[0]] = (Photo_Entity(stopNumber=fileName[0],stopKeywords=fullKeys, dateCreated=fullDate, index=index))
            else:
                continue

    for k in photos.values(): # Create list of all keywords in photos
        for keyword in k.getAllKeywords():
            all_keys.add(keyword.title())

    for k in photos.values(): # Create keyword objects dictionary or append keywords to existing objeect
            for keyword, stopNum in k.returnKeywordStopNumberPair():
                if keyword not in keyDict:
                    keyDict[keyword] = (Keyword_Entity(keyword.title(), stopNum)) # Change this to .title() when we're ready to rock :O 
                else: 
                    keyDict.get(keyword).addStop(stopNum)


    for files in os.listdir(sourceFilepath): # Ingest existing writing for stop files
        filepath = os.path.join(sourceFilepath, files)
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
                except Exception as e:
                    print(f"Stop number: {baseStop} is not in collection, {e}")

        elif ".md" in files: # Keyword file ingest
            baseKW = files[:-3]
            with open(filepath, "r") as f:
                noteText = []
                footnoteText = []
                for lines in f.read().splitlines():
                    if lines.strip().startswith((f"*[[", "![[", "# ", "## Stops with keyword {baseKW}", "*No stops currently reference this keyword*", "## Footnotes")):
                        continue 
                    if lines.strip():
                        if lines.strip().startswith("[^"):
                            footnoteText.append(lines)
                        else:
                            noteText.append(lines)
                try: 
                    keyDict[baseKW.title()].ingestWriting(noteText, footnoteText)
                except:
                    keyDict[baseKW.title()] = (Keyword_Entity(label=baseKW.title(), kwWriting=noteText, kwFootnote=footnoteText))
                    print (f"Keyword: {baseKW} does not appear in collection, creating empty keyword")

            
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

    fileGenerations = {}

    for p in photos.values(): # Generate photo files
        filename = f"Stop Number {p.stopNumber}.md"
        fileLines = []
        adjStops = get_neighbors(photos, p.stopNumber)
        newLine = 0
        if adjStops[0]:
            fileLines.append(f"Previous stop: [[Stop Number {adjStops[0]}]]")
            newLine = 1
            if adjStops[1]:
                fileLines.append("\n")
        if adjStops[1]:
            fileLines.append(f"Next stop: [[Stop Number {adjStops[1]}]]")
            newLine = 1
        if newLine == 1:
            fileLines.append("\n\n")
        fileLines.append(f"![[{p.getStopNumber()}.jpg]]\n\n")
        fileLines.append(f"## Notes\n\n")
        for ps in p.getPhotoWriting():
            fileLines.append(f"{ps}\n\n")
        fileLines.append(f"## Keywords\n\n")
        for kw in p.getAllKeywords():
            fileLines.append(f"- [[{kw}]]\n")
        if p.getFootnotes():
            fileLines.append("\n## Footnotes and Miscellany\n\n")
            for fn in p.getFootnotes():
                fileLines.append(f"{fn}\n\n")
        fileGenerations[filename] = "".join(fileLines).rstrip("\n")

    for k in keyDict.values(): # Write keyword files
        filename = f"{k.keywordLabel}.md"
        fileLines = []
        fileLines.append(f"# Stops with keyword {k.keywordLabel}\n\n")
        if not k.returnStops():
            fileLines.append("*No stops currently reference this keyword*\n\n")
        for a,b in zip_longest(k.getKeywordWriting(), k.returnStops(), fillvalue=""):
            if a:
                fileLines.append(str(a) + "\n\n")
            if b:
                fileLines.append(f"![[{str(b)}.jpg]]\n*[[Stop Number {str(b)}]]*\n\n")
        if k.getFootnotes():
            fileLines.append("\n## Footnotes and Miscellany\n\n")
            for fn in k.getFootnotes():
                fileLines.append(f"{fn}\n\n")
        fileGenerations[filename] = "".join(fileLines).rstrip("\n")

    # initialize empty lists to receive the files sorted into different categories.
    # used to both write the changelog and sort / maintain the backup directory.

    newfiles = []
    deletedLines = []
    addedLines = []
    moddedFile = []

    deletedLinesLength = {}
    addedLinesLength = {}

    for filename, newContents in fileGenerations.items():
        filepath = os.path.join(sourceFilepath, filename)
        oldContents = existingFileDict.get(filename.lower())           
        if oldContents == newContents:
            continue
        else:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(newContents)
            if oldContents is None:
                newfiles.append(filename)
            elif len(oldContents.splitlines()) > len(newContents.splitlines()):
                deletedLines.append(filename)
                deletedLinesLength[filename] = len(oldContents.splitlines()) - len(newContents.splitlines())
            elif len(oldContents.splitlines()) < len(newContents.splitlines()):
                addedLines.append(filename)
                addedLinesLength[filename] = len(newContents.splitlines()) - len(oldContents.splitlines())
            else:
                moddedFile.append(filename)

    def appendFiles(files):
        return "".join(f"{f}\n" for f in files)
    
    def addCountedLines(files):
        output = []
        for x in files:
            output.append(f"{x:<35} {addedLinesLength.get(x):>3} line(s) added\n")
        return "".join(output).rstrip("\n")
    
    def addSubstractedLines(files):
        output = []
        for x in files:
            output.append(f"{x:<35} {deletedLinesLength.get(x):>3} line(s) removed\n")
        return "".join(output).rstrip("\n")

    def createChangelog():
        fileLines = []
        fileLines.append(f"Changelog for {nowString}\n\n== New Files ==\n\n")
        fileLines.append(appendFiles(newfiles) + "\n\n")
        fileLines.append("== Added Lines ==\n\n")
        fileLines.append(addCountedLines(addedLines) + "\n\n")
        fileLines.append("== Deleted Lines ==\n\n")
        fileLines.append(addSubstractedLines(deletedLines) + "\n\n")
        fileLines.append("== Modded Lines ==\n\n")
        fileLines.append(appendFiles(moddedFile) + "\n\n")
        fileContents = "".join(fileLines).rstrip("\n")
        with open(f"{backupSubdir}/Changelog.txt", "w") as f:
            f.write(fileContents)
    
    def organize_backup(): # Currently, the conly complete chatGPT generated function because I was getting lazy at the end of developing this
        # Could be worth studying this I guess, might be a good point to jump off of for refactoring the above changelog file generator
        # and a general reference for file directory operations.

        categories = {
            "Added_Lines": addedLines,
            "Deleted_Lines": deletedLines,
            "Modified_Files": moddedFile,
        }

        # Make subfolders for categories
        for cat in categories:
            os.makedirs(os.path.join(backupSubdir, cat), exist_ok=True)

        # Move changed files into their categories
        for cat, filelist in categories.items():
            for filename in filelist:
                src = os.path.join(backupSubdir, filename)
                dst = os.path.join(backupSubdir, cat, filename)
                if os.path.exists(src):   # only move if backup copy exists
                    shutil.move(src, dst)

        # Delete leftover (unchanged) .md files from backup root
        for filename in os.listdir(backupSubdir):
            filepath = os.path.join(backupSubdir, filename)
            if filename.endswith(".md") and os.path.isfile(filepath):
                os.remove(filepath)
    
    createChangelog()
    organize_backup()

    # File comparator cleanup:
        # Iterate through markdown files in backup directory to list
        # Itereate through now existing files in live directory to list
        # compare differences using import difflib 
        # collect lines changed, added, unchanged, and new files

if __name__ == "__main__":
    main()