
from globals import *
from dokkanfunctions import *
from progress.bar import Bar
directory="dataJP/"
cardsJP=storedatabase(directory,"cards.csv")

DEVEXCEPTIONS=True
GLOBALPARSE=True
GLOBALREFRESH=False
MAKEJSON=True

CALCPASSIVE=True
CALCLINKS=True
CALCLEADER=True
CALCHIPO=True
CALCACTIVE=True
CALCSUPERATTACK=True
CALCLEVELS=True
CALCBASIC=True
CALCMULTIPLIER=True
CALCFINISH=True
CALCSTANDBY=True
CALCCIRCLE=True

passiveTime=0.0
leaderTime=0.0
hipoTime=0.0
activeTime=0.0
superTime=0.0
levelTime=0.0
basicTime=0.0
jsonTime=0.0
standbyTime=0.0
finishTime=0.0
linksTime=0.0
circleTime=0.0
multiplierTime=0.0

cardIDsToCheck=["4019761"]

#cardIDsToCheck=["4026911","4025741","4028381","4026401","4027631","4027301","4025781","4026541"]

cardsToCheck=[]


if(GLOBALREFRESH and GLOBALPARSE):
    emptyFolder("../frontend/dbManagement/jsons")
    emptyFolder("../frontend/dbManagement/jsonsEZA")
    emptyFolder("../frontend/dbManagement/jsonsSEZA")
    

temp=time.time()
if GLOBALPARSE:
    for unit in cardsJP:
        if qualifyUsable(unit):
            cardsToCheck.append(unit)
else:
    for ID in cardIDsToCheck:
        for unit in cardsJP:
            if unit[0]==ID:
                if(qualifyUsable(unit)):
                    cardsToCheck.append(unit)
                else:
                    print("UNUSABLLE UNIT",unit[0])

missingPassiveCount=0
missingUnitCount=0

unitCount=0
passivecount=0
#passive skill set id is mainunit[21]
#passive=(passivename(mainunit,passive_skills))
#passiveIdList=getpassiveid(mainunit,cards,optimal_awakening_growths,passive_skill_set_relations,eza)
#print(passive)
HiPoBoards={}

if GLOBALPARSE:
    bar = Bar('Parsing units', max=len(cardsToCheck))


dokkanAwakenings={}
transformations={}

for unit in cardsToCheck:
    ezaTrueFalse=[False]
    if(checkEza(unit[0])):
        ezaTrueFalse=[False,True]
    if(GLOBALPARSE):
            bar.next()
    for eza in ezaTrueFalse:
        if(checkSeza(unit[0]) and eza):
            sezaTrueFalse=[False,True]
        else:
            sezaTrueFalse=[False]
        for seza in sezaTrueFalse:
            unitCount=unitCount+1
            unitDictionary={}
            unit1=swapToUnitWith1(unit)
            unitGB=switchUnitToGlobal(unit)
            if(CALCBASIC):
                basicStart=time.time()
                unitDictionary["ID"]=unit[0]
                unitDictionary["Typing"]=getUnitTyping(unit)
                unitDictionary["Class"]=getUnitClass(unit)
                if(unitGB!=None):
                    unitDictionary["Name"]=unitGB[1]
                else:
                    card_unique_info_id=unit[3]
                    temp=searchbyid(code=card_unique_info_id,codecolumn=3,database=cardsGB,column=1)
                    if(temp!=None):
                        likelyName=longestCommonSubstring(temp)
                        if(likelyName!=""):
                            unitDictionary["Name"]=likelyName
                        else:
                            unitDictionary["Name"]=unit[1]
                    else:
                        unitDictionary["Name"]=unit[1]
                unitDictionary["Rarity"]=getrarity(unit)
                unitDictionary["Min Level"]=getMinLevel(unit,eza)
                unitDictionary["Max Level"]=getMaxLevel(unit,eza)
                unitDictionary["Categories"]=getallcategories(unit[0],printing=True)
                basicTime+=time.time()-basicStart
            

            if(CALCLINKS):
                linksStart=time.time()
                #unitDictionary["Links"]=getalllinkswithbuffs(unit)
                unitDictionary["Links"]=getalllinks(unit)
                linksTime+=time.time()-linksStart

            unitDictionary["Resource ID"]=unit[0]
            if(unit[48]!=""):
                unitDictionary["Resource ID"]=str(int(float(unit[48])))
            if(unit[0][-1]=="1"):
                unitDictionary["Resource ID"]=(unit[0][:-1]+"0")

            unitDictionary["Passive"]={}
            if(CALCPASSIVE):
                passiveStart=time.time()
                parsedPassive=parsePassiveSkill(unit,eza,seza,DEVEXCEPTIONS)
                unitDictionary["Passive"]=parsedPassive
                passiveTime+=time.time()-passiveStart

            unitDictionary["Max Attacks"]=1
            unitDictionary["Max Super Attacks"]=1
            if(unitDictionary["Rarity"]=="lr" or unitDictionary["Rarity"]=="ur"):
                unitDictionary["Max Super Attacks"]+=1
                unitDictionary["Max Attacks"]+=1
            for passive in unitDictionary["Passive"]:
                if("Additional Attack" in unitDictionary["Passive"][passive]):
                    if(unitDictionary["Passive"][passive]["Additional Attack"]["Chance of super"]!="0"):
                        if("Chance of another additional" in unitDictionary["Passive"][passive]["Additional Attack"]):
                            unitDictionary["Max Super Attacks"]+=2
                            unitDictionary["Max Attacks"]+=2    
                        else:
                            unitDictionary["Max Super Attacks"]+=1
                            unitDictionary["Max Attacks"]+=1
                    else:
                        unitDictionary["Max Attacks"]+=1

            


            unitDictionary["Stats at levels"]={}
            if(CALCLEVELS):
                levelStart=time.time()
                unitDictionary["Stats at levels"]=getStatsAtAllLevels(unit,eza)
                levelTime+=time.time()-levelStart
            
            unitDictionary["Leader Skill"]={}
            if(CALCLEADER and unit[22]!=""):
                leaderStart=time.time()
                unitDictionary["Leader Skill"]=parseLeaderSkill(unit,eza,DEVEXCEPTIONS)
                leaderTime+=time.time()-leaderStart

            unitDictionary["Hidden Potential"]={}
            if(CALCHIPO):
                hipoStart=time.time()
                if(unit[52][:-2]not in HiPoBoards):
                    HiPoBoards[unit[52][:-2]]=parseHiddenPotential(unit[52][:-2],DEVEXCEPTIONS)
                unitDictionary["Hidden Potential"]=HiPoBoards[unit[52][:-2]]
                hipoTime+=time.time()-hipoStart

            unitDictionary["Super Attack"]={}
            if(CALCSUPERATTACK):
                superStart=time.time()
                unitDictionary["Super Attack"]=parseSuperAttack(unit,eza,DEVEXCEPTIONS)
                superTime+=time.time()-superStart


            unitDictionary["Active Skill"]={}
            if(CALCACTIVE):    
                activeStart=time.time()
                unitDictionary["Active Skill"]=parseActiveSkill(unit,DEVEXCEPTIONS)
                activeTime+=time.time()-activeStart

            unitDictionary["Standby Skill"]={}
            if(CALCSTANDBY):
                standbyStart=time.time()
                unitDictionary["Standby Skill"]=parseStandby(unit,DEVEXCEPTIONS)
                standbyTime+=time.time()-standbyStart

            unitDictionary["Finish Skill"]={}
            if(CALCFINISH):
                finishStart=time.time()
                unitDictionary["Finish Skill"]=parseFinish(unit,DEVEXCEPTIONS)
                finishTime+=time.time()-finishStart


            unitDictionary["Transforms from"]=[]


            unitDictionary["Transformations"]=[]
            if("Exchanges to" in unitDictionary["Standby Skill"]):
                unitDictionary["Transformations"].append(unitDictionary["Standby Skill"]["Exchanges to"])
                if(unit[0] in transformations):
                    transformations[unit[0]].append(unitDictionary["Standby Skill"]["Exchanges to"])
                else:
                    transformations[unit[0]]=[unitDictionary["Standby Skill"]["Exchanges to"]]
            if(unitDictionary["Finish Skill"] != {}):
                for finishRow in unitDictionary["Finish Skill"]:
                    unitDictionary["Transformations"].append(unitDictionary["Finish Skill"][finishRow]["Exchanges to"])
                    if(unit[0] in transformations):
                        transformations[unit[0]].append(unitDictionary["Finish Skill"][finishRow]["Exchanges to"])
                    else:
                        transformations[unit[0]]=[unitDictionary["Finish Skill"][finishRow]["Exchanges to"]]
            unitDictionary["Max Appearances In Form"]=maxAppearancesInForm(unitDictionary["Passive"],DEVEXCEPTIONS)


            if(unitDictionary["Passive"]!=None):
                for passiveLine in unitDictionary["Passive"]:
                    if "Transformation" in unitDictionary["Passive"][passiveLine]:
                        unitDictionary["Transformations"].append(unitDictionary["Passive"][passiveLine]["Transformation"]["Unit"])
                        if(unit[0] in transformations):
                            transformations[unit[0]].append(unitDictionary["Passive"][passiveLine]["Transformation"]["Unit"])
                        else:
                            transformations[unit[0]]=[unitDictionary["Passive"][passiveLine]["Transformation"]["Unit"]]
            if(unitDictionary["Active Skill"]!=None):
                for activeLine in unitDictionary["Active Skill"]["Effects"]:
                    if "Unit" in unitDictionary["Active Skill"]["Effects"][activeLine]["Effect"]:
                        unitDictionary["Transformations"].append(unitDictionary["Active Skill"]["Effects"][activeLine]["Effect"]["Unit"])
                        if(unit[0] in transformations):
                            transformations[unit[0]].append(unitDictionary["Active Skill"]["Effects"][activeLine]["Effect"]["Unit"])
                        else:
                            transformations[unit[0]]=[unitDictionary["Active Skill"]["Effects"][activeLine]["Effect"]["Unit"]]

            unitDictionary["Transforms from"]=[]

            newFound=True
            forms=[unit[0]]
            while newFound==True:
                newFound=False
                for transform in transformations:
                    if(forms[-1] in transformations[transform] and transform not in forms):
                        unitDictionary["Transforms from"].append(transform)
                        forms.append(transform)
                        newFound=True

            
            for transform in unitDictionary["Transformations"]:
                if (transform in unitDictionary["Transforms from"]):
                    unitDictionary["Transformations"].remove(transform)



            unitDictionary["Dokkan awakenings"]=[]
            relevant_awakenings=searchbycolumn(code=unit1[0],database=card_awakening_routesJP,column=2)
            relevant_awakenings=searchbycolumn(code="CardAwakeningRoute::Dokkan",database=relevant_awakenings,column=1)
            for awakening in relevant_awakenings:
                unitDictionary["Dokkan awakenings"].append(awakening[3])
                dokkanAwakenings[unit[0]]=awakening[3]
            
            unitDictionary["Dokkan Reverse awakenings"]=[]
            for awakening in dokkanAwakenings:
                if(dokkanAwakenings[awakening]==unit[0]):
                    unitDictionary["Dokkan Reverse awakenings"].append(awakening)



            unitDictionary["Ki Multiplier"]={}
            if(CALCMULTIPLIER):
                multiplierStart=time.time()
                unitDictionary["Ki Multiplier"]=getKiMultipliers(unit)
                multiplierTime+=time.time()-multiplierStart
            
            unitDictionary["Ki Circle Segments"]={}
            if(CALCCIRCLE):
                circleStart=time.time()
                unitDictionary["Ki Circle Segments"]=getKiCircleSegments(unitDictionary)
                circleTime+=time.time()-circleStart

            
            unitDictionary["SuperMinKi"]=getSuperMinKi(unitDictionary["Ki Circle Segments"])
            unitDictionary["AdditionalSuperID"]=getAdditionalSuperID(unitDictionary)

            unitDictionary["Can EZA"]=checkEza(unit[0])
            unitDictionary["Can SEZA"]=checkSeza(unit[0])

            




            jsonName=unit[0]

            



            if(MAKEJSON):
                jsonStart=time.time()
                if(seza):
                    directoryName="../frontend/dbManagement/jsonsSEZA"
                elif(eza):
                    directoryName="../frontend/dbManagement/jsonsEZA"
                else:
                    directoryName="../frontend/dbManagement/jsons"
                turnintoJson(unitDictionary, jsonName,directoryName=directoryName)
                jsonTime+=time.time()-jsonStart
        


if(GLOBALPARSE):
    bar.finish()
print("Basic time:",round(basicTime,2))
print("Links time:",round(linksTime,2))
print("Leader time:",round(leaderTime,2))
print("Passive time:",round(passiveTime,2))
print("Super time:",round(superTime,2))
print("Level time:",round(levelTime,2))
print("HiPo time:",round(hipoTime,2))
print("Ki segments time:",round(circleTime,2))
print("Multiplier time:",round(multiplierTime,2))
print("Active time:",round(activeTime,2))
print("Standby time:",round(standbyTime,2))
print("Json time:",round(jsonTime,2))
print("Total time:",round(passiveTime+finishTime+linksTime+leaderTime+hipoTime+activeTime+superTime+levelTime+basicTime+jsonTime+multiplierTime+standbyTime,2))
print("Average per unit",round((passiveTime+finishTime+linksTime+leaderTime+hipoTime+activeTime+superTime+levelTime+basicTime+jsonTime+multiplierTime+standbyTime)/unitCount,5))