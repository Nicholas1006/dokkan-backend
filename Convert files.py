import os
import sqlite3 as sl
import time

import pandas as pd
from progress.bar import Bar
import requests
from PIL import Image

from dokkanfunctions import *


directory="dataGB/"
cards=storedatabase(directory,"cards.csv")

print("scraping GB units")
scrapeallunitassetsv2(cards,thumb=True,circle=True,full=True,sp_name=True,printing=True)
print("units scraped")        

#cardsGB=storedatabase("dataGB/","cards.csv")
#print("scraping gb units")
#scrapeallunitassetsv2(cardsGB,thumb=True,circle=True,full=True,sp_name=True,printing=True)
#print("units scraped")        

misc_assets_urls=storedatabase(directory,"misc_assets_urls.csv")
print("Character id's retrieved")


print("Retrieving icons and misc. assets")

filterIncompletePngs("../frontend/dbManagement/assets/", 1000)

acquiredlist = os.listdir(r'../frontend/dbManagement/assets/misc')
for asset in misc_assets_urls:
    assetid=asset[0]
    url=(assetid)
    #temp=("card_"+unitid+"_thumb.png")
    #if temp not in acquiredlist:  
    if url.split('/')[-1] not in acquiredlist:
        print(url)
        filename = ("../frontend/dbManagement/assets/misc/"+url.split('/')[-1])
        r = requests.get(url, allow_redirects=True, timeout=300)
        if("404 Not Found" not in str(r._content)):
            open(filename, 'wb').write(r.content)
        else:
            print("NOT SCRAPED")
        #time.sleep(1)
print("all misc. assets acquired")


filterIncompletePngs("../frontend/dbManagement/assets/final_assets", 1000)
print("Creating final assets")
acquiredlist = os.listdir(r'../frontend/dbManagement/assets/final_assets')
leader_skills=storedatabase(directory,"leader_skills.csv")
total=1

for card in cards:
    if qualifyUsable(card) and (((card[0]+".png") not in acquiredlist)):
    #if(qualifyUsable(card)):
        if total%100==0:
            print(total)
        total+=1
        createFinalAsset(card)


        
print("All final assets created")

