import requests
from requests.auth import HTTPBasicAuth
import time
import json
import os, errno
import sys
import hashlib
import glob
import re

defaultURL = "https://e621.net/posts.json"
pastURL = ""
currentFolder = os.path.dirname(os.path.realpath(__file__))
apiKeyFile = currentFolder + os.sep + "apikey.txt"

absoluteLimit = 320
rateLimit = 1
lastTime = time.time()
lowestID = -1
stop = False

headers = {"User-Agent":"E6-Post-Downloader/3.0 (by jezzar on E621)"}

def rateLimiting():
    global lastTime
    timeTaken = time.time() - lastTime
    if timeTaken <= rateLimit:
        time.sleep(rateLimit-timeTaken)
    lastTime = time.time()
    
try:
    with open(apiKeyFile) as apiFile:
        apiKeys = apiFile.read().splitlines()
except FileNotFoundError:
    with open(apiKeyFile,"w") as apiFile:
        apiFile.write("user="+os.linesep+"api_key=")
    print("apikey.txt created - Add your username and API Key (https://e621.net/users/home -> Manage API Access) then restart")
    input()
    exit()

apiUser = apiKeys[0].split("=")[1]
apiKey = apiKeys[2].split("=")[1]

if apiUser == "" or apiKey == "":
    print("Please actually enter your username and API Key (https://e621.net/users/home -> Manage API Access)...")
    input()
    exit()

namingsw = str(input("what naming scheme would you like? (md5, tags(default))?\n"))
if namingsw.lower() != "md5":
    # set tag file naming default
    naming = "tags"
    # set how many general tags to write
    maxtags=input("Please select how many general tags you want?(default=5)\n")
    if maxtags == (""):
        maxtags = 5

ratings = str(input("Please enter what rating you want [(-)Safe, (-)Questionable, (-)Explicit, All(Default)]:\n"))
if ratings.lower() == "safe":
    rating = "rating:safe"
elif ratings.lower() == "questionable":
    rating = "rating:questionable"
elif ratings.lower() == "explicit":
    rating = "rating:explicit"
elif ratings.lower() == "-safe":
    rating = "-rating:safe"
elif ratings.lower() == "-questionable":
    rating = "-rating:questionable"
elif ratings.lower() == "-explicit":
    rating = "-rating:explicit"
else:
    rating = ""

tagstr = False
while not tagstr:
    print("Please enter what tags you would like (separated with a space):")
    seg1 = input()
    # check if something is typed
    if seg1 != (""):
        tagstr = True
        tag = str(seg1)
        tags = tag.split(" ")

# chose/create folder where the images will be downloaded
downfoldersw = str(input("Please enter download folder name(tags default):\n"))
if downfoldersw:
    downfolder = downfoldersw.capitalize()
else:# if nothing is typed tags will be used as folder name
    downfolder = tag.title()
    
if not os.path.exists(downfolder):
    try:# create folder
        os.makedirs(downfolder)
        print("Folder "+downfolder+" created!\nStarting download!!")
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
else:# strart download if already exist
    print("Folder "+downfolder+" already exists!\nStarting download!!")
    
grabURL = f"{defaultURL}?tags="
x = " ".join(tags)
grabURL += x
grabURL += f" {rating}"

req = requests.get(grabURL, headers=headers, auth=HTTPBasicAuth(apiUser,apiKey))
data = req.json()

if req.status_code != 200:
    print(f"Couldn't contact server. Error code: {req.status_code}.")
    print(data)
    sys.exit()

predownloaded = os.listdir(downfolder)
downloaded = []
for x in predownloaded:
    downloaded.append(x.split(".")[0])

# alot of checks for file naming(based on SkylerMews code)
def safe_filename(string):
    # set valid windows characters
    set = '-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    # replace ♥ emotes
    string = string.replace("<3_eyes","heart_eyes")
    string = string.replace("<3_penis","heart_penis")
    string = string.replace("<3_tail","heart_tail")
    string = string.replace("<3_censor","heart_censor")
    # remove ♥ emotes
    string = string.replace("<3","")
    string = string.replace("</3","")
    # remove aspect ratio tags
    string = string.replace("1:2","")
    string = string.replace("2:3","")
    string = string.replace("3:4","")
    string = string.replace("4:5","")
    string = string.replace("5:6","")
    string = string.replace("1:1","")
    string = string.replace("5:4","")
    string = string.replace("4:3","")
    string = string.replace("3:2","")
    string = string.replace("16:10","")
    string = string.replace("7:4","")
    string = string.replace("16:9","")
    string = string.replace("2:1","")
    # replace some
    string = string.replace("/","-")
    string = string.replace(":","-")
    # remove elipsis
    string = string.replace("...","")
    # remove multiple spacing
    string = ' '.join(string.split())
    s = ''
    for c in string:
        if set.find(c) != -1:
            s = s + c
    return s
    
while stop != True:
    if len(data["posts"]) > absoluteLimit:
        stop = True
    for posts in data["posts"]:
        postURL = posts["file"]["url"]
        if lowestID > posts['id'] or lowestID == -1:
            lowestID = posts['id']
        if pastURL == postURL:
            continue
        # tags
        ArtistTags = " ".join(posts["tags"]["artist"])+" "
        CharacterTags = " ".join(posts["tags"]["character"])+" "
        CopyrightTags = " ".join(posts["tags"]["copyright"])+" "
        GeneralTags = " ".join(posts["tags"]["general"])
        fileName = ArtistTags + CopyrightTags + CharacterTags
        # --
        if len(fileName) > 150:
                fileName = fileName[:150]
        # check if file already exists         
        if posts["file"]["md5"] in downloaded:
            print("Skipping existing post.")
            continue
        # check if file already exists based on post id thanks to SkylerMews
        if len( glob.glob( downfolder + "/" + str(lowestID) + ' *' ) ) > 0:
             print( 'File already exists. Post ID: "' + str(lowestID) + '"',)
             continue
        pastURL = posts["file"]["url"]
        img = requests.get(postURL)
        if naming.lower() == "md5":
            fileName = postURL[36:]
            filePath = currentFolder + os.path.sep + downfolder + os.path.sep + fileName
        elif naming.lower() == "tags":
            if len(fileName) > 150:
                fileName = fileName[:150]
            fileExt = "." + pastURL.split(".")[3]
            writeName = str(lowestID) + " " + safe_filename(fileName+' '.join(GeneralTags.split()[:int(maxtags)]))
            filePath = currentFolder + os.path.sep + downfolder + os.path.sep + writeName + fileExt
        img = requests.get(postURL)
        with open(filePath,"wb") as image:
            print(f"Downloading: {writeName}")
            image.write(img.content)
    rateLimiting()

    grabURL = f"{defaultURL}?tags="
    x = " ".join(tags)
    grabURL += x
    grabURL += f" {rating}&page=b{lowestID}&limit=320"
    
    req = requests.get(grabURL, headers=headers, auth=HTTPBasicAuth(apiUser,apiKey))
    data = req.json()
    
    if req.status_code != 200:
        print(f"Couldn't contact server. Error code: {req.status_code}.")
        print(data)
        sys.exit()
