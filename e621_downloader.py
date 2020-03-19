import requests
from requests.auth import HTTPBasicAuth
import time
import json
import os
import sys
import hashlib

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

naming = str(input("What naming scheme would you like? (md5, tags)?\n"))

ratings = str(input("Please enter what rating you want [(-)Safe, (-)Questionable, (-)Explicit, All]:\n"))
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

tag = str(input("Please enter what tags you would like (separated with a space):\n"))
tags = tag.split(" ")

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

predownloaded = os.listdir("Downloads")
downloaded = []
for x in predownloaded:
    downloaded.append(x.split(".")[0])
    

while stop != True:
    if len(data["posts"]) > absoluteLimit:
        stop = True
    
    for posts in data["posts"]:
        postURL = posts["file"]["url"]
        if lowestID > posts['id'] or lowestID == -1:
            lowestID = posts['id']
        if pastURL == postURL:
            continue
        fileName = "-".join(posts["tags"]["general"])
        if len(fileName) > 150:
                fileName = fileName[:150]
        if posts["file"]["md5"] in downloaded:
            print("Skipping existing post.")
            continue
        if fileName in downloaded:
            print("Skipping existing post.")
            continue
        pastURL = posts["file"]["url"]
        img = requests.get(postURL)
        if naming.lower() == "md5":
            fileName = postURL[36:]
            filePath = currentFolder + os.path.sep + "Downloads" + os.path.sep + fileName
        elif naming.lower() == "tags":
            fileName = "-".join(posts["tags"]["general"])
            if len(fileName) > 150:
                fileName = fileName[:150]
            fileName = fileName.replace("/","")
            fileName = fileName.replace(":","")
            fileExt = "." + pastURL.split(".")[3]
            filePath = currentFolder + os.path.sep + "Downloads" + os.path.sep + fileName + fileExt
        img = requests.get(postURL)
        with open(filePath,"wb") as image:
            print(f"Downloading {fileName}")
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
