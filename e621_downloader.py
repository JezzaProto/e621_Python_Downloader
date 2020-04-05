import tkinter as tk
import requests, time, json, os, sys, hashlib, errno, glob, re, threading
from requests.auth import HTTPBasicAuth
from tkinter.ttk import Combobox

headers = {"User-Agent":"E6-Post-Downloader/4.0 (by jezzar on E621)"}

def rateLimiting():
    global lastTime
    timeTaken = time.time() - lastTime
    if timeTaken <= rateLimit:
        time.sleep(rateLimit-timeTaken)
    lastTime = time.time()

def startDownload():
    # setup variables:
    defaultURL = "https://e621.net/posts.json"
    pastURL = ""
    currentFolder = os.path.dirname(os.path.realpath(__file__))
    apiKeyFile = currentFolder + os.sep + "apikey.txt"
    stop = False
    absoluteLimit = 320
    rateLimit = 1
    lastTime = time.time()
    lowestID = -1
    # get api key and username
    try:
        with open(apiKeyFile) as apiFile:
            apiKeys = apiFile.read().splitlines()
    except FileNotFoundError:
        with open(apiKeyFile,"w") as apiFile:
            apiFile.write("user="+os.linesep+"api_key=")
        outputLabel.config(text="apikey.txt created - Add your username and API Key (https://e621.net/users/home -> Manage API Access) then press download again.")
        input()
    GUI.update()
    apiUser = apiKeys[0].split("=")[1]
    apiKey = apiKeys[2].split("=")[1]

    if apiUser == "" or apiKey == "":
        outputLabel.config(text="Please actually put your username and API key into apikey.txt")
        input()
    GUI.update()
    naming = namingList.get()
    if naming.lower() != "md5":
    # set tag file naming default
        naming = "tags"
    # set how many general tags to write
        maxtags=namingTagNumEntry.get()
        if maxtags == (""):
            maxtags = 5
    else:
        naming = "md5"
    # set appropriate ratings
    ratings = ratingList.get()
    if ratings.lower() == "Safe":
        rating = "rating:safe"
    elif ratings.lower() == "Questionable":
        rating = "rating:questionable"
    elif ratings.lower() == "Explicit":
        rating = "rating:explicit"
    elif ratings.lower() == "-Safe":
        rating = "-rating:safe"
    elif ratings.lower() == "-Questionable":
        rating = "-rating:questionable"
    elif ratings.lower() == "-Explicit":
        rating = "-rating:explicit"
    else:
        rating = ""

    tagstr = False
    while not tagstr:
        seg1 = tagEntry.get()
        # check if something is typed
        if seg1 != (""):
            tagstr = True
            tag = str(seg1)
            tags = tag.split(" ")

    grabURL = f"{defaultURL}?tags="
    x = " ".join(tags)
    grabURL += x
    grabURL += f" {rating}"

    downfoldersw = downFolderEntry.get()
    if downfoldersw:
        downfolder = downfoldersw.capitalize()
    else:# if nothing is typed tags will be used as folder name
        downfolder = tag.title()
    GUI.update()
    if not os.path.exists(downfolder):
        try:# create folder
            os.makedirs(downfolder)
            outputLabel.config(text="Folder "+downfolder+" created!\nStarting download!!")
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    else:# strart download if already exist
        outputLabel.config(text="Folder "+downfolder+" already exists!\nStarting download!!")
    GUI.update()
    req = requests.get(grabURL, headers=headers, auth=HTTPBasicAuth(apiUser,apiKey))
    data = req.json()

    if req.status_code != 200:
        outputLabel.config(text=f"Couldn't contact e621. Error code: {req.status_code}.\nJson: {data}")
        sys.exit()

    predownloaded = os.listdir("Downloads")
    downloaded = []
    for path, subdirs, files in os.walk(currentFolder + os.path.sep + "Downloads"):
        for name in files:
            downloaded.append(name.split(".")[0])
    GUI.update()
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
    GUI.update()
    while stop != True:
        if len(data["posts"]) > absoluteLimit:
            stop = True
        GUI.update()
        for posts in data["posts"]:
            postURL = posts["file"]["url"]
            if lowestID > posts['id'] or lowestID == -1:
                lowestID = posts['id']
            if pastURL == postURL:
                continue
            ArtistTags = " ".join(posts["tags"]["artist"])+" "
            CharacterTags = " ".join(posts["tags"]["character"])+" "
            CopyrightTags = " ".join(posts["tags"]["copyright"])+" "
            GeneralTags = " ".join(posts["tags"]["general"])
            fileName = ArtistTags + CopyrightTags + CharacterTags
            if len(fileName) > 150:
                    fileName = fileName[:150]
            if posts["file"]["md5"] in downloaded:
                outputLabel.config(text="Skipping existing post.")
                GUI.update()
                continue
            if fileName in downloaded:
                outputLabel.config(text="Skipping existing post.")
                GUI.update()
                continue
            if len(glob.glob(downfolder+"/"+str(lowestID)+' *')) > 0:
                 outputLabel.config(text=f'File already exists. Post ID: "{lowestID}"')
                 GUI.update()
                 continue
            pastURL = posts["file"]["url"]
            img = requests.get(postURL)
            if naming.lower() == "md5":
                fileName = postURL[36:]
                filePath = currentFolder + os.path.sep + "Downloads" + os.path.sep + fileName
            elif naming.lower() == "tags":
                if len(fileName) > 150:
                    fileName = fileName[:150]
                fileExt = "." + pastURL.split(".")[3]
                writeName = str(lowestID) + " " + safe_filename(fileName+' '.join(GeneralTags.split()[:int(maxtags)]))
                filePath = currentFolder + os.path.sep + downfolder + os.path.sep + writeName + fileExt
            img = requests.get(postURL)
            with open(filePath,"wb") as image:
                outputLabel.config(text=f"Downloading {fileName}")
                GUI.update()
                image.write(img.content)

        rateLimiting()

        grabURL = f"{defaultURL}?tags="
        x = " ".join(tags)
        grabURL += x
        grabURL += f" {rating}&page=b{lowestID}&limit=320"
        
        GUI.update()
        
        req = requests.get(grabURL, headers=headers, auth=HTTPBasicAuth(apiUser,apiKey))
        data = req.json()

        GUI.update()
        
        if req.status_code != 200:
            outputLabel.config(text=f"Couldn't contact e621. Error code: {req.status_code}.\nJson: {data}")
            GUI.update()
            sys.exit()

GUI = tk.Tk()

namingLabel = tk.Label(GUI,text="Naming Scheme")

namingOptions = ("md5","tags")
namingList = Combobox(GUI,values=namingOptions)

namingTagNumLabel = tk.Label(GUI,text="If naming as tags:\nhow many general tags would you like?\n(Default=5)")

namingTagNumEntry = tk.Entry(GUI,text="")

ratingLabel = tk.Label(GUI,text="Select Rating")

ratingOptions = ("All","Safe","Questionable","Explicit","-Safe","-Questionable","-Explicit")
ratingList = Combobox(GUI,values=ratingOptions)

tagLabel = tk.Label(GUI,text="Enter Tags")

tagEntry = tk.Entry(GUI,text="")

downFolderLabel = tk.Label(GUI,text="Enter the Download Folder\n(Default=tags)")

downFolderEntry = tk.Entry(GUI,text="")

downloadButton = tk.Button(GUI,text="Download!",command=startDownload)

outputLabel = tk.Label(GUI,text="")

namingLabel.grid(column=0,row=0)
namingList.grid(column=0,row=1)
namingTagNumLabel.grid(column=0,row=2)
namingTagNumEntry.grid(column=0,row=3)
ratingLabel.grid(column=0,row=4)
ratingList.grid(column=0,row=5)
tagLabel.grid(column=0,row=6)
tagEntry.grid(column=0,row=7)
downFolderLabel.grid(column=0,row=8)
downFolderEntry.grid(column=0,row=9)
downloadButton.grid(column=0,row=10)
outputLabel.grid(column=0,row=11)

GUI.update()
GUI.mainloop()
