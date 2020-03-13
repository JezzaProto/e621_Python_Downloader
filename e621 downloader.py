import requests
import time
import json
import os
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
tag = str(input("Please enter what tags you would like (separated with a semicolon):\n"))
tags = tag.split(";")
postnum = str(input("Please enter how many posts you would like to download (Beware, a large number will take a while to download):\n"))
# Get user-defined url
url = "https://e621.net/posts.json?tags=" # Generates first static part of e621.net api url
for x in tags: # Add all tags specified
    url += x
    url += "%20"
url += rating
url += "&limit={0}&callback=callback".format(postnum) # Add rest of url
req = requests.get(url) # Sends a get request to server to get back urls of images
data = req.json() # Records the response as json
data = str(data)
res = [i for i in range(len(data)) if data.startswith("https://static1.e621.net/data", i)] # Find all strings starting with the e621 url
x = 0
while x < len(res):
    startpos = res[x]
    endpos = res[x]+73 # Standard url length
    strings = data[startpos:endpos] # Set strings to whole url
    if "preview" in strings or "sample" in strings: # Find if it is a low-res image
        data = data [:startpos] + data[endpos+8:] # Remove the url
        res.pop(x)
    else:
        x += 1
    res = [i for i in range(len(data)) if data.startswith("https://static1.e621.net/data", i)] # Update res
urls = []
x = 0
while x < len(res):
    res = [i for i in range(len(data)) if data.startswith("https://static1.e621.net/data", i)] # Update res
    startpos = res[x]
    endpos = res[x]+73 # Standard url length
    tempurl = data[startpos:endpos]
    tempurl = tempurl.replace("'","")
    urls.append(tempurl)
    x += 1
x = 0
urls.sort()
while x < len(urls):
    try:
        if urls[x] == urls[x+1]:
            urls.pop(x+1)
    except:
        y = 0
    fileName = urls[x]
    fileName = fileName[36:]
    img = requests.get(urls[x])
    cwd = os.getcwd() # Get current directory
    filePath = cwd + "\\Downloads\\" + fileName # Set download folder
    with open(filePath,"wb") as image:
        print("Downloading {0}".format(fileName))
        image.write(img.content)
    x += 1
    time.sleep(1) # Rate Limit
