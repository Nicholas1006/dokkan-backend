from PIL import Image
import os
from dokkanfunctions import *
import math
directory="dataGB/"
cards=storedatabase(directory,"cards.csv")
card_awakening_routes=storedatabase(directory, "card_awakening_routes.csv")
active_skills=storedatabase(directory,"active_skills.csv")
card_active_skills=storedatabase(directory,"card_active_skills.csv")
passive_skills=storedatabase(directory,"passive_skills.csv")
passive_skill_set_relations=storedatabase(directory,"passive_skill_set_relations.csv")
createDFEWallpapers(cards, directory)

print("Creating DFE mosaic")
acquiredlist2 = os.listdir(r'./assets/final_assets')
acquiredlist=[]
for card in cards:
    if qualifyAsDFE(card):
        acquiredlist.append(card[0]+".png")
amount=len(acquiredlist)
screenx=1280
screeny=720
size=screenx+screeny
fitx=0
fity=0
while (fitx*fity)<amount:
    size-=1
    fitx=math.floor(screenx/size)
    fity=math.floor(screeny/size)
print("Each unit will be",size,"x",size)

(width,height)=(screenx,screeny)
cfinal=Image.new("RGBA",(width,height))

print("ordering cards",end=" ")
temp=[]
for x in range(0,len(acquiredlist)):
    temp.append(acquiredlist[x][0:7])
DFEcard=[]    
for unit2 in temp:
    for card in cards:
        if card[0]==unit2:
            DFEcard+=[card] 
DFEcard=sortultralist(DFEcard,0,True)
DFEcard=sortultralist(DFEcard,12,True)
DFEcard=sortultralist(DFEcard,53,False)
acquiredlist=[]
for unit in DFEcard:
    temp=definewith0(unit[0])
    temp+=(".png")
    acquiredlist.append(temp)
print("completed")



unitnumber=0
for y in range(0,fity):
    for x in range(0,fitx):
        if unitnumber<amount:
            uniturl=("assets/DFE wallpapers/")
            uniturl+=(acquiredlist[unitnumber])
            cunit = Image.open(uniturl).convert("RGBA")
            cunit=cunit.resize((size,size))
            xloc=x*size
            yloc=y*size
            cfinal.paste(cunit, (xloc,yloc),cunit)
            unitnumber+=1
cfinal.save("assets/Mosaic wallpapers/DFE wallpaper.png")
print("Completed")