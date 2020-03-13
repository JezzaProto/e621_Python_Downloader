import requests
import time
import json
tag = str(input("Please enter what tags you would like (separated with a colon):\n"))
tags = tag.split(":")
postnum = str(input("Please enter how many posts you would like to download:\n"))
# Get user-defined url
url = "https://e621.net/posts.json?tags=" # Generates first static part of e621.net api url
for x in tags: # Add all tags specified
    url += x
    url += "%20"
url = url[:-3]
url += "&limit={0}&callback=callback".format(postnum) # Add rest of url
req = requests.get(url) # Sends a get request to server to get back urls of images
data = req.json() # Records the response as json
data = str(data)
res = [i for i in range(len(data)) if data.startswith("https://static1.e621.net/data", i)]
print(res)
print(url)
x = 0
while x < len(res):
    startpos = res[x]
    endpos = res[x]+72
    strings = data[startpos:endpos]
    if "preview" in strings or "sample" in strings:
        data = data [:startpos] + data[endpos+8:]
        res.pop(x)
    else:
        x += 1
    res = [i for i in range(len(data)) if data.startswith("https://static1.e621.net/data", i)]
print(data)