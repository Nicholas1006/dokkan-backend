from dokkanfunctions import *
import sqlite3
totalTime=time.time()
setupStart=time.time()
from globals import *
directory="data/"

import dotenv
dotenv.load_dotenv('.env')

GLOBAL_DB_LOC=os.path.dirname(os.path.abspath(__file__))+"/Dokkan_Asset_Downloader/card_assets/global/en/sqlite/current/en/database.db"
connection = sqlite3.connect(GLOBAL_DB_LOC)

DEVEXCEPTIONS=os.getenv('DEVEXCEPTIONS')  == "True"
print("DEVEXCEPTIONS",DEVEXCEPTIONS)
GLOBALPARSE=os.getenv('GLOBALPARSE')  == "True"
print("GLOBALPARSE",GLOBALPARSE)
MAKEJSON=os.getenv('MAKEJSON')  == "True"
print("MAKEJSON",MAKEJSON)
DEBUG=os.getenv('DEBUG')  == "True"
print("DEBUG",DEBUG)

CALCPASSIVE=os.getenv('CALCPASSIVE')  == "True"
print("CALCPASSIVE",CALCPASSIVE)
CALCLINKS=os.getenv('CALCLINKS')  == "True"
print("CALCLINKS",CALCLINKS)
CALCLEADER=os.getenv('CALCLEADER')  == "True"
print("CALCLEADER",CALCLEADER)
CALCHIPO=os.getenv('CALCHIPO')  == "True"
print("CALCHIPO",CALCHIPO)
CALCORBS=os.getenv('CALCORBS')  == "True"
print("CALCORBS",CALCORBS)
CALCACTIVE=os.getenv('CALCACTIVE')  == "True"
print("CALCACTIVE",CALCACTIVE)
CALCSUPERATTACK=os.getenv('CALCSUPERATTACK')  == "True"
print("CALCSUPERATTACK",CALCSUPERATTACK)
CALCLEVELS=os.getenv('CALCLEVELS')  == "True"
print("CALCLEVELS",CALCLEVELS)
CALCBASIC=os.getenv('CALCBASIC')  == "True"
print("CALCBASIC",CALCBASIC)
CALCMULTIPLIER=os.getenv('CALCMULTIPLIER')  == "True"
print("CALCMULTIPLIER",CALCMULTIPLIER)
CALCFINISH=os.getenv('CALCFINISH')  == "True"
print("CALCFINISH",CALCFINISH)
CALCSTANDBY=os.getenv('CALCSTANDBY')  == "True"
print("CALCSTANDBY",CALCSTANDBY)
CALCCIRCLE=os.getenv('CALCCIRCLE')  == "True"
print("CALCCIRCLE",CALCCIRCLE)
CALCAWAKENINGS=os.getenv('CALCAWAKENINGS')  == "True"
print("CALCAWAKENINGS",CALCAWAKENINGS)
CALCTRANSFORMATIONS=os.getenv('CALCTRANSFORMATIONS')  == "True"
print("CALCTRANSFORMATIONS",CALCTRANSFORMATIONS)

setupTime=0.0
passiveTime=0.0
leaderTime=0.0
hipoTime=0.0
orbsTime=0.0
activeTime=0.0
superTime=0.0
levelTime=0.0
basicTime=0.0
jsonTime=0.0
standbyTime=0.0
finishTime=0.0
linksTime=0.0
circleTime=0.0
backtrackTime=0.0
highestLeaderTime=0.0
multiplierTime=0.0

cardIDsToCheck=["1010901"]
#cardIDsToCheck=["4026911","4025741","4028381","4026401","4027631","4027301","4025781","4026541"]

cardsToCheck=[]

leaderSkills=[]
    

if GLOBALPARSE:
    for unit in cards[1:]:
        if qualifyOwnableSQL(connection,unit[0]):
            cardsToCheck.append(unit)
else:
    for ID in cardIDsToCheck:
        for unit in cards[1:]:
            if unit[0]==ID:
                if(qualifyOwnableSQL(connection,unit[0])):
                    cardsToCheck.append(unit)
                else:
                    print("UNUSABLE UNIT",unit[0])

missingPassiveCount=0
missingUnitCount=0

unitCount=0
passivecount=0
#passive skill set id is mainunit[21]
#passive=(passivename(mainunit,passive_skills))
#passiveIdList=getpassiveid(mainunit,cards,optimal_awakening_growths,passive_skill_set_relations,eza)
#print(passive)
HiPoBoards={}

unitsChecked=1

totalUnitJson={}
totalEZAUnitJson={}
totalSEZAUnitJson={}

dokkanAwakenings={}
transformations={}

print("Setup time:",round(time.time()-setupStart,2))
for unit in cardsToCheck[:]:
    print(str(unitsChecked)+"/"+str(len(cardsToCheck))+" "+unit[0])
    unitsChecked=unitsChecked+1
    ezaTrueFalse=[False]
    if(checkEza(unit[0])):
        ezaTrueFalse=[False,True]
    for eza in ezaTrueFalse:
        if(checkSeza(unit[0]) and eza):
            sezaTrueFalse=[False,True]
        else:
            sezaTrueFalse=[False]
        for seza in sezaTrueFalse:
            unitCount=unitCount+1
            unitDictionary={}
            unit1=swapToUnitWith1(unit)
            if(CALCBASIC):
                basicStart=time.time()
                unitDictionary["ID"]=unit[0]
                unitDictionary["Type"]=getUnitTypeSQL(connection,unit[0])
                unitDictionary["Class"]=getUnitClassSQL(connection,unit[0])
                unitDictionary["Name"]=getNameSQL(connection,unit[0])
                unitDictionary["Rarity"]=getRaritySQL(connection,unit[0])
                unitDictionary["Min Level"]=getMinLevelSQL(connection,unit[0],eza)
                unitDictionary["Max Level"]=getMaxLevelSQL(connection,unit[0],eza)
                unitDictionary["Categories"]=getAllCategoriesSQL(connection,unit[0])
                unitDictionary["Can EZA"]=checkEzaSQL(connection,unit[0])
                unitDictionary["Can SEZA"]=checkSezaSQL(connection,unit[0])
                if(seza):
                    unitDictionary["Eza Level"]="eza"
                elif(eza):
                    unitDictionary["Eza Level"]="seza"
                else:
                    unitDictionary["Eza Level"]="none"
                basicTime+=time.time()-basicStart
            

            if(CALCLINKS):
                linksStart=time.time()
                #unitDictionary["Links"]=getalllinkswithbuffs(unit)
                unitDictionary["Links"]=getAllLinksSQL(connection,unit[0])
                linksTime+=time.time()-linksStart

            unitDictionary["Resource ID"]=getResourceIDSQL(connection,unit[0])

            unitDictionary["Passive"]={}
            if(CALCPASSIVE):
                passiveStart=time.time()
                unitDictionary["Passive"]=parsePassiveSkillSQL(connection,unit,eza,seza,DEVEXCEPTIONS)
                unitDictionary["Itemized Passive Description"]=parsePassiveSkillItemizedDescriptionSQL(connection,unit[0],eza,seza)
                passiveTime+=time.time()-passiveStart

            unitDictionary["Max Attacks"]=1
            unitDictionary["Max Super Attacks"]=1
            if(getRaritySQL(connection,unit[0])in ["lr","ur"]):
                unitDictionary["Max Super Attacks"]+=1
                unitDictionary["Max Attacks"]+=1
            for passive in unitDictionary["Passive"]:
                if("Additional Attack" in unitDictionary["Passive"][passive]):
                    if(unitDictionary["Passive"][passive]["Additional Attack"]["Chance of super"]!="0"):
                        if(unitDictionary["Passive"][passive]["Additional Attack"]["Chance of another additional"]!="0"):
                            unitDictionary["Max Super Attacks"]+=2
                            unitDictionary["Max Attacks"]+=2    
                        else:
                            unitDictionary["Max Super Attacks"]+=1
                            unitDictionary["Max Attacks"]+=1
                    else:
                        if(unitDictionary["Passive"][passive]["Additional Attack"]["Chance of another additional"]!="0"):
                            unitDictionary["Max Attacks"]+=2    
                        else:
                            unitDictionary["Max Attacks"]+=1

            


            unitDictionary["Stats at levels"]={}
            if(CALCLEVELS):
                levelStart=time.time()
                unitDictionary["Stats at levels"]=getStatsAtAllLevelsSQL(connection,unit[0],unitDictionary["Min Level"],unitDictionary["Max Level"])
                levelTime+=time.time()-levelStart
            
            unitDictionary["Leader Skill"]={}
            if(CALCLEADER and unit[22]!=""):
                leaderStart=time.time()
                unitDictionary["Leader Skill"]=parseLeaderSkill(unit,eza,DEVEXCEPTIONS)
                leaderSkills.append(unitDictionary["Leader Skill"])
                leaderTime+=time.time()-leaderStart

            
            unitDictionary["Hidden Potential"]={}
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
            if(unitDictionary["Standby Skill"] != None):
                if("Exchanges to" in unitDictionary["Standby Skill"]):
                    unitDictionary["Transformations"].append(unitDictionary["Standby Skill"]["Exchanges to"])
                    if(unit[0] in transformations):
                        transformations[unit[0]].append(unitDictionary["Standby Skill"]["Exchanges to"])
                    else:
                        transformations[unit[0]]=[unitDictionary["Standby Skill"]["Exchanges to"]]
            if(unitDictionary["Finish Skill"] != None):
                for finishRow in unitDictionary["Finish Skill"]:
                    unitDictionary["Transformations"].append(unitDictionary["Finish Skill"][finishRow]["Exchanges to"])
                    if(unit[0] in transformations):
                        transformations[unit[0]].append(unitDictionary["Finish Skill"][finishRow]["Exchanges to"])
                    else:
                        transformations[unit[0]]=[unitDictionary["Finish Skill"][finishRow]["Exchanges to"]]
            unitDictionary["Max Appearances In Form"]=maxAppearancesInForm(unitDictionary["Passive"],DEVEXCEPTIONS)

            
            if(CALCPASSIVE):
                if(unitDictionary["Passive"]!=None):
                    for passiveLine in unitDictionary["Passive"]:
                        if "Transformation" in unitDictionary["Passive"][passiveLine]:
                            unitDictionary["Transformations"].append(unitDictionary["Passive"][passiveLine]["Transformation"]["Unit"])
                            if(unit[0] in transformations):
                                transformations[unit[0]].append(unitDictionary["Passive"][passiveLine]["Transformation"]["Unit"])
                            else:
                                transformations[unit[0]]=[unitDictionary["Passive"][passiveLine]["Transformation"]["Unit"]]
                        if("Standby" in unitDictionary["Passive"][passiveLine]):
                            if("Change form" in unitDictionary["Passive"][passiveLine]["Standby"]):
                                unitDictionary["Transformations"].append(unitDictionary["Passive"][passiveLine]["Standby"]["Change form"]["Unit"])
                                if(unit[0] in transformations):
                                    transformations[unit[0]].append(unitDictionary["Passive"][passiveLine]["Standby"]["Change form"]["Unit"])
                                else:
                                    transformations[unit[0]]=[unitDictionary["Passive"][passiveLine]["Standby"]["Change form"]["Unit"]]
                        if("Reversible exchange" in unitDictionary["Passive"][passiveLine]):
                            unitDictionary["Transformations"].append(unitDictionary["Passive"][passiveLine]["Reversible exchange"]["Unit"])
                            if(unit[0] in transformations):
                                transformations[unit[0]].append(unitDictionary["Passive"][passiveLine]["Reversible exchange"]["Unit"])
                            else:
                                transformations[unit[0]]=[unitDictionary["Passive"][passiveLine]["Reversible exchange"]["Unit"]]
                        if("Domain" in unitDictionary["Passive"][passiveLine]):
                            unitDictionary["Domain"]={
                                "ID":unitDictionary["Passive"][passiveLine]["Domain"],
                                "Locked": False
                            }
            if(CALCACTIVE): 
                if(unitDictionary["Active Skill"]!=None):
                    for activeLine in unitDictionary["Active Skill"]["Effects"]:
                        if "Unit" in unitDictionary["Active Skill"]["Effects"][activeLine]["Effect"]:
                            unitDictionary["Transformations"].append(unitDictionary["Active Skill"]["Effects"][activeLine]["Effect"]["Unit"])
                            if(unit[0] in transformations):
                                transformations[unit[0]].append(unitDictionary["Active Skill"]["Effects"][activeLine]["Effect"]["Unit"])
                            else:
                                transformations[unit[0]]=[unitDictionary["Active Skill"]["Effects"][activeLine]["Effect"]["Unit"]]

            if(CALCTRANSFORMATIONS):
                for transformation in unitDictionary["Transformations"]:
                    if(unit[0][-1]=="1" and str(transformation)[-1]=="0"):
                        unitDictionary["Transformations"][unitDictionary["Transformations"].index(transformation)]=str(transformation)[:-1]+"1"
                    elif(unit[0][-1]=="0" and str(transformation)[-1]=="1"):
                        unitDictionary["Transformations"][unitDictionary["Transformations"].index(transformation)]=str(transformation)[:-1]+"0"
                unitDictionary["Transformations"]=list(set(unitDictionary["Transformations"]))

            unitDictionary["Dokkan awakenings"]=[]
            unitDictionary["Dokkan Reverse awakenings"]=[]
            if(CALCAWAKENINGS):
                relevant_awakenings=searchbycolumn(code=unit1[0],database=card_awakening_routes,column=2)
                relevant_awakenings=searchbycolumn(code="CardAwakeningRoute::Dokkan",database=relevant_awakenings,column=1)
                for awakening in relevant_awakenings:
                    unitDictionary["Dokkan awakenings"].append(awakening[3])
                    dokkanAwakenings[unit[0]]=awakening[3]
                
                for awakening in dokkanAwakenings:
                    if(dokkanAwakenings[awakening]==unit[0]):
                        unitDictionary["Dokkan Reverse awakenings"].append(awakening)

            unitDictionary["Hidden Potential"]={}
            if(CALCHIPO):
                hipoStart=time.time()
                if(unit[52]=='' and (getrarity(unit)=="ur" or getrarity(unit)=="lr")):
                    unitDictionary["Hidden Potential"]={"INCOMPLETE":True}

                else:
                    if(unit[52][:-2]not in HiPoBoards):
                        HiPoBoards[unit[52][:-2]]=parseHiddenPotential(unit[52][:-2],DEVEXCEPTIONS)
                    unitDictionary["Hidden Potential"]=HiPoBoards[unit[52][:-2]]
                hipoTime+=time.time()-hipoStart

            if(CALCORBS):
                orbsStart=time.time()
                if(unitDictionary["Rarity"]=="ur" or unitDictionary["Rarity"]=="lr"):
                    unitDictionary["Orbs"]=calculateOrbs(unit,unitDictionary)
                else:
                    unitDictionary["Orbs"]={
                        "gold":{"HP":0,"ATK":0,"DEF":0},
                        "silver": {"HP":0,"ATK":0,"DEF":0},
                        "bronze": {"HP":0,"ATK":0,"DEF":0},
                        "overall":{"HP":0,"ATK":0,"DEF":0}
                    }
                orbsTime+=time.time()-orbsStart

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

            

            




            jsonName=unit[0]

            #unitDictionary = {k: unitDictionary[k] for k in sorted(unitDictionary)}



            if(seza):
                totalSEZAUnitJson[jsonName]=unitDictionary
            elif(eza):
                totalEZAUnitJson[jsonName]=unitDictionary
            else:
                totalUnitJson[jsonName]=unitDictionary

#backtrack fix all transformations and transforms from
backtrackstart=time.time()
for jsonList in [totalUnitJson,totalEZAUnitJson,totalSEZAUnitJson]:
    for unit in jsonList:
        if(jsonList[unit]["Transformations"]!=[]):
            possibleFutureForms=[]
            accountedFutureForms=[]
            for transformation in jsonList[unit]["Transformations"]:
                possibleFutureForms.append(transformation)
            while(possibleFutureForms!=[]):
                transformation=possibleFutureForms.pop(0)
                accountedFutureForms.append(transformation)
                if(transformation in jsonList):
                    if(unit not in jsonList[transformation]["Transforms from"]):
                        jsonList[transformation]["Transforms from"].append(unit)
                    if(jsonList[transformation]["Transformations"]!=[]):
                        for futureForm in jsonList[transformation]["Transformations"]:
                            if(futureForm not in accountedFutureForms and futureForm!=unit):
                                possibleFutureForms.append(futureForm)
        
        if(jsonList[unit]["Transforms from"]!=[]):
            possiblePastForms=[]
            accountedPastForms=[]
            for transformation in jsonList[unit]["Transforms from"]:
                possiblePastForms.append(transformation)
            while(possiblePastForms!=[]):
                transformation=possiblePastForms.pop(0)
                accountedPastForms.append(transformation)
                if(transformation in jsonList):
                    if(unit not in jsonList[transformation]["Transformations"]):
                        jsonList[transformation]["Transformations"].append(unit)
                    if(jsonList[transformation]["Transforms from"]!=[]):
                        for PastForm in jsonList[transformation]["Transforms from"]:
                            if(PastForm not in accountedPastForms and PastForm!=unit):
                                possiblePastForms.append(PastForm)
        
        #fix incomplete hidden potential systems
        if("INCOMPLETE" in jsonList[unit]["Hidden Potential"]):
            betterHiPoBoardFound=False
            for deTransformedUnit in jsonList[unit]["Transforms from"]:
                if(betterHiPoBoardFound==False):
                    possibleBoard=searchbyid(code=deTransformedUnit,codecolumn=0,database=cards,column=52)[0]
                    if(possibleBoard!=''):
                        betterHiPoBoardFound=possibleBoard[:-2]

            if(betterHiPoBoardFound not in HiPoBoards):
                HiPoBoards[betterHiPoBoardFound]=parseHiddenPotential(betterHiPoBoardFound,DEVEXCEPTIONS)
            jsonList[unit]["Hidden Potential"]=HiPoBoards[betterHiPoBoardFound]
                    
for jsonList in [totalUnitJson,totalEZAUnitJson,totalSEZAUnitJson]:
    for unit in jsonList:
        jsonList[unit]["Transformations"]=[str(x) for x in jsonList[unit]["Transformations"]]
        jsonList[unit]["Transformations"]=list(set(jsonList[unit]["Transformations"]))
        jsonList[unit]["Transformations"].sort()

        jsonList[unit]["Transforms from"]=[str(x) for x in jsonList[unit]["Transforms from"]]
        jsonList[unit]["Transforms from"]=list(set(jsonList[unit]["Transforms from"]))
        jsonList[unit]["Transforms from"].sort()


#place any domains onto transformed units
for jsonList in [totalUnitJson,totalEZAUnitJson,totalSEZAUnitJson]:
    for unit in jsonList:
        if(jsonList[unit]["Active Skill"]!=None):
            if("Domain" in jsonList[unit]["Active Skill"]):
                if(jsonList[unit]["Transformations"]!=[]):
                    for transformation in jsonList[unit]["Transformations"]:
                        jsonList[transformation]["Domain"]={
                            "ID":jsonList[unit]["Active Skill"]["Domain"],
                            "Locked":(jsonList[transformation]["Max Appearances In Form"]!=50)
                        }
                else:
                    jsonList[unit]["Domain"]={
                        "ID":jsonList[unit]["Active Skill"]["Domain"],
                        "Locked":False
                    }
backtrackTime+=time.time()-backtrackstart

#find the max lead for all units
if(CALCLEADER):
    highestLeaderStartTime=time.time()
    for unit in totalUnitJson:
        totalUnitJson[unit]["Max Leader Skill"]=findHighestLeaderSkill(totalUnitJson[unit],leaderSkills,DEVEXCEPTIONS)
        if(unit in totalEZAUnitJson):
            totalEZAUnitJson[unit]["Max Leader Skill"]=totalUnitJson[unit]["Max Leader Skill"]
        if(unit in totalSEZAUnitJson):
            totalSEZAUnitJson[unit]["Max Leader Skill"]=totalUnitJson[unit]["Max Leader Skill"]
    highestLeaderTime=time.time()-highestLeaderStartTime

            

                
if(MAKEJSON):
    jsonStart=time.time()
    for unit in totalUnitJson:
        turnintoJson(totalUnitJson[unit], unit, directoryName="temp_jsons/jsons")
    for unit in totalEZAUnitJson:
        turnintoJson(totalEZAUnitJson[unit], unit, directoryName="temp_jsons/jsonsEZA")
    for unit in totalSEZAUnitJson:
        turnintoJson(totalSEZAUnitJson[unit], unit, directoryName="temp_jsons/jsonsSEZA")
    jsonTime+=time.time()-jsonStart
        
totalTime=time.time()-totalTime

print("Basic time:",round(basicTime,2))
print("Links time:",round(linksTime,2))
print("Leader time:",round(leaderTime,2))
print("Passive time:",round(passiveTime,2))
print("Super time:",round(superTime,2))
print("Level time:",round(levelTime,2))
print("HiPo time:",round(hipoTime,2))
print("Orbs time:",round(orbsTime,2))
print("Ki segments time:",round(circleTime,2))
print("Multiplier time:",round(multiplierTime,2))
print("Active time:",round(activeTime,2))
print("Standby time:",round(standbyTime,2))
print("Highest Leader time:",round(highestLeaderTime,2))
print("Json time:",round(jsonTime,2))
print("Backtrack time:",round(backtrackTime,2))
print("Other time:" ,round(totalTime-(passiveTime+finishTime+linksTime+leaderTime+hipoTime+orbsTime+activeTime+superTime+levelTime+basicTime+jsonTime+multiplierTime+standbyTime+highestLeaderTime+backtrackTime),2))
print("Total time:",round(totalTime,2))
print("Average per unit",round((totalTime)/unitCount,5))