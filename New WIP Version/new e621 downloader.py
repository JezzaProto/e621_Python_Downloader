import requests
from requests.auth import HTTPBasicAuth
import time
import json
import os
import sys

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
currentFolder = os.cwd()
apiKeyFile = currentFolder + os.sep + "apikey.txt"

