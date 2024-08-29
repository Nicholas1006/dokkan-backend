from ast import parse
from globals import *
from calendar import c
import csv
from xml import dom
from colorama import Fore
import requests
import os
from PIL import Image
import time
import math
import json
import shutil
from datetime import datetime


def getUnitCost(unit):
    return(unit[4])

def getUnitReleaseTime(card):
    releaseDateTime=card[53]
    releaseInt=int(datetime.strptime(releaseDateTime, "%Y-%m-%d %H:%M:%S").timestamp())
    return(releaseInt)

def getCharacterNameID(unit):
    return(unit[3])

def sub_target_types_extractor(sub_target_type_set_id,DEVELOPEREXCEPTIONS=False):
    temp=searchbycolumn(code=sub_target_type_set_id,database=sub_target_typesJP,column=1)
    output={}
    output["Category"]=[]
    output["Excluded Category"]=[]
    for line in temp:   
        if(line[2]=="1"):
            output["Category"].append(CategoryExtractor(line[3]))
        elif(line[2]=="2"):
            output["Excluded Category"].append(CategoryExtractor(line[3]))
        elif(line[2]=="3"):
            output["Amount of times to turn giant"]=1
        else:
            output["Category"].append("UNKNOWN")
            if(DEVELOPEREXCEPTIONS==True):
                raise Exception("Unknown sub target type")
    return (output)

def openJson(prefix, name, suffix):
    # Construct the file path
    file_path = f"{prefix}{name}{suffix}"
    
    # Open the JSON file and load its content
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file {file_path}.")
        return None


def filterUltraList(ultraList,slot,filter):
    #filter must be a List
    output=[]
    for line in ultraList:
        if(line[slot] in filter):
            output.append(line)
    return(output)

def removeDuplicatesUltraList(ultraList,slot):
    output=[]
    for line in ultraList:
        if(line[slot] not in output):
            output.append(line)
    return(output)

def superAttackMultiplierExtractor(superAttackID,super_attack_lvl,DEVEXCEPTIONS=False):
    specialRow=searchbycolumn(code=superAttackID,database=special_setsJP,column=0)
    growth_rate=int(specialRow[0][6])
    increase_rate=int(specialRow[0][5])
    multiplier=(100)+(increase_rate)+(growth_rate*(super_attack_lvl-1))

    return(multiplier)
    
def getMinLevel(unit,eza=False):
    #if its a z unit return the max level of its previous form
    #if its an eza unit return the max level of itself
    unit0=swapToUnitWith0(unit)
    oldRarity=unit0[5]
    #If the unit has been z awakened
    if(unit[5]!=unit0[5]):
        return(int(unit0[13]))
    elif(eza):
        return(int(unit[13]))
    else:
        return(1)
def getMaxLevel(unit,eza=False):
    if(eza):
        cardOptimalAwakeningGrowthID=unit[16][:-2]
        growthRows=searchbycolumn(code=cardOptimalAwakeningGrowthID,database=optimal_awakening_growthsJP,column=1)
        maxLevel=int(unit[14])
        for growthRow in growthRows:
            maxLevel=max(maxLevel,int(growthRow[3]))
        return(maxLevel)
    else:
        return(int(unit[13]))

def parse_domain_efficiacy(efficiacy):
    output={}
    output["ID"]=efficiacy[0]
    if(efficiacy[2]=="1"):
        output["Timing"]="At the start of turn"
    elif(efficiacy[2]=="18"):
        output["Timing"]="On domain Being out"
    else:
        print("UNKNOWN DOMAIN EFFICIACY TIMING:",efficiacy[2])

    #NO DEFENSE BUFF
    if(efficiacy[3]=="1"):
        output["Effect"]={"Type":"ATK & DEF","ATK":max(int(efficiacy[8]),int(efficiacy[9])),"DEF":0}
    #PRESUMABLY NO ATTACK BUFF
    elif(efficiacy[3]=="2"):
        output["Effect"]={"Type":"ATK & DEF","ATK":0,"DEF":max(int(efficiacy[8]),int(efficiacy[9]))}
    elif(efficiacy[3]=="3"):
        output["Effect"]={"Type":"ATK & DEF","ATK":int(efficiacy[8]),"DEF":int(efficiacy[9])}
    elif(efficiacy[3]=="121"):
        output["Effect"]={"Type":"Closes domain"}
    elif(efficiacy[3]=="122"):
        output["Effect"]={"Type":"Increases damage recieved","Amount":int(efficiacy[8])}
    elif(efficiacy[3]=="129"):
        output["Effect"]={"Type":"Disables guaranteed hit effect"}
    else:
        print("UNKNOWN DOMAIN EFFICIACY TYPE:",efficiacy[3])

    if(efficiacy[4]=="0"):
        pass
    elif(efficiacy[4]=="2"):
        pass
    else:
        print("UNKNOWN DOMAIN EFFICIACY TARGET:",efficiacy[4])

    output["Turn activation"]=efficiacy[5]

    if(efficiacy[6]=="0"):
        pass
    else:
        output["Is Once Only"]=True

    if(efficiacy[7]=="100"):
        pass
    else:
        output["Chance to activate"]=efficiacy[7]

    if(efficiacy[12]!=""):
        causalityCondition=logicalCausalityExtractor(efficiacy[12])
        causalityCondition=CausalityLogicalExtractor(unit=[],causality=causalityCondition,DEVEXCEPTIONS=False)
        for CausalityKey in causalityCondition["Causalities"].keys():
            ButtonName=causalityCondition["Causalities"][CausalityKey]["Button"]["Name"]
            if("category" in ButtonName):
                CategoryName=ButtonName.split(" on the ")[1].split(" category")[0]
                causalityCondition["Causalities"][CausalityKey]={"Class": "any","Category":CategoryName}
            else:
                ClassName=ButtonName.split(" character ")[1].split(" class")[0]
                ClassName.replace("super","Super").replace("extreme","Extreme")
                causalityCondition["Causalities"][CausalityKey]={"Class": ClassName,"Category":"any"}
        output["superCondition"]=causalityCondition


    return(output)

def getSuperAttackTypes(unit, eza=False):
    output=[]
    card_specialss=searchbycolumn(code=unit[0],column=1,database=card_specialsJP)
    card_specialss=removeDuplicatesUltraList(ultraList=card_specialss,slot=0)
    for card_special in card_specialss:
        if((eza and int(unit[14])<int(card_special[5])) or (eza==False and int(unit[14])>=int(card_special[5]))):
            output.append(getSuperAttackType(card_special))
    return output

def getSuperAttackType(card_special):
    view_id=card_special[7]
    special_category_id=searchbyid(code=view_id,codecolumn=0,database=special_viewsJP,column=7)[0]
    if(special_category_id==""):
        return "Other"
    elif(special_category_id=="1.0"):
        return "Ki blast"
    elif(special_category_id=="2.0"):
        return "Unarmed"
    elif(special_category_id=="3.0"):
        return "Physical"

def parseSuperAttack(unit,eza=False,DEVEXCEPTIONS=False):
    output={}

    card_specialss=searchbycolumn(code=unit[0],column=1,database=card_specialsJP)
    card_specialss=removeDuplicatesUltraList(ultraList=card_specialss,slot=0)
    for card_special in card_specialss:
        if((eza and int(unit[14])<int(card_special[5])) or (eza==False and int(unit[14])>=int(card_special[5]))):
            superAttackDictionary={}
            if(JPExclusiveCheck(unit[0])==False):
                superSetGB=searchbycolumn(code=card_special[2],column=0,database=special_setsGB)
            else:
                superSetGB=[]
            superSet=searchbycolumn(code=card_special[2],column=0,database=special_setsJP)
            superAttackDictionary["superID"]=superSet[0][0]
            view_id=card_special[7]
            special_category_id=searchbyid(code=view_id,codecolumn=0,database=special_viewsJP,column=7)[0]
            if(special_category_id==""):
                superAttackDictionary["Type"]="Other"
            elif(special_category_id=="1.0"):
                superAttackDictionary["Type"]="Ki blast"
            elif(special_category_id=="2.0"):
                superAttackDictionary["Type"]="Unarmed"
            elif(special_category_id=="3.0"):
                superAttackDictionary["Type"]="Physical"


            superAttackDictionary["special_name_no"]=searchbyid(code=view_id,codecolumn=0,database=special_viewsJP,column=3)[0]
            if(superSetGB==[]):
                superAttackDictionary["superName"]=superSet[0][1]
                superAttackDictionary["superDescription"]=superSet[0][2]
            else:
                superAttackDictionary["superName"]=superSetGB[0][1]
                superAttackDictionary["superDescription"]=superSetGB[0][2]

            
            superAttackDictionary["superMinKi"]=card_special[6]
            superAttackDictionary["superPriority"]=card_special[3]
            superAttackDictionary["superStyle"]=card_special[4]
            superAttackDictionary["superMinLVL"]=card_special[5]
            superAttackDictionary["superCausality"]=superSet[0][3]
            superAttackDictionary["superAimTarget"]=superSet[0][4]
            superAttackDictionary["superBuffs"]={}
            superAttackDictionary["superIsInactive"]=superSet[0][7]
            if(superAttackDictionary["superStyle"]=="Condition"):
                causalityCondition=logicalCausalityExtractor(card_special[15])
                causalityCondition=CausalityLogicalExtractor(unit,causalityCondition,DEVEXCEPTIONS=DEVEXCEPTIONS)
                superAttackDictionary["superCondition"]=causalityCondition
            superAttackDictionary["SpecialBonus"]={}
            superAttackDictionary["SpecialBonus"]["ID"]=card_special[9]
            SALevel=int(unit[14])
            if(eza):
                cardOptimalAwakeningGrowthID=unit[16][:-2]
                growthRows=searchbycolumn(code=cardOptimalAwakeningGrowthID,database=optimal_awakening_growthsJP,column=1)
                for growthRow in growthRows:
                    SALevel = max(int(growthRow[4]), SALevel)
            superAttackDictionary["Multiplier"]=superAttackMultiplierExtractor(superAttackID=superAttackDictionary["superID"],super_attack_lvl=SALevel,DEVEXCEPTIONS=DEVEXCEPTIONS)
            card_supers=searchbycolumn(code=superAttackDictionary["superID"],column=1,database=specialsJP)
            for special in card_supers:
                specialsEffect=parseSpecials(special,DEVEXCEPTIONS)    
                superAttackDictionary["superBuffs"][special[0]]=specialsEffect
            output[card_special[2]]=superAttackDictionary

            if(superAttackDictionary["SpecialBonus"]["ID"]!="0"):
                superAttackDictionary["Multiplier"]=superAttackMultiplierExtractor(superAttackID=superAttackDictionary["superID"],super_attack_lvl=SALevel,DEVEXCEPTIONS=DEVEXCEPTIONS)
                special_bonus=searchbycolumn(code=superAttackDictionary["SpecialBonus"]["ID"],column=0,database=special_bonusesJP)
                if(JPExclusiveCheck(unit[0])==False):
                    special_bonus=searchbycolumn(code=superAttackDictionary["SpecialBonus"]["ID"],column=0,database=special_bonusesGB)
                special_bonus=special_bonus[0]
                superAttackDictionary["SpecialBonus"]["Type"]=special_bonus[1]
                superAttackDictionary["SpecialBonus"]["Description"]=special_bonus[2]
                superAttackDictionary["SpecialBonus"]["Chance"]=special_bonus[7]
                superAttackDictionary["SpecialBonus"]["Duration"]=special_bonus[6]
                if(special_bonus[3]=="1"):
                    superAttackDictionary["SpecialBonus"]["Type"]="SA multiplier increase"
                    superAttackDictionary["SpecialBonus"]["Amount"]=special_bonus[9]
                    
                elif(special_bonus[3]=="2"):
                    superAttackDictionary["SpecialBonus"]["Type"]="Super attack Defense increase"
                    superAttackDictionary["SpecialBonus"]["Amount"]=special_bonus[9]
                    if(special_bonus[3]=="3"):
                        superAttackDictionary["SpecialBonus"]["Amount"]*=-1
                elif(special_bonus[3]=="3"):
                    superAttackDictionary["SpecialBonus"]["Type"]="Super attack Attack and Defense increase"
                    superAttackDictionary["SpecialBonus"]["Amount"]=special_bonus[9]
                    if(special_bonus[3]=="3"):
                        superAttackDictionary["SpecialBonus"]["Amount"]*=-1
                elif(special_bonus[3]=="63"):
                    superAttackDictionary["SpecialBonus"]["Type"]="Ki requirement decrease"
                    superAttackDictionary["SpecialBonus"]["Amount"]=special_bonus[9]
            
    return(output)

def parseSpecials(specialRow,DEVEXCEPTIONS=False):
    output={}
    output["Type"]=specialRow[2][9:]
    output["Chance"]=specialRow[7]
    output["Duration"]=specialRow[6]
    output["Buff"]={}
    if(specialRow[5]=="0"):
        output["Buff"]["Type"]="Raw stats"
        output["Buff"]["+ or -"]="+"

    elif(specialRow[5]=="1"):
        output["Buff"]["Type"]="Raw stats"
        output["Buff"]["+ or -"]="-"

    elif(specialRow[5]=="2"):
        output["Buff"]["Type"]="Percentage"
        output["Buff"]["+ or -"]="+"

    elif(specialRow[5]=="3"):
        output["Buff"]["Type"]="Percentage"
        output["Buff"]["+ or -"]="-"
    else:
        output["Buff"]["Type"]="Unknown"
        output["Buff"]["+ or -"]="Unknown"
        if(DEVEXCEPTIONS==True):
                raise Exception("Unknown stat increase type")

    if(specialRow[4]=="1"):
        output["Target"]="Self"
    elif(specialRow[4]=="2"):
        output["Target"]="Allies"
    elif(specialRow[4]=="3"):
        output["Target"]="Enemy"
    elif(specialRow[4]=="4"):
        output["Target"]="All Enemies"
    elif(specialRow[4]=="12"):
        output["Target"]="Super class Allies"
    elif(specialRow[4]=="13"):
        output["Target"]="Extreme class Allies"
    elif(specialRow[4]=="16"):
        output["Target"]="Allies (self excluded)"
    else:
        output["Target"]="UNKNOWN"
        if(DEVEXCEPTIONS==True):
            raise Exception("Unknown target type")

    if(specialRow[3]=="1"):
        output["ATK"]=specialRow[9]
    elif(specialRow[3]=="2"):
        output["DEF"]=specialRow[9]
    elif(specialRow[3]=="3"):
        output["ATK"]=specialRow[9]
        output["DEF"]=specialRow[10]
    elif(specialRow[3]=="9"):
        output["Status"]="Stun"
    elif(specialRow[3]=="24"):
        output["Status"]="Disabled guard"
    elif(specialRow[3]=="48"):
        output["Status"]="Seals"
    elif(specialRow[3]=="76"):
        output["Status"]="Effective against all"
    elif(specialRow[3]=="84"):
        output["Heals"]=specialRow[9]
    elif(specialRow[3]=="90"):
        output["Crit Chance"]=specialRow[9]
    elif(specialRow[3]=="91"):
        output["Dodge chance"]=specialRow[9]
    elif(specialRow[3]=="111"):
        output["Status"]="Disabled action"
    else:
        output["Status"]="UNKNOWN"
        if(DEVEXCEPTIONS==True):
            raise Exception("Unknown special attack effect")
    return(output)
        
def parseHiddenPotential(Potential_board_id,DEVEXCEPTIONS=False):
    nodesSearched={}
    
    nodesSearching={}
    allNodes=searchbycolumn(code=Potential_board_id,column=1,database=potential_squaresJP)
    allNodeIDs=[node[0] for node in allNodes]
    relevantRelations=[]
    for connection in potential_square_relationsJP:
        if(connection[1] in allNodeIDs):
            relevantRelations.append(connection)
    pathNodes=[]
    for node in allNodes:
        if(node[4]=="1"):
            pathNodes.append(node[0])
        if("" in searchbyid(code=node[0],codecolumn=1,database=relevantRelations,column=2)):
            nodesSearched[node[0]]=0
    furthestNodesFound=nodesSearched.copy()
    newNodes=True
    
    while(newNodes==True):
        newNodes=False
        for node in furthestNodesFound:
            connections=searchbyid(code=node,codecolumn=1,database=relevantRelations,column=2)
            for connection in connections:
                if(connection!=""):
                    if(connection[:-2] not in pathNodes):
                        if(connection[:-2] not in nodesSearched and connection[:-2] not in nodesSearching):
                            nodesSearching[connection[:-2]]=nodesSearched[node]
                            newNodes=True
                    else:
                        if(connection[:-2] not in nodesSearched and connection[:-2] not in nodesSearching):
                            path=searchbyid(code=connection[:-2],codecolumn=0,database=potential_squaresJP,column=5)
                            nodesSearching[connection[:-2]]=1+int(path[0][:-2])
                            newNodes=True
        nodesSearched.update(nodesSearching)
        furthestNodesFound=nodesSearching.copy()
        nodesSearching={}
                







    output={}
    output[0]={"HP":0,"ATK":0,"DEF":0, "Additional": 0, "Crit": 0, "Evasion": 0, "Type ATK": 0, "Type DEF": 0, "Super Attack boost": 0, "Recovery boost": 0}
    output[1]={"HP":0,"ATK":0,"DEF":0, "Additional": 0, "Crit": 0, "Evasion": 0, "Type ATK": 0, "Type DEF": 0, "Super Attack boost": 0, "Recovery boost": 0}
    output[2]={"HP":0,"ATK":0,"DEF":0, "Additional": 0, "Crit": 0, "Evasion": 0, "Type ATK": 0, "Type DEF": 0, "Super Attack boost": 0, "Recovery boost": 0}
    output[3]={"HP":0,"ATK":0,"DEF":0, "Additional": 0, "Crit": 0, "Evasion": 0, "Type ATK": 0, "Type DEF": 0, "Super Attack boost": 0, "Recovery boost": 0}
    output[4]={"HP":0,"ATK":0,"DEF":0, "Additional": 0, "Crit": 0, "Evasion": 0, "Type ATK": 0, "Type DEF": 0, "Super Attack boost": 0, "Recovery boost": 0}
    for node in nodesSearched:
        eventid=searchbyid(code=node,codecolumn=0,database=potential_squaresJP,column=2)[0]
        event=searchbycolumn(code=eventid,database=potential_eventsJP,column=0)[0]
        if(event[1]=="PotentialEvent::Hp"):
            output[nodesSearched[node]]["HP"]+=int(event[3])
        elif(event[1]=="PotentialEvent::Atk"):
            output[nodesSearched[node]]["ATK"]+=int(event[3])
        elif(event[1]=="PotentialEvent::Defense"):
            output[nodesSearched[node]]["DEF"]+=int(event[3])
        elif(event[1]=="PotentialEvent::Skill" and event[2]=="1.0"):
            output[nodesSearched[node]]["Additional"]+=int(event[3])
        elif(event[1]=="PotentialEvent::Skill" and event[2]=="2.0"):
            output[nodesSearched[node]]["Crit"]+=int(event[3])
        elif(event[1]=="PotentialEvent::Skill" and event[2]=="3.0"):
            output[nodesSearched[node]]["Evasion"]+=int(event[3])
        elif(event[1]=="PotentialEvent::Skill" and event[2]=="4.0"):
            output[nodesSearched[node]]["Type ATK"]+=int(event[3])
        elif(event[1]=="PotentialEvent::Skill" and event[2]=="5.0"):
            output[nodesSearched[node]]["Type DEF"]+=int(event[3])
        elif(event[1]=="PotentialEvent::Skill" and event[2]=="6.0"):
            output[nodesSearched[node]]["Super Attack boost"]+=int(event[3])
        elif(event[1]=="PotentialEvent::Skill" and event[2]=="7.0"):
            output[nodesSearched[node]]["Recovery boost"]+=int(event[3])
    return(output)

def parseLeaderSkill(unit,eza,DEVEXCEPTIONS=False):
    output={}
    if(JPExclusiveCheck(unit[0])):
        leader_skill_name=searchbyid(code=unit[22][:-2],codecolumn=0,database=leader_skill_setsJP,column=1,)
        output["Name"]=leader_skill_name[0]
    else:
        leader_skill_name=searchbyid(code=unit[22][:-2],codecolumn=0,database=leader_skill_setsGB,column=1,)
        output["Name"]=leader_skill_name[0]
    leader_skill_set_id=unit[22][:-2]
    if(eza):
        optimal_awakening_rows=searchbycolumn(code=unit[16][:-2],column=1,database=optimal_awakening_growthsJP)
        for optimal_awakening_row in optimal_awakening_rows:
            if(optimal_awakening_row[6]!=unit[22][:-2]):
                leader_skill_set_id=optimal_awakening_row[6]
    leader_skill_lines=searchbycolumn(code=leader_skill_set_id,database=leader_skillsJP,column=1,printing=False)
    for leader_skill_line in leader_skill_lines:
        output[leader_skill_line[0]]={}
        output[leader_skill_line[0]]["Buff"]={}
        if(leader_skill_line[8]=="0"):
            output[leader_skill_line[0]]["Buff"]["Type"]="Raw stats"
            output[leader_skill_line[0]]["Buff"]["+ or -"]="+"

        elif(leader_skill_line[8]=="1"):
            output[leader_skill_line[0]]["Buff"]["Type"]="Raw stats"
            output[leader_skill_line[0]]["Buff"]["+ or -"]="-"

        elif(leader_skill_line[8]=="2"):
            output[leader_skill_line[0]]["Buff"]["Type"]="Percentage"
            output[leader_skill_line[0]]["Buff"]["+ or -"]="+"

        elif(leader_skill_line[8]=="3"):
            output[leader_skill_line[0]]["Buff"]["Type"]="Percentage"
            output[leader_skill_line[0]]["Buff"]["+ or -"]="-"
        else:
            output[leader_skill_line[0]]["Buff"]["Type"]="Unknown"
            output[leader_skill_line[0]]["Buff"]["+ or -"]="Unknown"
            if(DEVEXCEPTIONS==True):
                    raise Exception("Unknown stat increase type")
        
        output[leader_skill_line[0]]["Target"]={}
        efficiacy_values=leader_skill_line[7].replace("[","").replace("]","").split(",")
        output[leader_skill_line[0]]["Target"]=(sub_target_types_extractor(leader_skill_line[4],DEVEXCEPTIONS))
        if(leader_skill_line[3]=="4"):
            output[leader_skill_line[0]]["Target"]["Allies or enemies"]="Enemies"
        elif(leader_skill_line[3]=="2"):
            output[leader_skill_line[0]]["Target"]["Allies or enemies"]="Allies"
        if leader_skill_line[6]=="0":
            output[leader_skill_line[0]]["NOT WORKING"]=True
        elif(leader_skill_line[6]=="1"):
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[0])
        elif(leader_skill_line[6]=="2"):
            #Enemy ["DEF", ??, ??] 
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[0])
        elif(leader_skill_line[6]=="3"):
            #Category ["HP and ATK", "DEF", ""] 
            output[leader_skill_line[0]]["HP"]=int(efficiacy_values[0])
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[0])
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="5"):
            #Category ["Ki", "", ""] 
            output[leader_skill_line[0]]["Ki"]=int(efficiacy_values[0])
        elif(leader_skill_line[6]=="13"):
            #All types damage reduction
            output[leader_skill_line[0]]["DR"]=100-int(efficiacy_values[0])
        elif(leader_skill_line[6]=="16"):
            #Single type [Typing, "ATK", ""] 
            output[leader_skill_line[0]]["Target"]["Typing"]=typefinder(efficiacy_values[0],printing=True)
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="17"):
            #Single type [Typing, "DEF", ""] 
            output[leader_skill_line[0]]["Target"]["Typing"]=typefinder(efficiacy_values[0],printing=True)
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="18"):
            #Single type [Typing, "ATK and DEF", ""] 
            output[leader_skill_line[0]]["Target"]["Typing"]=typefinder(efficiacy_values[0],printing=True)
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[2])
        elif(leader_skill_line[6]=="19"):
            #Single type [Type, "HP", ""] 
            output[leader_skill_line[0]]["Target"]["Typing"]=typefinder(efficiacy_values[0],printing=True)
            output[leader_skill_line[0]]["HP"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="20"):
            #Single Type (Type, "Ki", "") 
            output[leader_skill_line[0]]["Target"]["Typing"]=typefinder(efficiacy_values[0],printing=True)
            output[leader_skill_line[0]]["Ki"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="44"):
            #Single Type (Type, HP, ATK) 
            output[leader_skill_line[0]]["Target"]["Typing"]=typefinder(efficiacy_values[0],printing=True)
            output[leader_skill_line[0]]["HP"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[2])
        elif(leader_skill_line[6]=="50"):
            #Immune to negative effects
            output[leader_skill_line[0]]["Status"]=["Immune to negative effects"]
        elif(leader_skill_line[6]=="58"):
            #Heal per ki of own type
            output[leader_skill_line[0]]["Building Stat"]= {"Cause":"Ki sphere obtained", "Type":"Own type"}
            output[leader_skill_line[0]]["Heals"]=int(efficiacy_values[0])
        elif(leader_skill_line[6]=="59"):
            #ATK per ki sphere obtained
            output[leader_skill_line[0]]["Building Stat"]= {"Cause":"Ki sphere obtained", "Type":"Any"}
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[0])
        elif(leader_skill_line[6]=="61"):
            #ATK and DEF per ki sphere obtained
            output[leader_skill_line[0]]["Building Stat"]= {"Cause":"Ki sphere obtained", "Type":"Any"}
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[0])
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="64"):
            #ATK per ki sphere obtained of a type
            output[leader_skill_line[0]]["Building Stat"]= {"Cause":"Ki sphere obtained", "Type":KiOrbType(efficiacy_values[0],DEVEXCEPTIONS=DEVEXCEPTIONS)}
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["Target"]["Typing"]=typefinder(efficiacy_values[0],printing=True)
        elif(leader_skill_line[6]=="71"):
            #HP based ["Min ATK", "MAX ATK", ???] 
            output[leader_skill_line[0]]["Building Stat"]={"Cause":"HP", "Type":"More HP remaining"}
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["Building Stat"]["Min"]=int(efficiacy_values[0])
            output[leader_skill_line[0]]["Building Stat"]["Max"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="82"):
            #Typing [Typing, "HP and ATK and DEF", ""] 
            output[leader_skill_line[0]]["Target"]["Class"]=extractClassType(efficiacy_values[0],DEVEXCEPTIONS=DEVEXCEPTIONS)[0]
            output[leader_skill_line[0]]["Target"]["Typing"]=extractClassType(efficiacy_values[0],DEVEXCEPTIONS=DEVEXCEPTIONS)[1]
            output[leader_skill_line[0]]["HP"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="83"):
            #Typing ki
            output[leader_skill_line[0]]["Ki"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="84"):
            #Typing HP ATK and DEF
            output[leader_skill_line[0]]["HP"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="93"):
            #All types or specific type HP
            output[leader_skill_line[0]]["Target"]["Class"]=extractClassType(efficiacy_values[0],DEVEXCEPTIONS=DEVEXCEPTIONS)[0]
            output[leader_skill_line[0]]["Target"]["Typing"]=extractClassType(efficiacy_values[0],DEVEXCEPTIONS=DEVEXCEPTIONS)[1]
            output[leader_skill_line[0]]["HP"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="102"):
            output[leader_skill_line[0]]["Times to turn giant"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="104"):
            #Category ["HP", "ATK","DEF"] 
            output[leader_skill_line[0]]["HP"]=int(efficiacy_values[0])
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[2])
        else:
            output[leader_skill_line[0]]["Ki"]="UNKNOWN"
            output[leader_skill_line[0]]["HP"]="UNKNOWN"
            output[leader_skill_line[0]]["ATK"]="UNKNOWN"
            output[leader_skill_line[0]]["DEF"]="UNKNOWN"
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown leader skill")
            
        if(leader_skill_line[5]!=""):
            causalityCondition=logicalCausalityExtractor(leader_skill_line[5])
            causalityCondition=CausalityLogicalExtractor(unit,causalityCondition,DEVEXCEPTIONS=DEVEXCEPTIONS)
            output[leader_skill_line[0]]["Condition"]=causalityCondition
        if("Typing" in output[leader_skill_line[0]]["Target"]):
            if(output[leader_skill_line[0]]["Target"]["Typing"]==["PHY","STR","INT","TEQ","AGL"]):
                output[leader_skill_line[0]]["Target"].pop("Typing")

    temp=output.copy()
    for line in temp:
        if("NOT WORKING" in output[line]):
            output.pop(line)
    return(output)

def turnintoJson(data,filename, directoryName="" ):
    if filename.endswith(".json")==False:
        filename+=".json"
    if(directoryName!=""):
        if(directoryName[-1]!="/"):
            directoryName+="/"
    with open(directoryName+filename, 'w') as f:
        json.dump(data, f, indent=4)

def JPExclusiveCheck(unitid):
    globalVersion=searchbycolumn(code=unitid,column=0,database=cardsGB)
    if(globalVersion==[]):
        return(True)
    else:
        return(False)
    
def checkEza(unitid):
    unit=searchbycolumn(code=unitid,column=0,database=cardsJP)[0]
    awakeningID=unit[16][:-2]
    ezaRow=searchbycolumn(code=awakeningID,column=1,database=optimal_awakening_growthsJP)
    if(ezaRow==[]):
        return(False)
    else:
        return(True)

def checkSeza(unitid):
    unit=searchbycolumn(code=unitid,column=0,database=cardsJP)[0]
    awakeningID=unit[16][:-2]
    ezaRow=searchbycolumn(code=awakeningID,column=1,database=optimal_awakening_growthsJP)
    if(ezaRow==[]):
        return(False)
    else:
        for row in ezaRow:
            #tur Seza would be number 8
            if(row[2]=="8" and unit[5]=="4"):
                return(True)
            #lr Seza would be number 4
            if(row[2]=="4" and unit[5]=="5"):
                return(True)
        return(False)


def logic_reducer(expression):
    def apply_operator(operators, values):
        operator = operators.pop()
        if operator == "Not":
            values.append(not values.pop())
        elif operator == "And":
            right = values.pop()
            left = values.pop()
            values.append(left and right)
        elif operator == "Or":
            right = values.pop()
            left = values.pop()
            values.append(left or right)

    def parse(expression):
        tokens = expression.replace('(', ' ( ').replace(')', ' ) ').split()
        operators = []
        values = []

        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == '(':
                operators.append('(')
            elif token == ')':
                while operators and operators[-1] != '(':
                    apply_operator(operators, values)
                operators.pop()  # Remove '('
            elif token in {'And', 'Or', 'Not'}:
                operators.append(token)
            elif token == 'True':
                values.append(True)
            elif token == 'False':
                values.append(False)
            i += 1

        while operators:
            apply_operator(operators, values)

        return values[0]

    return parse(expression)

def standbyConditionLogicalCausalityExtractor(causalityCondition,seed=10000):
    output={}
    causalityCondition=causalityCondition.replace(" ","")
    causalityCondition=split_into_lists(causalityCondition[1:-1],",")
    logic=listListToLogic(causalityCondition,seed=seed)
    return(logic)

def earliestUnused(previouslyUsed,seed):
    if(previouslyUsed==[]):
        return(str(int(seed)*12345))
    return(str(int(previouslyUsed[-1])+1))

def listListToLogic(listList,previouslyUsed=[],seed=10000):
    output={"Logic":"", "Causality":{}}
    if(listList[0]=='"&"'):
        output["Logic"]+="("
        for logic in listList[1:]:
            calculatedLogic=listListToLogic(logic,previouslyUsed,seed)
            output["Logic"]+=calculatedLogic["Logic"]
            output["Logic"]+=" And "
            output["Causality"].update(calculatedLogic["Causality"])
        output["Logic"]=output["Logic"][:-5]
        output["Logic"]+=")"
    elif(listList[0]=='"|"'):
        output["Logic"]+="("
        for logic in listList[1:]:
            calculatedLogic=listListToLogic(logic,previouslyUsed,seed)
            output["Logic"]+=calculatedLogic["Logic"]
            output["Logic"]+=" Or "
            output["Causality"].update(calculatedLogic["Causality"])
        output["Logic"]=output["Logic"][:-4]
        output["Logic"]+=")"
    elif(listList[0]=='"type"'):
        formattedCausality=["","","","",""]
        formattedCausality[1]=listList[1]

        causalityType=listList[1]
        formattedCausality[1]=causalityType
        
        if(len(listList)==3):
            effeciacy_values=listList[2]
            if(type(effeciacy_values)==str):
                formattedCausality[2]=effeciacy_values[1:-1]
            else:
                for x in range(0,len(effeciacy_values)):
                    formattedCausality[x+2]=effeciacy_values[x]

        calculatedLogic=causalityLineToLogic(formattedCausality)
        causalityID=earliestUnused(previouslyUsed,seed)
        previouslyUsed.append(causalityID)
        output["Logic"]=str(causalityID)
        output["Causality"][causalityID]=(calculatedLogic)
    elif(listList[0]=='"not"'):
        calculatedLogic=listListToLogic(listList[1],previouslyUsed,seed)
        output["Logic"]+="(not "
        output["Logic"]+=calculatedLogic["Logic"]
        output["Logic"]+=")"
        output["Causality"].update(calculatedLogic["Causality"])
    else:
        raise Exception("Unknown logic type")
    return(output)

def split_into_lists(stringToSplit,splitter):
    components=[]
    bracket_level = 0
    current_component = ""
    for char in stringToSplit:
        if char == splitter and bracket_level == 0:
            if(splitter in current_component):
                components.append(split_into_lists(current_component[1:-1],splitter))
            else:
                components.append(current_component)
            current_component = ""
        else:
            current_component+=char
            if char == "[":
                bracket_level += 1
            elif char == "]":
                bracket_level -= 1
    if (current_component!=""):
        if(splitter in current_component):
            components.append(split_into_lists(current_component[1:-1],splitter))
        else:
            components.append(current_component)
    return components

def parseStandby(unit,DEVEXCEPTIONS=False):
    output={}
    standby_skill_set_id=searchbyid(code=unit[0],codecolumn=1,database=card_standby_skill_set_relationsJP,column=2)
    if(standby_skill_set_id!=None):
        standby_skill_set_id=standby_skill_set_id[0]
        standby_skill_setsRow=searchbycolumn(code=standby_skill_set_id,database=standby_skill_setsJP,column=0)[0]
        output["ID"]=standby_skill_set_id
        output["Exec limit"]=standby_skill_setsRow[5]
        compiled_causality_conditions=standby_skill_setsRow[6]
        compiled_causality_conditions=logicalCausalityExtractor(compiled_causality_conditions)
        compiled_causality_conditions=CausalityLogicalExtractor(unit,compiled_causality_conditions)

        output["Condition"]=compiled_causality_conditions
        standby_skills_rows=searchbycolumn(code=standby_skill_set_id,database=standby_skillsJP,column=1)
        for standby_skill_row in standby_skills_rows:
            efficiacy_value=standby_skill_row[8].replace("[","").replace("]","").replace("{","").replace("}","").replace(" ","").replace('"',"").split(",")
            if(standby_skill_row[6]=="103"):
                output["Exchanges to"]=efficiacy_value[0]
            elif(standby_skill_row[6]=="115"):
                output["Standby Exclusivity"]=efficiacy_value[0][5:]
            elif(standby_skill_row[6]=="116"):
                output["Charge type"]={}
                output["Charge type"]["type"]=efficiacy_value[0][5:]
                if(output["Charge type"]["type"]=="energy_ball" and len(efficiacy_value)>4):
                    if(efficiacy_value[4][:-1]=='ball_type_multiplier:'):
                        charge_per_orb=efficiacy_value[-5:]
                        output["Charge type"]["charge_per_orb"]={}
                        output["Charge type"]["charge_per_orb"]["AGL"]=int(efficiacy_value[4][-1])
                        output["Charge type"]["charge_per_orb"]["TEQ"]=int(charge_per_orb[0])
                        output["Charge type"]["charge_per_orb"]["INT"]=int(charge_per_orb[1])
                        output["Charge type"]["charge_per_orb"]["STR"]=int(charge_per_orb[2])
                        output["Charge type"]["charge_per_orb"]["PHY"]=int(charge_per_orb[3])
                        output["Charge type"]["charge_per_orb"]["Rainbow"]=int(charge_per_orb[4])

                output["Charge type"]["gauge_value"]=efficiacy_value[1][12:]
                output["Charge type"]["count_multiplier"]=efficiacy_value[2][17:]
                output["Charge type"]["max_effect_value"]=efficiacy_value[3][17:]
            else:
                if(DEVEXCEPTIONS):
                    raise Exception("Unknown standby skill")
    return(output)




def parseFinish(unit,DEVEXCEPTIONS=False):
    output={}
    finish_skill_set_ids=searchbyid(code=unit[0],codecolumn=1,database=card_finish_skill_set_relationsJP,column=2)
    if(finish_skill_set_ids!=None):
        for finish_skill_set_id in finish_skill_set_ids:
            output[finish_skill_set_id]={}
            if(JPExclusiveCheck(unit[0])):
                finish_skill_setsRow=searchbycolumn(code=finish_skill_set_id,database=finish_skill_setsJP,column=0)[0]
            else:
                finish_skill_setsRow=searchbycolumn(code=finish_skill_set_id,database=finish_skill_setsGB,column=0)[0]
            output[finish_skill_set_id]["ID"]=finish_skill_set_id
            output[finish_skill_set_id]["Name"]=finish_skill_setsRow[1]
            output[finish_skill_set_id]["Description"]=finish_skill_setsRow[2]
            if(finish_skill_setsRow[6]=="0"):
                output[finish_skill_set_id]["Timing"]="On activation"
            elif(finish_skill_setsRow[6]=="17"):
                output[finish_skill_set_id]["Timing"]="On Revive"
            elif(finish_skill_setsRow[6]=="6"):
                output[finish_skill_set_id]["Timing"]="On Counter"
            elif(finish_skill_setsRow[6]=="7"):
                output[finish_skill_set_id]["Timing"]="On super attack Counter(Held by str dragon fist)"
            else:
                output[finish_skill_set_id]["Timing"]="UNKNOWN"
                if(DEVEXCEPTIONS):
                    raise Exception("Unknown timing")
                
            compiled_causality_conditions=finish_skill_setsRow[8]
            condition=standbylogicalCausalityExtractor(compiled_causality_conditions)
            output[finish_skill_set_id]["Condition"]=condition

            finish_special_id=finish_skill_setsRow[9]
            finish_special_multiplier=searchbyid(code=finish_special_id,codecolumn=0,database=finish_specialsJP,column=1)
            if(finish_special_multiplier!=None):
                finish_special_multiplier=finish_special_multiplier[0]
                output[finish_skill_set_id]["Multiplier"]=int(finish_special_multiplier)

            finish_skills_rows=searchbycolumn(code=finish_skill_set_id,database=finish_skillsJP,column=1)
            for finish_skill_row in finish_skills_rows:
                if(finish_skill_row[5]!="1"):
                    output[finish_skill_set_id]["Duration"]=finish_skill_row[5]
                efficiacy_value=finish_skill_row[8].replace("[","").replace("]","").replace("{","").replace("}","").replace(" ","").replace('"',"").split(",")
                if(finish_skill_row[6]=="1"):
                    output[finish_skill_set_id]["Attack"]=int(efficiacy_value[0])
                elif(finish_skill_row[6]=="4"):
                    output[finish_skill_set_id]["Heals"]=int(efficiacy_value[0])
                elif(finish_skill_row[6]=="5"):
                    output[finish_skill_set_id]["Ki"]=int(efficiacy_value[0])
                elif(finish_skill_row[6]=="9"):
                    output[finish_skill_set_id]["Effect"]="Stun"
                elif(finish_skill_row[6]=="90"):
                    output[finish_skill_set_id]["Crit Chance"]=int(efficiacy_value[0])
                elif(finish_skill_row[6]=="103"):
                    output[finish_skill_set_id]["Exchanges to"]=efficiacy_value[0]
                elif(finish_skill_row[6]=="110"):
                    output[finish_skill_set_id]["Disable Other Line"]={}
                    output[finish_skill_set_id]["Disable Other Line"]["Activated"]=True
                    output[finish_skill_set_id]["Disable Other Line"]["Line"]=efficiacy_value[2]
                elif(finish_skill_row[6]=="115"):
                    output[finish_skill_set_id]["Standby Exclusivity"]=efficiacy_value[0][5:]
                elif(finish_skill_row[6]=="116"):
                    output[finish_skill_set_id]["CONFUSION"]=True
                elif(finish_skill_row[6]=="117"):
                    output[finish_skill_set_id]["CONFUSION"]=True
                elif(finish_skill_row[6]=="118"):
                    output[finish_skill_set_id]["Multipler per charge"]=int(efficiacy_value[0])
                    output[finish_skill_set_id]["Max multiplier"]=int(efficiacy_value[1])
                elif(finish_skill_row[6]=="119"):
                    output[finish_skill_set_id]["Nullification"]={}
                    output[finish_skill_set_id]["Nullification"]["Activated"]=True
                elif(finish_skill_row[6]=="120"):
                    output[finish_skill_set_id]["Counter"]={"Activated":True, "Multiplier":efficiacy_value[1]}
                else:
                    if(DEVEXCEPTIONS):
                        raise Exception("Unknown finish skill")
            if("Exchanges to" not in output[finish_skill_set_id]):
                for standbySkillRow in standby_skillsJP:
                    if(unit[0][:-1] in standbySkillRow[8]):
                        standbySkillSetId=standbySkillRow[1]
                        sourceUnitID=searchbyid(code=standbySkillSetId,codecolumn=0,database=card_standby_skill_set_relationsJP,column=1)
                        if(sourceUnitID!=None):
                            sourceUnitID=sourceUnitID[0]
                            output[finish_skill_set_id]["Exchanges to"]=sourceUnitID
    return(output)

def unicode_fixer(input):
    if isinstance(input, str):
        return input.encode('utf-8').decode('unicode-escape')
    elif isinstance(input, list):
        return [unicode_fixer(item) for item in input]
    elif isinstance(input, dict):
        return {key: unicode_fixer(value) for key, value in input.items()}
    else:
        return input




def standbylogicalCausalityExtractor(compiled_causality_conditions):
    causality=unicode_fixer(compiled_causality_conditions)
    causality=causality.replace(' ',"")
    causality=causality.replace('["&",["',"")
    causality=causality.replace('type",55,[1]],["',"Charge generated")
    causality=causality.replace('",["type",52],["int",',"")
    causality=causality.replace(']]]',"")
    causality=causality.replace('["type",40]',"When a super attack is aimed at this character")
    causality=causality.replace('["type",0]',"When this character revives")
    

    return(causality)



def getKiMultipliers(unit):
    multipliers={}
    if(getrarity(unit)=="lr"):
        eball_mod_max=float(unit[34])
        eball_mod_mid=float(unit[32])
        for kiAmount in range(0,25):
            multipliers[int(kiAmount)]=((eball_mod_max-eball_mod_mid)/12)*(kiAmount-12)+eball_mod_mid
    else:
        eball_mod_max=float(unit[34])
        max_ki=12.0
        for kiAmount in range(0,13):
            multipliers[int(kiAmount)]=(eball_mod_max/2)+(eball_mod_max/2)*(kiAmount/max_ki)
    return(multipliers)

def getStatsAtAllLevels(unit,eza):
    output={}
    maxLevel=getMaxLevel(unit,eza)
    minLevel=getMinLevel(unit,eza)
    for level in range(minLevel,maxLevel+1):
        output[level]=getUnitStats(unit,level)
    return(output)

def shortenPassiveDictionary(oldPassiveDictionary):
    passiveDictionary=oldPassiveDictionary.copy()
    if "Revive" in passiveDictionary:
        if passiveDictionary["Revive"]["Activated"]==False:
            passiveDictionary.pop("Revive")
    if "Disable Other Line" in passiveDictionary:
        if passiveDictionary["Disable Other Line"]["Activated"]==False:
            passiveDictionary.pop("Disable Other Line")
    if "Standby" in passiveDictionary:
        if "Change form" in passiveDictionary["Standby"]:
            if passiveDictionary["Standby"]["Change form"]["Activated"]==False:
                passiveDictionary["Standby"].pop("Change form")
        if "Damage enemy" in passiveDictionary["Standby"]:
            if passiveDictionary["Standby"]["Damage enemy"]["Activated"]==False:
                passiveDictionary["Standby"].pop("Damage enemy")
        if passiveDictionary["Standby"]["Activated"]==False:
            passiveDictionary.pop("Standby")
    if "Forsee Super Attack" in passiveDictionary:
        if passiveDictionary["Forsee Super Attack"]==False:
            passiveDictionary.pop("Forsee Super Attack")
    if "Guaranteed hit" in passiveDictionary:
        if passiveDictionary["Guaranteed hit"]==False:
            passiveDictionary.pop("Guaranteed hit")
    if "Dodge chance" in passiveDictionary:
        if passiveDictionary["Dodge chance"]==0:
            passiveDictionary.pop("Dodge chance")
    if "Effective against all" in passiveDictionary:
        if passiveDictionary["Effective against all"]==False:
            passiveDictionary.pop("Effective against all")
    if "Transformation" in passiveDictionary:
        if passiveDictionary["Transformation"]["Activated"]==False:
            passiveDictionary.pop("Transformation")
    if "Slot" in passiveDictionary:
        if passiveDictionary["Slot"]==None:
            passiveDictionary.pop("Slot")
    if "Additional attack" in passiveDictionary:
        if passiveDictionary["Additional attack"]["Activated"]==False:
            passiveDictionary.pop("Additional attack")
    if "Timing" in passiveDictionary:
        if passiveDictionary["Timing"]==None:
            passiveDictionary.pop("Timing")
    if "Building Stat" in passiveDictionary:
        if passiveDictionary["Building Stat"]["Cause"]==None:
            passiveDictionary.pop("Building Stat")
    if "ATK" in passiveDictionary:
        if passiveDictionary["ATK"]==0:
            passiveDictionary.pop("ATK")
    if "DEF" in passiveDictionary:
        if passiveDictionary["DEF"]==0:
            passiveDictionary.pop("DEF")
    if "Heals" in passiveDictionary:
        if passiveDictionary["Heals"]==0:
            passiveDictionary.pop("Heals")
    if "Ki" in passiveDictionary:
        if passiveDictionary["Ki"]==0:
            passiveDictionary.pop("Ki")
    if "Status" in passiveDictionary:
        if passiveDictionary["Status"]==[]:
            passiveDictionary.pop("Status")
    if "DR" in passiveDictionary:
        if passiveDictionary["DR"]==0:
            passiveDictionary.pop("DR")
    if "Guard" in passiveDictionary:
        if passiveDictionary["Guard"]==False:
            passiveDictionary.pop("Guard")
    if "Crit Chance" in passiveDictionary:
        if passiveDictionary["Crit Chance"]==0:
            passiveDictionary.pop("Crit Chance")
    if "Ki change" in passiveDictionary:
        if (passiveDictionary["Ki change"]["From"]==None and passiveDictionary["Ki change"]["To"]==None):
            passiveDictionary.pop("Ki change")
    if "Target" in passiveDictionary:
        if "Category" in passiveDictionary["Target"]:
            if passiveDictionary["Target"]["Category"]==None:
                passiveDictionary["Target"].pop("Category")
        if "Class" in passiveDictionary["Target"]:
            if passiveDictionary["Target"]["Class"]==[]:
                passiveDictionary["Target"].pop("Class")
        if "Type" in passiveDictionary["Target"]:
            if passiveDictionary["Target"]["Type"]==[]:
                passiveDictionary["Target"].pop("Type")
        if passiveDictionary["Target"]=={}:
            passiveDictionary.pop("Target")
    if "Chance" in passiveDictionary:
        if passiveDictionary["Chance"]=="100":
            passiveDictionary.pop("Chance")
    if "Length" in passiveDictionary:
        if passiveDictionary["Length"]==None:
            passiveDictionary.pop("Length")
    if "First turn to activate" in passiveDictionary:
        if passiveDictionary["First turn to activate"]==0:
            passiveDictionary.pop("First turn to activate")
    if "Condition" in passiveDictionary:
        if passiveDictionary["Condition"]==None:
            passiveDictionary.pop("Condition")
    if "Once only" in passiveDictionary:
        if passiveDictionary["Once only"]==False:
            passiveDictionary.pop("Once only")
    if "Counter" in passiveDictionary:
        if "Activated" in passiveDictionary["Counter"]:
            if "DR from normals" in passiveDictionary["Counter"]:
                if passiveDictionary["Counter"]["DR from normals"]==None:
                    passiveDictionary["Counter"].pop("DR from normals")
            if passiveDictionary["Counter"]["Activated"]==False:
                passiveDictionary.pop("Counter")
    if "Nullification" in passiveDictionary:
        if passiveDictionary["Nullification"]["Activated"]==False:
            passiveDictionary.pop("Nullification")
    if "Domain expansion" in passiveDictionary:
        if passiveDictionary["Domain expansion"]["Activated"]==False:
            passiveDictionary.pop("Domain expansion")
        

    return(passiveDictionary)

def getSuperMinKi(kiCircleSegments):
    for segment in kiCircleSegments:
        if kiCircleSegments[segment]=="super":
            return segment

def extractPassiveLine(unit,passiveskill,printing=False,DEVEXCEPTIONS=False):
    effects={
        "ID": passiveskill[0],
        "Calc option": passiveskill[8],
        "Domain expansion": {
            "Activated": False,
            "ID": None,
            "Name": None
        },
        "Revive":{
            "Activated": False,
            "HP recovered": None
        },
        "Nullification": {
            "Activated": False,
            "Absorbed": 0
        },
        "Disable Other Line":{
            "Activated": False,
            "Line": None
        },
        "Counter": {
            "Activated": False,
            "Multiplier": None,
            "DR from normals": None
        },
        "Standby": {
            "Activated": False,
            "Change form": {
                "Activated": False,
                "Unit": None
            },
            "Damage enemy": {
                "Activated": False,
                "Multiplier": None
            }
        },
        "Forsee Super Attack": False,
        "Guaranteed hit": False,
        "Dodge chance": 0,
        "Effective against all": False,
        "Transformation": {
            "Activated": False,
            "Unit": None,
            "Giant/Rage": False,
            "Min Turns": None,
            "Max Turns": None,
            "Reverse chance": None
        },
        "Slot": None,
        "Additional attack":{
            "Activated": False,
            "Chance of super": None
        },
        "Timing": None,
        "Building Stat":{
            "Min": 0,
            "Max": 0,
            "Cause": None
        },
        "ATK": 0,
        "DEF": 0,
        "Heals": 0,
        "Ki": 0,
        "Status": [],
        "DR": 0,
        "Guard": False,
        "Crit Chance": 0,
        "Ki change": {
            "From": None,
            "To": None
        },
        "Target": {
            "Category": None,
            "Target": None,
            "Class": [],
            "Type": []
        },
        "Buff": {
            "Type": None,
            "+ or -": None
        },
        "Chance": None,
        "Length": None,
        #first turn counts as turn 0
        "First turn to activate": 0,
        "Condition": None,
        "Once only": False
    }
    if(causalityExtractor(passiveskill[12])!=[]):
        causalityCondition=logicalCausalityExtractor(passiveskill[12])
        causalityCondition=CausalityLogicalExtractor(unit=unit,causality=causalityCondition,DEVEXCEPTIONS=DEVEXCEPTIONS)
        if(causalityCondition!=None):
            effects["Condition"]=causalityCondition
    
    if(passiveskill[8]=="0"):
        effects["Buff"]["Type"]="Raw stats"
        effects["Buff"]["+ or -"]="+"

    elif(passiveskill[8]=="1"):
        effects["Buff"]["Type"]="Raw stats"
        effects["Buff"]["+ or -"]="-"

    elif(passiveskill[8]=="2"):
        effects["Buff"]["Type"]="Percentage"
        effects["Buff"]["+ or -"]="+"

    elif(passiveskill[8]=="3"):
        effects["Buff"]["Type"]="Percentage"
        effects["Buff"]["+ or -"]="-"
    else:
        effects["Buff"]["Type"]="Unknown"
        effects["Buff"]["+ or -"]="Unknown"
        if(DEVEXCEPTIONS==True):
                raise Exception("Unknown stat increase type")
    

    effects["Chance"]=passiveskill[11]

    if(passiveskill[6]!="0"):
        effects["Target"]["Category"]={"Included": [],"Excluded": []}
        TargetRows=searchbycolumn(code=passiveskill[6],database=sub_target_typesJP,column=1)
        for TargetRow in TargetRows:
            if(TargetRow[2]=="1"):
                TargetCategory=CategoryExtractor(TargetRow[3])
                effects["Target"]["Category"]["Included"].append(TargetCategory)
            elif(TargetRow[2]=="2"):
                TargetCategory=CategoryExtractor(TargetRow[3])
                effects["Target"]["Category"]["Excluded"].append(TargetCategory)


    if(passiveskill[5]=="1"):
        effects["Target"]["Target"]="Self"
    elif(passiveskill[5]=="2"):
        effects["Target"]["Target"]="Allies"
    elif(passiveskill[5]=="3"):
        effects["Target"]["Target"]="Enemy"
    elif(passiveskill[5]=="4"):
        effects["Target"]["Target"]="Enemies"
    elif(passiveskill[5]=="5"):
        effects["Target"]["Target"]="Allies"
        #For some reason int dfe future gohan has this on his ki support, even though this couldve been under 2
    elif(passiveskill[5]=="12"):
        effects["Target"]["Class"]="Super"
        effects["Target"]["Target"]="Allies"
    elif(passiveskill[5]=="13"):
        effects["Target"]["Class"]="Extreme"
        effects["Target"]["Target"]="Allies"
    elif(passiveskill[5]=="14"):
        effects["Target"]["Class"]="Super"
        effects["Target"]["Target"]="Enemies"
    elif(passiveskill[5]=="15"):
        effects["Target"]["Class"]="Extreme"
        effects["Target"]["Target"]="Enemies"
    elif(passiveskill[5]=="16"):
        effects["Target"]["Target"]="Allies(self excluded)"
    else:
        effects["Target"]["Target"]=("UNKNOWN TARGET")
        if(DEVEXCEPTIONS==True):
            raise Exception("UNKNOWN TARGET")

    
    if(passiveskill[4]=="0"):
        effects["Domain expansion"]["Activated"]=True
        domainID=searchbyid(code=passiveskill[0],codecolumn=2,database=dokkan_field_passive_skill_relationsJP,column=1)[0]
        effects["Domain expansion"]["ID"]=domainID
        domainName=searchbyid(code=domainID,codecolumn=1,database=dokkan_fieldsJP,column=2)[0]
        GBdomainName=searchbyid(code=domainID,codecolumn=1,database=dokkan_fieldsGB,column=2)
        if(GBdomainName!=[]):
            domainName=GBdomainName[0]
        effects["Domain expansion"]["Name"]=domainName

    elif passiveskill[4]=="1":
        effects["ATK"]+=int(passiveskill[13])
    elif passiveskill[4]=="2":
        effects["DEF"]+=int(passiveskill[13])
    elif passiveskill[4]=="3":
        effects["ATK"]+=int(passiveskill[13])
        effects["DEF"]+=int(passiveskill[14])
    elif passiveskill[4]=="4":
        effects["Heals"]+=int(passiveskill[13])
    elif passiveskill[4]=="5":
        effects["Ki"]+=int(passiveskill[13])
    elif passiveskill[4]=="9":
        effects["Status"].append("Stun")
    elif passiveskill[4]=="13":
        effects["DR"]+=100-int(passiveskill[13])
    elif passiveskill[4]=="16":
        typing=extractAllyTyping(passiveskill[13],DEVEXCEPTIONS=DEVEXCEPTIONS)
        effects["ATK"]+=int(passiveskill[14])
        effects["Target"]["Type"]=typing
    elif passiveskill[4]=="17":
        typing=extractAllyTyping(passiveskill[13],DEVEXCEPTIONS=DEVEXCEPTIONS)
        effects["DEF"]+=int(passiveskill[14])
        effects["Target"]["Type"]=typing
    elif passiveskill[4]=="18":
        typing=extractAllyTyping(passiveskill[13],DEVEXCEPTIONS=DEVEXCEPTIONS)
        effects["ATK"]+=int(passiveskill[14])
        effects["DEF"]+=int(passiveskill[14])
        effects["Target"]["Type"]=typing
    elif passiveskill[4]=="20":
        typing=extractAllyTyping(passiveskill[13],DEVEXCEPTIONS=DEVEXCEPTIONS)
        effects["Ki"]+=int(passiveskill[14])
        effects["Target"]["Type"]=typing
    elif passiveskill[4]=="24":
        effects["Status"].append("Disable guard")
    elif passiveskill[4]=="28":
        effects["Heals"]+=int(passiveskill[13])
    elif passiveskill[4]=="38":
        if(DEVEXCEPTIONS==True):
            raise Exception("Unknown effect")
    elif passiveskill[4]=="47":
        if(DEVEXCEPTIONS==True):
            raise Exception("Unknown effect")
    elif passiveskill[4]=="48":
        effects["Status"].append("Seal")
    elif passiveskill[4]=="50":
        effects["Status"].append("Immune to negative effects")
    elif passiveskill[4]=="51":
        type1=KiOrbType(passiveskill[13],DEVEXCEPTIONS=DEVEXCEPTIONS)
        type2=KiOrbType(passiveskill[14],DEVEXCEPTIONS=DEVEXCEPTIONS)
        effects["Ki change"]["From"]=type1
        effects["Ki change"]["To"]=type2
    elif passiveskill[4]=="52":
        effects["Status"].append("Survive K.O attacks")
    elif passiveskill[4]=="53":
        effects["Status"].append("DEF reduced to 0")
    elif passiveskill[4]=="59":
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":"any"}
        effects["Building Stat"]["Slider"]="How many "
        #for orbType in ["Rainbow","PHY","STR","INT","TEQ","AGL"]:
        #    effects["Building Stat"]["Slider"]+=orbType
        #    effects["Building Stat"]["Slider"]+=" or "
        #effects["Building Stat"]["Slider"]=effects["Building Stat"]["Slider"][:-4]
        effects["Building Stat"]["Slider"]+=" Ki Spheres have been obtained?"
        effects["Building Stat"]["Max"]=23
        effects["ATK"]+=int(passiveskill[13])
    elif passiveskill[4]=="60":
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":"any"}
        effects["Building Stat"]["Slider"]="How many "
        #for orbType in ["Rainbow","PHY","STR","INT","TEQ","AGL"]:
        #    effects["Building Stat"]["Slider"]+=orbType
        #    effects["Building Stat"]["Slider"]+=" or "
        #effects["Building Stat"]["Slider"]=effects["Building Stat"]["Slider"][:-4]
        effects["Building Stat"]["Slider"]+=" Ki Spheres have been obtained?"
        effects["Building Stat"]["Max"]=23
        effects["DEF"]+=int(passiveskill[13])
    elif passiveskill[4]=="61":
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":"any"}
        effects["Building Stat"]["Slider"]="How many "
        #for orbType in ["Rainbow","PHY","STR","INT","TEQ","AGL"]:
        #    effects["Building Stat"]["Slider"]+=orbType
        #    effects["Building Stat"]["Slider"]+=" or "
        #effects["Building Stat"]["Slider"]=effects["Building Stat"]["Slider"][:-4]
        effects["Building Stat"]["Slider"]+=" Ki Spheres have been obtained?"
        effects["Building Stat"]["Max"]=23
        effects["ATK"]+=int(passiveskill[13])
        effects["DEF"]+=int(passiveskill[13])
    elif passiveskill[4]=="64":
        typing=KiOrbType(passiveskill[13],DEVEXCEPTIONS=DEVEXCEPTIONS)
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":typing}
        effects["Building Stat"]["Slider"]="How many "
        effects["Building Stat"]["Slider"]+=typing
        effects["Building Stat"]["Slider"]+=" Ki Spheres have been obtained?"
        if(typing==["Rainbow"]):
            effects["Building Stat"]["Max"]=5
        else:
            effects["Building Stat"]["Max"]=23
        effects["ATK"]+=int(passiveskill[14])
    elif passiveskill[4]=="65":
        typing=KiOrbType(passiveskill[13],DEVEXCEPTIONS=DEVEXCEPTIONS)
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":typing}
        effects["Building Stat"]["Slider"]="How many "
        effects["Building Stat"]["Slider"]+=typing
        effects["Building Stat"]["Slider"]+=" Ki Spheres have been obtained?"
        if(typing==["Rainbow"]):
            effects["Building Stat"]["Max"]=5
        else:
            effects["Building Stat"]["Max"]=23
        effects["DEF"]+=int(passiveskill[14])
    elif passiveskill[4]=="66":
        typing=KiOrbType(passiveskill[13],DEVEXCEPTIONS=DEVEXCEPTIONS)
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":typing}
        effects["Building Stat"]["Slider"]="How many "
        effects["Building Stat"]["Slider"]+=typing
        effects["Building Stat"]["Slider"]+=" Ki Spheres have been obtained?"
        if(typing==["Rainbow"]):
            effects["Building Stat"]["Max"]=5
        else:
            effects["Building Stat"]["Max"]=23
        effects["ATK"]+=int(passiveskill[14])
        effects["DEF"]+=int(passiveskill[14])
    elif passiveskill[4]=="67":
        type1=binaryOrbType(passiveskill[13],DEVEXCEPTIONS)
        type2=binaryOrbType(passiveskill[14],DEVEXCEPTIONS)
        effects["Ki change"]["From"]=type1
        effects["Ki change"]["To"]=type2
        
    elif passiveskill[4]=="68":
        #buffs per ki sphere
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":binaryOrbType(passiveskill[13],DEVEXCEPTIONS)}
        effects["Building Stat"]["Slider"]="How many "
        for orbType in binaryOrbType(passiveskill[13],DEVEXCEPTIONS):
            effects["Building Stat"]["Slider"]+=orbType
            effects["Building Stat"]["Slider"]+=" or "
        effects["Building Stat"]["Slider"]=effects["Building Stat"]["Slider"][:-4]
        effects["Building Stat"]["Slider"]+=" Ki Spheres have been obtained?"
        if(binaryOrbType(passiveskill[13],DEVEXCEPTIONS)==["Rainbow"]):
            effects["Building Stat"]["Max"]=5
        else:
            effects["Building Stat"]["Max"]=23
        if(passiveskill[14]=="1"):
            effects["ATK"]+=int(passiveskill[15])
        elif(passiveskill[14]=="2"):
            effects["Heals"]+=int(passiveskill[15])
        elif(passiveskill[14]=="3"):
            effects["DEF"]+=int(passiveskill[15])
        elif(passiveskill[14]=="4"):
            effects["Crit Chance"]+=int(passiveskill[15])
        elif(passiveskill[14]=="5"):
            effects["Dodge chance"]+=int(passiveskill[15])
        elif(passiveskill[14]=="6"):
            effects["DR"]+=int(passiveskill[15])
        else:
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown buff")
    elif passiveskill[4]=="69":
        effects["Ki change"]["From"]=["AGL","TEQ","INT","STR","PHY","Rainbow","Sweet treats"]
        effects["Ki change"]["To"]=KiOrbType(passiveskill[13])
    elif passiveskill[4]=="71":
        if(int(passiveskill[13])>int(passiveskill[14])):
            #The less HP remaining the greater the stats boost
            effects["ATK"]+=int(passiveskill[13])
            effects["Building Stat"]["Cause"]={"Cause":"HP", "Type":"Less HP remaining"}
            effects["Building Stat"]["Max"]+=int(passiveskill[13])
            effects["Building Stat"]["Min"]+=int(passiveskill[14])
            effects["Building Stat"]["Slider"]="What percentage of HP is remaining?"
        else:
            #The more HP remaining the greater the stats boost
            effects["ATK"]+=int(passiveskill[14])
            effects["Building Stat"]["Cause"]={"Cause":"HP", "Type":"More HP remaining"}
            effects["Building Stat"]["Max"]+=int(passiveskill[14])
            effects["Building Stat"]["Min"]+=int(passiveskill[13])
            effects["Building Stat"]["Slider"]="What percentage of HP is remaining?"
    elif passiveskill[4]=="72":
        if(int(passiveskill[13])>int(passiveskill[14])):
            #The less HP remaining the greater the stats boost
            effects["DEF"]+=int(passiveskill[13])
            effects["Building Stat"]["Cause"]={"Cause":"HP", "Type":"Less HP remaining"}
            effects["Building Stat"]["Max"]+=int(passiveskill[13])
            effects["Building Stat"]["Min"]+=int(passiveskill[14])
            effects["Building Stat"]["Slider"]="What percentage of HP is remaining?"
        else:
            #The more HP remaining the greater the stats boost
            effects["DEF"]+=int(passiveskill[14])
            effects["Building Stat"]["Cause"]={"Cause":"HP", "Type":"More HP remaining"}
            effects["Building Stat"]["Max"]+=int(passiveskill[14])
            effects["Building Stat"]["Min"]+=int(passiveskill[13])
            effects["Building Stat"]["Slider"]="What percentage of HP is remaining?"
    elif passiveskill[4]=="73":
        if(int(passiveskill[13])>int(passiveskill[14])):
            #The less HP remaining the greater the stats boost
            effects["ATK"]+=int(passiveskill[13])
            effects["DEF"]+=int(passiveskill[13])
            effects["Building Stat"]["Cause"]={"Cause":"HP", "Type":"Less HP remaining"}
            effects["Building Stat"]["Max"]+=int(passiveskill[13])
            effects["Building Stat"]["Min"]+=int(passiveskill[14])
            effects["Building Stat"]["Slider"]="What percentage of HP is remaining?"
        else:
            #The more HP remaining the greater the stats boost
            effects["ATK"]+=int(passiveskill[14])
            effects["DEF"]+=int(passiveskill[14])
            effects["Building Stat"]["Cause"]={"Cause":"HP", "Type":"More HP remaining"}
            effects["Building Stat"]["Max"]+=int(passiveskill[14])
            effects["Building Stat"]["Min"]+=int(passiveskill[13])
            effects["Building Stat"]["Slider"]="What percentage of HP is remaining?"
    elif passiveskill[4]=="76":
        effects["Effective against all"]=True
    elif passiveskill[4]=="78":
        effects["Guard"]=True
    elif passiveskill[4]=="79":
        effects["Transformation"]["Activated"]=True
        effects["Transformation"]["Unit"]=passiveskill[13]
        effects["Transformation"]["Giant/Rage"]=True
        params=searchbycolumn(code=passiveskill[14],database=battle_paramsJP,column=1)
        for param in params:
            if(param[2]=="0"):
                effects["Transformation"]["Min Turns"]=param[3]
            elif(param[2]=="1"):
                effects["Transformation"]["Max Turns"]=param[3]
            elif(param[2]=="2"):
                effects["Transformation"]["Reverse chance"]=param[3]
        
    elif passiveskill[4]=="80":
        if(DEVEXCEPTIONS==True):
            raise Exception("Counter without dodge")
    elif passiveskill[4]=="81":
        effects["Additional attack"]["Activated"]=True
        effects["Additional attack"]["Chance of super"]=passiveskill[15]
        if(passiveskill[14]!="0"):
            effects["Additional attack"]["Chance of another additional"]=passiveskill[14]
    elif passiveskill[4]=="82":
        effects["ATK"]+=int(passiveskill[14])
        effects["DEF"]+=int(passiveskill[14])
        effects["Target"]["Type"]=extractClassType(passiveskill[13],DEVEXCEPTIONS=DEVEXCEPTIONS)[1]
        effects["Target"]["Class"]=extractClassType(passiveskill[13],DEVEXCEPTIONS=DEVEXCEPTIONS)[0]
    elif passiveskill[4]=="83":
        effects["Ki"]+=int(passiveskill[14])
        effects["Target"]["Type"]=extractClassType(passiveskill[13],DEVEXCEPTIONS=DEVEXCEPTIONS)[1]
        effects["Target"]["Class"]=extractClassType(passiveskill[13],DEVEXCEPTIONS=DEVEXCEPTIONS)[0]
    elif passiveskill[4]=="90":
        effects["Crit Chance"]+=int(passiveskill[13])
    elif passiveskill[4]=="91":
        effects["Dodge chance"]+=int(passiveskill[13])
    elif passiveskill[4]=="92":
        effects["Guaranteed hit"]=True
    elif passiveskill[4]=="95":
        if(DEVEXCEPTIONS==True):
            raise Exception("Dodge and counter")
    elif passiveskill[4]=="96":
        kiSphereType=binaryOrbType(passiveskill[13],DEVEXCEPTIONS)
        effects["Ki"]+=int(passiveskill[14])
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":kiSphereType}
        effects["Building Stat"]["Slider"]="How many "
        for orbType in kiSphereType:
            effects["Building Stat"]["Slider"]+=orbType
            effects["Building Stat"]["Slider"]+=" or "
        effects["Building Stat"]["Slider"]=effects["Building Stat"]["Slider"][:-4]
        if(kiSphereType==["Rainbow"]):
            effects["Building Stat"]["Max"]=5
        else:
            effects["Building Stat"]["Max"]=23
        effects["Building Stat"]["Slider"]+=" Ki Spheres have been obtained?"

        
    elif passiveskill[4]=="97":
        if(passiveskill[14]=="1"):
            effects["Nullification"]["Activated"]=True
            effects["Nullification"]["Absorbed"]=int(passiveskill[13])
        else:
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown effect")
    elif passiveskill[4]=="98":
        if(passiveskill[15]=="0"):
            effects["ATK"]+=int(passiveskill[13])
        elif(passiveskill[15]=="1"):
            effects["DEF"]+=int(passiveskill[13])
        elif(passiveskill[15]=="2"):
            effects["Crit Chance"]+=int(passiveskill[13])
        elif(passiveskill[15]=="3"):
            effects["Dodge chance"]+=int(passiveskill[13])
        elif(passiveskill[15]=="4"):
            #CONFUSED
            effects["DR"]+=int(passiveskill[13])
        elif(passiveskill[15]=="5"):
            effects["Ki"]+=int(passiveskill[13])
        else:
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown stat increase")
        effects["Building Stat"]["Cause"]={"Cause":"Look Elsewhere"}
        effects["Building Stat"]["Max"]+=int(passiveskill[14])
    elif passiveskill[4]=="101":
        effects["Forsee Super Attack"]=True
    elif passiveskill[4]=="103":
        effects["Transformation"]["Activated"]=True
        effects["Transformation"]["Unit"]=passiveskill[13]

        effects["First turn to activate"]+=(int(passiveskill[14]))
    elif passiveskill[4]=="109":
        effects["Revive"]["Activated"]=True
        effects["Revive"]["HP recovered"]=int(passiveskill[13])
    elif passiveskill[4]=="110":
        if(passiveskill[13]=="2"):
            effects["Disable Other Line"]["Activated"]=True
            effects["Disable Other Line"]["Line"]=passiveskill[14]
        elif(passiveskill[13]=="15"):
            print("Something related to charging standby skills")

    elif passiveskill[4]=="111":
        effects["Status"].append("Disable action")
    elif(passiveskill[4]=="114"):
        effects["Status"].append("Unable to attack")
    elif(passiveskill[4]=="115"):
        effects["Standby"]["Activated"]=True
    elif(passiveskill[4]=="117"):
        effects["Standby"]["Activated"]=True
        effects["Standby"]["Change form"]["Activated"]=True
        revertUnit=str(int(unit[22][:-2]))+"0"
        effects["Standby"]["Change form"]["Unit"]=revertUnit
    elif passiveskill[4]=="119":
        effects["Nullification"]["Activated"]=True
    elif(passiveskill[4]=="120"):
        effects["Counter"]={"Activated":True, "Multiplier":passiveskill[14]}
        if(passiveskill[13]!="0"):
            effects["Counter"]["DR from normals"]=passiveskill[13]
    elif(passiveskill[4]=="128"):
        effects["Counter"]={"Activated":True, "Multiplier":passiveskill[14], "Cause":"Evaded attack"}
        
    else:
        if(DEVEXCEPTIONS==True):
                raise Exception("Unknown effect")
        

    

    
    
    
    effects["Length"]=passiveskill[9]



    if passiveskill[3]=="1":
        effects["Timing"]="Start of turn"
    elif passiveskill[3]=="3":
        effects["Timing"]="Attacking"
    elif passiveskill[3]=="4":
        effects["Timing"]="On Super"
    elif passiveskill[3]=="5":
        effects["Timing"]="Attacking the enemy"
    elif passiveskill[3]=="6":
        effects["Timing"]="Being hit"
    elif passiveskill[3]=="7":
        effects["Timing"]="Hit recieved"
    elif passiveskill[3]=="9":
        effects["Timing"]="End of turn"
    elif passiveskill[3]=="11":
        effects["Timing"]="After all ki collected"
    elif passiveskill[3]=="12":
        effects["Timing"]="Activating standby"
    elif passiveskill[3]=="14":
        effects["Timing"]="When final blow delivered"
    elif passiveskill[3]=="15":
        effects["Timing"]="When ki spheres collected"
    else:
        print("UNKNOWN TRIGGER",end=" ")
        if(DEVEXCEPTIONS==True):
                raise Exception("Unknown trigger")

    

    

        
                    

    if(passiveskill[10]=="1"):
        effects["Once only"]=True
        
    
    
    return(effects)

def KiOrbType(kiOrbNumber, DEVEXCEPTIONS=False):
    if(kiOrbNumber=="0"):
        output="AGL"
    elif(kiOrbNumber=="1"):
        output="TEQ"
    elif(kiOrbNumber=="2"):
        output="INT"
    elif(kiOrbNumber=="3"):
        output="STR"
    elif(kiOrbNumber=="4"):
        output="PHY"
    elif(kiOrbNumber=="5"):
        output="RAINBOW"
    else:
        output="UNKNOWN"
        if(DEVEXCEPTIONS==True):
            raise Exception("Unknown ki orb type")
    return(output)

def extractClassType(classTypeNumber, DEVEXCEPTIONS=False):
    outputClass=[]
    outputType=[]
    classTypeNumber=int(classTypeNumber)
    binaryclassTypeNumber=bin(int(classTypeNumber))[2:]
    binaryclassTypeNumber=binaryclassTypeNumber.zfill(32)
    if binaryclassTypeNumber[27]=="1" or binaryclassTypeNumber[15]=="1" or binaryclassTypeNumber[10]=="1":
        outputType.append("PHY")
    if binaryclassTypeNumber[28]=="1" or binaryclassTypeNumber[16]=="1" or binaryclassTypeNumber[11]=="1":
        outputType.append("STR")
    if binaryclassTypeNumber[29]=="1" or binaryclassTypeNumber[17]=="1" or binaryclassTypeNumber[12]=="1":
        outputType.append("INT")
    if binaryclassTypeNumber[30]=="1" or binaryclassTypeNumber[18]=="1" or binaryclassTypeNumber[13]=="1":
        outputType.append("TEQ")
    if binaryclassTypeNumber[31]=="1" or binaryclassTypeNumber[19]=="1" or binaryclassTypeNumber[14]=="1":
        outputType.append("AGL")
    
    if binaryclassTypeNumber[25]=="1":
        outputClass.append("Extreme")
    if binaryclassTypeNumber[26]=="1":
        outputClass.append("Super")

    if "1" in binaryclassTypeNumber[15:20]:
        outputClass.append("Super")
    if "1" in binaryclassTypeNumber[10:15]:
        outputClass.append("Extreme")

    return(outputClass,outputType)

def extractAllyTyping(typingID,DEVEXCEPTIONS=False):
    if(typingID=="0"):
        typing="AGL"
    elif(typingID=="1"):
        typing="TEQ"
    elif(typingID=="2"):
        typing="INT"
    elif(typingID=="3"):
        typing="STR"
    elif(typingID=="4"):
        typing="PHY"
    else:
        typing="UNKNOWN TYPE"
        if(DEVEXCEPTIONS==True):
            raise Exception("Unknown type")
    return(typing)

def filterIncompletePngs(directory, thresholdInBytes,printing=True):
    if(directory[-1]!="/"):
        directory+="/"
    assumeFalse=False
    allPngs=os.listdir(directory)
    for png in allPngs:
        if(os.path.isdir(directory+png)):
            if(filterIncompletePngs(directory+png, thresholdInBytes)):
                assumeFalse=True
        else:
            if(os.path.getsize(directory+png)<thresholdInBytes):
            
                os.remove(directory+png)
                assumeFalse=True
    return(assumeFalse)
            
def definewith0(unitid,printing=True):
    if unitid.endswith('1'):
        return unitid[:-1] + '0'
    else:
        return unitid
    
def definewith1(unitid,printing=True):
    if unitid.endswith('0'):
        return unitid[:-1] + '1'
    else:
        return unitid

def causalityExtractor(causality):
    if(causality==""):
        return([])
    else:
        result=causality.split("compiled")[1]
        result=result.replace('"',"")
        result=result.replace("\\","")
        result=result.replace("[","")
        result=result.replace("]","")
        result=result.replace(":","")
        result=result.replace("}","")
        result=result.replace(" ","")
        result=result.split(",")
        for x in result:
            if "u" in x:
                result.remove(x)
        return(result)

def logicalCausalityExtractor(causality):
    if(causality==""):
        return([])
    else:
        result=causality.split('","compiled')
        if(len(result)==1):
            result=causality.split('", "compiled')
        result=result[0]
        if(len(result.split('source":"'))!=1):
            result=result.split('source":"')[1]
        else:
            result=result.split('source": "')[1]
        result=unicode_fixer(result)
        return(result)
    
def CausalityLogicalExtractor(unit,causality,printing=True,DEVEXCEPTIONS=False):
    output={}
    result=causality.replace("|"," || ").replace("&"," && ")
    currentCausality=""
    for x in causality:
        if(x.isnumeric()):
            currentCausality+=x
        else:
            if(currentCausality!=""):
                newCausality=causalityLogicFinder(unit,currentCausality,printing=True,DEVEXCEPTIONS=DEVEXCEPTIONS)
                if(newCausality=={"Button":{}, "Slider": {"Name": None, "Logic": None}}):
                    newCausality=None
                output[currentCausality]=newCausality
            currentCausality=""

    if(currentCausality!=""):
        newCausality=causalityLogicFinder(unit=unit,causalityCondition=currentCausality,printing=True,DEVEXCEPTIONS=DEVEXCEPTIONS)
        if(newCausality=={"Button":{}, "Slider": {"Name": None, "Logic": None}}):
            newCausality=None
        output[currentCausality]=newCausality
    for key in output.copy():
        if(output[key]==None):
            output.pop(key)
    returnDictionary={"Logic":result,"Causalities":output}
    if(returnDictionary["Causalities"]=={}):
        returnDictionary=None
    return(returnDictionary)

def longestCommonSubstring(listOfStrings):
    listOfStrings.sort(key=len)
    baseString=listOfStrings[0]
    longestString=""
    for startingChar in range(0,len(baseString)+1):
        for endingChar in range(startingChar,len(baseString)+1):
            validString=True
            for string in listOfStrings:
                if(baseString[startingChar:endingChar] not in string):
                    validString=False
                    break
        if(validString==True):
            if(len(baseString[startingChar:endingChar])>len(longestString)):
                longestString=baseString[startingChar:endingChar]


    return(longestString)


def CategoryExtractor(CategoryId):
    for category in card_categoriesGB:
        if category[0]==CategoryId:
            return(category[1])

def causalityLineToLogic(causalityLine,DEVEXCEPTIONS=False):
    CausalityRow=causalityLine
    output={"Button":{},"Slider":{}}
    if(CausalityRow[1]=="0"):
        pass
    elif(CausalityRow[1]=="1"):
        output["Button"]["Name"]="Is HP "
        output["Button"]["Name"]+=CausalityRow[2]
        output["Button"]["Name"]+=" % or more?"
        output["Slider"]["Name"]="What percentage of HP is remaining?"
        output["Slider"]["Logic"]=">="
        output["Slider"]["Logic"]+=CausalityRow[2]
        output["Slider"]["Min"]=0
        output["Slider"]["Max"]=100

    elif(CausalityRow[1]=="2"):
        output["Button"]["Name"]="Is HP "
        output["Button"]["Name"]+=CausalityRow[2]
        output["Button"]["Name"]+=" % or less?"
        output["Slider"]["Name"]="What percentage of HP is remaining?"
        output["Slider"]["Logic"]="<="
        output["Slider"]["Logic"]+=CausalityRow[2]
        output["Slider"]["Min"]=0
        output["Slider"]["Max"]=100
    elif(CausalityRow[1]=="3"):
        Ca2=int(CausalityRow[2])
        unit31=int(unit[31])
        kiAmount=(Ca2*unit31)//99

        output["Button"]["Name"]="Is ki "
        output["Button"]["Name"]+=str(kiAmount)
        output["Button"]["Name"]+=" or more"

        output["Slider"]["Name"]="How much ki is there?"
        output["Slider"]["Logic"]=">="
        output["Slider"]["Logic"]+=str(kiAmount)
        output["Slider"]["Min"]=0
        if(unit[5]=="5"):
            output["Slider"]["Max"]=24
        else:
            output["Slider"]["Max"]=12
    elif(CausalityRow[1]=="4"):
        Ca2=int(CausalityRow[2])
        unit31=int(unit[31])
        kiAmount=(Ca2*unit31)//99

        output["Button"]["Name"]="Is ki "
        output["Button"]["Name"]+=str(kiAmount)
        output["Button"]["Name"]+=" or less"

        output["Slider"]["Name"]="How much ki is there?"
        output["Slider"]["Logic"]="<="
        output["Slider"]["Logic"]+=str(kiAmount)
        output["Slider"]["Min"]=0
        if(unit[5]=="5"):
            output["Slider"]["Max"]=24
        else:
            output["Slider"]["Max"]=12
    elif(CausalityRow[1]=="5"):
        output["Button"]["Name"]="Is the turn count "
        output["Button"]["Name"]+=str(int(CausalityRow[2])+1)
        output["Button"]["Name"]+=" or more?"

        output["Slider"]["Name"]="What turn is it?"
        output["Slider"]["Logic"]=">="
        output["Slider"]["Logic"]+=str(int(CausalityRow[2])+1)
        output["Slider"]["Min"]=1
    elif(CausalityRow[1]=="8"):
        output["Button"]["Name"]="Is attack higher than enemy's?"
    elif(CausalityRow[1]=="9"):
        output["Button"]["Name"]="Is attack lower than enemy's?"
    elif(CausalityRow[1]=="14"):
        output["Button"]["Name"]="Is the first to attack?"
    elif(CausalityRow[1]=="15"):
        output["Button"]["Name"]="Is there "
        output["Button"]["Name"]+=CausalityRow[2]
        output["Button"]["Name"]+=" or more enemies?"
        
        output["Slider"]["Name"]="How many enemies are there?"
        output["Slider"]["Logic"]=">="
        output["Slider"]["Logic"]+=CausalityRow[2]
        output["Slider"]["Min"]=1
        output["Slider"]["Max"]=7
    elif(CausalityRow[1]=="16"):
        output["Button"]["Name"]="Is there less than "
        output["Button"]["Name"]+=CausalityRow[2]
        output["Button"]["Name"]+=" enemies?"
        
        output["Slider"]["Name"]="How many enemies are there?"
        output["Slider"]["Logic"]="<"
        output["Slider"]["Logic"]+=CausalityRow[2]
        output["Slider"]["Min"]=1
        output["Slider"]["Max"]=7
    elif(CausalityRow[1]=="17"):
        output["Button"]["Name"]="Is the enemy's health "
        output["Button"]["Name"]+=CausalityRow[2]
        output["Button"]["Name"]+=" % or more?"

        output["Slider"]["Name"]="What percentage of HP does the enemy have?"
        output["Slider"]["Logic"]=">="
        output["Slider"]["Logic"]+=CausalityRow[2]
        output["Slider"]["Max"]=100
    elif(CausalityRow[1]=="18"):
        output["Button"]["Name"]="Is the enemy's health "
        output["Button"]["Name"]+=CausalityRow[2]
        output["Button"]["Name"]+=" % or less?"

        output["Slider"]["Name"]="What percentage of HP does the enemy have?"
        output["Slider"]["Logic"]="<="
        output["Slider"]["Logic"]+=CausalityRow[2]
        output["Slider"]["Max"]=100
    elif(CausalityRow[1]=="19"):
        output["Button"]["Name"]="Is this the "
        output["Button"]["Name"]+=ordinalise(int(CausalityRow[2])+1)
        output["Button"]["Name"]+=" attacker in the turn?"

        output["Slider"]["Name"]="What position is this character attacking in?"
        output["Slider"]["Logic"]="=="
        output["Slider"]["Logic"]+=str(int(CausalityRow[2])+1)
        output["Slider"]["Min"]=1
        output["Slider"]["Max"]=3

    elif(CausalityRow[1]=="24"):
        output["Button"]["Name"]="Has attack been recieved?"
        output["Slider"]["Name"]="How many attacks has this character recieved?"
        output["Slider"]["Logic"]=">=1"
        output["Slider"]["Min"]=0
        output["Slider"]["Max"]=1
    elif(CausalityRow[1]=="25"):
        output["Button"]["Name"]="Has this character delivered the final blow?"

    elif(CausalityRow[1]=="30"):
        output["Button"]["Name"]="Has guard been activated?"
    elif(CausalityRow[1]=="31"):
        output["Button"]["Name"]="Has 3 attacks in a row?"
    elif(CausalityRow[1]=="33"):
        output["Button"]["Name"]="Is HP between "
        output["Button"]["Name"]+=CausalityRow[2]
        output["Button"]["Name"]+=" % and "
        output["Button"]["Name"]+=CausalityRow[3]
        output["Button"]["Name"]+=" %?"

        output["Slider"]["Name"]="What percentage of HP is remaining?"
        output["Slider"]["Logic"]=">="
        output["Slider"]["Logic"]+=CausalityRow[2]
        output["Slider"]["Logic"]+=" && <="
        output["Slider"]["Logic"]+=CausalityRow[3]
        output["Slider"]["Min"]=0
        output["Slider"]["Max"]=100
    elif(CausalityRow[1]=="34"):
        if(CausalityRow[2]=="0"):
            target="units on the team?"
            output["Slider"]["Max"]=7
        elif(CausalityRow[2]=="1"):
            target="enemies "
            output["Slider"]["Max"]=7
        elif(CausalityRow[2]=="2"):
            target="units on the same turn?"
            output["Slider"]["Max"]=3
        categoryType=searchbyid(CausalityRow[3],codecolumn=0,database=card_categoriesGB,column=1)[0]

        output["Button"]["Name"]="Are there "


        if(CausalityRow[4]=="0"):
            output["Button"]["Name"]="Are there no "
            output["Button"]["Name"]+=categoryType
            output["Button"]["Name"]+=" category "
            output["Button"]["Name"]+=target
            output["Slider"]["Name"]="?"

            output["Slider"]["Name"]="How many "
            output["Slider"]["Name"]+=categoryType
            output["Slider"]["Name"]+=" category "
            output["Slider"]["Name"]+=target
            output["Slider"]["Logic"]="=="
            output["Slider"]["Logic"]+=0
            output["Slider"]["Min"]=0
        else:
            output["Button"]["Name"]="Are there "
            output["Button"]["Name"]+=CausalityRow[4]
            output["Button"]["Name"]+=" or more "
            output["Button"]["Name"]+=categoryType
            output["Button"]["Name"]+=" category "
            output["Button"]["Name"]+=target
            output["Slider"]["Name"]="?"

            output["Slider"]["Name"]="How many "
            output["Slider"]["Name"]+=categoryType
            output["Slider"]["Name"]+=" category "
            output["Slider"]["Name"]+=target
            output["Slider"]["Logic"]=">="
            output["Slider"]["Logic"]+=CausalityRow[4]
            output["Slider"]["Min"]=0
    elif(CausalityRow[1]=="35"):
        output["Button"]["Name"]="Does the team include "
        if(extractClassType(CausalityRow[2],DEVEXCEPTIONS=DEVEXCEPTIONS)==(["Super"],["PHY","STR","INT","TEQ","AGL"])):
            output["Button"]["Name"]+="all five Super types?"
        elif(extractClassType(CausalityRow[2],DEVEXCEPTIONS=DEVEXCEPTIONS)==(["Extreme"],["PHY","STR","INT","TEQ","AGL"])):
            output["Button"]["Name"]+="all five Extreme types?"
        else:
            print("UNKNOWN TYPE")
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown type")
    elif(CausalityRow[1]=="37"):
        output["Button"]["Name"]="Is HP "
        output["Button"]["Name"]+=CausalityRow[2]
        output["Button"]["Name"]+=" % or less starting from the "
        output["Button"]["Name"]+=ordinalise(int(CausalityRow[3])+1)
        output["Button"]["Name"]+=" turn from the start of battle?"

    elif(CausalityRow[1]=="38"):
        Status=binaryStatus(CausalityRow[2])
        output["Button"]["Name"]="Is the target enemy "
        output["Button"]["Name"]+=Status
        output["Button"]["Name"]+="?"
    elif(CausalityRow[1]=="39"):
        if(CausalityRow[2]=="32"):
            output["Button"]["Name"]="Is this unit attacking a super class enemy?"
        elif(CausalityRow[2]=="64"):
            output["Button"]["Name"]="Is this unit attacking an extreme class enemy?"
        else:
            print("UNKNOWN TYPE")
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown type")
    elif(CausalityRow[1]=="40"):
        output["Button"]["Name"]="Is a super being performed?"
    elif(CausalityRow[1]=="41"):
        if(CausalityRow[2]=="0"):
            output["Button"]["Name"]="Is there an ally on the team whose name includes "
        elif(CausalityRow[2]=="1"):
            output["Button"]["Name"]="Is there an enemy whose name includes "
        elif(CausalityRow[2]=="2"):
            output["Button"]["Name"]="Is there an ally attacking in the same turn whose name includes "
        else:
            output+=("UNKNOWN NAME TYPE")
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown name type")
        card_unique_info_id=searchbyid(code=CausalityRow[3],codecolumn=2,database=card_unique_info_set_relationsJP,column=1)
        possible_names=[]
        for id in card_unique_info_id:
            name=searchbycolumn(code=id,column=3,database=cardsGB)
            for unit in name:
                if(qualifyUsable(card=unit)):
                    possible_names.append(unit[1])
        likelyName=longestCommonSubstring(possible_names) 
        output["Button"]["Name"]+=likelyName
        output["Button"]["Name"]+=("?")

            

    elif(CausalityRow[1]=="42"):
        output["Button"]["Name"]="Has "
        output["Button"]["Name"]+=CausalityRow[3]
        output["Button"]["Name"]+=" or more "
        kiSphereType=binaryOrbType(CausalityRow[2],DEVEXCEPTIONS)
        for orbType in kiSphereType:
            output["Button"]["Name"]+=orbType
            output["Button"]["Name"]+=" or "
        output["Button"]["Name"]=output["Button"]["Name"][:-4]
        output["Button"]["Name"]+=" Ki Spheres been obtained?"
        output["Slider"]["Name"]="How many "
        for orbType in kiSphereType:
            output["Slider"]["Name"]+=orbType
            output["Slider"]["Name"]+=" or "
        output["Slider"]["Name"]=output["Slider"]["Name"][:-4]
        output["Slider"]["Name"]+=" Ki Spheres have been obtained?"
        output["Slider"]["Logic"]=">="
        output["Slider"]["Logic"]+=CausalityRow[3]
    elif(CausalityRow[1]=="43"):
        output["Button"]["Name"]="Has this unit evaded an attack?"
    elif(CausalityRow[1]=="44"):
        if(CausalityRow[2]=="0" or CausalityRow[2]=="1"):
            output["Button"]["Name"]="Has this character performed their "
            output["Button"]["Name"]+=(ordinalise(CausalityRow[3]))
            output["Button"]["Name"]+=(" super attack in battle?")
        elif(CausalityRow[2])=="2":
            output["Button"]["Name"]="Has this character performed their "
            output["Button"]["Name"]+=(ordinalise(CausalityRow[3]))
            output["Button"]["Name"]+=(" attack in battle?")

            output["Slider"]["Name"]="How many attacks has this character performed?"
            output["Slider"]["Logic"]=">="
            output["Slider"]["Logic"]+=CausalityRow[3]
            output["Slider"]["Min"]=0
            output["Slider"]["Max"]=int(CausalityRow[3])
        elif(CausalityRow[2]=="3"):
            output["Button"]["Name"]="Has this character recieved their "
            output["Button"]["Name"]+=(ordinalise(CausalityRow[3]))
            output["Button"]["Name"]+=(" attack in battle?")

            output["Slider"]["Name"]="How many attacks has this character recieved?"
            output["Slider"]["Logic"]=">="
            output["Slider"]["Logic"]+=CausalityRow[3]
            output["Slider"]["Min"]=0
            output["Slider"]["Max"]=int(CausalityRow[3])
        elif(CausalityRow[2]=="4"):
            output["Button"]["Name"]="Has this character's guard been activated "
            output["Button"]["Name"]+=(ordinalise(CausalityRow[3]))
            output["Button"]["Name"]+=(" times in battle?")

            output["Slider"]["Name"]="How many times has this character's guard been activated?"
            output["Slider"]["Logic"]=">="
            output["Slider"]["Logic"]+=CausalityRow[3]
            output["Slider"]["Min"]=0
            output["Slider"]["Max"]=int(CausalityRow[3])
        elif(CausalityRow[2]=="5"):
            output["Button"]["Name"]="Has this character evaded "
            output["Button"]["Name"]+=(ordinalise(CausalityRow[3]))
            output["Button"]["Name"]+=(" times in battle?")

            output["Slider"]["Name"]="How many attacks have been evaded?"
            output["Slider"]["Logic"]=">="
            output["Slider"]["Logic"]+=CausalityRow[3]
            output["Slider"]["Min"]=0
            output["Slider"]["Max"]=int(CausalityRow[3])
        else:
            output+=("UNKNOWN NAME TYPE")
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown name type")
    elif(CausalityRow[1]=="45"):
        categoryType=searchbyid(CausalityRow[3],codecolumn=0,database=card_categoriesGB,column=1)[0]

        card_unique_info_id=searchbyid(code=CausalityRow[4],codecolumn=2,database=card_unique_info_set_relationsJP,column=1)
        possible_names=[]
        for id in card_unique_info_id:
            name=searchbyid(code=id,codecolumn=3,database=cardsJP,column=1)
            if (name!=None):
                possible_names.append(name)
        likelyName=longestCommonSubstring(possible_names) 

        if(CausalityRow[2]=="0"):
            output["Button"]["Name"]=("Is there a ")
            output["Button"]["Name"]+=(categoryType)
            output["Button"]["Name"]+=(" Category ally whose name includes ")
            output["Button"]["Name"]+=likelyName
            output["Button"]["Name"]+=(" on the team?")
        elif(CausalityRow[2]=="1"):
            output["Button"]["Name"]=("Is there a ")
            output["Button"]["Name"]+=(categoryType)
            output["Button"]["Name"]+=(" Category enemy whose name includes ")
            output["Button"]["Name"]+=likelyName
            output["Button"]["Name"]+=("?")
        elif(CausalityRow[2]=="2"):
            output["Button"]["Name"]=("Is there a ")
            output["Button"]["Name"]+=(categoryType)
            output["Button"]["Name"]+=(" Category ally whose name includes ")
            output["Button"]["Name"]+=likelyName
            output["Button"]["Name"]+=(" attacking in the same turn?")
        else:
            output+=("UNKNOWN NAME TYPE")
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown name type")

    elif(CausalityRow[1]=="46"):
        output["Button"]["Name"]=("Is there an extreme class enemy?")
    elif(CausalityRow[1]=="47"):
        output["Button"]["Name"]=("Has this character or an ally attacking in the same turn been KO'd?")
    elif(CausalityRow[1]=="48"):
        output["Button"]["Name"]=("Has the enemy been hit by the characters ultra super attack?")
    elif(CausalityRow[1]=="49"):
        if(CausalityRow[2]=="1"):
            output["Button"]["Name"]=("Has the character been attacked by a ki blast super attack?")
        elif(CausalityRow[2]=="2"):
            output["Button"]["Name"]=("Has the character been attacked by an unarmed super attack?")
        elif(CausalityRow[2]=="4"):
            output["Button"]["Name"]=("Has the character been attacked by a physical super attack?")
        else:
            output+=("UNKNOWN SUPER ATTACK TYPE")
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown super attack type")
    elif(CausalityRow[1]=="51"):
        output["Button"]["Name"]=("Is it within the first ")
        output["Button"]["Name"]+=CausalityRow[2]
        output["Button"]["Name"]+=(" turns from entry turn?")
        
        output["Slider"]["Name"]="How many turns is it since entry turn?"
        output["Slider"]["Logic"]="<="
        output["Slider"]["Logic"]+=CausalityRow[2]
        output["Slider"]["Min"]=0
        output["Slider"]["Max"]=int(CausalityRow[2])
    elif(CausalityRow[1]=="53"):
        output["Button"]["Name"]=("Has this characters finish effect been activated?")
    elif(CausalityRow[1]=="54"):
        output["Button"]["Name"]=("Has the character or an ally's revival skill been activated?")
    elif(CausalityRow[1]=="55"):
        output["Button"]["Name"]=("Is it on or after the first ")
        output["Button"]["Name"]+=CausalityRow[2]
        output["Button"]["Name"]+=(" turns from this characters entry turn?")

        output["Slider"]["Name"]="How many turns is it since entry turn?"
        output["Slider"]["Logic"]=">="
        output["Slider"]["Logic"]+=CausalityRow[2]
    elif(CausalityRow[1]=="56"):
        output["Button"]["Name"]=("Has the character recieved a normal attack?")
    elif(CausalityRow[1]=="57"):
        output["Button"]["Name"]=("Is the Domain ")
        output["Button"]["Name"]+=searchbyid(code=CausalityRow[2],codecolumn=1,database=dokkan_fieldsJP,column=2)[0]
        GBdomain=searchbyid(code=CausalityRow[2],codecolumn=1,database=dokkan_fieldsGB,column=2)
        if(GBdomain!=[]):
            output["Button"]["Name"]+=GBdomain[0]
        else:
            output["Button"]["Name"]+=searchbyid(code=CausalityRow[2],codecolumn=1,database=dokkan_fieldsJP,column=2)[0]
        output["Button"]["Name"]+=(" active")
    elif(CausalityRow[1]=="58"):
        output["Button"]["Name"]=("Is no domain active?")
    elif(CausalityRow[1]=="61"):
        output["Button"]["Name"]=("Did the character recieve an attack on this turn?")
    else:
        output["Button"]["Name"]=("UNKNOWN CAUSALITY CONDITION")
        if(DEVEXCEPTIONS==True):
            raise Exception("Unknown causality condition")
    return(output)

def causalityLogicFinder(unit,causalityCondition,printing=True,DEVEXCEPTIONS=False):
    output={"Button":{}, "Slider": {"Name": None, "Logic": None}}
    for row in skill_causalitiesJP:
        if row[0] == causalityCondition:
            CausalityRow=row
            if(CausalityRow[1]=="0"):
                pass
            elif(CausalityRow[1]=="1"):
                output["Button"]["Name"]="Is HP "
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=" % or more?"
                output["Slider"]["Name"]="What percentage of HP is remaining?"
                output["Slider"]["Logic"]=">="
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Min"]=0
                output["Slider"]["Max"]=100

            elif(CausalityRow[1]=="2"):
                output["Button"]["Name"]="Is HP "
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=" % or less?"
                output["Slider"]["Name"]="What percentage of HP is remaining?"
                output["Slider"]["Logic"]="<="
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Min"]=0
                output["Slider"]["Max"]=100
            elif(CausalityRow[1]=="3"):
                Ca2=int(CausalityRow[2])
                unit31=int(unit[31])
                kiAmount=(Ca2*unit31)//99

                output["Button"]["Name"]="Is Ki at least "
                output["Button"]["Name"]+=str(kiAmount)
                output["Button"]["Name"]+="?"

                output["Slider"]["Name"]="How much ki is there?"
                output["Slider"]["Logic"]=">="
                output["Slider"]["Logic"]+=str(kiAmount)
                output["Slider"]["Min"]=0
                if(unit[5]=="5"):
                    output["Slider"]["Max"]=24
                else:
                    output["Slider"]["Max"]=12
            elif(CausalityRow[1]=="4"):
                Ca2=int(CausalityRow[2])
                unit31=int(unit[31])
                kiAmount=(Ca2*unit31)//99

                output["Button"]["Name"]="Is Ki at least "
                output["Button"]["Name"]+=str(kiAmount)
                output["Button"]["Name"]+="?"


                output["Slider"]["Name"]="How much ki is there?"
                output["Slider"]["Logic"]="<="
                output["Slider"]["Logic"]+=str(kiAmount)
                output["Slider"]["Min"]=0
                if(unit[5]=="5"):
                    output["Slider"]["Max"]=24
                else:
                    output["Slider"]["Max"]=12
            elif(CausalityRow[1]=="5"):
                output["Button"]["Name"]="Is the turn count "
                output["Button"]["Name"]+=str(int(CausalityRow[2])+1)
                output["Button"]["Name"]+=" or more?"

                output["Slider"]["Name"]="What turn is it?"
                output["Slider"]["Logic"]=">="
                output["Slider"]["Logic"]+=str(int(CausalityRow[2])+1)
                output["Slider"]["Min"]=1
            elif(CausalityRow[1]=="8"):
                output["Button"]["Name"]="Is attack higher than enemy's?"
            elif(CausalityRow[1]=="9"):
                output["Button"]["Name"]="Is attack lower than enemy's?"
            elif(CausalityRow[1]=="14"):
                output["Button"]["Name"]="Is the first to attack?"
            elif(CausalityRow[1]=="15"):
                output["Button"]["Name"]="Is there "
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=" or more enemies?"
                
                output["Slider"]["Name"]="How many enemies are there?"
                output["Slider"]["Logic"]=">="
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Min"]=1
                output["Slider"]["Max"]=7
            elif(CausalityRow[1]=="16"):
                output["Button"]["Name"]="Is there less than "
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=" enemies?"
                
                output["Slider"]["Name"]="How many enemies are there?"
                output["Slider"]["Logic"]="<"
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Min"]=1
                output["Slider"]["Max"]=7
            elif(CausalityRow[1]=="17"):
                output["Button"]["Name"]="Is the enemy's health "
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=" % or more?"

                output["Slider"]["Name"]="What percentage of HP does the enemy have?"
                output["Slider"]["Logic"]=">="
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Max"]=100
            elif(CausalityRow[1]=="18"):
                output["Button"]["Name"]="Is the enemy's health "
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=" % or less?"

                output["Slider"]["Name"]="What percentage of HP does the enemy have?"
                output["Slider"]["Logic"]="<="
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Max"]=100
            elif(CausalityRow[1]=="19"):
                output["Button"]["Name"]="Is this the "
                output["Button"]["Name"]+=ordinalise(int(CausalityRow[2])+1)
                output["Button"]["Name"]+=" attacker in the turn?"

                output["Slider"]["Name"]="What position is this character attacking in?"
                output["Slider"]["Logic"]="=="
                output["Slider"]["Logic"]+=str(int(CausalityRow[2])+1)
                output["Slider"]["Min"]=1
                output["Slider"]["Max"]=3

            elif(CausalityRow[1]=="24"):
                output["Button"]["Name"]="Has attack been recieved?"
                output["Slider"]["Name"]="How many attacks has this character recieved?"
                output["Slider"]["Logic"]=">=1"
                output["Slider"]["Min"]=0
                output["Slider"]["Max"]=1
            elif(CausalityRow[1]=="25"):
                output["Button"]["Name"]="Has this character delivered the final blow?"

            elif(CausalityRow[1]=="30"):
                output["Button"]["Name"]="Has guard been activated?"
            elif(CausalityRow[1]=="31"):
                output["Button"]["Name"]="Has 3 attacks in a row?"
            elif(CausalityRow[1]=="33"):
                output["Button"]["Name"]="Is HP between "
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=" % and "
                output["Button"]["Name"]+=CausalityRow[3]
                output["Button"]["Name"]+=" %?"

                output["Slider"]["Name"]="What percentage of HP is remaining?"
                output["Slider"]["Logic"]=">="
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Logic"]+=" and <="
                output["Slider"]["Logic"]+=CausalityRow[3]
                output["Slider"]["Min"]=0
                output["Slider"]["Max"]=100
            elif(CausalityRow[1]=="34"):
                if(CausalityRow[2]=="0"):
                    target="units on the team "
                    output["Slider"]["Max"]=7
                elif(CausalityRow[2]=="1"):
                    target="enemies "
                    output["Slider"]["Max"]=7
                elif(CausalityRow[2]=="2"):
                    target="units on the same turn "
                    output["Slider"]["Max"]=3
                categoryType=searchbyid(CausalityRow[3],codecolumn=0,database=card_categoriesGB,column=1)[0]

                output["Button"]["Name"]="Are there "


                if(CausalityRow[4]=="0"):
                    output["Button"]["Name"]="Are there no "
                    output["Button"]["Name"]+=categoryType
                    output["Button"]["Name"]+=" category "
                    output["Button"]["Name"]+=target
                    output["Slider"]["Name"]="?"

                    output["Slider"]["Name"]="How many "
                    output["Slider"]["Name"]+=categoryType
                    output["Slider"]["Name"]+=" category "
                    output["Slider"]["Name"]+=target
                    output["Slider"]["Logic"]="=="
                    output["Slider"]["Logic"]+=0
                    output["Slider"]["Min"]=0
                else:
                    output["Button"]["Name"]="Are there "
                    output["Button"]["Name"]+=CausalityRow[4]
                    output["Button"]["Name"]+=" or more "
                    output["Button"]["Name"]+=categoryType
                    output["Button"]["Name"]+=" category "
                    output["Button"]["Name"]+=target
                    output["Slider"]["Name"]="?"

                    output["Slider"]["Name"]="How many "
                    output["Slider"]["Name"]+=categoryType
                    output["Slider"]["Name"]+=" category "
                    output["Slider"]["Name"]+=target
                    output["Slider"]["Logic"]=">="
                    output["Slider"]["Logic"]+=CausalityRow[4]
                    output["Slider"]["Min"]=0
            elif(CausalityRow[1]=="35"):
                output["Button"]["Name"]="Does the team include "
                if(extractClassType(CausalityRow[2],DEVEXCEPTIONS=DEVEXCEPTIONS)==(["Super"],["PHY","STR","INT","TEQ","AGL"])):
                    output["Button"]["Name"]+="all five Super types?"
                elif(extractClassType(CausalityRow[2],DEVEXCEPTIONS=DEVEXCEPTIONS)==(["Extreme"],["PHY","STR","INT","TEQ","AGL"])):
                    output["Button"]["Name"]+="all five Extreme types?"
                else:
                    print("UNKNOWN TYPE")
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown type")
            elif(CausalityRow[1]=="37"):
                output["Button"]["Name"]="Is HP "
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=" % or less starting from the "
                output["Button"]["Name"]+=ordinalise(int(CausalityRow[3])+1)
                output["Button"]["Name"]+=" turn from the start of battle?"

            elif(CausalityRow[1]=="38"):
                Status=binaryStatus(CausalityRow[2])
                output["Button"]["Name"]="Is the target enemy "
                output["Button"]["Name"]+=Status
                output["Button"]["Name"]+="?"
            elif(CausalityRow[1]=="39"):
                if(CausalityRow[2]=="32"):
                    output["Button"]["Name"]="Is this unit attacking a super class enemy?"
                elif(CausalityRow[2]=="64"):
                    output["Button"]["Name"]="Is this unit attacking an extreme class enemy?"
                else:
                    print("UNKNOWN TYPE")
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown type")
            elif(CausalityRow[1]=="40"):
                output["Button"]["Name"]="Is a super being performed?"
            elif(CausalityRow[1]=="41"):
                if(CausalityRow[2]=="0"):
                    output["Button"]["Name"]="Is there an ally on the team whose name includes "
                elif(CausalityRow[2]=="1"):
                    output["Button"]["Name"]="Is there an enemy whose name includes "
                elif(CausalityRow[2]=="2"):
                    output["Button"]["Name"]="Is there an ally attacking in the same turn whose name includes "
                else:
                    output+=("UNKNOWN NAME TYPE")
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown name type")
                card_unique_info_id=searchbyid(code=CausalityRow[3],codecolumn=2,database=card_unique_info_set_relationsJP,column=1)
                possible_names=[]
                for id in card_unique_info_id:
                    name=searchbycolumn(code=id,column=3,database=cardsGB)
                    for unit in name:
                        if(qualifyUsable(card=unit) and unit[0][0]=="1"):
                            possible_names.append(unit[1])
                likelyName=longestCommonSubstring(possible_names) 
                output["Button"]["Name"]+=likelyName
                output["Button"]["Name"]+=("?")

                    

            elif(CausalityRow[1]=="42"):
                output["Button"]["Name"]="Has "
                output["Button"]["Name"]+=CausalityRow[3]
                output["Button"]["Name"]+=" or more "
                kiSphereType=binaryOrbType(CausalityRow[2],DEVEXCEPTIONS)
                for orbType in kiSphereType:
                    output["Button"]["Name"]+=orbType
                    output["Button"]["Name"]+=" or "
                output["Button"]["Name"]=output["Button"]["Name"][:-4]
                output["Button"]["Name"]+=" Ki Spheres been obtained?"
                output["Slider"]["Name"]="How many "
                for orbType in kiSphereType:
                    output["Slider"]["Name"]+=orbType
                    output["Slider"]["Name"]+=" or "
                output["Slider"]["Name"]=output["Slider"]["Name"][:-4]
                output["Slider"]["Name"]+=" Ki Spheres have been obtained?"
                output["Slider"]["Logic"]=">="
                output["Slider"]["Logic"]+=CausalityRow[3]
                output["Slider"]["Min"]=0
                output["Slider"]["Max"]=int(CausalityRow[3])
            elif(CausalityRow[1]=="43"):
                output["Button"]["Name"]="Has this unit evaded an attack?"
            elif(CausalityRow[1]=="44"):
                if(CausalityRow[2]=="0" or CausalityRow[2]=="1"):
                    output["Slider"]["Name"]="How many super attacks has this character performed?"
                    output["Slider"]["Logic"]=">="
                    output["Slider"]["Logic"]+=CausalityRow[3]
                    output["Slider"]["Min"]=0
                    output["Slider"]["Max"]=int(CausalityRow[3])
                elif(CausalityRow[2])=="2":
                    output["Slider"]["Name"]="How many attacks has this character performed in battle?"
                    output["Slider"]["Logic"]=">="
                    output["Slider"]["Logic"]+=CausalityRow[3]
                    output["Slider"]["Min"]=0
                    output["Slider"]["Max"]=int(CausalityRow[3])
                elif(CausalityRow[2]=="3"):
                    output["Button"]["Name"]="Has this character recieved their "
                    output["Button"]["Name"]+=(ordinalise(CausalityRow[3]))
                    output["Button"]["Name"]+=(" attack in battle?")

                    output["Slider"]["Name"]="How many attacks has this character recieved?"
                    output["Slider"]["Logic"]=">="
                    output["Slider"]["Logic"]+=CausalityRow[3]
                    output["Slider"]["Min"]=0
                    output["Slider"]["Max"]=int(CausalityRow[3])
                elif(CausalityRow[2]=="4"):
                    output["Button"]["Name"]="Has this character's guard been activated "
                    output["Button"]["Name"]+=(ordinalise(CausalityRow[3]))
                    output["Button"]["Name"]+=(" times in battle?")

                    output["Slider"]["Name"]="How many times has this character's guard been activated?"
                    output["Slider"]["Logic"]=">="
                    output["Slider"]["Logic"]+=CausalityRow[3]
                    output["Slider"]["Min"]=0
                    output["Slider"]["Max"]=int(CausalityRow[3])
                elif(CausalityRow[2]=="5"):
                    output["Button"]["Name"]="Has this character evaded "
                    output["Button"]["Name"]+=(ordinalise(CausalityRow[3]))
                    output["Button"]["Name"]+=(" times in battle?")

                    output["Slider"]["Name"]="How many attacks have been evaded?"
                    output["Slider"]["Logic"]=">="
                    output["Slider"]["Logic"]+=CausalityRow[3]
                    output["Slider"]["Min"]=0
                    output["Slider"]["Max"]=int(CausalityRow[3])
                else:
                    output+=("UNKNOWN NAME TYPE")
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown name type")
            elif(CausalityRow[1]=="45"):
                categoryType=searchbyid(CausalityRow[3],codecolumn=0,database=card_categoriesGB,column=1)[0]

                card_unique_info_id=searchbyid(code=CausalityRow[4],codecolumn=2,database=card_unique_info_set_relationsJP,column=1)
                possible_names=[]
                for id in card_unique_info_id:
                    name=searchbyid(code=id,codecolumn=3,database=cardsJP,column=1)
                    if (name!=None):
                        possible_names.append(name)
                likelyName=longestCommonSubstring(possible_names) 

                if(CausalityRow[2]=="0"):
                    output["Button"]["Name"]=("Is there a ")
                    output["Button"]["Name"]+=(categoryType)
                    output["Button"]["Name"]+=(" Category ally whose name includes ")
                    output["Button"]["Name"]+=likelyName
                    output["Button"]["Name"]+=(" on the team?")
                elif(CausalityRow[2]=="1"):
                    output["Button"]["Name"]=("Is there a ")
                    output["Button"]["Name"]+=(categoryType)
                    output["Button"]["Name"]+=(" Category enemy whose name includes ")
                    output["Button"]["Name"]+=likelyName
                    output["Button"]["Name"]+=("?")
                elif(CausalityRow[2]=="2"):
                    output["Button"]["Name"]=("Is there a ")
                    output["Button"]["Name"]+=(categoryType)
                    output["Button"]["Name"]+=(" Category ally whose name includes ")
                    output["Button"]["Name"]+=likelyName
                    output["Button"]["Name"]+=(" attacking in the same turn?")
                else:
                    output+=("UNKNOWN NAME TYPE")
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown name type")

            elif(CausalityRow[1]=="46"):
                output["Button"]["Name"]=("Is there an extreme class enemy?")
            elif(CausalityRow[1]=="47"):
                output["Button"]["Name"]=("Has this character or an ally attacking in the same turn been KO'd?")
            elif(CausalityRow[1]=="48"):
                output["Button"]["Name"]=("Has the enemy been hit by the characters ultra super attack?")
            elif(CausalityRow[1]=="49"):
                if(CausalityRow[2]=="1"):
                    output["Button"]["Name"]=("Has the character been attacked by a ki blast super attack?")
                elif(CausalityRow[2]=="2"):
                    output["Button"]["Name"]=("Has the character been attacked by an unarmed super attack?")
                elif(CausalityRow[2]=="4"):
                    output["Button"]["Name"]=("Has the character been attacked by a physical super attack?")
                else:
                    output+=("UNKNOWN SUPER ATTACK TYPE")
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown super attack type")
            elif(CausalityRow[1]=="51"):
                output["Button"]["Name"]=("Is it within the first ")
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=(" turns from entry turn?")
                
                output["Slider"]["Name"]="How many turns is it since entry turn?"
                output["Slider"]["Logic"]="<="
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Min"]=0
                output["Slider"]["Max"]=int(CausalityRow[2])
            elif(CausalityRow[1]=="53"):
                output["Button"]["Name"]=("Has this characters finish effect been activated?")
            elif(CausalityRow[1]=="54"):
                output["Button"]["Name"]=("Has the character or an ally's revival skill been activated?")
            elif(CausalityRow[1]=="55"):
                output["Button"]["Name"]=("Is it on or after the first ")
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=(" turns from this characters entry turn?")

                output["Slider"]["Name"]="How many turns is it since entry turn?"
                output["Slider"]["Logic"]=">="
                output["Slider"]["Logic"]+=CausalityRow[2]
            elif(CausalityRow[1]=="56"):
                output["Button"]["Name"]=("Has the character recieved a normal attack?")
            elif(CausalityRow[1]=="57"):
                output["Button"]["Name"]=("Is the Domain ")
                GBdomain=searchbyid(code=CausalityRow[2],codecolumn=1,database=dokkan_fieldsGB,column=2)
                if(GBdomain!=[]):
                    output["Button"]["Name"]+=GBdomain[0]
                else:
                    output["Button"]["Name"]+=searchbyid(code=CausalityRow[2],codecolumn=1,database=dokkan_fieldsJP,column=2)[0]

                output["Button"]["Name"]+=(" active")
            elif(CausalityRow[1]=="58"):
                output["Button"]["Name"]=("Is no domain active?")
            elif(CausalityRow[1]=="59"):
                if(CausalityRow[2]=="1"):
                    output["Button"]["Name"]=("Is this character super class?")
                elif(CausalityRow[2]=="2"):
                    output["Button"]["Name"]=("Is this character extreme class?")
            elif(CausalityRow[1]=="60"):
                Categories=sub_target_types_extractor(CausalityRow[2])
                output["Button"]["Name"]="Is this character on the "
                for category in Categories["Category"]:
                    output["Button"]["Name"]+=category
                    output["Button"]["Name"]+=(" or ")
                output["Button"]["Name"]=output["Button"]["Name"][:-3]
                output["Button"]["Name"]+="category?"

                if(Categories["Excluded Category"]!=[]):
                    output["Button"]["Name"]+=" (Excluding "
                    for category in Categories["Excluded Category"]:
                        output["Button"]["Name"]+=category
                        output["Button"]["Name"]+=(" or ")
                    output["Button"]["Name"]=output["Button"]["Name"][:-3]
                    output["Button"]["Name"]+="category)"
            elif(CausalityRow[1]=="61"):
                output["Button"]["Name"]=("Did the character recieve an attack on this turn?")
            else:
                output["Button"]["Name"]=("UNKNOWN CAUSALITY CONDITION")
                if(DEVEXCEPTIONS==True):
                    raise Exception("Unknown causality condition")
    if(output["Button"]=={}):
        output.pop("Button")
    if(output["Slider"]=={"Name": None, "Logic": None}):
        output.pop("Slider")
    return(output)

def binaryStatus(Statusid):
    output=""
    binaryId=bin(int(Statusid))[2:]
    binaryId=binaryId.zfill(11)
    if(binaryId[6]=="1"):
        output+='in "ATK down" status or '
    if(binaryId[5]=="1"):
        output+='in "DEF down" status or '
    if(binaryId[2]=="1"):
        output+="stunned or "
    if(binaryId[0]=="1"):
        output+="sealed or "
    
    output=output[:-4]
    return(output)

def binaryOrbType(kiOrbType,DEVEXCEPTIONS=False):
    output=[]
    AllTypes=True
    AllOrbs=True
    kiOrbType=int(kiOrbType)
    binarykiOrb=bin(int(kiOrbType))[2:]
    binarykiOrb=binarykiOrb.zfill(10)
    if(binarykiOrb[0:4])=="0111":
        output.append("Sweet treats")
    if(binarykiOrb[2]=="1"):
        output.append("Cookies")
    if(binarykiOrb[4]=="1"):
        output.append("Rainbow")
    if(binarykiOrb[5]=="1"):
        output.append("PHY")
    if(binarykiOrb[6]=="1"):
        output.append("STR")
    if(binarykiOrb[7]=="1"):
        output.append("INT")
    if(binarykiOrb[8]=="1"):
        output.append("TEQ")
    if(binarykiOrb[9]=="1"):
        output.append("AGL")
    if(output==[]):
        if(DEVEXCEPTIONS==True):
            raise Exception("Unknown orb type")
    return(output)
    
def TransformationReverseUnit(card,printing=True):
    for passiveskillpiece in passive_skillsJP:
        if passiveskillpiece[13]==card[0]:
            #is a transformation
            for passiverelation in passive_skill_set_relationsJP:#
                if passiverelation[2]==passiveskillpiece[0]:
                    #passiveset found
                    for unit in cardsJP:
                        if unit[21][0:-2]==passiverelation[1]:
                            return(unit)
    
def activeSkillTransformationReverseUnit(card,printing=True):
    for possibleactive in active_skillsJP:
        if(possibleactive[6]==card[0]):
            #unit comes from an active skill
            for possibleactivelink in card_active_skillsJP:
                if possibleactivelink[2]==possibleactive[1]:
                    #link found
                    for unit in cardsJP:
                        if unit[0]==possibleactivelink[1]:
                            return(unit)

def activeSkillTransformationUnit(card,printing=True):
    for possibleactivelink in card_active_skillsJP:
        if possibleactivelink[1]==card[0]:
            #they have an active
            for possibleactive in active_skillsJP:
                if possibleactivelink[2]==possibleactive[1]:
                    
                    #has a transforming one, defined in possibleactive
                    for unit in cardsJP:
                        if unit[0]==possibleactive[6]:
                            return(unit)

def dokkanAwakenUnit(card,printing=False):
    possibleAwakening=searchbycolumn(code=card[0],database=card_awakening_routesJP,column=2)
    possibleDokkanAwakening=searchbycolumn(code="CardAwakeningRoute::Dokkan",database=possibleAwakening, column=1)
    if(possibleDokkanAwakening==[]):
        return(None)
    else:
        return(possibleDokkanAwakening[0][3])


def dokkanreverseunit(card,printing=False):
    for awakenable_unit in card_awakening_routesJP:
        if awakenable_unit[1]=="CardAwakeningRoute::Dokkan":
            if(card[0])==(awakenable_unit[3]):
                for unit in cardsJP:
                    if unit[0]==awakenable_unit[2]:
                        return(unit)
    return(None)

def qualifyAsDFETUR(card,printing=True):
    if qualifyUsable(card) and card[4]=="58" and ((card[29]=="" and card[0][0]=="1")==False):
        return(True)
    else:
        return(False)
    
def qualifyAsDFE(card,printing=True):
    if(qualifyAsDFELR(card) or qualifyAsDFETUR(card)):
        return(True)
    else:
        return(False)            

def qualifyAsDFELR(card,printing=True):
    assumeFalse=False
    reversed=dokkanreverseunit(card)
    if(reversed==None):
        assumeFalse=(False)
    elif(reversed[4]=="58"):
        return(True)
        
    reversed=activeSkillTransformationReverseUnit(card)
    if(reversed==None):
        assumeFalse=(False)
    else:
        return(qualifyAsDFELR(reversed))
    
    reversed=TransformationReverseUnit(card)
    if(reversed==None):
        assumeFalse=(False)
    else:
        return(qualifyAsDFELR(reversed))
    
    if assumeFalse==False:
        return(False)
    
def qualifyAsLR(card,printing=True):
    if qualifyUsable(card) and (getrarity(card)=="lr"):
        return(True)
    else:
        return(False)
    
def qualifyEZA(card,printing=True):
    directory="data/"
    if qualifyUsable(card) and (checkeza(card)):
        return(True)
    else:
        return(False)

def switchUnitToGlobal(unitJP):
    unitGB = searchbycolumn(code=unitJP[0],database=cardsGB,column=0)
    if(unitGB!=[]):
        unitGB=unitGB[0]
    else:
        unitGB=None
    return(unitGB)


def qualifyUsable(card,printing=True):
    #if the unit is a tur+ and id ends in 0
    if(card[5] in ["5","4"] and card[0][-1]=="0"):
        return(False)
    #if the unit id doesnt start with a 1 or a 4
    if(card[0][0] not in ["1","2","4"]):
        return(False)
    #if the unit is selling only
    if(card[0]=="id"):
        return(False)
    #if the unit has a placeholder release date
    if(card[53] in ["2030-12-31 23:59:59",'2030-01-01 00:00:00',"2038-01-01 00:00:00"]):
        return(False)
    #if the unit has 1 in their stats
    if("1" in card[6:12]):
        return(False)
    #if all the units stats are divisible by 50
    if(0==sum([int(card[6])%50,int(card[7])%50,int(card[8])%50,int(card[9])%50,int(card[10])%50,int(card[11])%50])):
        return(False)
    #If the unit has selling only
    if(card[46]=="1"):
        return(False)
    #if the unit is the header
    return(True)

def emptyFolder(path):
    for filename in os.listdir(path):
        file_path = os.path.join(path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

def getKiCircleSegments(unitDictionary):
    kiAmounts=unitDictionary["Ki Multiplier"]
    circleSegments={}
    if(unitDictionary["Rarity"]=="lr"):
        maxki=24
    else:
        maxki=12
    minsuperKi=24
    minUltraKi=24
    for super in unitDictionary["Super Attack"]:
        kiRequired=int(unitDictionary["Super Attack"][super]["superMinKi"])
        if(unitDictionary["Super Attack"][super]["SpecialBonus"]["ID"]!="0"):
            if(unitDictionary["Super Attack"][super]["SpecialBonus"]["Type"]=="Ki requirement decrease"):
                kiRequired-=int(unitDictionary["Super Attack"][super]["SpecialBonus"]["Amount"])
        if(unitDictionary["Super Attack"][super]["superStyle"]=="Hyper"):
            minUltraKi=min(minUltraKi,kiRequired)
        elif(unitDictionary["Super Attack"][super]["superStyle"]=="Normal"):
            minsuperKi=min(minsuperKi,kiRequired)

    for ki in range(1,maxki+1):
        if(kiAmounts[ki]<100):
            circleSegments[ki]="weaker"
        else:
            circleSegments[ki]="equal"
        if(ki>=minsuperKi):
            circleSegments[ki]="super"
        if(ki>=minUltraKi):
            circleSegments[ki]="ultra"

    return(circleSegments)
        

def getAdditionalSuperID(unitDictionary):
    lowestConditionSuperID=None
    lowestKiRequired=24
    for super in unitDictionary["Super Attack"]:
        if(unitDictionary["Super Attack"][super]["superStyle"]=="Normal"):
            kiRequired=int(unitDictionary["Super Attack"][super]["superMinKi"])
            if(kiRequired<lowestKiRequired):
                lowestKiRequired=kiRequired
                lowestConditionSuperID=super
    return(lowestConditionSuperID)


        

        

def createEZAWallpapers(cards, directory,printing=True):
    if(printing): print("Creating EZA wallpapers")
    acquiredlist = os.listdir(r'./assets/EZA wallpapers')
    leader_skills=storedatabase(directory,"leader_skills.csv")
    optimal_awakening_growths=storedatabase(directory,"optimal_awakening_growths.csv")
    total=0
    for card in cards:
        if (card[53]!="2030-12-31 23:59:59") and (card[0][0]!="9") and (card[0][-1]=="0") and (card[22]!="") and ((("final_"+card[0]+".png") not in acquiredlist)) and (checkeza(card)):
            unitid=card[0]
            if unitid[-1]=="1":
                unitid=str(int(unitid)-1)
            mainunit=card

        #background
            cframeurl=("../frontend/dbManagement/assets/misc/cha_base_0")
        #element
            cframeurl+=(mainunit[12][-1])
            cframeurl+=("_0")
        #rarity
            cframeurl+=(mainunit[5])
            cframeurl+=(".png")


            cframe = Image.open(cframeurl).convert("RGBA")
            cframe=cframe.resize((200,200))

        #character icon
            ciconurl=("../frontend/dbManagement/assets/thumb/")
            if card[48]=="" or card[48]=="0.0":
                ciconurl+=unitid
            else:
                ciconurl+=str(int(float(card[48])))
            ciconurl+=(".png")
            cicon = Image.open(ciconurl).convert("RGBA")
            cicon.resize((250,250))


        #rarity
            crarityurl=("../frontend/dbManagement/assets/misc/cha_rare_")
            crarityurl+=(getrarity(mainunit))
            crarityurl+=(".png")
            crarity = Image.open(crarityurl).convert("RGBA")
            if getrarity(mainunit)=="ssr":
                crarity=crarity.resize((120,72))
            else:    
                crarity=crarity.resize((160,96))

        #element
            celementurl=("../frontend/dbManagement/assets/misc/cha_type_icon_")
            if len(mainunit[12])==1:
                celementurl+=("0")
            celementurl+=(mainunit[12])
            celementurl+=(".png")
            celement = Image.open(celementurl).convert("RGBA")
            celement=celement.resize((90,90))
            if mainunit[12] in ("20","10"):
                if(printing): print("AGL ",end="")
            elif mainunit[12] in ("21","11"):
                if(printing): print("TEQ ",end="")
            elif mainunit[12] in ("22","12"):
                if(printing): print("INT ",end="")
            elif mainunit[12] in ("23","13"):
                if(printing): print("STR ",end="")
            elif mainunit[12] in ("24","14"):
                if(printing): print("PHY ",end="")

            (width,height)=(cicon.width+10,cicon.height+10)
            cfinal=Image.new("RGBA",(width,height))
            cfinal.paste(cframe, (25,35), cframe)
            cfinal.paste(cicon, (0,1), cicon)
            if getrarity(mainunit)=="n":
                cfinal.paste(crarity, (-37,160),crarity)
                if(printing): print("N ",end="")
            elif getrarity(mainunit)=="r":
                cfinal.paste(crarity, (-42,160), crarity)
                if(printing): print("R ",end="")
            elif getrarity(mainunit)=="sr":
                cfinal.paste(crarity, (-25,158), crarity)
                if(printing): print("SR ",end="")
            elif getrarity(mainunit)=="ssr":
                cfinal.paste(crarity, (-5,171), crarity)
                if(printing): print("SSR ",end="")
            elif getrarity(mainunit)=="ur":
                cfinal.paste(crarity, (-25,160), crarity)
                if(printing): print("UR ",end="")
            elif getrarity(mainunit)=="lr" or True:
                cfinal.paste(crarity, (-25,155),crarity)
                if(printing): print("LR ",end="")
            cfinal.paste(celement, (170,5),celement)
            
            if(printing): print(mainunit[1])
            wallpapername=("../frontend/dbManagement/assets/EZA wallpapers/final_")
            wallpapername+=(unitid)
            wallpapername+=(".png")
            cfinal.save(wallpapername)
            total+=1
            if total%100==0:
                if(printing): print(total)
            #print("Created final asset for",total,getfullname(card,leader_skills))
    if(printing): print("All EZA assets created")

def parsePassiveSkill(unit,eza=False,seza=False,DEVEXCEPTIONS=False):
    output={}
    passiveIdList=getpassiveid(unit,eza,seza)
    if (passiveIdList!=None):
        for passiveskill in passive_skillsJP[1:]:
            if (passiveskill[0] in passiveIdList):
                parsedLine=(extractPassiveLine(unit,passiveskill,printing=False,DEVEXCEPTIONS=DEVEXCEPTIONS))
                #output=shortenPassiveDictionary(output)
                parsedLine=shortenPassiveDictionary(parsedLine)
                if("Building Stat" in parsedLine):
                    if(parsedLine["Building Stat"]["Cause"]["Cause"]=="Look Elsewhere"):
                        parsedLine=removeLookElseWhere(parsedLine,True)
                parsedLine=polishPassiveLine(parsedLine)
                output[passiveskill[0]]=parsedLine
    return(output)


def polishPassiveLine(parsedLine):
    output=parsedLine.copy()
    if("Once only" in parsedLine):
        if("Condition" in parsedLine):
            output["Condition"]["Causalities"]=parsedLine["Condition"]["Causalities"].copy()
            newCausality={}
            newCausality["Button"]={"Name":""}
            
            if(parsedLine["Length"]=="99"):
                newCausality["Button"]["Name"]+="Has the following been true:"
            elif(parsedLine["Length"]=="1"):
                newCausality["Button"]["Name"]+="Is it the first time that the following is true:"
            elif(parsedLine["Length"]!="1"):
                newCausality["Button"]["Name"]+="Was it the first time that the following is true:"

            CausalitiesLogic=(" "+parsedLine["Condition"]["Logic"]+" ").replace("&&","and").replace("||","or").replace("("," ( ").replace(")"," ) ")
            currentCausality=""
            for char in parsedLine["Condition"]["Logic"]+" ":
                if char!=" " and char.isdigit():
                    currentCausality+=char
                elif char==" " and currentCausality!="":
                    #use current char
                    if("Button" in parsedLine["Condition"]["Causalities"][currentCausality]):
                        new_logic=parsedLine["Condition"]["Causalities"][currentCausality]["Button"]["Name"][:-1]
                    else:
                        new_logic=parsedLine["Condition"]["Causalities"][currentCausality]["Slider"]["Name"][:-1]
                        logicalOperation=parsedLine["Condition"]["Causalities"][currentCausality]["Slider"]["Logic"]
                        logicalOperation=logicalOperation.replace(">="," is greater than or equal to ").replace(">"," is greater than ").replace("<=", " is less than or equal to ").replace("<"," is less than ")
                        new_logic+=logicalOperation

                    CausalitiesLogic=CausalitiesLogic.replace(" "+      currentCausality      +" ",              " "+  new_logic   +" ")
                    currentCausality=""
            newCausality["Button"]["Name"]+=CausalitiesLogic
            CausalityKeys=list(output["Condition"]["Causalities"].keys()).copy()
            for oldCausality in CausalityKeys:
                del output["Condition"]["Causalities"][oldCausality]
            if(parsedLine["Length"]!="1" and parsedLine["Length"]!="99"):
                newCausality["Button"]["Name"]+=" within the last "+parsedLine["Length"]+" turns"
            while "  " in newCausality["Button"]["Name"]:
                newCausality["Button"]["Name"]=newCausality["Button"]["Name"].replace("  "," ")
            output["Condition"]["Logic"]=output["ID"]
            output["Condition"]["Causalities"][output["ID"]]=newCausality
        #Once only, no condition
        else:
            newCondition={"Logic":output["ID"],"Causalities":{output["ID"]: {"Button":{"Name":"Is it within the first "+output["Length"]+" turns from entry turn?"},"Slider":{"Name":"How many turns is it since entry turn?","Logic":"<="+output["Length"],"Max": str(int(output["Length"])+1),"Min":"1"}}}}
            output["Condition"]=newCondition

    elif("Condition" in parsedLine):
        duration=parsedLine["Length"]
        for CausalityKey in parsedLine["Condition"]["Causalities"]:
            Causality=parsedLine["Condition"]["Causalities"][CausalityKey]
            if("Button" in Causality):
                if("turns" not in Causality["Button"]["Name"]):
                    if(duration=="1"):
                        Causality["Button"]["Name"]=Causality["Button"]["Name"][:-1]+" on this turn?"
                    elif(duration!="99"):
                        Causality["Button"]["Name"]=Causality["Button"]["Name"][:-1]+" within the last "+duration+" turns?"
                
            if("Slider" in Causality):
                if("turns" not in Causality["Slider"]["Name"]):
                    if(duration=="1"):
                        Causality["Slider"]["Name"]=Causality["Slider"]["Name"][:-1]+" on this turn?"
                    elif(duration!="99"):
                        Causality["Slider"]["Name"]=Causality["Slider"]["Name"][:-1]+" within the last "+duration+" turns?"

    elif(parsedLine["Timing"]=="End of turn"):
        if("Condition" in parsedLine):
            for CausalityKey in parsedLine["Condition"]["Causalities"]:
                Causality=parsedLine["Condition"]["Causalities"][CausalityKey]
                if("Button" in Causality):
                    Causality["Button"]["Name"]=Causality["Button"]["Name"][:-1].replace("Is ","Was ")+" on the previous turn?"
                if("Slider" in Causality):
                    Causality["Slider"]["Name"]=Causality["Slider"]["Name"][:-1].replace("Is ","Was ")+" on previous turns?"


    elif("Disable Other Line" in parsedLine):
        if("Condition" not in parsedLine and parsedLine["Timing"]=="Attacking the enemy"):
            newCondition={"Logic":output["ID"],"Causalities":{output["ID"]: {"Button":{"Name":"How many attacks has this character performed on this turn?"},"Slider":{"Name":"How many attacks has this character performed? on this turn","Logic":"<="+output["Length"],"Max": str(int(output["Length"])+1),"Min":"1"}}}}
            output["Condition"]=newCondition


 

                    



    return(output)

def removeLookElseWhere(parsedLine,DEVECXEPTION=True):
    output=parsedLine
    causalities=[""]
    if("Condition" in parsedLine):
        causalities=[]
        for causalityKey in parsedLine["Condition"]["Causalities"]:
            causalities.append(parsedLine["Condition"]["Causalities"][causalityKey]["Button"]["Name"])

    if(parsedLine["Timing"]=="Hit recieved" and len(causalities)==1 and causalities[0]=="Has this unit evaded an attack?"):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Attacks evaded"
        output["Building Stat"]["Slider"]="How many attacks have been evaded?"

    elif(parsedLine["Timing"]=="Hit recieved" and len(causalities)==1 and causalities[0][:33]=='Has this character recieved their'):
        quantity=causalities[0][34]
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]=quantity+" attacks recieved"
        output["Building Stat"]["Slider"]="How many times has this character recieved "+quantity+" attacks?"
    
    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==1 and causalities[0]=='Is HP 80 % or less?'):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="HP 80% or less"
        output["Building Stat"]["Slider"]="How many times has HP been 80% or less?"

    elif(parsedLine["Timing"]=="Hit recieved" and len(causalities)==1 and causalities[0]=='Has attack been recieved?'):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Attacks recieved"
        output["Building Stat"]["Slider"]="How many attacks has this character recieved?"

    elif(parsedLine["Timing"]=="Attacking the enemy" and causalities[0]==""):
        output["Building Stat"]["Cause"]["Cause"]="Attacks performed"
        output["Building Stat"]["Slider"]="How many attacks has this character performed in battle?"

    elif(parsedLine["Timing"]=="Start of turn" and causalities[0]==""):
        output["Building Stat"]["Cause"]["Cause"]="Start of turn"
        output["Building Stat"]["Slider"]="How many turns has this character been on?"

    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==1 and causalities[0][:63]=='Is there an ally attacking in the same turn whose name includes'):
        del output["Condition"]
        allyName=causalities[0][64:-1]
        output["Building Stat"]["Cause"]["Cause"]="Turns with ally "+allyName
        output["Building Stat"]["Slider"]="How many turns has this character been on with an ally whose name includes "+allyName+"?"

    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==1 and causalities[0][:48]=='Is there an ally on the team whose name includes'):
        del output["Condition"]
        allyName=causalities[0][49:-1]
        output["Building Stat"]["Cause"]["Cause"]="Turns with ally on the team whose name includes "+allyName
        output["Building Stat"]["Slider"]="How many turns has this character been on with an ally on the team whose name includes "+allyName+"?"

    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==2 and causalities[0][:63]=='Is there an ally attacking in the same turn whose name includes' and causalities[1][:63]=='Is there an ally attacking in the same turn whose name includes'):
        del output["Condition"]
        ally1Name=causalities[0][64:-1]
        ally2Name=causalities[1][64:-1]
        output["Building Stat"]["Cause"]["Cause"]="Turns with ally "+ally1Name+" or "+ally2Name
        output["Building Stat"]["Slider"]="How many turns has this character been on with an ally whose name includes "+ally1Name+" or "+ally2Name+"?"
    
    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==1 and causalities[0][-17:]=='category enemies ' and causalities[0][:20]=='Are there 1 or more '):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Turns with a "+causalities[0][20:-18]+" category enemy"
        output["Building Stat"]["Slider"]="How many turns has this character been on with a "+causalities[0][20:-18]+" category enemy?"

    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==2 and causalities[0][:20]=='Are there 1 or more ' and causalities[0][-17:]=='category enemies ' and causalities[1][:20]=='Are there 1 or more ' and causalities[1][-17:]=='category enemies '):
        del output["Condition"]
        enemy1=causalities[0][20:-18]
        enemy2=causalities[1][20:-18]
        output["Building Stat"]["Cause"]["Cause"]="Turns with a "+enemy1+""+" or "+enemy2+" category enemy"
        output["Building Stat"]["Slider"]="How many turns has this character been on with a "+enemy1+" or "+enemy2+" category enemy?"
    
    elif((parsedLine["Timing"]=="Being hit" or parsedLine["Timing"]=="Hit recieved") and len(causalities)==1 and causalities[0]=='Has guard been activated?'):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Guard activated"
        output["Building Stat"]["Slider"]="How many times has this character's guard been activated?"
    
    elif(parsedLine["Timing"]=="Hit recieved" and len(causalities)==2 and causalities[0]=='Has attack been recieved?' and causalities[1][-32:]=='category units on the same turn '):
        del output["Condition"]
        category=causalities[1][20:-34]
        quantity=causalities[1][10]
        output["Building Stat"]["Cause"]["Cause"]="Attacks recieved with "+quantity+" or more "+category+" category units on the same turn"
        output["Building Stat"]["Slider"]="How many attacks has this character recieved while there was "+quantity+" or more "+category+" category units on the same turn?"
    
    elif(parsedLine["Timing"]=="Hit recieved" and len(causalities)==2 and causalities[0]=="Has this unit evaded an attack?" and causalities[1][:48]=='Is there an ally on the team whose name includes'):
        del output["Condition"]
        allyName=causalities[1][49:-1]
        output["Building Stat"]["Cause"]["Cause"]="Attacks evaded with an ally on the team whose name includes "+allyName
        output["Building Stat"]["Slider"]="How many attacks has this unit evaded with an ally on the team whose name includes "+allyName+"?"

    elif(parsedLine["Timing"]=="Hit recieved" and len(causalities)==2 and causalities[0]=='Has attack been recieved?' and causalities[1]=='Has this unit evaded an attack?'):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Attacks recieved or evaded"
        output["Building Stat"]["Slider"]="How many attacks has this unit recieved or evaded?"

    elif(parsedLine["Timing"]=="When final blow delivered" and len(causalities)==1 and causalities[0]=='Has this character delivered the final blow?'):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Final blow delivered"
        
    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==1 and causalities[0][:12]=='Is there an ' and causalities[0][-12:]=='class enemy?'):
        del output["Condition"]
        enemyClass=causalities[0][12:-14]
        output["Building Stat"]["Cause"]["Cause"]="Turns with a "+enemyClass+" class enemy"
        output["Building Stat"]["Slider"]="How many turns has this character been on with a "+enemyClass+" class enemy?"

    elif(parsedLine["Timing"]=="Attacking the enemy" and len(causalities)<=2 and causalities[0][:12]=="Is this the " and causalities[0][-21:]=="attacker in the turn?"):
        del output["Condition"]
        firstSlot=causalities[0][12:-22]
        if(len(causalities)==2):
            secondSlot=causalities[1][12:-22]
            output["Building Stat"]["Cause"]["Cause"]="Attacking as the "+firstSlot+" or "+secondSlot+"attacker in the turn"
            output["Building Stat"]["Slider"]="How many times has this character attacked as the "+firstSlot+" or "+secondSlot+"attacker in the turn?"
        else:
            output["Building Stat"]["Cause"]["Cause"]="Attacking as the "+firstSlot+"attacker in the turn"
            output["Building Stat"]["Slider"]="How many times has this character attacked as the "+firstSlot+"attacker in the turn?"

    elif(parsedLine["Timing"]=="Hit recieved" and causalities[0][:9]=='Are there' and causalities[0][-27:]=='category units on the team ' and causalities[2][:9]=='Are there' and causalities[2][-27:]=='category units on the team ' and causalities[1]=="Has guard been activated?"):
        del output["Condition"]
        quantity1=causalities[0][10]
        quantity2=causalities[2][10]
        category1=causalities[0][20:-28]
        category2=causalities[2][20:-28]
        output["Building Stat"]["Cause"]["Cause"]="Guard activated with "+quantity1+" or more "+category1+" category units on the team or "+quantity2+" or more "+category2+" category units on the team"
        output["Building Stat"]["Slider"]="How many times has this character's guard been activated with "+quantity1+" or more "+category1+" category units on the team or "+quantity2+" or more "+category2+" category units on the team?"

    elif(parsedLine["Timing"]=="Start of turn" and causalities[0][:9]=='Are there' and causalities[0][-27:]=='category units on the team '):
        del output["Condition"]
        quantity=causalities[0][10]
        category=causalities[0][20:-28]
        output["Building Stat"]["Cause"]["Cause"]="Turns with "+quantity+" or more "+category+" category units on the team"
        output["Building Stat"]["Slider"]="How many turns has this character been on with "+quantity+" or more "+category+" category units on the team?"

    elif(parsedLine["Timing"]=="Attacking the enemy" and len(causalities)==1 and causalities[0][:22]=='Is the target enemy in'):
        del output["Condition"]
        condition=causalities[0][23:-1]
        output["Building Stat"]["Cause"]["Cause"]="Attacking the enemy in "+condition
        output["Building Stat"]["Slider"]="How many times has this character attacked the enemy in "+condition+"?"

    elif(parsedLine["Timing"]=="Being hit" and len(causalities)==1 and causalities[0]=="Is a super being performed?"):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Super attack recieved"
        output["Building Stat"]["Slider"]="How many super attacks has this character recieved?"

    elif((parsedLine["Timing"]=="Attacking the enemy" and len(causalities)==1 and causalities[0]=='Is a super being performed?') or (parsedLine["Timing"]=="On Super" and len(causalities)==1 and causalities[0]=='') or (parsedLine["Timing"]=='On Super' and len(causalities)==1 and causalities[0]=='Is a super being performed?')):
        if("Condition" in output):
            del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Super being performed"
        output["Building Stat"]["Slider"]="How many super attacks has this character performed?"
    


    else:
        print("LOOK ELSEWHERE NOT ACCOUNTED FOR",parsedLine)
        if(DEVECXEPTION):
            raise Exception("LOOK ELSEWHERE NOT ACCOUNTED FOR",parsedLine)



    return(output)

def parseActiveSkill(unit,DEVEXCEPTIONS=False):
    active_id=searchbyid(unit[0],codecolumn=1,database=card_active_skillsJP,column=2)
    if(active_id!=None):
        active_id=active_id[0]
        active_lineGB=searchbycolumn(code=active_id,column=0,database=active_skill_setsGB)
        active_lineJP=searchbycolumn(code=active_id,column=0,database=active_skill_setsJP)
        active_lineJP=active_lineJP[0]
        if(active_lineGB==[]):
            JPexclusive=True
        else:
            active_lineGB=active_lineGB[0]
            JPexclusive=False

        output={}
        if(JPexclusive):
            output["Name"]=active_lineJP[1]
            output["Effect Description"]=active_lineJP[2]
            output["Condition Description"]=active_lineJP[3]
        else:
            output["Name"]=active_lineGB[1]
            output["Effect Description"]=active_lineGB[2]
            output["Condition Description"]=active_lineGB[3]
        causalityCondition=logicalCausalityExtractor(active_lineJP[6])
        output["Condition"]={}
        output["Condition"]["Logic"]=causalityCondition
        causalityCondition=CausalityLogicalExtractor(unit,causalityCondition,DEVEXCEPTIONS=DEVEXCEPTIONS)
        output["Condition"].update(causalityCondition)
        output["Uses"]=int(active_lineJP[5])
        
        if(active_lineJP[7]!=""):
            special_id=active_lineJP[7][:-2]
            ultimate_row=searchbycolumn(code=special_id,database=ultimate_specialsJP,column=0)
            ultimate_row=ultimate_row[0]
            output["Attack"]={}
            output["Attack"]["Multiplier"]=int(ultimate_row[3])
            if(ultimate_row[4]=="0"):
                output["Attack"]["Target"]="Enemy"
            elif(ultimate_row[4]=="1"):
                output["Attack"]["Target"]="All enemies"
        output["Effects"]={}
        effects_line=searchbycolumn(code=active_id,database=active_skillsJP,column=1)
        for line in effects_line:
            output["Effects"][line[0]]={}
            output["Effects"][line[0]]["Duration"]=active_lineJP[4]
            output["Effects"][line[0]]["Effect"]={}
            
            
            if(line[4]=="0"):
                output["Effects"][line[0]]["Effect"]["Type"]="Raw stats"
                output["Effects"][line[0]]["Effect"]["+ or -"]="+"

            elif(line[4]=="1"):
                output["Effects"][line[0]]["Effect"]["Type"]="Raw stats"
                output["Effects"][line[0]]["Effect"]["+ or -"]="-"

            elif(line[4]=="2"):
                output["Effects"][line[0]]["Effect"]["Type"]="Percentage"
                output["Effects"][line[0]]["Effect"]["+ or -"]="+"

            elif(line[4]=="3"):
                output["Effects"][line[0]]["Effect"]["Type"]="Percentage"
                output["Effects"][line[0]]["Effect"]["+ or -"]="-"
            else:
                output["Effects"][line[0]]["Effect"]["Type"]="Unknown"
                output["Effects"][line[0]]["Effect"]["+ or -"]="Unknown"
                if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown stat increase type")

            if(line[2]=="1"):
                output["Effects"][line[0]]["Target"]="Self"
            elif(line[2]=="2"):
                output["Effects"][line[0]]["Target"]="All allies"
            elif(line[2]=="3"):
                output["Effects"][line[0]]["Target"]="Enemy"
            elif(line[2]=="4"):
                output["Effects"][line[0]]["Target"]="All enemies"
            elif(line[2]=="12"):
                output["Effects"][line[0]]["Target"]="Super class enemies"
            elif(line[2]=="13"):
                output["Effects"][line[0]]["Target"]="Extreme class allies"
            elif(line[2]=="16"):
                output["Effects"][line[0]]["Target"]="All allies other than this character on every turn"
            else:
                print("Unknown target")
                if(DEVEXCEPTIONS):
                    raise Exception("Unknown Target")

            if(line[5]=="1"):
                output["Effects"][line[0]]["Effect"]["Buff"]="ATK Buff"
                output["Effects"][line[0]]["Effect"]["Amount"]=int(line[6])
            elif(line[5]=="2"):
                output["Effects"][line[0]]["Effect"]["Buff"]="DEF Buff"
                output["Effects"][line[0]]["Effect"]["Amount"]=int(line[6])
            elif(line[5]=="4"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Heals"
                output["Effects"][line[0]]["Effect"]["Amount"]=int(line[6])
            elif(line[5]=="5"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Ki Buff"
                output["Effects"][line[0]]["Effect"]["Amount"]=int(line[6])
            elif(line[5]=="9"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Stun"
            elif(line[5]=="22"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Remove negative effects"
            elif(line[5]=="48"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Seal"
            elif(line[5]=="51"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Changes orbs"
                output["Effects"][line[0]]["Effect"]["From"]=KiOrbType(line[6],DEVEXCEPTIONS)
                output["Effects"][line[0]]["Effect"]["To"]=KiOrbType(line[7],DEVEXCEPTIONS)
            elif(line[5]=="76"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Effective against all"
            elif(line[5]=="78"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Guard"
            elif(line[5]=="79"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Giant form/Rage"
                output["Effects"][line[0]]["Effect"]["Unit"]=line[6]
                battle_params=searchbycolumn(code=line[7],column=1,database=battle_paramsJP)
                for param in battle_params:
                    if(param[2]=="0"):
                        output["Effects"][line[0]]["Effect"]["Min turns"]=int(param[3])
                    elif(param[2]=="1"):
                        output["Effects"][line[0]]["Effect"]["Max turns"]=int(param[3])
                    elif(param[2]=="2"):
                        output["Effects"][line[0]]["Effect"]["Reverse chance"]=int(param[3])
            elif(line[5]=="90"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Crit chance"
                output["Effects"][line[0]]["Effect"]["Amount"]=int(line[6])
            elif(line[5]=="91"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Dodge chance"
                output["Effects"][line[0]]["Effect"]["Amount"]=int(line[6])
            elif(line[5]=="92"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Guaranteed to hit"
            elif(line[5]=="103"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Transforms"
                output["Effects"][line[0]]["Effect"]["Unit"]=line[6]
            elif(line[5]=="105"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Changes orbs"
                output["Effects"][line[0]]["Effect"]["From"]=["AGL","TEQ","INT","STR","PHY","Rainbow","Sweet treats"]
                output["Effects"][line[0]]["Effect"]["To"]=binaryOrbType(line[6],DEVEXCEPTIONS)
            elif(line[5]=="107"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Delays enemy attack"
                output["Effects"][line[0]]["Effect"]["Amount"]=int(line[6])
            elif(line[5]=="111"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Disable action"
            elif(line[5]=="123"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Redirect attacks to me"
            else:
                if(DEVEXCEPTIONS):
                    print("UNKNOWN ACTIVE EFFECT")
                    raise Exception("Unknown Active")





        return(output)
    






def createDFEWallpapers(cards, directory,printing=True):
    if(printing): print("Creating DFE wallpapers")
    acquiredlist = os.listdir(r'./assets/DFE wallpapers')
    leader_skills=storedatabase(directory,"leader_skills.csv")
    total=0
    for card in cards:
        if qualifyAsDFE(card) and (((definewith0(card[0])+".png") not in acquiredlist)):
            unitid=card[0]
            if unitid[-1]=="1":
                unitid=str(int(unitid)-1)
            mainunit=card

        #background
            cframeurl=("../frontend/dbManagement/assets/misc/cha_base_0")
        #element
            cframeurl+=(mainunit[12][-1])
            cframeurl+=("_0")
        #rarity
            cframeurl+=(mainunit[5])
            cframeurl+=(".png")


            cframe = Image.open(cframeurl).convert("RGBA")
            cframe=cframe.resize((200,200))

        #character icon
            ciconurl=("../frontend/dbManagement/assets/thumb/")
            if card[48]=="" or card[48]=="0.0":
                ciconurl+=unitid
            else:
                ciconurl+=str(int(float(card[48])))
            ciconurl+=(".png")
            cicon = Image.open(ciconurl).convert("RGBA")
            cicon.resize((250,250))


        #rarity
            crarityurl=("../frontend/dbManagement/assets/misc/cha_rare_")
            crarityurl+=(getrarity(mainunit))
            crarityurl+=(".png")
            crarity = Image.open(crarityurl).convert("RGBA")
            if getrarity(mainunit)=="ssr":
                crarity=crarity.resize((120,72))
            else:    
                crarity=crarity.resize((160,96))

        #element
            celementurl=("../frontend/dbManagement/assets/misc/cha_type_icon_")
            if len(mainunit[12])==1:
                celementurl+=("0")
            celementurl+=(mainunit[12])
            celementurl+=(".png")
            celement = Image.open(celementurl).convert("RGBA")
            celement=celement.resize((90,90))
            if mainunit[12] in ("20","10"):
                if(printing): print("AGL ",end="")
            elif mainunit[12] in ("21","11"):
                if(printing): print("TEQ ",end="")
            elif mainunit[12] in ("22","12"):
                if(printing): print("INT ",end="")
            elif mainunit[12] in ("23","13"):
                if(printing): print("STR ",end="")
            elif mainunit[12] in ("24","14"):
                if(printing): print("PHY ",end="")

            (width,height)=(cicon.width+10,cicon.height+10)
            cfinal=Image.new("RGBA",(width,height))
            cfinal.paste(cframe, (25,35), cframe)
            cfinal.paste(cicon, (0,1), cicon)
            if getrarity(mainunit)=="n":
                cfinal.paste(crarity, (-37,160),crarity)
                if(printing): print("N ",end="")
            elif getrarity(mainunit)=="r":
                cfinal.paste(crarity, (-42,160), crarity)
                if(printing): print("R ",end="")
            elif getrarity(mainunit)=="sr":
                cfinal.paste(crarity, (-25,158), crarity)
                if(printing): print("SR ",end="")
            elif getrarity(mainunit)=="ssr":
                cfinal.paste(crarity, (-5,171), crarity)
                if(printing): print("SSR ",end="")
            elif getrarity(mainunit)=="ur":
                cfinal.paste(crarity, (-25,160), crarity)
                if(printing): print("UR ",end="")
            elif getrarity(mainunit)=="lr" or True:
                cfinal.paste(crarity, (-25,155),crarity)
                if(printing): print("LR ",end="")
            cfinal.paste(celement, (170,5),celement)
            
            
            wallpapername=("../frontend/dbManagement/assets/DFE wallpapers/")
            wallpapername+=(unitid)
            wallpapername+=(".png")
            if(printing): print(mainunit[1])
            cfinal.save(wallpapername)
            total+=1
            if total%100==0:
                if(printing): print(total)
            #print("Created final asset for",total,getfullname(card,leader_skills))
    if(printing): print("All DFE assets created")

def createLRWallpapers(cards,directory,printing=True):
    if(printing): print("Creating LR wallpapers")
    acquiredlist = os.listdir(r'./assets/LR wallpapers')
    leader_skills=storedatabase(directory,"leader_skills.csv")
    total=0
    for card in cards:
        if (card[53]!="2030-12-31 23:59:59") and (card[0][0]!="9") and (card[0][-1]=="0") and (card[22]!="") and ((("final_"+card[0]+".png") not in acquiredlist)) and (getrarity(card)=="lr"):
            unitid=card[0]
            if unitid[-1]=="1":
                unitid=str(int(unitid)-1)
            mainunit=card

        #background
            cframeurl=("../frontend/dbManagement/assets/misc/cha_base_0")
        #element
            cframeurl+=(mainunit[12][-1])
            cframeurl+=("_0")
        #rarity
            cframeurl+=(mainunit[5])
            cframeurl+=(".png")

            cframe = Image.open(cframeurl).convert("RGBA")
            cframe=cframe.resize((200,200))

        #character icon
            ciconurl=("../frontend/dbManagement/assets/thumb/")
            if card[48]=="" or card[48]=="0.0":
                ciconurl+=unitid
            else:
                ciconurl+=str(int(float(card[48])))
            ciconurl+=(".png")
            cicon = Image.open(ciconurl).convert("RGBA")
            cicon.resize((250,250))


        #rarity
            crarityurl=("../frontend/dbManagement/assets/misc/cha_rare_")
            crarityurl+=(getrarity(mainunit))
            crarityurl+=(".png")
            crarity = Image.open(crarityurl).convert("RGBA")
            if getrarity(mainunit)=="ssr":
                crarity=crarity.resize((120,72))
            else:    
                crarity=crarity.resize((160,96))

        #element
            celementurl=("../frontend/dbManagement/assets/misc/cha_type_icon_")
            if len(mainunit[12])==1:
                celementurl+=("0")
            celementurl+=(mainunit[12])
            celementurl+=(".png")
            celement = Image.open(celementurl).convert("RGBA")
            celement=celement.resize((90,90))
            if mainunit[12] in ("20","10"):
                if(printing): print("AGL ",end="")
            elif mainunit[12] in ("21","11"):
                if(printing): print("TEQ ",end="")
            elif mainunit[12] in ("22","12"):
                if(printing): print("INT ",end="")
            elif mainunit[12] in ("23","13"):
                if(printing): print("STR ",end="")
            elif mainunit[12] in ("24","14"):
                if(printing): print("PHY ",end="")

            (width,height)=(cicon.width+10,cicon.height+10)
            cfinal=Image.new("RGBA",(width,height))
            cfinal.paste(cframe, (25,35), cframe)
            cfinal.paste(cicon, (0,1), cicon)
            if getrarity(mainunit)=="n":
                cfinal.paste(crarity, (-37,160),crarity)
                if(printing): print("N ",end="")
            elif getrarity(mainunit)=="r":
                cfinal.paste(crarity, (-42,160), crarity)
                if(printing): print("R ",end="")
            elif getrarity(mainunit)=="sr":
                cfinal.paste(crarity, (-25,158), crarity)
                if(printing): print("SR ",end="")
            elif getrarity(mainunit)=="ssr":
                cfinal.paste(crarity, (-5,171), crarity)
                if(printing): print("SSR ",end="")
            elif getrarity(mainunit)=="ur":
                cfinal.paste(crarity, (-25,160), crarity)
                if(printing): print("UR ",end="")
            elif getrarity(mainunit)=="lr" or True:
                cfinal.paste(crarity, (-25,155),crarity)
                if(printing): print("LR ",end="")
            cfinal.paste(celement, (170,5),celement)
            
            
            if(printing): print(mainunit[1])
            wallpapername=("../frontend/dbManagement/assets/LR wallpapers/final_")
            wallpapername+=(unitid)
            wallpapername+=(".png")
            cfinal.save(wallpapername)
            total+=1
            if total%100==0:
                if(printing): print(total)
            
    if(printing): print("All LR wallpapers created")

def getUnitTyping(unit,printing=True,DEVEXCEPTIONS=False):
    if unit[12][-1]=="0":
        typing="AGL"
    elif unit[12][-1]=="1":
        typing="TEQ"
    elif unit[12][-1]=="2":
        typing="INT"
    elif unit[12][-1]=="3":
        typing="STR"
    elif unit[12][-1]=="4":
        typing="PHY"
    else:
        typing="UNKNOWN"
        if(DEVEXCEPTIONS==True):
            raise Exception("Unknown typing")
    return(typing)

def getUnitClass(unit,printing=True,DEVEXCEPTIONS=False):
    if(len(unit[12])==1):
        return(None)
    elif unit[12][0]=="1":
        return("Super")
    elif unit[12][0]=="2":
        return("Extreme")
    
def createFinalAsset(card,printing=True):
    if qualifyUsable(card):
        if(card[48]!=""):
            resource_id=str(int(float(card[48])))
            if(resource_id[-1]=="1"):
                resource_id=str(int(resource_id)-1)
        else:
            if(card[0][-1]=="1"):
                resource_id=str(int(card[0])-1)
            else:
                resource_id=card[0]
        unitid=card[0]
        mainunit=card

    #background
        cframeurl=("../frontend/dbManagement/assets/misc/cha_base_0")
    #element
        cframeurl+=(mainunit[12][-1])
        cframeurl+=("_0")
    #rarity
        cframeurl+=(mainunit[5])
        cframeurl+=(".png")


        cframe = Image.open(cframeurl).convert("RGBA")
        cframe=cframe.resize((200,200))

    #character icon
        ciconurl=("../frontend/dbManagement/assets/thumb/")
        ciconurl+=resource_id
        ciconurl+=(".png")
        cicon = Image.open(ciconurl).convert("RGBA")
        cicon.resize((250,250))


    #rarity
        crarityurl=("../frontend/dbManagement/assets/misc/cha_rare_")
        crarityurl+=(getrarity(mainunit))
        crarityurl+=(".png")
        crarity = Image.open(crarityurl).convert("RGBA")
        if getrarity(mainunit)=="ssr":
            crarity=crarity.resize((120,72))
        else:    
            crarity=crarity.resize((160,96))

    #element
        celementurl=("../frontend/dbManagement/assets/misc/cha_type_icon_")
        if len(mainunit[12])==1:
            celementurl+=("0")
        celementurl+=(mainunit[12])
        celementurl+=(".png")
        celement = Image.open(celementurl).convert("RGBA")
        celement=celement.resize((90,90))

        (width,height)=(cicon.width+10,cicon.height+10)
        cfinal=Image.new("RGBA",(width,height))
        cfinal.paste(cframe, (25,35), cframe)
        cfinal.paste(cicon, (0,1), cicon)
        if getrarity(mainunit)=="n":
            cfinal.paste(crarity, (-37,160),crarity)
        elif getrarity(mainunit)=="r":
            cfinal.paste(crarity, (-42,160), crarity)
        elif getrarity(mainunit)=="sr":
            cfinal.paste(crarity, (-25,158), crarity)
        elif getrarity(mainunit)=="ssr":
            cfinal.paste(crarity, (-5,171), crarity)
        elif getrarity(mainunit)=="ur":
            cfinal.paste(crarity, (-25,160), crarity)
        elif getrarity(mainunit)=="lr" or True:
            cfinal.paste(crarity, (-25,155),crarity)
        cfinal.paste(celement, (170,5),celement)
        
        cfinal=cfinal.crop((10,10,256,235))
        
        name=("../frontend/dbManagement/assets/final_assets/")
        name+=(unitid)
        name+=(".png")
        
        cfinal.save(name)

def scrapeallunitassetsv2(cards,thumb=False,full=False,bg=False,character=False,circle=False,cutin=False,effect=False,piece=False,sticker_mask=False,sp_cutin_1=False,sp_name=False,printing=True):
    assetsNeeded=[]
    if thumb: assetsNeeded.append("thumb")
    if full: assetsNeeded.append("full")
    if bg: assetsNeeded.append("bg")
    if character: assetsNeeded.append("character")
    if circle: assetsNeeded.append("circle")
    if cutin: assetsNeeded.append("cutin")
    if effect: assetsNeeded.append("effect")
    if piece: assetsNeeded.append("piece")
    if sticker_mask: assetsNeeded.append("sticker_mask")
    if sp_cutin_1: assetsNeeded.append("sp_cutin_1")
    if sp_name: assetsNeeded.append("sp_name")


    toScrapeList=[]
    amountScraped=0
    for unit in cards:
        if(qualifyUsable(unit)):
            if(unit[48]!=""):
                assetid=unit[48][:-2]
                if(assetid[-1]=="1"):
                    assetid=str(int(assetid)-1)
            else:
                if(unit[0][-1]=="1"):
                    assetid=str(int(unit[0])-1)
                else:
                    assetid=unit[0]


            allAssetsDownloaded=True
            for dataType in assetsNeeded:
                if(allAssetsDownloaded==True):
                    temp=os.path.join("../frontend/dbManagement/assets",dataType)
                    if(dataType=="sp_name"):
                        temp=os.path.join("../frontend/dbManagement/assets",dataType+"_00")
                    temp=os.path.join(temp,assetid+".png")
                    temp2=os.path.exists(temp)
                    if (temp2==False):
                        if(printing): 
                            start_time=time.time()
                        scrapeFullUnit(assetid,thumb,full,bg,character,circle,cutin,effect,piece,sticker_mask,sp_cutin_1,printing)
                        scrapeFullUnit(assetid,thumb,full,bg,character,circle,cutin,effect,piece,sticker_mask,sp_cutin_1,sp_name,printing=True)
                        if(printing):print(unit[0],"took: ",round((time.time()-start_time),3)," seconds")

def scrapeallunitassets(cards,printing=True):
    scrapedunitsreader=open("Scraped units.txt", "r")
    scrapedunitslist=scrapedunitsreader.read()
    scrapedunitslist=scrapedunitslist.split("\n")

    scrapedunitsappender=open("Scraped units.txt", "a")
    toScrapeList=[]
    amountScraped=0
    for unit in cards:
        if (unit[0][-1]=="0") and (unit[0][0]!="5") and (unit[53]!="2030-12-31 23:59:59") and (unit[0][0]!="9") and (unit[0][-1]=="0") and (unit[22]!=""):
            if unit[0] not in scrapedunitslist:
                toScrapeList.append(unit[0])

    if(printing): print("Now going to scrape",len(toScrapeList),"units")
    for unit in cards:
        if (unit[0][-1]=="0") and (unit[0][0]!="5") and (unit[53]!="2030-12-31 23:59:59") and (unit[0][0]!="9") and (unit[0][-1]=="0") and (unit[22]!=""):
            if unit[0] not in scrapedunitslist:
                if(printing): print(amountScraped,"/",len(toScrapeList),"scraping ",unit[0], end=": ")
                start_time=time.time()
                scrapeFullUnit(unit[0])
                scrapedunitsappender.write(unit[0]+"\n")
                scrapedunitslist.append(unit[0])
                amountScraped+=1
                if(printing): print("took: ",round((time.time()-start_time),3)," seconds")

def scrapeassetspecific(filesource, fileDest,printing=True):
    if(printing): print(filesource)
    r = requests.get(filesource, allow_redirects=True, timeout=300)
    if("404" not in str(r._content)):
        open(fileDest, 'wb').write(r.content)
    else:
        if(printing): print(filesource," NOT FOUND ", )

def screpeassetlineant(fileID, fileType,printing=True):
    
    #filetype option:
    #thumb
    #full
    #bg
    #character
    #circle
    #cutin
    #effect
    #piece
    #sticker_mask
    #sp_cutin_1
    fileDest="../frontend/dbManagement/assets/"+fileType+"/"+fileID+".png"
    
    if(os.path.isfile(fileDest)==False):
        if fileType=="thumb":filesource="https://glben.dokkaninfo.com/assets/global/en/character/thumb/card_"+fileID+"_thumb.png"
        elif fileType=="full": filesource="https://glben.dokkaninfo.com/assets/global/en/character/card/"+fileID+"/"+fileID+".png"
        elif fileType=="bg": filesource= "https://glben.dokkaninfo.com/assets/global/en/character/card/"+fileID+"/card_"+fileID+"_bg.png"
        elif fileType=="character": filesource= "https://glben.dokkaninfo.com/assets/global/en/character/card/"+fileID+"/card_"+fileID+"_character.png"
        elif fileType=="circle": filesource= "https://glben.dokkaninfo.com/assets/global/en/character/card/"+fileID+"/card_"+fileID+"_circle.png"
        elif fileType=="cutin": filesource= "https://glben.dokkaninfo.com/assets/global/en/character/card/"+fileID+"/card_"+fileID+"_cutin.png"
        elif fileType=="effect": filesource="https://glben.dokkaninfo.com/assets/global/en/character/card/"+fileID+"/card_"+fileID+"_effect.png"
        elif fileType=="piece": filesource="https://glben.dokkaninfo.com/assets/global/en/character/card/"+fileID+"/card_"+fileID+"_piece.png"
        elif fileType=="sticker_mask": filesource="https://glben.dokkaninfo.com/assets/global/en/character/card/"+fileID+"/card_"+fileID+"_sticker_mask.png"
        elif fileType=="sp_cutin_1": filesource="https://glben.dokkaninfo.com/assets/global/en/character/card/"+fileID+"/card_"+fileID+"sp_cutin_1.png"
        
        
        
        elif fileType=="sp_name": 
            nextSAFound=True
            SAcount=0
            while (nextSAFound):
                if(SAcount==1):
                    SAcount=2
                if(SAcount==0):
                    filesource="https://glben.dokkaninfo.com/assets/global/en/character/card/"+fileID+"/en/card_"+fileID+"_sp_name.png"
                else:
                    filesource="https://glben.dokkaninfo.com/assets/global/en/character/card/"+fileID+"/en/card_"+fileID+"_sp0"+str(SAcount)+"_name.png"
                fileDest="../frontend/dbManagement/assets/"+fileType+"_0"+str(SAcount)+"/"+fileID+".png"
                SAcount+=1
                r = requests.get(filesource, allow_redirects=True, timeout=120)
                if("404 Not Found" not in str(r._content)):
                    open(fileDest, 'wb').write(r.content)
                    nextSAFound=True
                else:
                    filesource=filesource.replace("global/en","japan")
                    filesource=filesource.replace("/en","/ja")
                    filesource=filesource.replace("glben","jpnen")
                    r = requests.get(filesource, allow_redirects=True, timeout=120)
                    if("404 Not Found" not in str(r._content)):
                        open(fileDest, 'wb').write(r.content)
                        nextSAFound=True
                    else:
                        nextSAFound=False

                
        
        
        else: 
            if(printing): print(fileType, "fileType invalid")
        
        if(fileType!="sp_name"):
            r = requests.get(filesource, allow_redirects=True, timeout=120)
            if("404 Not Found" not in str(r._content)):
                open(fileDest, 'wb').write(r.content)
            else:
                filesource=filesource.replace("global","japan")
                filesource=filesource.replace("/en","")
                r = requests.get(filesource, allow_redirects=True, timeout=120)
                if("404 Not Found" not in str(r._content)):
                    open(fileDest, 'wb').write(r.content)
                elif(fileType!="sticker_mask"):
                    if(printing): print(filesource," NOT FOUND ", )

def scrapeFullUnit(fileID,thumb=True,full=True,bg=True,character=True,circle=True,cutin=True,effect=True,piece=True,sticker_mask=True,sp_cutin_1=True,sp_name=True,printing=True):
    assetsNeeded=[]
    if thumb: assetsNeeded.append("thumb")
    if full: assetsNeeded.append("full")
    if bg: assetsNeeded.append("bg")
    if character: assetsNeeded.append("character")
    if circle: assetsNeeded.append("circle")
    if cutin: assetsNeeded.append("cutin")
    if effect: assetsNeeded.append("effect")
    if piece: assetsNeeded.append("piece")
    if sticker_mask: assetsNeeded.append("sticker_mask")
    if sp_cutin_1: assetsNeeded.append("sp_cutin_1")
    if sp_name: assetsNeeded.append("sp_name")

    for fileType in assetsNeeded:
        screpeassetlineant(fileID, fileType,printing)
    
def passivename(unit,printing=True):
    return(listtostr(searchbyid(str(int(float(unit[21]))), 0, passive_skillsJP, 1)))

def floattoint(number,printing=True):
    if(type(number)==str):
        number=float(number)
    if number%1==0:
        return(int(number))
    else:
        return(number)

def checkeza(unit,printing=True):
    for eza in optimal_awakening_growthsJP[1:]:
        if str(int(float(unit[22]))) in str(int(float(eza[6]))):
            return(True)
    return(False)
    
def returnRow(ID, IDRow, database, printing=True):
    output=[]
    for row in database:
        if ID==row[IDRow]:
            output.append(row)
    return(output)

#this function takes in a piece of data
#checks within the destincation_csv along the column
#once it finds one that matches it will return that row's entry on the destination_column
#def searchbycolumn(code, database, column, printing=True):
#    temp=[]
#    for row in database:
#        if (code==row[column]):
#            temp.append(row)
#    return(temp)
                
def searchbycolumn(code, database, column, printing=True):
    return [row for row in database if code == row[column]]

    
#def searchbyid(code, codecolumn, database, column,printing=True):
#    temp=[]
#    for row in database:
#        if code==row[codecolumn]:
#            temp.append(row[column])
#    if temp==[]:
#        return(None)
#    else:
#        return(temp)

def searchbyid(code, codecolumn, database, column, printing=True):
    result = [row[column] for row in database if code == row[codecolumn]]
    return result if result else None

def searchbyidsorted(code, codecolumn, database, column, printing=True):
    pivot=len(database)//2
    if code==database[pivot][codecolumn]:
        return(database[pivot][column])
    elif code>database[pivot][codecolumn]:
        return(searchbyidsorted(code, codecolumn, database[pivot:], column, printing))
    else:
        return(searchbyidsorted(code, codecolumn, database[:pivot], column, printing))

def combinelinks(linklist,lvl,printing=True):
    ATK=0
    DEF=0
    KI=0
    ENEMYDEF=0
    EVASION=0
    CRIT=0
    HEAL=0
    DREDUCTION=0
    #create variable for links that activate under certain hp. NO

    for link in linklist:
        if link!="":
            linkid=searchedbyid(link, 1, link_skillsJP, 0)[0]
            linkcode=searchedbyid(linkid, 1, link_skill_lvsJP, 0)[lvl-1]
            for linkdetails in link_skill_efficaciesJP:
            
                if linkcode==linkdetails[1]:

                    #retrieve all nessessary data from link
                    if linkdetails[3]=="1":
                        ATK+=float(linkdetails[11])
                    if linkdetails[3]=="2":
                        if linkdetails[4]=="1":
                            DEF+=float(linkdetails[11])
                        elif linkdetails[4]=="4":
                            ENEMYDEF+=float(linkdetails[11])
                    if linkdetails[3]=="3":
                        ATK+=float(linkdetails[11])
                        DEF+=float(linkdetails[12])
                    if linkdetails[3]=="4":
                        HEAL+=float(linkdetails[11])
                    if linkdetails[3]=="5":
                        KI+=float(linkdetails[11])
                    if linkdetails[3]=="13":
                        DREDUCTION+=(100-float(linkdetails[11]))
                    if linkdetails[3]=="90":
                        CRIT+=float(linkdetails[11])
                    if linkdetails[3]=="91":
                        EVASION+=float(linkdetails[11])
    return(ATK,DEF,KI,ENEMYDEF,EVASION,CRIT,HEAL,DREDUCTION)

def presentcharacter(unit,printing=True):
    if unit[3]=="STR":
        if(printing): print(Fore.RED,end="")
    elif unit[3]=="PHY":
        if(printing): print(Fore.YELLOW,end="")
    elif unit[3]=="INT":
        if(printing): print(Fore.MAGENTA,end="")
    elif unit[3]=="TEQ":
        if(printing): print(Fore.GREEN,end="")
    elif unit[3]=="AGL":
        if(printing): print(Fore.BLUE,end="")
    tempreturn=""
    
    #rarity
    tempreturn+=unit[4]
    tempreturn+=" "
    
    #element
    tempreturn+=unit[3]
    tempreturn+=" "
    
    #name
    tempreturn+=unit[2]
    tempreturn+=" "
    
    return(tempreturn)

def search(OGwordlist,searched,printing=True):
    wordlist=OGwordlist.copy()
    if searched.isdigit():
        if 1+len(wordlist)>int(searched):
            if(printing): print("Are you selecting entry no. ",searched," ", wordlist[int(searched)-1]," y/n: ",sep="")
            if input().upper()=="Y":
                if(printing): print(wordlist[int(searched)-1])
                return(wordlist[int(searched)-1])
            

    for x in reversed(wordlist):
        if searched.upper() not in x.upper():
            wordlist.remove(x)
    if len(wordlist)==0:
        if(printing): print("NO ENTRIES CONTAIN THAT")
        return(search(OGwordlist,input("Which one do you want to use?: ")))
    if len(wordlist)==1:
        if(printing): print(wordlist[0])
        return(wordlist[0])
    for y in wordlist:
        if(printing): print(1+wordlist.index(y),y)
    return(search(wordlist,input("Which one do you want to use?: ")))
        
#ultralist is a list consisting of other lists
#slot is the list value that is used across all lists to sort the individual lists
def sortultralist(ultralist,slot,reverse=False,printing=True):
    tempultralist=((sorted(ultralist, key=lambda x:x[slot])))
    if reverse:
        tempultralist.reverse()
    return(tempultralist)
    
#sorts through a list consisting of words and returns the sorted list
def wordsort(mylist,printing=True):
    mylist.sort()
    return(mylist)
    
#used to quickly store all data of a database
def storedatabase(directory,name,printing=True):
    directory+=name
    file = open(directory, encoding="utf-8-sig")
    dbtemp=csv.reader(file)
    name=[]
    for row in dbtemp:
        name.append(row)
    return(name)
    
def listtostr(mylist,printing=True):
    temp=""
    if mylist!=None:
        for x in mylist:
            temp+=str(x)
    return(temp)
#used initially to searched for and return a list of a specific character
def charactersearched(searcheded,database,printing=True):
    searchedoptions=[]
    for unit in database:
        if searcheded.lower() in unit[1].lower():
            searchedoptions.append(unit)
    return(searchedoptions)

#used to remove any unused entries in the database list
def removedupes(unit,searchedoptions,printing=True):
    #checks if unit id ends in 0
    if unit[0][-1]=="0":
        searchedoptions.remove(unit)
        return(True,searchedoptions)
    else:
        for x in searchedoptions:
            #check if passive_skill_set_id is already included or is empty
            if unit[21]=="":
                if unit!=x:
                    searchedoptions.remove(unit)
                    return(True,searchedoptions)
    return(False,searchedoptions)

#used to select which of the given options will be used in calculations
def choosechoice(choice,searchedoptions,printing=True):
    return(searchedoptions[choice-1])
    
#used to cross reference id's within diferent databases, unit column variable is used to see where the desired value is
def searchedbyid(code, codecolumn, database, column,printing=True):
    temp=[]
    for x in database:
        if code==x[codecolumn]:
            temp.append(x[column])
    if temp==[]:
        return(None)
    else:
        return(temp)
        
#used to find if a unit is SUPER/EXTREME class(includes code for if they are neither, but isn't very usable)
def superextremefinder(element,printing=True):
    if int(element)>19:
        return("E.")
    elif int(element)>9:
        return("S.")
    else:
        return(" ")

#Used to find the typing of the character (AGL/TEQ/INT/STR/PHY)
def typefinder(element,printing=True):
    if element[-1]=="0":
        return("AGL")
    if element[-1]=="1":
        return("TEQ")
    if element[-1]=="2":
        return("INT")
    if element[-1]=="3":
        return("STR")
    if element[-1]=="4":
        return("PHY")
    else:
        return("NO TYPING!!!!!!!!!!!!!")

def getrarity(unit,printing=True):
    
    if(type(unit)==list):
        if unit[5]=="5":
            return("lr")
        elif unit[5]=="4":
            return("ur")
        elif unit[5]=="3":
            return("ssr")
        elif unit[5]=="2":
            return("sr")
        elif unit[5]=="1":
            return("r")
        elif unit[5]=="0":
            return("n")

    elif(type(unit)==str):
        unitDetails=searchbycolumn(code=unit,column=0,database=cardsJP)[0]
        return(getrarity(unitDetails))

        
    
    return("ERROR IN GETRARITY UNIT MAX LEVEL IS",unit[13])

def getUnitStats(unit,level,DEVEXCEPTIONS=False):
    hp_init=int(unit[6])
    hp_max=int(unit[7])
    atk_init=int(unit[8])
    atk_max=int(unit[9])
    def_init=int(unit[10])
    def_max=int(unit[11])
    level_max=int(unit[13])
    growthInfo=searchbycolumn(code=unit[15],column=1,database=card_growthsJP)
    temp=searchbyid(code=str(level),codecolumn=2,database=growthInfo,column=3)
    if(temp!=None):
        coef=float(searchbyid(code=str(level),codecolumn=2,database=growthInfo,column=3)[0])
        stats={}
        stats["HP"]=math.floor((0.5 * (level - 1) * (hp_max - hp_init)) / (level_max - 1) + 0.5 * coef * (hp_max - hp_init) + hp_init)
        stats["ATK"]=math.floor((0.5 * (level - 1) * (atk_max - atk_init)) / (level_max - 1) + 0.5 * coef * (atk_max - atk_init) + atk_init)
        stats["DEF"]=math.floor((0.5 * (level - 1) * (def_max - def_init)) / (level_max - 1) + 0.5 * coef * (def_max - def_init) + def_init)
        return(stats)
    else:
        return(None)
    

def swapToUnitWith0(unit):
    unitId=definewith0(unit[0])
    for card in cardsJP:
        if card[0]==unitId:
            return(card)
    return(None)

def swapToUnitWith1(unit):
    unitId=definewith1(unit[0])
    for card in cardsJP:
        if card[0]==unitId:
            return(card)
    return(None)

def getpassiveid(unit,eza=False,seza=False, printing=False,DEVEXCEPTIONS=False):
    unitPassiveId=unit[21]
    if(eza):
        if(swapToUnitWith1(unit)!=None):
            unitEZA=swapToUnitWith1(unit)
        else:
            return(getpassiveid(unit,eza=False, printing=printing))
        unitEZAGrowthId=unitEZA[16][0:-2]
        if(unitEZAGrowthId==""):
            return(getpassiveid(unit,eza=False, printing=printing))
        if(seza):
            relevantAwakenings=searchbycolumn(code=unitEZAGrowthId,database=optimal_awakening_growthsJP,column=1)
            #if the unit is an ur
            if(unit[5]=="4"):
                relevantAwakenings=searchbycolumn(code="8",database=relevantAwakenings,column=2)
            #if the unit is an lr
            elif(unit[5]=="5"):
                relevantAwakenings=searchbycolumn(code="4",database=relevantAwakenings,column=2)
            else:
                if(DEVEXCEPTIONS):
                    raise Exception("Unit is not an LR or UR but has a supereza")
        elif(eza):
            relevantAwakenings=searchbycolumn(code=unitEZAGrowthId,database=optimal_awakening_growthsJP,column=1)
            #if the unit is an ur
            if(unit[5]=="4"):
                relevantAwakenings=searchbycolumn(code="7",database=relevantAwakenings,column=2)
            #if the unit is an lr
            elif(unit[5]=="5"):
                relevantAwakenings=searchbycolumn(code="3",database=relevantAwakenings,column=2)
            else:
                if(DEVEXCEPTIONS):
                    raise Exception("Unit is not an LR or UR but has a supereza")
        unitEZAPassiveId=relevantAwakenings[0][5][:-2]
        
        unitEZAPassiveList=searchbyid(code=unitEZAPassiveId,codecolumn=1,database=passive_skill_set_relationsJP,column=2)
        return(unitEZAPassiveList)
    else:
        unitPassiveId=unitPassiveId[0:-2]
        unitPassiveList=searchbyid(code=unitPassiveId,codecolumn=1,database=passive_skill_set_relationsJP,column=2)
        return(unitPassiveList)

#retrieves full character name(e.g. "E.TEQ LR Nightmarish Impact Legendary Super Saiyan Broly 4016881")
def getfullname(unit,printing=True):
    #create empty variable
    temp=""
    
    temp+=(getrarity(unit))
        
    temp+=" "
    
    #add if unit is super or extreme
    temp+=(superextremefinder(unit[12]))
    temp+=""
    
    #add unit typing
    temp+=(typefinder(unit[12]))
    temp+=" "
    
    #get unit name
    temp+=(unit[1])
    temp+=" "
    
    #get unit leader skill name
    temp+=(listtostr(searchedbyid(unit[22],0,leader_skillsJP,1)))
    temp+=" "
    
    #get unit id
    temp+=(unit[0])
    temp+=" "
    
    #return variable
    return(temp)
    
def getallcategories(unitid,printing=True):
    temp1=searchedbyid(unitid, 1, card_card_categoriesJP, 2)
    categoryList=[]
    if temp1!=None:
        for x in temp1:
            globalListedCategory=searchedbyid(x,0,card_categoriesGB,1)
            if(globalListedCategory!=None):
                categoryList.append(globalListedCategory[0])
            else:
                categoryList.append(searchedbyid(x,0,card_categoriesJP,1)[0])
    return(categoryList)

def getalllinkswithbuffs(unit,printing=True,DEVEXCEPTIONS=True):
    links=getalllinks(unit)
    output={}
    for link in links:
        output[link]=getlinkBuffsAtAllLevel(linkNameOrID=link,printing=printing,DEVEXCEPTIONS=DEVEXCEPTIONS)
    return(output)

def getlinkBuffsAtAllLevel(linkNameOrID="",printing=True,DEVEXCEPTIONS=True):
    output={}
    if linkNameOrID.isdigit():
        linkID=linkNameOrID
    else:
        linkID=searchbyid(code=linkNameOrID,codecolumn=1,database=link_skillsGB,column=0)
    linkID=linkID[0]
    linkLevelIDs=searchbycolumn(code=linkID,column=1,database=link_skill_lvsJP)
    for levelIDRow in linkLevelIDs:
        levelID=levelIDRow[0]
        efficiacy_rows=searchbycolumn(code=levelID,database=link_skill_efficaciesJP,column=1)
        buffs={"ATK":0,
               "DEF":0,
               "ENEMYDEF":0,
               "HEAL":0,
               "KI":0,
               "DREDUCTION":0,
               "CRIT":0,
               "EVASION":0}
        for row in efficiacy_rows:
            if row[3]=="1":
                buffs["ATK"]+=float(row[11])
            elif row[3]=="2":
                if row[4]=="1":
                    buffs["DEF"]+=float(row[11])
                elif row[4]=="4":
                    buffs["ENEMYDEF"]+=float(row[11])
            elif row[3]=="3":
                buffs["ATK"]+=float(row[11])
                buffs["DEF"]+=float(row[12])
            elif row[3]=="4":
                buffs["HEAL"]+=float(row[11])
            elif row[3]=="5":
                buffs["KI"]+=float(row[11])
            elif row[3]=="13":
                buffs["DREDUCTION"]=+100-float(row[11])
            elif row[3]=="90":
                buffs["CRIT"]+=float(row[11])
            elif row[3]=="91":
                buffs["EVASION"]+=float(row[11])
        output[levelIDRow[2]]=buffs
    return(output)



def getalllinks(unit,printing=True):
    linksList=[]
    for x in range(23,30):
       if(unit[x]!=""):
        code=unit[x][:-2]
        temp1=searchbyid(code,0,link_skillsGB,1)
        linksList.append(temp1[0])

    return(linksList)
    
def ordinalise(number,printing=True):
    if(type(number)==str):
        number=int(number)
    if number==1:
        return("1st")
    elif number==2:
        return("2nd")
    elif number==3:
        return("3rd")
    else:
        return(str(number)+"th")

def ezastat(minlvl,maxlvl,printing=True):
    minlvl=int(minlvl)
    maxlvl=int(maxlvl)
    return(round(((maxlvl-minlvl)*0.4839)+maxlvl))

