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




print("Creating full thumbs")
requiredList=[]
for unitID in os.listdir(r'../frontend/dbManagement/DokkanFiles/global/en/character/card'):
    finalAssetLocation=os.path.join("../frontend/dbManagement/DokkanFiles/global/en/character/card", unitID, "card_"+unitID+"_full_thumb.png"   )
    if not os.path.exists(finalAssetLocation):
        requiredList.append(unitID)

total=1

for unitID in requiredList:
    print(total,"/",len(requiredList),"Making: ",unitID,end="")
    total+=1
    card=searchbycolumn(unitID,cards,0)
    if(card!=[]):
        card=card[0]
        if(qualifyUsable(card) or qualifyUsable(swapToUnitWith1(card))):
            createFullThumb(card)
            print(": Done")
        else:
            print(": Not usable")
    else:
        print(": Not found")
    


        
print("All final assets created")

