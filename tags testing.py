from exiftool import ExifToolHelper
import os
import pprint
import datetime

sourceFilepath = "/Users/nicholasseitz/Pictures/Update Directory/"
photos = {}

with ExifToolHelper() as et:
    for files in os.listdir(sourceFilepath):
        filePath = os.path.join(sourceFilepath + files)
        fileName = os.path.splitext(files)
        if ".jpg" in files:
            for d in et.get_tags([filePath], ["IPTC:Keywords", "IPTC:Caption-Abstract", "EXIF:DateTimeOriginal"]):
                keywords = d.get("IPTC:Keywords", [])
                index = d.get("IPTC:Caption-Abstract", "")
                dateTime = d.get("EXIF:DateTimeOriginal", "")
                fullDate = datetime.datetime(
                    int(dateTime[:4]),
                    int(dateTime[5:7]),
                    int(dateTime[8:10]),
                    int(dateTime[11:13]),
                    int(dateTime[14:16]),
                    int(dateTime[17:19])
                )
                if isinstance(keywords, str):
                    keywords = [keywords]
                fullKeys = []
                for kw in keywords:
                    if kw in ("onPage", "Edited") or "_" in kw:
                        continue
                    else:
                        fullKeys.append(kw)
                print(index)
                # photos[fileName[0]] = (Photo_Entity(stopNumber=fileName[0],stopKeywords=fullKeys))
            else:
                continue