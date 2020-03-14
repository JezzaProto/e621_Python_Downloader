import requests
from requests.auth import HTTPBasicAuth
import time
import json
import os
import sys

defaultURL = "https://e621.net/posts.json"
currentFolder = os.getcwd()
apiKeyFile = currentFolder + os.sep + "apikey.txt"

absoluteLimit = 250
rateLimit = 1
lastTime = time.time()
lowestID = 0
stop = False

headers = {"User-Agent":"E6-Post-Downloader/1.0 (by JezzaR on E621)"}
params = {"Tags":""}

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
    print("apikey.txt created - Add your username and API Key then press enter to continue")
    input()
    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

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

tag = str(input("Please enter what tags you would like (separated with a semicolon):\n"))
tags = tag.split(";")

postnum = str(input("Please enter how many posts you would like to download (Beware, a large number will take a while to download):\n"))

defaultURL = "https://e621.net/posts.json"
currentFolder = os.getcwd()
apiKeyFile = currentFolder + os.sep + "apikey.txt"

absoluteLimit = 250
rateLimit = 1
lastTime = time.time()
lowestID = 0
stop = False

headers = {"User-Agent":"E6-Post-Downloader/1.0 (by JezzaR on E621)"}
params = {"Tags":tag}

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
    print("apikey.txt created - Add your username and API Key then press enter to continue")
    input()
    os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)
