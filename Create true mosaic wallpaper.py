from PIL import Image
import os
from dokkanfunctions import *
import math
from progress.bar import Bar
directory="data/"
cards=storedatabase(directory,"cards.csv")

print("Creating true mosaic")
acquiredlist = os.listdir(r'./assets/final_assets')
amount=len(acquiredlist)
screenx=1280
screeny=720

uniturl=("assets/final_assets/")
uniturl+=(acquiredlist[0])
cunit = Image.open(uniturl).convert("RGBA")
size=int(cunit.width)
fitx=0
fity=0


while (fitx*fity)<amount:
    screenx+=1
    screeny=math.floor(screenx*(720/1280))
    fitx=math.floor(screenx/size)
    fity=math.floor(screeny/size)
    
print("Each unit will be",size,"x",size)

(width,height)=(screenx,screeny)
cfinal=Image.new("RGBA",(width,height))
print("formatting cards file")
temp=[]
for x in range(0,len(acquiredlist)):
    temp.append(acquiredlist[x][0:7])
ALLcard=[]    
for unit2 in temp:
    for card in cards:
        if card[0]==unit2 and qualifyUsable(card):
            ALLcard+=[card]
            
#ALLcard=sortultralist(ALLcard,0,False)
ALLcard=sortultralist(ALLcard,0,True)
ALLcard=sortultralist(ALLcard,5,True)
ALLcard=sortultralist(ALLcard,12,True)
ALLcard=sortultralist(ALLcard,53,False)

acquiredlist=[]
for unit in ALLcard:
    temp=("")
    temp+=unit[0]
    temp+=(".png")
    acquiredlist.append(temp)
    
unitnumber=0
bar = Bar('Placing cards onto final image', max=amount)
for y in range(0,fity):
    for x in range(0,fitx):
        if unitnumber<amount:
            uniturl=("assets/final_assets/")
            uniturl+=(acquiredlist[unitnumber])
            cunit = Image.open(uniturl).convert("RGBA")
            xloc=x*size
            yloc=y*size
            cfinal.paste(cunit, (xloc,yloc),cunit)
            unitnumber+=1
            bar.next()
bar.finish()
print("Saving final image")
cfinal.save("assets/Mosaic wallpapers/Truest wallpaper.png")
print("Completed")
