from PIL import Image
import sqlite3 as sl
import time
import requests
import os
from dokkanfunctions import *
import pandas as pd
from progress.bar import Bar

directory="dataGB/"
cards=storedatabase(directory,"cards.csv")
transferredicon=[]
transferreddata=[]

for unit in cards:
    if unit[0][-1]=="1":
        transferreddata.append(unit[0])

for unit in cards:
    if (unit[0][-1]=="0") and (unit[53]!="2030-12-31 23:59:59") and (unit[0][0]!="9") and (unit[0][-1]=="0") and (unit[22]!=""):
        transferredicon.append(unit[0])
        
df = pd.DataFrame(transferredicon)

misc_assets_urls=storedatabase(directory,"misc_assets_urls.csv")
print("Character id's retrieved")


print("Retrieving icons and misc. assets")
transferredicon=[]
transferreddata=[]
for unit in cards:
    if unit[0][-1]=="1":
        transferreddata.append(unit[0])


for unit in cards:
    if unit[0][-1]=="0":
        transferredicon.append(unit[0])



acquiredlist = os.listdir(r'./assets/backgrounds')
print("retrieving character backgrounds")
count=0
maxcount=0
for unit in cards:
    unitid=unit[0]
    
    temp=("bg_card_"+unitid+"_bg.png")
    if temp not in acquiredlist and (unit[53]!="2030-12-31 23:59:59") and (unit[0][0]!="9") and (unit[0][-1]=="0") and (unit[22]!=""):  
        maxcount+=1

for unit in cards:
    unitid=unit[0]
    
    temp=("bg_card_"+unitid+"_bg.png")
    if temp not in acquiredlist and (unit[53]!="2030-12-31 23:59:59") and (unit[0][0]!="9") and (unit[0][-1]=="0") and (unit[22]!=""):  
        url=("https://jpnen.dokkaninfo.com/assets/japan/character/card/"+unitid+"/card_"+unitid+"_bg.png")
        count+=1
        print(url,count,"completed out of", maxcount)
        filename = ("assets/backgrounds/bg_"+url.split('/')[-1])
        r = requests.get(url, allow_redirects=True)
        open(filename, 'wb').write(r.content)
        time.sleep(0.7)
print("all backgrounds acquired")



print("retrieving card effects")
acquiredlist = os.listdir(r'./assets/card_effect')
count=0
maxcount=0

for unit in cards:
    unitid=unit[0]
    
    temp=("card_effect_card_"+unitid+"_effect.png")
    if temp not in acquiredlist and (unit[53]!="2030-12-31 23:59:59") and (unit[0][0]!="9") and (unit[0][-1]=="0") and (unit[22]!=""):  
        maxcount+=1

for unit in cards:
    unitid=unit[0]
    
    temp=("card_effect_card_"+unitid+"_effect.png")
    if temp not in acquiredlist and (unit[53]!="2030-12-31 23:59:59") and (unit[0][0]!="9") and (unit[0][-1]=="0") and (unit[22]!=""):  
        url=("https://jpnen.dokkaninfo.com/assets/japan/character/card/"+unitid+"/card_"+unitid+"_effect.png")
        print(url,count,"completed out of", maxcount)
        filename = ("assets/card_effect/card_effect_"+url.split('/')[-1])
        r = requests.get(url, allow_redirects=True)
        open(filename, 'wb').write(r.content)
        time.sleep(1)
print("all card effects acquired")




print("retrieving portraits")
acquiredlist = os.listdir(r'./assets/portrait')
count=0
maxcount=0
for unit in cards:
    unitid=unit[0]
    
    temp=("portrait_card_"+unitid+"_character.png")
    if temp not in acquiredlist and (unit[53]!="2030-12-31 23:59:59") and (unit[0][0]!="9") and (unit[0][-1]=="0") and (unit[22]!=""):  
        maxcount+=1

for unit in cards:
    unitid=unit[0]
    
    temp=("portrait_card_"+unitid+"_character.png")
    if temp not in acquiredlist and (unit[53]!="2030-12-31 23:59:59") and (unit[0][0]!="9") and (unit[0][-1]=="0") and (unit[22]!=""):  
        url=("https://jpnen.dokkaninfo.com/assets/japan/character/card/"+unitid+"/card_"+unitid+"_character.png")
        print(url,count,"completed out of", maxcount)
        filename = ("assets/portrait/portrait_"+url.split('/')[-1])
        r = requests.get(url, allow_redirects=True)
        open(filename, 'wb').write(r.content)
        time.sleep(1)
print("all portraits acquired")


print("All required assets required")


print("Creating final assets")
acquiredlist = os.listdir(r'./assets/final_portraits')
leader_skills=storedatabase(directory,"leader_skills.csv")
total=1
for unit in cards:
    if (unit[53]!="2030-12-31 23:59:59") and (unit[0][0]!="9") and (unit[0][-1]=="0") and (unit[22]!="") and ((("final_portrait_"+unit[0]+".png") not in acquiredlist)):
        unitid=unit[0]
        if unitid[-1]=="1":
            unitid=str(int(unitid)-1)
        mainunit=unit

    #background
        cbgurl=("assets/backgrounds/bg_card_"+mainunit[0]+"_bg.png")
        print(cbgurl)
        cbg = Image.open(cbgurl).convert("RGBA")


    #character portrait
        cportraiturl=("assets/portrait/portrait_card_"+mainunit[0]+"_character.png")
        cportrait = Image.open(cportraiturl).convert("RGBA")


    #effect
        ceffectyurl=("assets/card_effect/card_effect_card_"+mainunit[0]+"_effect.png")
        crarity = Image.open(crarityurl).convert("RGBA")


        (width,height)=(cicon.width,cicon.height)
        cfinal=Image.new("RGBA",(width,height))
        cfinal.paste(cbg, (0,0), cbg)
        cfinal.paste(cportrait, (0,0), cportrait)
        cfinal.paste(crarity, (0,0),crarity)
        name=("assets/final_portraits/final_portrait_")
        name+=(unit[0])
        name+=(".png")
        cfinal.save(name)
        total+=1
        if total%100==0:
            print(total)
        #print("Created final asset for",total,getfullname(card,leader_skills))
print("All final assets created")

