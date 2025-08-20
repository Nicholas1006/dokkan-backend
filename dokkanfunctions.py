
from globals import *
import csv
import os
#from PIL import Image
import math
import json
import shutil
from datetime import datetime
import time
from itertools import combinations


def getUnitCost(unit):
    return(unit[4])

def dateTimeToTimestamp(date):
    return(int(datetime.strptime(date, "%Y-%m-%d %H:%M:%S").timestamp()))

def getUnitReleaseTime(card):
    return(dateTimeToTimestamp(card[53]))

def getEzaReleaseTime(unit,DEVEXCEPTIONS=True):
    awakening_options=searchbycolumn(unit[0],card_awakening_routes,2)
    if(awakening_options!=[]):
        for awakening_option in awakening_options:
            if(awakening_option[7]=="1"):
                return(dateTimeToTimestamp(awakening_option[10]))
    else:
        unitID=None
        #unit is transformed
        passiveTransformationLine=searchbyid(code=unit[0],codecolumn=12,database=passive_skills,column=0)
        if(passiveTransformationLine!=None):
            for line in passiveTransformationLine:
                passiveSkillSet=searchbyid(code=line,codecolumn=2,database=passive_skill_set_relations,column=1)[0]+".0"
                if(searchbyid(code=passiveSkillSet,codecolumn=21,database=cards,column=0)!=None):
                    unitID=searchbyid(code=passiveSkillSet,codecolumn=21,database=cards,column=0)[0]
        activeTransformationLine=searchbyid(code=unit[0],codecolumn=6,database=active_skills,column=0)
        if(activeTransformationLine!=None):
            for line in activeTransformationLine:
                activeSkillSet=searchbyid(code=line, codecolumn=0,database=active_skills,column=1)
                unitID=searchbyid(code=activeSkillSet[0],codecolumn=2,database=card_active_skills,column=1)[0]
        for costumeChange in card_costumes:
            if unit[0][:-1]==costumeChange[1][:-1]:
                costume_id=costumeChange[0]
                unitID=searchbyid(code=costume_id,codecolumn=0,database=card_costume_conditions,column=2)[0]
        for standbySkill in standby_skills:
            if(standbySkill[8][1:-1].split(",")[0][:-1]==unit[0][:-1]):
                unitID=searchbyid(code=standbySkill[1],codecolumn=2,database=card_standby_skill_set_relations,column=1)[0]
        for finishSkill in finish_skills:
            if(finishSkill[8][1:-1].split(",")[0][:-1]==unit[0][:-1]):
                unitID=searchbyid(code=finishSkill[1],codecolumn=2,database=card_finish_skill_set_relations,column=1)[0]
        if(unitID==None):
            if(unit[0][-1]=="1"):
                print(unit,"NO EZA RELEASE TIME")

                if(DEVEXCEPTIONS):
                    raise Exception("UNKNOWN EZA RELEASE TIME")
                else:
                    return(getUnitReleaseTime(unit))
            else:
                return(getEzaReleaseTime(swapToUnitWith1(unit)))
        else:
            unitBase=searchbycolumn(code=unitID,column=0,database=cards)[0]
            return(getEzaReleaseTime(unitBase))
        
def getSezaReleaseTime(unit,DEVEXCEPTIONS=True):
    awakening_options=searchbycolumn(unit[0],card_awakening_routes,2)
    if(awakening_options!=[]):
        for awakening_option in awakening_options:
            if(awakening_option[7]=="2"):
                return(dateTimeToTimestamp(awakening_option[10]))
    else:
        unitID=None
        #unit is transformed
        passiveTransformationLine=searchbyid(code=unit[0],codecolumn=12,database=passive_skills,column=0)
        if(passiveTransformationLine!=None):
            for line in passiveTransformationLine:
                passiveSkillSet=searchbyid(code=line,codecolumn=2,database=passive_skill_set_relations,column=1)[0]+".0"
                if(searchbyid(code=passiveSkillSet,codecolumn=21,database=cards,column=0)!=None):
                    unitID=searchbyid(code=passiveSkillSet,codecolumn=21,database=cards,column=0)[0]
        activeTransformationLine=searchbyid(code=unit[0],codecolumn=5,database=active_skills,column=0)
        if(activeTransformationLine!=None):
            for line in activeTransformationLine:
                activeSkillSet=searchbyid(code=line, codecolumn=0,database=active_skills,column=1)
                unitID=searchbyid(code=activeSkillSet[0],codecolumn=2,database=card_active_skills,column=1)[0]
        for standbySkill in standby_skills:
            if(standbySkill[8][1:-1].split(",")[0][:-1]==unit[0][:-1]):
                unitID=searchbyid(code=standbySkill[1],codecolumn=2,database=card_standby_skill_set_relations,column=1)[0]
        for finishSkill in finish_skills:
            if(finishSkill[8][1:-1].split(",")[0][:-1]==unit[0][:-1]):
                unitID=searchbyid(code=finishSkill[1],codecolumn=2,database=card_finish_skill_set_relations,column=1)[0]
        if(unitID==None):
            if(unit[0][-1]=="1"):
                print(unit,"NO SEZA TIME FOR THIS UNIT")
                if(DEVEXCEPTIONS):
                    raise Exception("No SEZA TIME for this unit")
                else:
                    return(getUnitReleaseTime(unit))
            else:
                return(getSezaReleaseTime(swapToUnitWith1(unit)))
        else:
            unitBase=searchbycolumn(code=unitID,column=0,database=cards)[0]
            return(getSezaReleaseTime(unitBase))


def getCharacterNameID(unit):
    return(unit[3])

def sub_target_types_extractor(sub_target_type_set_id,DEVELOPEREXCEPTIONS=False):
    temp=searchbycolumn(code=sub_target_type_set_id,database=sub_target_types,column=1)
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
    specialRow=searchbycolumn(code=superAttackID,database=special_sets,column=0)
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
        growthRows=searchbycolumn(code=cardOptimalAwakeningGrowthID,database=optimal_awakening_growths,column=1)
        maxLevel=int(unit[14])
        for growthRow in growthRows:
            maxLevel=max(maxLevel,int(growthRow[3]))
        return(maxLevel)
    else:
        return(int(unit[13]))

def parse_domain_efficiacy(efficiacy,DEVEXCEPTIONS=False):
    output={}
    output["ID"]=efficiacy[0]
    if(efficiacy[2]=="1"):
        output["Timing"]="At the start of turn"
    elif(efficiacy[2]=="18"):
        output["Timing"]="On domain Being out"
    else:
        print("UNKNOWN DOMAIN EFFICIACY TIMING:",efficiacy[2])
        if(DEVEXCEPTIONS==True):
            raise Exception("UNKNOWN DOMAIN EFFICIENCY TIMING")

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
        if(DEVEXCEPTIONS==True):
            raise Exception("UNKNOWN DOMAIN EFFICIENCY TYPE")

    if(efficiacy[4]=="0"):
        pass
    elif(efficiacy[4]=="2"):
        pass
    else:
        print("UNKNOWN DOMAIN EFFICIACY TARGET:",efficiacy[4])
        if(DEVEXCEPTIONS==True):
            raise Exception("UNKNOWN DOMAIN EFFICIENCY TARGET")

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
        causalityCondition=CausalityLogicalExtractor(unit=[],causality=causalityCondition,DEVEXCEPTIONS=DEVEXCEPTIONS)
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
    card_specialss=searchbycolumn(code=unit[0],column=1,database=card_specials)
    card_specialss=removeDuplicatesUltraList(ultraList=card_specialss,slot=0)
    for card_special in card_specialss:
        if((eza and int(unit[14])<int(card_special[5])) or (eza==False and int(unit[14])>=int(card_special[5]))):
            output.append(getSuperAttackType(card_special))
    return output

def getSuperAttackType(card_special):
    view_id=card_special[7]
    special_category_id=searchbyid(code=view_id,codecolumn=0,database=special_views,column=7)[0]
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

    card_specialss=searchbycolumn(code=unit[0],column=1,database=card_specials)
    card_specialss=removeDuplicatesUltraList(ultraList=card_specialss,slot=0)
    for card_special in card_specialss:
        if((eza and int(unit[14])<int(card_special[5])) or (eza==False and int(unit[14])>=int(card_special[5]))):
            superAttackDictionary={}
            superSet=searchbycolumn(code=card_special[2],column=0,database=special_sets)
            superAttackDictionary["superID"]=superSet[0][0]
            view_id=card_special[7]
            special_category_id=searchbyid(code=view_id,codecolumn=0,database=special_views,column=7)[0]
            if(special_category_id==""):
                superAttackDictionary["Type"]="Other"
            elif(special_category_id=="1.0"):
                superAttackDictionary["Type"]="Ki blast"
            elif(special_category_id=="2.0"):
                superAttackDictionary["Type"]="Unarmed"
            elif(special_category_id=="3.0"):
                superAttackDictionary["Type"]="Physical"


            superAttackDictionary["special_name_no"]=searchbyid(code=view_id,codecolumn=0,database=special_views,column=3)[0]
            if(superSet==[]):
                superAttackDictionary["superName"]=superSet[0][1]
                superAttackDictionary["superDescription"]=superSet[0][2]
            else:
                superAttackDictionary["superName"]=superSet[0][1]
                superAttackDictionary["superDescription"]=superSet[0][2]

            
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
                growthRows=searchbycolumn(code=cardOptimalAwakeningGrowthID,database=optimal_awakening_growths,column=1)
                for growthRow in growthRows:
                    SALevel = max(int(growthRow[4]), SALevel)
            superAttackDictionary["Multiplier"]=superAttackMultiplierExtractor(superAttackID=superAttackDictionary["superID"],super_attack_lvl=SALevel,DEVEXCEPTIONS=DEVEXCEPTIONS)
            card_supers=searchbycolumn(code=superAttackDictionary["superID"],column=1,database=specials)
            for special in card_supers:
                specialsEffect=parseSpecials(special,DEVEXCEPTIONS)    
                superAttackDictionary["superBuffs"][special[0]]=specialsEffect
            output[card_special[2]]=superAttackDictionary

            if(superAttackDictionary["SpecialBonus"]["ID"]!="0"):
                superAttackDictionary["Multiplier"]=superAttackMultiplierExtractor(superAttackID=superAttackDictionary["superID"],super_attack_lvl=SALevel,DEVEXCEPTIONS=DEVEXCEPTIONS)
                special_bonus=searchbycolumn(code=superAttackDictionary["SpecialBonus"]["ID"],column=0,database=special_bonuses)
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
            
            superAttackDictionary["relevantLua"]=searchbyid(code=view_id,codecolumn=0,database=special_views,column=1)
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
        output["Target"]="allies"
    elif(specialRow[4]=="3"):
        output["Target"]="Enemy"
    elif(specialRow[4]=="4"):
        output["Target"]="All Enemies"
    elif(specialRow[4]=="12"):
        output["Target"]="Super class allies"
    elif(specialRow[4]=="13"):
        output["Target"]="Extreme class allies"
    elif(specialRow[4]=="16"):
        output["Target"]="allies (self excluded)"
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
        output["Status"]="Effective Against All"
    elif(specialRow[3]=="84"):
        output["Heals"]=specialRow[9]
    elif(specialRow[3]=="90"):
        output["Crit Chance"]=specialRow[9]
    elif(specialRow[3]=="91"):
        output["Dodge Chance"]=specialRow[9]
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
    allNodes=searchbycolumn(code=Potential_board_id,column=1,database=potential_squares)
    allNodeIDs=[node[0] for node in allNodes]
    relevantRelations=[]
    for connection in potential_square_relations:
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
                            path=searchbyid(code=connection[:-2],codecolumn=0,database=potential_squares,column=5)
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
        eventid=searchbyid(code=node,codecolumn=0,database=potential_squares,column=2)[0]
        event=searchbycolumn(code=eventid,database=potential_events,column=0)[0]
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
    leader_skill_name=searchbyid(code=unit[22][:-2],codecolumn=0,database=leader_skill_sets,column=1,)
    output["Name"]=leader_skill_name[0]
    leader_skill_set_id=unit[22][:-2]
    if(eza):
        optimal_awakening_rows=searchbycolumn(code=unit[16][:-2],column=1,database=optimal_awakening_growths)
        for optimal_awakening_row in optimal_awakening_rows:
            if(optimal_awakening_row[6]!=unit[22][:-2]):
                leader_skill_set_id=optimal_awakening_row[6]
    leader_skill_lines=searchbycolumn(code=leader_skill_set_id,database=leader_skills,column=1,printing=False)
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
        
        efficiacy_values=leader_skill_line[7].replace("[","").replace("]","").split(",")
        output[leader_skill_line[0]]["Target"]=(sub_target_types_extractor(leader_skill_line[4],DEVEXCEPTIONS))

        output[leader_skill_line[0]]["Target"]["Class"]=[]
        output[leader_skill_line[0]]["Target"]["Type"]=[]
        output[leader_skill_line[0]]["ATK"]=0
        output[leader_skill_line[0]]["DEF"]=0
        output[leader_skill_line[0]]["HP"]=0
        output[leader_skill_line[0]]["Ki"]=0

        if(leader_skill_line[3]=="4"):
            output[leader_skill_line[0]]["Target"]["allies or enemies"]="Enemies"
        elif(leader_skill_line[3]=="2"):
            output[leader_skill_line[0]]["Target"]["allies or enemies"]="allies"
        if leader_skill_line[6]=="0":
            output[leader_skill_line[0]]["NOT WORKING"]=True
        elif(leader_skill_line[6]=="1"):
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[0])
        elif(leader_skill_line[6]=="2"):
            #Enemy ["DEF", ??, ??] 
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[0])
        elif(leader_skill_line[6]=="3"):
            #Category ["HP and ATK", "DEF", ""] 
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
            output[leader_skill_line[0]]["Target"]["Type"]=[typefinder(efficiacy_values[0],printing=True)]
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="17"):
            #Single type [Typing, "DEF", ""] 
            output[leader_skill_line[0]]["Target"]["Type"]=[typefinder(efficiacy_values[0],printing=True)]
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="18"):
            #Single type [Typing, "ATK and DEF", ""] 
            output[leader_skill_line[0]]["Target"]["Type"]=[typefinder(efficiacy_values[0],printing=True)]
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[2])
        elif(leader_skill_line[6]=="19"):
            #Single type [Type, "HP", ""] 
            output[leader_skill_line[0]]["Target"]["Type"]=[typefinder(efficiacy_values[0],printing=True)]
            output[leader_skill_line[0]]["HP"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="20"):
            #Single Type (Type, "Ki", "") 
            output[leader_skill_line[0]]["Target"]["Type"]=[typefinder(efficiacy_values[0],printing=True)]
            output[leader_skill_line[0]]["Ki"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="44"):
            #Single Type (Type, HP, ATK) 
            output[leader_skill_line[0]]["Target"]["Type"]=[typefinder(efficiacy_values[0],printing=True)]
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
            output[leader_skill_line[0]]["Building Stat"]= {"Cause":"Ki sphere obtained", "Type":["AGL","INT","PHY","STR","TEQ","Rainbow","Sweet treats"]}
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[0])
        elif(leader_skill_line[6]=="61"):
            #ATK and DEF per ki sphere obtained
            output[leader_skill_line[0]]["Building Stat"]= {"Cause":"Ki sphere obtained", "Type":["AGL","INT","PHY","STR","TEQ","Rainbow","Sweet treats"]}
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[0])
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="64"):
            #ATK per ki sphere obtained of a type
            output[leader_skill_line[0]]["Building Stat"]= {"Cause":"Ki sphere obtained", "Type":[KiOrbType(efficiacy_values[0],DEVEXCEPTIONS=DEVEXCEPTIONS)]}
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["Target"]["Type"]=[typefinder(efficiacy_values[0],printing=True)]
        elif(leader_skill_line[6]=="71"):
            #HP based ["Min ATK", "MAX ATK", ???] 
            output[leader_skill_line[0]]["Building Stat"]={"Cause":"HP", "Type":"More HP remaining"}
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["Building Stat"]["Min"]=int(efficiacy_values[0])
            output[leader_skill_line[0]]["Building Stat"]["Max"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="82"):
            #Typing [Typing, "HP and ATK and DEF", ""] 
            output[leader_skill_line[0]]["Target"]["Class"]=extractClassType(efficiacy_values[0],DEVEXCEPTIONS=DEVEXCEPTIONS)[0]
            output[leader_skill_line[0]]["Target"]["Type"]=extractClassType(efficiacy_values[0],DEVEXCEPTIONS=DEVEXCEPTIONS)[1]
            output[leader_skill_line[0]]["HP"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="83"):
            #Typing ki
            output[leader_skill_line[0]]["Target"]["Class"]=extractClassType(efficiacy_values[0],DEVEXCEPTIONS=DEVEXCEPTIONS)[0]
            output[leader_skill_line[0]]["Target"]["Type"]=extractClassType(efficiacy_values[0],DEVEXCEPTIONS=DEVEXCEPTIONS)[1]
            output[leader_skill_line[0]]["Ki"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="84"):
            #Typing HP ATK and DEF
            output[leader_skill_line[0]]["HP"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["ATK"]=int(efficiacy_values[1])
            output[leader_skill_line[0]]["DEF"]=int(efficiacy_values[1])
        elif(leader_skill_line[6]=="93"):
            #All types or specific type HP
            output[leader_skill_line[0]]["Target"]["Class"]=extractClassType(efficiacy_values[0],DEVEXCEPTIONS=DEVEXCEPTIONS)[0]
            output[leader_skill_line[0]]["Target"]["Type"]=extractClassType(efficiacy_values[0],DEVEXCEPTIONS=DEVEXCEPTIONS)[1]
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
        if("Type" in output[leader_skill_line[0]]["Target"]):
            if(output[leader_skill_line[0]]["Target"]["Type"]==["PHY","STR","INT","TEQ","AGL"]):
                output[leader_skill_line[0]]["Target"]["Type"]=[]

    temp=output.copy()
    for line in temp:
        if("NOT WORKING" in output[line]):
            output.pop(line)
    return(output)

def getLeadViability(unit,eza,DEVEXCEPTIONS=False):
    maxBuff=0
    lead=parseLeaderSkill(unit,eza)
    for leadLine in lead:
        if(leadLine!="Name"):
            maxBuff=max(maxBuff,lead[leadLine]["HP"],lead[leadLine]["ATK"],lead[leadLine]["DEF"])
    return(maxBuff)


def turnintoJson(data,filename, directoryName="" ):
    if filename.endswith(".json")==False:
        filename+=".json"
    if(directoryName!=""):
        if(directoryName[-1]!="/"):
            directoryName+="/"
    with open(directoryName+filename, 'w') as f:
        json.dump(data, f, indent=4)
    
def checkEza(unitid):
    unit=searchbycolumn(code=unitid,column=0,database=cards)[0]
    awakeningID=unit[16][:-2]
    ezaRow=searchbycolumn(code=awakeningID,column=1,database=optimal_awakening_growths)
    if(ezaRow==[]):
        return(False)
    else:
        return(True)

def checkSeza(unitid):
    unit=searchbycolumn(code=unitid,column=0,database=cards)[0]
    awakeningID=unit[16][:-2]
    ezaRow=searchbycolumn(code=awakeningID,column=1,database=optimal_awakening_growths)
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
    standby_skill_set_id=searchbyid(code=unit[0],codecolumn=1,database=card_standby_skill_set_relations,column=2)
    if(standby_skill_set_id!=None):
        standby_skill_set_id=standby_skill_set_id[0]
        standby_skill_setsRow=searchbycolumn(code=standby_skill_set_id,database=standby_skill_sets,column=0)[0]
        output["ID"]=standby_skill_set_id
        output["Exec limit"]=standby_skill_setsRow[5]
        compiled_causality_conditions=standby_skill_setsRow[6]
        compiled_causality_conditions=logicalCausalityExtractor(compiled_causality_conditions)
        compiled_causality_conditions=CausalityLogicalExtractor(unit,compiled_causality_conditions)

        output["Condition"]=compiled_causality_conditions
        standby_skills_rows=searchbycolumn(code=standby_skill_set_id,database=standby_skills,column=1)
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

            elif(standby_skill_row[6]=="130"):
                output["Charge type"]["charge_per_orb"]={}
                output["Charge type"]["charge_per_orb"]["Orb_With_Dragon_Ball"]=int(standby_skill_row[5])

            else:
                if(DEVEXCEPTIONS):
                    raise Exception("Unknown standby skill")
        return(output)




def parseFinish(unit,DEVEXCEPTIONS=False):
    output={}
    finish_skill_set_ids=searchbyid(code=unit[0],codecolumn=1,database=card_finish_skill_set_relations,column=2)
    if(finish_skill_set_ids!=None):
        for finish_skill_set_id in finish_skill_set_ids:
            output[finish_skill_set_id]={}
            finish_skill_setsRow=searchbycolumn(code=finish_skill_set_id,database=finish_skill_sets,column=0)[0]
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
            condition=unicode_fixer(condition)
            output[finish_skill_set_id]["Condition"]=CausalityLogicalExtractor(unit,condition,DEVEXCEPTIONS)

            finish_special_id=finish_skill_setsRow[9]
            finish_special_multiplier=searchbyid(code=finish_special_id,codecolumn=0,database=finish_specials,column=1)
            if(finish_special_multiplier!=None):
                finish_special_multiplier=finish_special_multiplier[0]
                output[finish_skill_set_id]["Multiplier"]=int(finish_special_multiplier)

            finish_skills_rows=searchbycolumn(code=finish_skill_set_id,database=finish_skills,column=1)
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
                elif(finish_skill_row[6]=="76"):
                    output[finish_skill_set_id]["CONFUSION"]=True
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
                    output[finish_skill_set_id]["Multiplier per charge"]=int(efficiacy_value[0])
                    output[finish_skill_set_id]["Max multiplier"]=int(efficiacy_value[1])

                    for causalityKey in output[finish_skill_set_id]["Condition"]["Causalities"]:
                        if(output[finish_skill_set_id]["Condition"]["Causalities"][causalityKey]["Slider"]["Name"]=="What is the charge count at?"):
                            output[finish_skill_set_id]["Condition"]["Causalities"][causalityKey]["Slider"]["Max"]=math.ceil(output[finish_skill_set_id]["Max multiplier"]/output[finish_skill_set_id]["Multiplier per charge"])


                elif(finish_skill_row[6]=="119"):
                    output[finish_skill_set_id]["Nullification"]={}
                    output[finish_skill_set_id]["Nullification"]["Activated"]=True
                elif(finish_skill_row[6]=="120"):
                    output[finish_skill_set_id]["Counter"]={"Activated":True, "Multiplier":efficiacy_value[1]}
                elif(finish_skill_row[6]=="130"):
                    output[finish_skill_set_id]["CONFUSION"]=True
                else:
                    if(DEVEXCEPTIONS):
                        raise Exception("Unknown finish skill")
            if("Exchanges to" not in output[finish_skill_set_id]):
                for standbySkillRow in standby_skills:
                    if(unit[0][:-1] in standbySkillRow[8]):
                        standbySkillSetId=standbySkillRow[1]
                        sourceUnitID=searchbyid(code=standbySkillSetId,codecolumn=0,database=card_standby_skill_set_relations,column=1)
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
    
    causality=causality.replace('{"source":"',"")
    causality=causality.split('","compiled":')[0]

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

def getStatsAtAllLevels(unit,eza,minLevel,maxLevel):
    output={}
    intUnit = [int(x) for x in unit[6:14]]
    growthInfo=searchbycolumn(code=unit[15],column=1,database=card_growths)
    for level in range(minLevel,maxLevel+1):
        coef=float(searchbyid(code=str(level),codecolumn=2,database=growthInfo,column=3)[0])
        output[level]=getUnitStats(intUnit,level,coef)
    return(output)

def getUnitStats(unit,level,coef,DEVEXCEPTIONS=False):
    hp_init=(unit[0])
    hp_max=(unit[1])
    atk_init=(unit[2])
    atk_max=(unit[3])
    def_init=(unit[4])
    def_max=(unit[5])

    level_max=(unit[7])
    stats={}
    stats["HP"]=math.floor((0.5 * (level - 1) * (hp_max - hp_init)) / (level_max - 1) + 0.5 * coef * (hp_max - hp_init) + hp_init)
    stats["ATK"]=math.floor((0.5 * (level - 1) * (atk_max - atk_init)) / (level_max - 1) + 0.5 * coef * (atk_max - atk_init) + atk_init)
    stats["DEF"]=math.floor((0.5 * (level - 1) * (def_max - def_init)) / (level_max - 1) + 0.5 * coef * (def_max - def_init) + def_init)
    return(stats)

def shortenPassiveDictionary(oldPassiveDictionary):
    passiveDictionary=oldPassiveDictionary.copy()
    if "Causality" in passiveDictionary:
        if(passiveDictionary["Causality"]==[]):
            passiveDictionary.pop("Causality")
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
        if "Damage Enemy" in passiveDictionary["Standby"]:
            if passiveDictionary["Standby"]["Damage Enemy"]["Activated"]==False:
                passiveDictionary["Standby"].pop("Damage Enemy")
        if passiveDictionary["Standby"]["Activated"]==False:
            passiveDictionary.pop("Standby")
    if "Forsee Super Attack" in passiveDictionary:
        if passiveDictionary["Forsee Super Attack"]==False:
            passiveDictionary.pop("Forsee Super Attack")
    if "Guaranteed Hit" in passiveDictionary:
        if passiveDictionary["Guaranteed Hit"]==False:
            passiveDictionary.pop("Guaranteed Hit")
    if "Dodge Chance" in passiveDictionary:
        if passiveDictionary["Dodge Chance"]==0:
            passiveDictionary.pop("Dodge Chance")
    if "Effective Against All" in passiveDictionary:
        if passiveDictionary["Effective Against All"]==False:
            passiveDictionary.pop("Effective Against All")
    if "Transformation" in passiveDictionary:
        if passiveDictionary["Transformation"]["Activated"]==False:
            passiveDictionary.pop("Transformation")
    if "Reversible exchange" in passiveDictionary:
        if passiveDictionary["Reversible exchange"]["Activated"]==False:
            passiveDictionary.pop("Reversible exchange")
    if "Slot" in passiveDictionary:
        if passiveDictionary["Slot"]==None:
            passiveDictionary.pop("Slot")
    if "Additional Attack" in passiveDictionary:
        if passiveDictionary["Additional Attack"]["Activated"]==False:
            passiveDictionary.pop("Additional Attack")
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
    if "Ki Change" in passiveDictionary:
        if (passiveDictionary["Ki Change"]["From"]==None and passiveDictionary["Ki Change"]["To"]==None):
            passiveDictionary.pop("Ki Change")
    if "Target" in passiveDictionary:
        if "Class" in passiveDictionary["Target"]:
            if passiveDictionary["Target"]["Class"]==[]:
                passiveDictionary["Target"].pop("Class")
        if "Type" in passiveDictionary["Target"]:
            if passiveDictionary["Target"]["Type"]==[]:
                passiveDictionary["Target"].pop("Type")
        if("Category" in passiveDictionary["Target"]):
            if passiveDictionary["Target"]["Category"]=={"Included": [], "Excluded": []}:
                passiveDictionary["Target"].pop("Category")
        if("Name" in passiveDictionary["Target"]):
            if passiveDictionary["Target"]["Name"]=={"Included": [], "Excluded": []}:
                passiveDictionary["Target"].pop("Name")
        if passiveDictionary["Target"]=={}:
            passiveDictionary.pop("Target")
    if "Chance" in passiveDictionary:
        if passiveDictionary["Chance"]=="100":
            passiveDictionary.pop("Chance")
    if "Length" in passiveDictionary:
        if passiveDictionary["Length"]==None:
            passiveDictionary.pop("Length")
    if "First Turn To Activate" in passiveDictionary:
        if passiveDictionary["First Turn To Activate"]==0:
            passiveDictionary.pop("First Turn To Activate")
    if "Condition" in passiveDictionary:
        if passiveDictionary["Condition"]==None:
            passiveDictionary.pop("Condition")
    if "Once Only" in passiveDictionary:
        if passiveDictionary["Once Only"]==False:
            passiveDictionary.pop("Once Only")
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
    if "Domain" in passiveDictionary:
        if passiveDictionary["Domain"]=="":
            passiveDictionary.pop("Domain")
    if( "Has Animation" in passiveDictionary):
        if passiveDictionary["Has Animation"]==False:
            passiveDictionary.pop("Has Animation")


    return(passiveDictionary)

def getSuperMinKi(kiCircleSegments):
    for segment in kiCircleSegments:
        if kiCircleSegments[segment]=="super" or kiCircleSegments[segment]=="ultra":
            return segment

def extractPassiveLine(unit,passiveskill,printing=False,DEVEXCEPTIONS=False):
    effects={
        "ID": passiveskill[0],
        "Domain": "",
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
            "Damage Enemy": {
                "Activated": False,
                "Multiplier": None
            }
        },
        "Forsee Super Attack": False,
        "Guaranteed Hit": False,
        "Dodge Chance": 0,
        "Effective Against All": False,
        "Transformation": {
            "Activated": False,
            "Unit": None,
            "Giant/Rage": False,
            "Min Turns": None,
            "Max Turns": None,
            "Reverse chance": None
        },
        "Reversible exchange":{
            "Activated": False,
            "Unit": None
        },
        "Additional Attack":{
            "Activated": False,
            "Chance of super": None,
            "Chance of another additional": "0"
        },
        "Timing": None,
        "Building Stat":{
            "Min": 0,
            "Max": 0,
            "Stat Per Proc": 0,
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
        "Ki Change": {
            "From": None,
            "To": None
        },
        "Target": {
            "Category": {"Included": [],"Excluded": []},
            "Target": {"Included": [],"Excluded": []},
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
        "First Turn To Activate": 0,
        "Condition": None,
        "CausalityLogic":passiveskill[11],
        "Once Only": False,
        "Has Animation": False
    }
    if(causalityExtractor(passiveskill[11])!=[]):
        causalityCondition=logicalCausalityExtractor(passiveskill[11])
        causalityCondition=CausalityLogicalExtractor(unit=unit,causality=causalityCondition,DEVEXCEPTIONS=DEVEXCEPTIONS)
        if(causalityCondition!=None):
            effects["Condition"]=causalityCondition
    
    if(passiveskill[6]!=""):
        effects["Has Animation"]=True
    
    if(passiveskill[7]=="0"):
        effects["Buff"]["Type"]="Raw stats"
        effects["Buff"]["+ or -"]="+"

    elif(passiveskill[7]=="1"):
        effects["Buff"]["Type"]="Raw stats"
        effects["Buff"]["+ or -"]="-"

    elif(passiveskill[7]=="2"):
        effects["Buff"]["Type"]="Percentage"
        effects["Buff"]["+ or -"]="+"

    elif(passiveskill[7]=="3"):
        effects["Buff"]["Type"]="Percentage"
        effects["Buff"]["+ or -"]="-"
    else:
        effects["Buff"]["Type"]="Unknown"
        effects["Buff"]["+ or -"]="Unknown"
        if(DEVEXCEPTIONS==True):
                raise Exception("Unknown stat increase type")
    

    effects["Chance"]=passiveskill[10]

    if(passiveskill[5]!="0"):
        effects["Target"]["Category"]={"Included": [],"Excluded": []}
        effects["Target"]["Name"]={"Included": [],"Excluded": []}
        TargetRows=searchbycolumn(code=passiveskill[5],database=sub_target_types,column=1)
        for TargetRow in TargetRows:
            if(TargetRow[2]=="1"):
                TargetCategory=CategoryExtractor(TargetRow[3])
                effects["Target"]["Category"]["Included"].append(TargetCategory)
            elif(TargetRow[2]=="2"):
                TargetCategory=CategoryExtractor(TargetRow[3])
                effects["Target"]["Category"]["Excluded"].append(TargetCategory)
            elif(TargetRow[2]=="4"):
                #list(set([card[1] for x in searchbyid(code=TargetRow[3], codecolumn=2, database=card_unique_info_set_relations, column=1)       for card in searchbycolumn(code=x, column=3, database=cards)]))
                card_unique_info_id=searchbyid(code=TargetRow[3],codecolumn=2,database=card_unique_info_set_relations,column=1)
                possible_names=[]
                for id in card_unique_info_id:
                    name=searchbycolumn(code=id,column=3,database=cards)
                    for unit in name:
                        if(qualifyOwnable(card=unit)):
                            possible_names.append(unit[1])
                likelyName=longestCommonSubstring(possible_names) 
                effects["Target"]["Name"]["Included"]=[likelyName]
            elif(TargetRow[2]=="5"):
                #list(set([card[1] for x in searchbyid(code=TargetRow[3], codecolumn=2, database=card_unique_info_set_relations, column=1)       for card in searchbycolumn(code=x, column=3, database=cards)]))
                card_unique_info_id=searchbyid(code=TargetRow[3],codecolumn=2,database=card_unique_info_set_relations,column=1)
                possible_names=[]
                for id in card_unique_info_id:
                    name=searchbycolumn(code=id,column=3,database=cards)
                    for unit in name:
                        if(qualifyOwnable(card=unit)):
                            possible_names.append(unit[1])
                likelyName=longestCommonSubstring(possible_names) 
                effects["Target"]["Name"]["Excluded"]=likelyName
            else:
                #WIP
                print("Target NOT FOUND")
                if(DEVEXCEPTIONS==True):
                    raise Exception("Target NOT FOUND")


    if(passiveskill[4]=="1"):
        effects["Target"]["Target"]="Self"
    elif(passiveskill[4]=="2"):
        effects["Target"]["Target"]="allies"
    elif(passiveskill[4]=="3"):
        effects["Target"]["Target"]="Enemy"
    elif(passiveskill[4]=="4"):
        effects["Target"]["Target"]="Enemies"
    elif(passiveskill[4]=="5"):
        effects["Target"]["Target"]="allies"
        #For some reason int dfe future gohan has this on his ki support, even though this couldve been under 2
    elif(passiveskill[4]=="12"):
        effects["Target"]["Class"]="Super"
        effects["Target"]["Target"]="allies"
    elif(passiveskill[4]=="13"):
        effects["Target"]["Class"]="Extreme"
        effects["Target"]["Target"]="allies"
    elif(passiveskill[4]=="14"):
        effects["Target"]["Class"]="Super"
        effects["Target"]["Target"]="Enemies"
    elif(passiveskill[4]=="15"):
        effects["Target"]["Class"]="Extreme"
        effects["Target"]["Target"]="Enemies"
    elif(passiveskill[4]=="16"):
        effects["Target"]["Target"]="allies(self excluded)"
    else:
        effects["Target"]["Target"]=("UNKNOWN TARGET")
        if(DEVEXCEPTIONS==True):
            raise Exception("UNKNOWN TARGET")

    
    if(passiveskill[3]=="0"):
        effects["Domain"]=searchbyid(code=passiveskill[0],codecolumn=2,database=dokkan_field_passive_skill_relations,column=1)[0]

    elif passiveskill[3]=="1":
        effects["ATK"]+=int(passiveskill[12])
    elif passiveskill[3]=="2":
        effects["DEF"]+=int(passiveskill[12])
    elif passiveskill[3]=="3":
        effects["ATK"]+=int(passiveskill[12])
        effects["DEF"]+=int(passiveskill[13])
    elif passiveskill[3]=="4":
        effects["Heals"]+=int(passiveskill[12])
    elif passiveskill[3]=="5":
        effects["Ki"]+=int(passiveskill[12])
    elif passiveskill[3]=="9":
        effects["Status"].append("Stun")
    elif passiveskill[3]=="13":
        effects["DR"]+=100-int(passiveskill[12])
    elif passiveskill[3]=="16":
        typing=[extractAllyTyping(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)]
        effects["ATK"]+=int(passiveskill[13])
        effects["Target"]["Type"]=typing
    elif passiveskill[3]=="17":
        typing=[extractAllyTyping(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)]
        effects["DEF"]+=int(passiveskill[13])
        effects["Target"]["Type"]=typing
    elif passiveskill[3]=="18":
        typing=[extractAllyTyping(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)]
        effects["ATK"]+=int(passiveskill[13])
        effects["DEF"]+=int(passiveskill[13])
        effects["Target"]["Type"]=typing
    elif passiveskill[3]=="20":
        typing=[extractAllyTyping(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)]
        effects["Ki"]+=int(passiveskill[13])
        effects["Target"]["Type"]=typing
    elif passiveskill[3]=="24":
        effects["Status"].append("Disable guard")
    elif passiveskill[3]=="28":
        effects["Heals"]+=int(passiveskill[12])
    elif passiveskill[3]=="38":
        if(DEVEXCEPTIONS==True):
            raise Exception("Unknown effect")
    elif passiveskill[3]=="47":
        if(DEVEXCEPTIONS==True):
            raise Exception("Unknown effect")
    elif passiveskill[3]=="48":
        effects["Status"].append("Seal")
    elif passiveskill[3]=="50":
        effects["Status"].append("Immune to negative effects")
    elif passiveskill[3]=="51":
        type1=KiOrbType(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)
        type2=KiOrbType(passiveskill[13],DEVEXCEPTIONS=DEVEXCEPTIONS)
        effects["Ki Change"]["From"]=type1
        effects["Ki Change"]["To"]=type2
        effects["Ki Change"]["Style"]="Single"
    elif passiveskill[3]=="52":
        effects["Status"].append("Survive K.O attacks")
    elif passiveskill[3]=="53":
        effects["Status"].append("DEF reduced to 0")
    elif passiveskill[3]=="59":
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":["AGL","INT","PHY","STR","TEQ","Rainbow","Sweet treats"]}
        effects["Building Stat"]["Slider"]="How many Ki Spheres have been obtained?"
        effects["Building Stat"]["Max"]=23*int(passiveskill[12])
        effects["Building Stat"]["Stat Per Proc"]= int(passiveskill[12])
        effects["ATK"]+=int(passiveskill[12])
    elif passiveskill[3]=="60":
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":["AGL","INT","PHY","STR","TEQ","Rainbow","Sweet treats"]}
        effects["Building Stat"]["Slider"]="How many Ki Spheres have been obtained?"
        effects["Building Stat"]["Max"]=23*int(passiveskill[12])
        effects["Building Stat"]["Stat Per Proc"]= int(passiveskill[12])
        effects["DEF"]+=int(passiveskill[12])
    elif passiveskill[3]=="61":
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":["AGL","INT","PHY","STR","TEQ","Rainbow","Sweet treats"]}
        effects["Building Stat"]["Slider"]="How many Ki Spheres have been obtained?"
        effects["Building Stat"]["Max"]=23*int(passiveskill[12])
        effects["Building Stat"]["Stat Per Proc"]= int(passiveskill[12])
        effects["ATK"]+=int(passiveskill[12])
        effects["DEF"]+=int(passiveskill[12])
    elif passiveskill[3]=="64":
        typing=[KiOrbType(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)]
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":typing}
        effects["Building Stat"]["Slider"]="How many "
        effects["Building Stat"]["Slider"]+=typing[0]
        effects["Building Stat"]["Slider"]+=" Ki Spheres have been obtained?"
        if(typing==["Rainbow"]):
            effects["Building Stat"]["Max"]=5*int(passiveskill[13])
        else:
            effects["Building Stat"]["Max"]=23*int(passiveskill[13])
        effects["ATK"]+=int(passiveskill[13])
        effects["Building Stat"]["Stat Per Proc"]= int(passiveskill[13])
    elif passiveskill[3]=="65":
        typing=[KiOrbType(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)]
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":typing}
        effects["Building Stat"]["Slider"]="How many "
        effects["Building Stat"]["Slider"]+=typing[0]
        effects["Building Stat"]["Slider"]+=" Ki Spheres have been obtained?"
        if(typing==["Rainbow"]):
            effects["Building Stat"]["Max"]=5*int(passiveskill[12])
        else:
            effects["Building Stat"]["Max"]=23*int(passiveskill[12])
        effects["Building Stat"]["Stat Per Proc"]= int(passiveskill[12])
        effects["DEF"]+=int(passiveskill[13])
    elif passiveskill[3]=="66":
        typing=[KiOrbType(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)]
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":typing}
        effects["Building Stat"]["Slider"]="How many "
        effects["Building Stat"]["Slider"]+=typing[0]
        effects["Building Stat"]["Slider"]+=" Ki Spheres have been obtained?"
        if(typing==["Rainbow"]):
            effects["Building Stat"]["Max"]=5*int(passiveskill[13])
        else:
            effects["Building Stat"]["Max"]=23*int(passiveskill[13])
        effects["Building Stat"]["Stat Per Proc"]= int(passiveskill[13])
        effects["ATK"]+=int(passiveskill[13])
        effects["DEF"]+=int(passiveskill[13])
    elif passiveskill[3]=="67":
        type1=binaryOrbType(passiveskill[12],DEVEXCEPTIONS)
        type2=binaryOrbType(passiveskill[13],DEVEXCEPTIONS)
        effects["Ki Change"]["From"]=type1
        effects["Ki Change"]["To"]=type2
        effects["Ki Change"]["Style"]="Randomly"
        
    elif passiveskill[3]=="68":
        #buffs per ki sphere
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":binaryOrbType(passiveskill[12],DEVEXCEPTIONS)}
        effects["Building Stat"]["Slider"]="How many "
        for orbType in binaryOrbType(passiveskill[12],DEVEXCEPTIONS):
            effects["Building Stat"]["Slider"]+=orbType
            effects["Building Stat"]["Slider"]+=" or "
        effects["Building Stat"]["Slider"]=effects["Building Stat"]["Slider"][:-4]
        effects["Building Stat"]["Slider"]+=" Ki Spheres have been obtained?"
        if(binaryOrbType(passiveskill[12],DEVEXCEPTIONS)==["Rainbow"]):
            effects["Building Stat"]["Max"]=5*int(passiveskill[14])
        else:
            effects["Building Stat"]["Max"]=23*int(passiveskill[14])
        if(passiveskill[13]=="1"):
            effects["ATK"]+=int(passiveskill[14])
        elif(passiveskill[13]=="2"):
            effects["Heals"]+=int(passiveskill[14])
        elif(passiveskill[13]=="3"):
            effects["DEF"]+=int(passiveskill[14])
        elif(passiveskill[13]=="4"):
            effects["Crit Chance"]+=int(passiveskill[14])
        elif(passiveskill[13]=="5"):
            effects["Dodge Chance"]+=int(passiveskill[14])
        elif(passiveskill[13]=="6"):
            effects["DR"]+=int(passiveskill[14])
        else:
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown buff")
        effects["Building Stat"]["Stat Per Proc"]= int(passiveskill[14])
    elif passiveskill[3]=="69":
        effects["Ki Change"]["From"]=["AGL","TEQ","INT","STR","PHY","Rainbow","Sweet treats"]
        effects["Ki Change"]["To"]=[KiOrbType(passiveskill[12])]
        effects["Ki Change"]["Style"]="All"
    elif passiveskill[3]=="71":
        if(int(passiveskill[12])>int(passiveskill[13])):
            #The less HP remaining the greater the stats boost
            effects["ATK"]+=int(passiveskill[12])
            effects["Building Stat"]["Stat Per Proc"]= int(passiveskill[14])
            effects["Building Stat"]["Cause"]={"Cause":"HP", "Type":"Less HP remaining"}
            effects["Building Stat"]["Max"]+=int(passiveskill[12])
            effects["Building Stat"]["Min"]+=int(passiveskill[13])
            effects["Building Stat"]["Slider"]="What percentage of HP is remaining?"
        else:
            #The more HP remaining the greater the stats boost
            effects["ATK"]+=int(passiveskill[13])
            effects["Building Stat"]["Cause"]={"Cause":"HP", "Type":"More HP remaining"}
            effects["Building Stat"]["Stat Per Proc"]= int(passiveskill[14])
            effects["Building Stat"]["Max"]+=int(passiveskill[13])
            effects["Building Stat"]["Min"]+=int(passiveskill[12])
            effects["Building Stat"]["Slider"]="What percentage of HP is remaining?"
    elif passiveskill[3]=="72":
        if(int(passiveskill[12])>int(passiveskill[13])):
            #The less HP remaining the greater the stats boost
            effects["DEF"]+=int(passiveskill[12])
            effects["Building Stat"]["Cause"]={"Cause":"HP", "Type":"Less HP remaining"}
            effects["Building Stat"]["Stat Per Proc"]= int(passiveskill[14])
            effects["Building Stat"]["Max"]+=int(passiveskill[12])
            effects["Building Stat"]["Min"]+=int(passiveskill[13])
            effects["Building Stat"]["Slider"]="What percentage of HP is remaining?"
        else:
            #The more HP remaining the greater the stats boost
            effects["DEF"]+=int(passiveskill[13])
            effects["Building Stat"]["Cause"]={"Cause":"HP", "Type":"More HP remaining"}
            effects["Building Stat"]["Stat Per Proc"]= int(passiveskill[14])
            effects["Building Stat"]["Max"]+=int(passiveskill[13])
            effects["Building Stat"]["Min"]+=int(passiveskill[12])
            effects["Building Stat"]["Slider"]="What percentage of HP is remaining?"
    elif passiveskill[3]=="73":
        if(int(passiveskill[12])>int(passiveskill[13])):
            #The less HP remaining the greater the stats boost
            effects["ATK"]+=int(passiveskill[12])
            effects["DEF"]+=int(passiveskill[12])
            effects["Building Stat"]["Stat Per Proc"]= (int(passiveskill[12])-int(passiveskill[13]))/100
            effects["Building Stat"]["Cause"]={"Cause":"HP", "Type":"Less HP remaining"}
            effects["Building Stat"]["Max"]+=int(passiveskill[12])
            effects["Building Stat"]["Min"]+=int(passiveskill[13])
            effects["Building Stat"]["Slider"]="What percentage of HP is remaining?"
        else:
            #The more HP remaining the greater the stats boost
            effects["ATK"]+=int(passiveskill[13])
            effects["DEF"]+=int(passiveskill[13])
            effects["Building Stat"]["Stat Per Proc"]= (int(passiveskill[13])-int(passiveskill[12]))/100
            effects["Building Stat"]["Cause"]={"Cause":"HP", "Type":"More HP remaining"}
            effects["Building Stat"]["Max"]+=int(passiveskill[13])
            effects["Building Stat"]["Min"]+=int(passiveskill[12])
            effects["Building Stat"]["Slider"]="What percentage of HP is remaining?"
    elif passiveskill[3]=="76":
        effects["Effective Against All"]=True
    elif passiveskill[3]=="78":
        effects["Guard"]=True
    elif passiveskill[3]=="79":
        effects["Transformation"]["Activated"]=True
        effects["Transformation"]["Unit"]=passiveskill[12]
        effects["Transformation"]["Giant/Rage"]=True
        params=searchbycolumn(code=passiveskill[13],database=battle_params,column=1)
        for param in params:
            if(param[2]=="0"):
                effects["Transformation"]["Min Turns"]=param[3]
            elif(param[2]=="1"):
                effects["Transformation"]["Max Turns"]=param[3]
            elif(param[2]=="2"):
                effects["Transformation"]["Reverse chance"]=param[3]
        
    elif passiveskill[3]=="80":
        if(DEVEXCEPTIONS==True):
            raise Exception("Counter without dodge")
    elif passiveskill[3]=="81":
        effects["Additional Attack"]["Activated"]=True
        effects["Additional Attack"]["Chance of super"]=int(passiveskill[14])
        if(passiveskill[13]!="0"):
            effects["Additional Attack"]["Chance of another additional"]=passiveskill[13]
    elif passiveskill[3]=="82":
        effects["ATK"]+=int(passiveskill[13])
        effects["DEF"]+=int(passiveskill[13])
        if(extractClassType(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)[0]!=[]):
            effects["Target"]["Class"]=extractClassType(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)[0][0]
        if(extractClassType(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)[1]!=[]):
            effects["Target"]["Type"]=extractClassType(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)[1]
    elif passiveskill[3]=="83":
        effects["Ki"]+=int(passiveskill[13])
        if(extractClassType(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)[0]!=[]):
            effects["Target"]["Class"]=extractClassType(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)[0][0]
        if(extractClassType(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)[1]!=[]):
            effects["Target"]["Type"]=extractClassType(passiveskill[12],DEVEXCEPTIONS=DEVEXCEPTIONS)[1]
    elif passiveskill[3]=="90":
        effects["Crit Chance"]+=int(passiveskill[12])
    elif passiveskill[3]=="91":
        effects["Dodge Chance"]+=int(passiveskill[12])
    elif passiveskill[3]=="92":
        effects["Guaranteed Hit"]=True
    elif passiveskill[3]=="95":
        if(DEVEXCEPTIONS==True):
            raise Exception("Dodge and counter")
    elif passiveskill[3]=="96":
        kiSphereType=binaryOrbType(passiveskill[12],DEVEXCEPTIONS)
        effects["Ki"]+=int(passiveskill[13])
        effects["Building Stat"]["Stat Per Proc"]= int(passiveskill[13])
        effects["Building Stat"]["Cause"]={"Cause":"Ki sphere obtained", "Type":kiSphereType}
        effects["Building Stat"]["Slider"]="How many "
        for orbType in kiSphereType:
            effects["Building Stat"]["Slider"]+=orbType
            effects["Building Stat"]["Slider"]+=" or "
        effects["Building Stat"]["Slider"]=effects["Building Stat"]["Slider"][:-4]
        if(kiSphereType==["Rainbow"]):
            effects["Building Stat"]["Max"]=5*int(passiveskill[13])
        else:
            effects["Building Stat"]["Max"]=23*int(passiveskill[13])
        effects["Building Stat"]["Slider"]+=" Ki Spheres have been obtained?"

        
    elif passiveskill[3]=="97":
        if(passiveskill[13]=="1"):
            effects["Nullification"]["Activated"]=True
            effects["Nullification"]["Absorbed"]=int(passiveskill[12])
        else:
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown effect")
    elif passiveskill[3]=="98":
        if(passiveskill[14]=="0"):
            effects["ATK"]+=int(passiveskill[12])
        elif(passiveskill[14]=="1"):
            effects["DEF"]+=int(passiveskill[12])
        elif(passiveskill[14]=="2"):
            effects["Crit Chance"]+=int(passiveskill[12])
        elif(passiveskill[14]=="3"):
            effects["Dodge Chance"]+=int(passiveskill[12])
        elif(passiveskill[14]=="4"):
            #CONFUSED
            effects["DR"]+=int(passiveskill[12])
        elif(passiveskill[14]=="5"):
            effects["Ki"]+=int(passiveskill[12])
        else:
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown stat increase")
        effects["Building Stat"]["Stat Per Proc"]= int(passiveskill[12])
        effects["Building Stat"]["Cause"]={"Cause":"Look Elsewhere"}
        effects["Building Stat"]["Max"]+=int(passiveskill[13])
    elif passiveskill[3]=="101":
        effects["Forsee Super Attack"]=True
    elif passiveskill[3]=="103":
        effects["Transformation"]["Activated"]=True
        effects["Transformation"]["Unit"]=passiveskill[12]

        effects["First Turn To Activate"]+=(int(passiveskill[13])+1)
    elif passiveskill[3]=="105":
        effects["Ki Change"]["From"]=["AGL","TEQ","INT","STR","PHY","Rainbow","Sweet treats"]
        effects["Ki Change"]["To"]=binaryOrbType(int(passiveskill[12])+int(passiveskill[13]))
        effects["Ki Change"]["Style"]="All"
    elif passiveskill[3]=="109":
        effects["Revive"]["Activated"]=True
        effects["Revive"]["HP recovered"]=int(passiveskill[12])
    elif passiveskill[3]=="110":
        if(passiveskill[12]=="2"):
            effects["Disable Other Line"]["Activated"]=True
            effects["Disable Other Line"]["Line"]=passiveskill[13]
        elif(passiveskill[12]=="15"):
            #WIP
            #print("Something related to charging standby skills")
            effects["Building Stat"]["Cause"]={"Cause":"Charging standby skills"}
            effects["Building Stat"]["Slider"]="WIP"
            effects["Building Stat"]["Min"]=1
            effects["Building Stat"]["Max"]=1
            effects["Building Stat"]["Stat Per Proc"]= 1
            
        else:
            print("UNKNOWN EFFECT",passiveskill)
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown effect")

    elif passiveskill[3]=="111":
        effects["Status"].append("Disable action")
    elif(passiveskill[3]=="114"):
        effects["Status"].append("Unable to attack")
    elif(passiveskill[3]=="115"):
        effects["Standby"]["Activated"]=True
    elif(passiveskill[3]=="117"):
        effects["Standby"]["Activated"]=True
        effects["Standby"]["Change form"]["Activated"]=True
        revertUnit=str(int(unit[22][:-2]))+"0"
        effects["Standby"]["Change form"]["Unit"]=revertUnit
    elif passiveskill[3]=="119":
        effects["Nullification"]["Activated"]=True
    elif(passiveskill[3]=="120"):
        effects["Counter"]={"Activated":True, "Multiplier":passiveskill[13]}
        if(passiveskill[12]!="0"):
            effects["Counter"]["DR from normals"]=passiveskill[12]
    elif(passiveskill[3]=="128"):
        effects["Counter"]={"Activated":True, "Multiplier":passiveskill[13], "Cause":"Evaded attack"}
    elif(passiveskill[3]=="131"):
        effects["Reversible exchange"]["Activated"]=True
        effects["Reversible exchange"]["Unit"]=passiveskill[12]
        
    else:
        if(DEVEXCEPTIONS==True):
                raise Exception("Unknown effect")
        

    

    
    
    
    effects["Length"]=passiveskill[8]



    if passiveskill[2]=="1":
        effects["Timing"]="Start of turn"
    elif passiveskill[2]=="3":
        effects["Timing"]="Right before attack(SOT stat)"
    elif passiveskill[2]=="4":
        effects["Timing"]="Right before attack(MOT stat)"
    elif passiveskill[2]=="5":
        effects["Timing"]="Right after attack"
    elif passiveskill[2]=="6":
        effects["Timing"]="Right before being hit"
    elif passiveskill[2]=="7":
        effects["Timing"]="Right after being hit"
    elif passiveskill[2]=="9":
        effects["Timing"]="End of turn"
    elif passiveskill[2]=="11":
        effects["Timing"]="After all ki collected"
    elif passiveskill[2]=="12":
        effects["Timing"]="Activating standby"
    elif passiveskill[2]=="14":
        effects["Timing"]="When final blow delivered"
    elif passiveskill[2]=="15":
        effects["Timing"]="When ki spheres collected"
    else:
        print("UNKNOWN TRIGGER",end=" ")
        if(DEVEXCEPTIONS==True):
                raise Exception("Unknown trigger")

    

    

        
                    

    if(passiveskill[9]=="1"):
        effects["Once Only"]=True
        
    
    
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
        return(complexlogicalCausalityExtractor(causality.replace(" ","").split('","compiled":')[1][:-1]))


def complexlogicalCausalityExtractor(causality):
    if(causality.count("[")==0):
        return((" "+causality+" ").replace("  "," "))
    causalityList=[]
    bracketLevel=0
    currentString=""
    for char in causality[1:-1]:
        if(char=="["):
            bracketLevel+=1
        elif(char=="]"):
            bracketLevel-=1
        
        if(bracketLevel==0 and char==","):
            causalityList.append(currentString)
            currentString=""
        else:
            currentString+=char
    causalityList.append(currentString)

    for causalityEntryKey in range(1,len(causalityList)):
        causalityList[causalityEntryKey]=complexlogicalCausalityExtractor(causalityList[causalityEntryKey])

    if(" True " in causalityList):        
        causalityList=(filterTrue(causalityList))

    returnText="( "
    for causality in causalityList[1:]:
        returnText+=causality
        if(causalityList[0]=='"|"'):
            returnText+=" || "
        if(causalityList[0]=='"&"'):
            returnText+=" && "        
    returnText=returnText[:-4]
    returnText+=" )"
    return returnText.replace("  "," ")

def filterTrue(causalityList):
    if(causalityList[0]=='"&"'):
        temp=causalityList.copy()
        temp.remove(" True ")
        return(temp)
    if(causalityList[0]=='"|"'):
        if(" True " in causalityList):
            return(['"|"'," True "])

def simpleLogicalCausalityExtractor(causality):
    causality=causality[1:-1].split(",")
    if(causality[0]=='"|"'):
        return("(" + causality[1] + " || " +causality[2] + ")")
    if(causality[0]=='"&"'):
        return("(" + causality[1] + " && " +causality[2] + ")")
    

def CausalityLogicalExtractor(unit,causality,DEVEXCEPTIONS=False):
    output={}
    result=causality
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
    baseString = listOfStrings[0]
    longestString = ""
    for startingChar in range(len(baseString) + 1):
        for endingChar in range(startingChar, len(baseString) + 1):
            substring = baseString[startingChar:endingChar]
            valid = True
            for s in listOfStrings:
                if substring not in s:
                    valid = False
                    break
            if valid and len(substring) > len(longestString):
                longestString = substring
    return longestString


def CategoryExtractor(CategoryId):
    for category in card_categories:
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
        output["Button"]["Name"]="Has this character been hit?"
        output["Slider"]["Name"]="How many times has this character been hit?"
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
            target="units on this turn?"
            output["Slider"]["Max"]=3
        categoryType=searchbyid(CausalityRow[3],codecolumn=0,database=card_categories,column=1)[0]

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
        output["Button"]["Name"]="Is the target enemy in"
        for icon in Status:
            output["Button"]["Name"]+=iconToStatus(icon)
            output["Button"]["Name"]+=" or "
        output["Button"]["Name"]=output["Button"]["Name"][:-4]
        output["Button"]["Name"]+="?"
        output["Paragraph Title"]= "When the target enemy is in the following status"
        for icon in Status:
            output["Paragraph Title"]+=icon
            output["Paragraph Title"]+=" or "
        output["Paragraph Title"]=output["Paragraph Title"][:-4]
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
            output["Button"]["Name"]="Is there an ally attacking on this turn whose name includes "
        else:
            output+=("UNKNOWN NAME TYPE")
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown name type")
        card_unique_info_id=searchbyid(code=CausalityRow[3],codecolumn=2,database=card_unique_info_set_relations,column=1)
        possible_names=[]
        for id in card_unique_info_id:
            name=searchbycolumn(code=id,column=3,database=cards)
            for unit in name:
                if(qualifyEncounterable(card=unit)):
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
        categoryType=searchbyid(CausalityRow[3],codecolumn=0,database=card_categories,column=1)[0]

        card_unique_info_id=searchbyid(code=CausalityRow[4],codecolumn=2,database=card_unique_info_set_relations,column=1)
        possible_names=[]
        for id in card_unique_info_id:
            name=searchbycolumn(code=id,database=cards,column=3)
            for unit in name:
                if(unit[1] not in possible_names):
                    if(qualifyEncounterable(unit)):
                        possible_names.append(unit[1])
        possible_names=list(set(possible_names))
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
            output["Button"]["Name"]+=(" attacking on this turn?")
        else:
            output+=("UNKNOWN NAME TYPE")
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown name type")

    elif(CausalityRow[1]=="46"):
        output["Button"]["Name"]=("Is there an extreme class enemy?")
    elif(CausalityRow[1]=="47"):
        output["Button"]["Name"]=("Has this character or an ally attacking on this turn been KO'd?")
    elif(CausalityRow[1]=="48"):
        output["Button"]["Name"]=("Has the enemy been hit by the characters ultra super attack?")
    elif(CausalityRow[1]=="49"):
        if(CausalityRow[2]=="1"):
            output["Button"]["Name"]=("Has this character been hit by a ki blast super attack?")
        elif(CausalityRow[2]=="2"):
            output["Button"]["Name"]=("Has this character been hit by an unarmed super attack?")
        elif(CausalityRow[2]=="4"):
            output["Button"]["Name"]=("Has this character been hit by a physical super attack?")
        else:
            output+=("UNKNOWN SUPER ATTACK TYPE")
            if(DEVEXCEPTIONS==True):
                raise Exception("Unknown super attack type")
    elif(CausalityRow[1]=="51"):
        output["Button"]["Name"]=("Is it within the first ")
        output["Button"]["Name"]+=CausalityRow[2]
        output["Button"]["Name"]+=(" turn(s) from the character's entry turn?")
        
        output["Slider"]["Name"]="How many turns is it since entry turn?"
        output["Slider"]["Logic"]="<="
        output["Slider"]["Logic"]+=CausalityRow[2]
        output["Slider"]["Min"]=0
        output["Slider"]["Max"]=int(CausalityRow[2])+1
    elif(CausalityRow[1]=="53"):
        output["Button"]["Name"]=("Has this characters finish effect been activated?")
    elif(CausalityRow[1]=="54"):
        output["Button"]["Name"]=("Has this character or an ally's revival skill been activated?")
    elif(CausalityRow[1]=="55"):
        output["Button"]["Name"]=("Is it on or after the first ")
        output["Button"]["Name"]+=str(int(CausalityRow[2])+1)
        output["Button"]["Name"]+=(" turns from this characters entry turn?")

        output["Slider"]["Name"]="How many turns is it since entry turn?"
        output["Slider"]["Logic"]=">="
        output["Slider"]["Logic"]+=str(int(CausalityRow[2])+1)
        output["Slider"]["Min"]=0
        output["Slider"]["Max"]=int(CausalityRow[2])+1
    elif(CausalityRow[1]=="56"):
        output["Button"]["Name"]=("Has this character been hit by a normal attack?")
    elif(CausalityRow[1]=="57"):
        output["Button"]["Name"]=("Is the Domain ")
        output["Button"]["Name"]+=searchbyid(code=CausalityRow[2],codecolumn=1,database=dokkan_fields,column=2)[0]
        domain=searchbyid(code=CausalityRow[2],codecolumn=1,database=dokkan_fields,column=2)
        if(domain!=[]):
            output["Button"]["Name"]+=domain[0]
        else:
            output["Button"]["Name"]+=searchbyid(code=CausalityRow[2],codecolumn=1,database=dokkan_fields,column=2)[0]
        output["Button"]["Name"]+=(" active?")
    elif(CausalityRow[1]=="58"):
        output["Button"]["Name"]=("Is no domain active?")
    elif(CausalityRow[1]=="61"):
        output["Button"]["Name"]=("Has this character been hit on this turn?")
    else:
        output["Button"]["Name"]=("UNKNOWN CAUSALITY CONDITION")
        if(DEVEXCEPTIONS==True):
            raise Exception("Unknown causality condition")
    return(output)

def iconToStatus(statusIcon):
    if(statusIcon=="{passiveImg:atk_down}"): return "ATK Down"
    if(statusIcon=="{passiveImg:def_down}"): return "DEF Down"
    if(statusIcon=="{passiveImg:stun}"): return "Stunned"
    if(statusIcon=="{passiveImg:astute}"): return "Sealed"

def causalityLogicFinder(unit,causalityCondition,printing=True,DEVEXCEPTIONS=False):
    output={"Button":{}, "Slider": {"Name": None, "Logic": None}, "Paragraph Title": ""}
    for row in skill_causalities:
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
                output["Paragraph Title"]="When HP is "+str(CausalityRow[2])+"% or more"
            elif(CausalityRow[1]=="2"):
                output["Button"]["Name"]="Is HP "
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=" % or less?"
                output["Slider"]["Name"]="What percentage of HP is remaining?"
                output["Slider"]["Logic"]="<="
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Min"]=0
                output["Slider"]["Max"]=100
                output["Paragraph Title"]="When HP is "+str(CausalityRow[2])+"% or less"
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
                output["Paragraph Title"]="When Ki is " + str(kiAmount) + " or more"
            elif(CausalityRow[1]=="4"):
                Ca2=int(CausalityRow[2])
                unit31=int(unit[31])
                kiAmount=(Ca2*unit31)//99

                #output["Button"]["Name"]="Is Ki at least "
                #output["Button"]["Name"]+=str(kiAmount)
                #output["Button"]["Name"]+="?"


                output["Slider"]["Name"]="How much ki is there?"
                output["Slider"]["Logic"]="<="
                output["Slider"]["Logic"]+=str(kiAmount)
                output["Slider"]["Min"]=0
                if(unit[5]=="5"):
                    output["Slider"]["Max"]=24
                else:
                    output["Slider"]["Max"]=12
                output["Paragraph Title"]="When ki is "+str(kiAmount) + " or more"
            elif(CausalityRow[1]=="5"):
                output["Button"]["Name"]="Is the turn count "
                output["Button"]["Name"]+=str(int(CausalityRow[2])+1)
                output["Button"]["Name"]+=" or more?"

                output["Slider"]["Name"]="What turn is it?"
                output["Slider"]["Logic"]=">="
                output["Slider"]["Logic"]+=str(int(CausalityRow[2])+1)
                output["Slider"]["Min"]=1
                output["Paragraph Title"]="When the turn count is " + str(int(CausalityRow[2])+1)
            elif(CausalityRow[1]=="8"):
                output["Button"]["Name"]="Is attack higher than enemy's?"
                output["Paragraph Title"]="When attack is higher than enemy's"
            elif(CausalityRow[1]=="9"):
                output["Button"]["Name"]="Is attack lower than enemy's?"
                output["Paragraph Title"]="When attack is lower than enemy's"
            elif(CausalityRow[1]=="14"):
                output["Button"]["Name"]="Is the first to attack?"
                output["Paragraph Title"]="When the first to attack"
            elif(CausalityRow[1]=="15"):
                output["Button"]["Name"]="Is there "
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=" or more enemies?"
                
                output["Slider"]["Name"]="How many enemies are there?"
                output["Slider"]["Logic"]=">="
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Min"]=1
                output["Slider"]["Max"]=7
                output["Paragraph Title"]="When there are "+str(CausalityRow[2])+" or more enemies"
            elif(CausalityRow[1]=="16"):
                output["Button"]["Name"]="Is there less than "
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=" enemies?"
                
                output["Slider"]["Name"]="How many enemies are there?"
                output["Slider"]["Logic"]="<"
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Min"]=1
                output["Slider"]["Max"]=7
                output["Paragraph Title"]="When there are less than "+str(CausalityRow[2])+" enemies"
            elif(CausalityRow[1]=="17"):
                output["Button"]["Name"]="Is the enemy's health "
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=" % or more?"

                output["Slider"]["Name"]="What percentage of HP does the enemy have?"
                output["Slider"]["Logic"]=">="
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Max"]=100
                
                output["Paragraph Title"]="When enemy health is " + CausalityRow[2] + "% or more"
            elif(CausalityRow[1]=="18"):
                output["Button"]["Name"]="Is the enemy's health "
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=" % or less?"

                output["Slider"]["Name"]="What percentage of HP does the enemy have?"
                output["Slider"]["Logic"]="<="
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Max"]=100

                output["Paragraph Title"]="When enemy health is " + CausalityRow[2] + "% or less"
            elif(CausalityRow[1]=="19"):
                output["Button"]["Name"]="Is this the "
                output["Button"]["Name"]+=ordinalise(int(CausalityRow[2])+1)
                output["Button"]["Name"]+=" attacker in the turn?"

                output["Slider"]["Name"]="What position is this character attacking in?"
                output["Slider"]["Logic"]="=="
                output["Slider"]["Logic"]+=str(int(CausalityRow[2])+1)
                output["Slider"]["Min"]=1
                output["Slider"]["Max"]=3
                output["Paragraph Title"]="As the "+ordinalise(int(CausalityRow[2])+1)+" attacker in the turn"

            elif(CausalityRow[1]=="24"):
                output["Button"]["Name"]="Has this character been hit?"
                output["Slider"]["Name"]="How many times has this character been hit?"
                output["Slider"]["Logic"]=">=1"
                output["Slider"]["Min"]=0
                output["Slider"]["Max"]=1
                output["Paragraph Title"]="After recieving an attack"
            elif(CausalityRow[1]=="25"):
                output["Button"]["Name"]="Has this character delivered the final blow?"
                output["Paragraph Title"]="When this character has delivered the final blow"

            elif(CausalityRow[1]=="30"):
                output["Button"]["Name"]="Has guard been activated?"
                output["Paragraph Title"]="After guard is activated"
            elif(CausalityRow[1]=="31"):
                output["Button"]["Name"]="Has 3 attacks in a row?"
                output["Paragraph Title"]="When 3 attacks in a row"
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

                output["Paragraph Title"]="When HP is between " + CausalityRow[2] + "% and " + CausalityRow[3] + "%"
            elif(CausalityRow[1]=="34"):
                if(CausalityRow[2]=="0"):
                    target="allies "
                    output["Slider"]["Max"]=7
                elif(CausalityRow[2]=="1"):
                    target="enemies "
                    output["Slider"]["Max"]=7
                elif(CausalityRow[2]=="2"):
                    target="allies attacking on this turn"
                    output["Slider"]["Max"]=3
                categoryType=searchbyid(CausalityRow[3],codecolumn=0,database=card_categories,column=1)[0]

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

                    output["Paragraph Title"]="When there are no " + categoryType + " category " + target
                else:
                    output["Button"]["Name"]="Are there "
                    output["Button"]["Name"]+=CausalityRow[4]
                    output["Button"]["Name"]+=" or more "
                    output["Button"]["Name"]+=categoryType
                    output["Button"]["Name"]+=" category "
                    output["Button"]["Name"]+=target
                    output["Button"]["Name"]+="?"

                    output["Slider"]["Name"]="How many "
                    output["Slider"]["Name"]+=categoryType
                    output["Slider"]["Name"]+=" category "
                    output["Slider"]["Name"]+=target
                    output["Slider"]["Logic"]=">="
                    output["Slider"]["Logic"]+=CausalityRow[4]
                    output["Slider"]["Min"]=0
                    output["Paragraph Title"]="When there are "+str(CausalityRow[4])+" or more "+categoryType+" Category "+target

            elif(CausalityRow[1]=="35"):
                if(extractClassType(CausalityRow[2],DEVEXCEPTIONS=DEVEXCEPTIONS)==(["Super"],["PHY","STR","INT","TEQ","AGL"])):
                    output["Button"]["Name"]="Does the team include all five Super types?"
                    output["Paragraph Title"]="When the team includes all five Super types"
                elif(extractClassType(CausalityRow[2],DEVEXCEPTIONS=DEVEXCEPTIONS)==(["Extreme"],["PHY","STR","INT","TEQ","AGL"])):
                    output["Button"]["Name"]="Does the team include all five Extreme types?"
                    output["Paragraph Title"]="When the team includes all five Extreme types"
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

                output["Paragraph Title"]="When HP is " + CausalityRow[2] + "% or less starting from the " + ordinalise(int(CausalityRow[3])+1) + " turn from the start of battle"

            elif(CausalityRow[1]=="38"):
                Status=binaryStatus(CausalityRow[2])
                output["Button"]["Name"]="Is the target enemy in "
                for icon in Status:
                    output["Button"]["Name"]+=iconToStatus(icon)
                    output["Button"]["Name"]+=" or "
                output["Button"]["Name"]=output["Button"]["Name"][:-4]
                output["Button"]["Name"]+="?"
                output["Paragraph Title"]= "When the target enemy is in the following status"
                for icon in Status:
                    output["Paragraph Title"]+=icon
                    output["Paragraph Title"]+=" or "
                output["Paragraph Title"]=output["Paragraph Title"][:-4]
            elif(CausalityRow[1]=="39"):
                if(CausalityRow[2]=="32"):
                    output["Button"]["Name"]="Is this unit attacking a super class enemy?"
                    output["Paragraph Title"]="When the unit is attacking a super class enemy"
                elif(CausalityRow[2]=="64"):
                    output["Button"]["Name"]="Is this unit attacking an extreme class enemy?"
                    output["Paragraph Title"]="When the unit is attacking an extreme class enemy"
                else:
                    print("UNKNOWN TYPE")
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown type")
            elif(CausalityRow[1]=="40"):
                output["Button"]["Name"]="Is a super being performed?"
                output["Paragraph Title"]="When a super is being performed"
            elif(CausalityRow[1]=="41"):
                if(CausalityRow[2]=="0"):
                    output["Button"]["Name"]="Is there "+CausalityRow[4]+" or more allies on the team whose name includes "
                    output["Paragraph Title"]="When there are "+CausalityRow[4]+" or more allies whose name includes "
                elif(CausalityRow[2]=="1"):
                    output["Button"]["Name"]="Is there "+CausalityRow[4]+" or more enemies whose name includes "
                elif(CausalityRow[2]=="2"):
                    output["Button"]["Name"]="Is there "+CausalityRow[4]+" or more allies attacking on this turn whose name includes "
                    output["Paragraph Title"]="When there are "+CausalityRow[4]+"or more allies whose name includes "
                else:
                    output+=("UNKNOWN NAME TYPE")
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown name type")
                card_unique_info_id=searchbyid(code=CausalityRow[3],codecolumn=2,database=card_unique_info_set_relations,column=1)
                possible_names=[]
                for id in card_unique_info_id:
                    name=searchbycolumn(code=id,column=3,database=cards)
                    for unit in name:
                        if(qualifyEncounterable(card=unit) and unit[0][0]=="1"):
                            possible_names.append(unit[1])
                likelyName=longestCommonSubstring(possible_names) 
                output["Button"]["Name"]+=likelyName
                output["Button"]["Name"]+=("?")
                output["Paragraph Title"]+='"' + likelyName+'"'
                if(CausalityRow[2]=="0"):
                    pass
                elif(CausalityRow[2]=="1"):
                    pass
                elif(CausalityRow[2]=="2"):
                    output["Paragraph Title"]+=" attacking in the same turn "

                    

            elif(CausalityRow[1]=="42"):
                kiSphereType=binaryOrbType(CausalityRow[2],DEVEXCEPTIONS)
                if(kiSphereType==["PHY","STR","INT","TEQ","AGL"]):
                    output["Button"]["Name"]="Has " + CausalityRow[3] + " or more type Ki Spheres been obtained?"
                    output["Slider"]["Name"]="How many type Ki Spheres have been obtained?"
                    output["Paragraph Title"]="With " + CausalityRow[3] + " or more type Ki Spheres obtained"
                elif(kiSphereType==["Rainbow", "PHY", "STR", "INT", "TEQ", "AGL"]):
                    output["Button"]["Name"]="Has " + CausalityRow[3] + " or more Ki Spheres been obtained?"
                    output["Slider"]["Name"]="How many Ki Spheres have been obtained?"
                    output["Paragraph Title"]="With " + CausalityRow[3] + " or more Ki Spheres obtained"
                else:
                    output["Button"]["Name"]="Has "
                    output["Button"]["Name"]+=CausalityRow[3]
                    output["Button"]["Name"]+=" or more "
                    for orbType in kiSphereType:
                        output["Button"]["Name"]+=orbType
                        output["Button"]["Name"]+=" or "
                    output["Button"]["Name"]=output["Button"]["Name"][:-4]
                    output["Button"]["Name"]+=" Ki Spheres been obtained?"

                    output["Paragraph Title"]="With " + CausalityRow[3] + " or more "
                    for orbType in kiSphereType:
                        output["Paragraph Title"]+=orbType
                        output["Paragraph Title"]+=" or "
                    output["Paragraph Title"]=output["Paragraph Title"][:-4]
                    output["Paragraph Title"]+=" Ki Spheres obtained"

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
                output["Paragraph Title"]="After evading an attack"
            elif(CausalityRow[1]=="44"):
                if(CausalityRow[2]=="0" or CausalityRow[2]=="1"):
                    output["Slider"]["Name"]="How many super attacks has this character performed?"
                    output["Slider"]["Logic"]=">="
                    output["Slider"]["Logic"]+=CausalityRow[3]
                    output["Slider"]["Min"]=0
                    output["Slider"]["Max"]=int(CausalityRow[3])

                    output["Paragraph Title"]="When the character has performed " + CausalityRow[3] + " or more super attacks"
                elif(CausalityRow[2])=="2":
                    output["Slider"]["Name"]="How many attacks has this character performed in battle?"
                    output["Slider"]["Logic"]=">="
                    output["Slider"]["Logic"]+=CausalityRow[3]
                    output["Slider"]["Min"]=0
                    output["Slider"]["Max"]=int(CausalityRow[3])

                    output["Paragraph Title"]="When the character has performed " + CausalityRow[3] + " or more attacks"
                elif(CausalityRow[2]=="3"):
                    output["Button"]["Name"]="Has this character recieved their "
                    output["Button"]["Name"]+=(ordinalise(CausalityRow[3]))
                    output["Button"]["Name"]+=(" attack in battle?")

                    output["Slider"]["Name"]="How many attacks has this character recieved?"
                    output["Slider"]["Logic"]=">="
                    output["Slider"]["Logic"]+=CausalityRow[3]
                    output["Slider"]["Min"]=0
                    output["Slider"]["Max"]=int(CausalityRow[3])
                    if(CausalityRow[3]=="1"):
                        output["Paragraph Title"]="After recieving an attack"
                    else:
                        output["Paragraph Title"]="After recieving "+str(CausalityRow[3])+" attacks"
                elif(CausalityRow[2]=="4"):
                    output["Button"]["Name"]="Has this character's guard been activated "
                    output["Button"]["Name"]+=(ordinalise(CausalityRow[3]))
                    output["Button"]["Name"]+=(" times in battle?")

                    output["Slider"]["Name"]="How many times has this character's guard been activated?"
                    output["Slider"]["Logic"]=">="
                    output["Slider"]["Logic"]+=CausalityRow[3]
                    output["Slider"]["Min"]=0
                    output["Slider"]["Max"]=int(CausalityRow[3])

                    output["Paragraph Title"]="When the character has guarded " + CausalityRow[3] + " or more attacks"
                elif(CausalityRow[2]=="5"):
                    output["Button"]["Name"]="Has this character evaded "
                    output["Button"]["Name"]+=(ordinalise(CausalityRow[3]))
                    output["Button"]["Name"]+=(" times in battle?")

                    output["Slider"]["Name"]="How many attacks have been evaded?"
                    output["Slider"]["Logic"]=">="
                    output["Slider"]["Logic"]+=CausalityRow[3]
                    output["Slider"]["Min"]=0
                    output["Slider"]["Max"]=int(CausalityRow[3])

                    output["Paragraph Title"]="When the character has evaded " + CausalityRow[3] + " or more attacks"
                else:
                    output+=("UNKNOWN NAME TYPE")
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown name type")
            elif(CausalityRow[1]=="45"):
                categoryType=searchbyid(CausalityRow[3],codecolumn=0,database=card_categories,column=1)[0]

                card_unique_info_id=searchbyid(code=CausalityRow[4],codecolumn=2,database=card_unique_info_set_relations,column=1)
                possible_names=[]
                for id in card_unique_info_id:
                    name=searchbycolumn(code=id,database=cards,column=3)
                    for unit in name:
                        if(unit[1] not in possible_names):
                            if(qualifyEncounterable(unit)):
                                possible_names.append(unit[1])
                possible_names=list(set(possible_names))
                likelyName=longestCommonSubstring(possible_names) 

                if(CausalityRow[2]=="0"):
                    output["Button"]["Name"]=("Is there a ")
                    output["Button"]["Name"]+=(categoryType)
                    output["Button"]["Name"]+=(" Category ally whose name includes ")
                    output["Button"]["Name"]+=likelyName
                    output["Button"]["Name"]+=(" on the team?")

                    output["Paragraph Title"]="When there is a " + categoryType + " Category ally whose name includes " + likelyName + " on the team"
                elif(CausalityRow[2]=="1"):
                    output["Button"]["Name"]=("Is there a ")
                    output["Button"]["Name"]+=(categoryType)
                    output["Button"]["Name"]+=(" Category enemy whose name includes ")
                    output["Button"]["Name"]+=likelyName
                    output["Button"]["Name"]+=("?")

                    output["Paragraph Title"]="When there is a " + categoryType + " Category enemy whose name includes " + likelyName
                elif(CausalityRow[2]=="2"):
                    output["Button"]["Name"]=("Is there a ")
                    output["Button"]["Name"]+=(categoryType)
                    output["Button"]["Name"]+=(" Category ally whose name includes ")
                    output["Button"]["Name"]+=likelyName
                    output["Button"]["Name"]+=(" attacking on this turn?")

                    output["Paragraph Title"]="When there is a " + categoryType + " Category ally whose name includes " + likelyName + " attacking on this turn"
                else:
                    output+=("UNKNOWN NAME TYPE")
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown name type")

            elif(CausalityRow[1]=="46"):
                output["Button"]["Name"]=("Is there "+CausalityRow[4] + " or more ")
                output["Slider"]["Name"]=("How many ")
                output["Paragraph Title"]="When there are " + CausalityRow[4] + " or more "
                

                classType=extractClassType(CausalityRow[3])
                if(classType[0]!=[]):
                    output["Button"]["Name"]+=classType[0][0]
                    output["Slider"]["Name"]+=classType[0][0]
                    output["Paragraph Title"]+=classType[0][0]
                    output["Slider"]["Name"]+=" class "
                    output["Button"]["Name"]+=" class "
                    output["Paragraph Title"]+=" class "


                if(classType[1]!=[]):
                    for Type in classType[1]:
                        output["Button"]["Name"]+=(Type)
                        output["Slider"]["Name"]+=(Type)
                        output["Paragraph Title"]+=(Type)
                        output["Button"]["Name"]+=(" or ")
                        output["Slider"]["Name"]+=(" or ")
                        output["Paragraph Title"]+=(" or ")
                    output["Button"]["Name"]=output["Button"]["Name"][:-3]
                    output["Slider"]["Name"]=output["Slider"]["Name"][:-3]
                    output["Paragraph Title"]=output["Paragraph Title"][:-3]
                    output["Button"]["Name"]+=(" type ")
                    output["Slider"]["Name"]+=(" type ")
                    output["Paragraph Title"]+=(" type ")

                if(CausalityRow[2]=="0"):
                    output["Button"]["Name"]+=("allies on the team?")
                    output["Slider"]["Name"]+=("allies on the team?")
                    output["Paragraph Title"]+=("allies on the team")
                    output["Slider"]["Max"]=7
                elif(CausalityRow[2]=="1"):
                    output["Button"]["Name"]+=("enemies?")
                    output["Slider"]["Name"]+=("enemies?")
                    output["Paragraph Title"]+=("enemies")
                    output["Slider"]["Max"]=7
                elif(CausalityRow[2]=="2"):
                    output["Button"]["Name"]+=("allies attacking on this turn?")
                    output["Slider"]["Name"]+=("allies attacking on this turn?")
                    output["Paragraph Title"]+=("allies attacking on this turn")
                    output["Slider"]["Max"]=3
                else:
                    print("UNKNOWN target TYPE")
                    print(CausalityRow)
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown target type")
                output["Slider"]["Min"]=0
                output["Slider"]["Logic"]=">="
                output["Slider"]["Logic"]+=CausalityRow[4]
                


            elif(CausalityRow[1]=="47"):
                output["Button"]["Name"]=("Has this character's Revival Skill been activated?")
                output["Paragraph Title"]=("After the character's Revival Skill is activated")
            elif(CausalityRow[1]=="48"):
                #WIP CausalityRow[2] is the type of super attack
                if(CausalityRow[2]=="1"):
                    output["Button"]["Name"]=("Has the enemy been hit by the characters super attack?")
                    output["Paragraph Title"]=("When the enemy has been hit by the characters super attack?")
                elif(CausalityRow[2]=="2"):
                    output["Button"]["Name"]=("Has the enemy been hit by the characters super attack?")
                    output["Paragraph Title"]=("When the enemy has been hit by the characters super attack?")
                elif(CausalityRow[2]=="4"):
                    output["Button"]["Name"]=("Has the enemy been hit by the characters ultra super attack?")
                    output["Paragraph Title"]=("When the enemy has been hit by the characters ultra super attack?")
                else:
                    output["Button"]["Name"]="UNKNOWN ATTACK TYPE"
                    output["Paragraph Title"]="UNKNOWN ATTACK TYPE"
                    if(DEVEXCEPTIONS==True):
                        print(CausalityRow)
                        raise Exception("Unknown super attack type")
            elif(CausalityRow[1]=="49"):
                if(CausalityRow[2]=="1"):
                    output["Button"]["Name"]=("Has this character been hit by a ki blast super attack?")
                    output["Paragraph Title"]=("When this character has been hit by a ki blast super attack?")
                elif(CausalityRow[2]=="2"):
                    output["Button"]["Name"]=("Has this character been hit by an unarmed super attack?")
                    output["Paragraph Title"]=("When this character has been hit by an unarmed super attack?")
                elif(CausalityRow[2]=="4"):
                    output["Button"]["Name"]=("Has this character been hit by a physical super attack?")
                    output["Paragraph Title"]=("When this character has been hit by a physical super attack?")
                else:
                    output+=("UNKNOWN SUPER ATTACK TYPE")
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown super attack type")
            elif(CausalityRow[1]=="51"):
                output["Button"]["Name"]=("Is it within the first ")
                output["Button"]["Name"]+=CausalityRow[2]
                output["Button"]["Name"]+=(" turn(s) from the character's entry turn?")
                output["Slider"]["Name"]="How many turns is it since entry turn?"
                output["Slider"]["Logic"]="<="
                output["Slider"]["Logic"]+=CausalityRow[2]
                output["Slider"]["Min"]=0
                output["Slider"]["Max"]=int(CausalityRow[2])+1
                output["Paragraph Title"]="For "+ str(CausalityRow[2]) + " turns from the chraracter's entry turn"
            elif(CausalityRow[1]=="52"):
                if(CausalityRow[2]=="1" or CausalityRow[2]=="2"):
                    output["Button"]["Name"]=("Is the charge count less than ")
                    output["Button"]["Name"]+=CausalityRow[3]

                    output["Slider"]["Name"]="What is the charge count at?"
                    output["Slider"]["Logic"]="<="
                    output["Slider"]["Logic"]+=str(int(CausalityRow[3])-1)
                    output["Slider"]["Min"]=0

                    output["Paragraph Title"]="When the charge count is " + CausalityRow[3] + "or less"
                elif(CausalityRow[2]=="4"):
                    output["Button"]["Name"]=("Is the charge count greater than or equal to ")
                    output["Button"]["Name"]+=CausalityRow[3]

                    output["Slider"]["Name"]="What is the charge count at?"
                    output["Slider"]["Logic"]=">="
                    output["Slider"]["Logic"]+=CausalityRow[3]
                    output["Slider"]["Min"]=int(CausalityRow[3])

                    output["Paragraph Title"]="When the charge count is " + CausalityRow[3] + "or more"
                else:
                    output["Button"]["Name"]="UNKNOWN CHARGE TYP£"
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown charge type")


            elif(CausalityRow[1]=="53"):
                output["Button"]["Name"]=("Has this characters finish effect been activated?")
                output["Paragraph Title"]="When this characters finish effect has been activated"
            elif(CausalityRow[1]=="54"):
                output["Button"]["Name"]=("Has this character or an ally's revival skill been activated?")
                output["Paragraph Title"]="After the character's or an ally's Revival Skill is activated"
            elif(CausalityRow[1]=="55"):
                output["Button"]["Name"]=("Is it on or after the first ")
                output["Button"]["Name"]+=str(int(CausalityRow[2])+1)
                output["Button"]["Name"]+=(" turns from this characters entry turn?")

                output["Slider"]["Name"]="How many turns is it since entry turn?"
                output["Slider"]["Logic"]=">="
                output["Slider"]["Logic"]+=str(int(CausalityRow[2])+1)
                output["Slider"]["Min"]=0
                output["Slider"]["Max"]=int(CausalityRow[2])+1
                output["Paragraph Title"]="Starting from the "+str(int(CausalityRow[2])+1)+" turn from the character's entry turn"
            elif(CausalityRow[1]=="56"):
                output["Button"]["Name"]=("Has this character been hit by a normal attack?")
                output["Paragraph Title"]="When this character has been hit by a normal attack"
            elif(CausalityRow[1]=="57"):
                output["Button"]["Name"]=("Is the Domain ")
                output["Paragraph Title"]="When the Domain"
                domain=searchbyid(code=CausalityRow[2],codecolumn=1,database=dokkan_fields,column=2)
                if(domain!=[]):
                    output["Button"]["Name"]+=domain[0]
                    output["Paragraph Title"]+=domain[0]
                else:
                    output["Button"]["Name"]+=searchbyid(code=CausalityRow[2],codecolumn=1,database=dokkan_fields,column=2)[0]
                    output["Paragraph Title"]+=searchbyid(code=CausalityRow[2],codecolumn=1,database=dokkan_fields,column=2)[0]

                output["Button"]["Name"]+=(" active?")
                output["Paragraph Title"]+=(" active?")
            elif(CausalityRow[1]=="58"):
                output["Button"]["Name"]=("Is no domain active?")
                output["Paragraph Title"]="When no domain is active"
            elif(CausalityRow[1]=="59"):
                if(CausalityRow[2]=="1"):
                    output["Button"]["Name"]=("Is this character super class?")
                    output["Paragraph Title"]="When this character is super class"
                elif(CausalityRow[2]=="2"):
                    output["Button"]["Name"]=("Is this character extreme class?")
                    output["Paragraph Title"]="When this character is extreme class"
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
                output["Button"]["Name"]=("Has this character been hit on this turn?")
                output["Paragraph Title"]="When this character has been hit on this turn"
            elif(CausalityRow[1]=="64"):
                if(CausalityRow[2]=="2"):
                    output["Button"]["Name"]="Have less than or equal to "
                    output["Button"]["Name"]+=CausalityRow[3]
                    output["Button"]["Name"]+=" dragon ball orbs been obtained?"

                    output["Slider"]["Name"]="How many dragon ball orbs have been obtained?"
                    output["Slider"]["Logic"]="<="
                    output["Slider"]["Logic"]+=CausalityRow[3]
                    output["Slider"]["Min"]=0
                    output["Slider"]["Max"]=7

                    output["Paragraph Title"]="When " + CausalityRow[3] + "or less dragon ball orbs have been obtained"
                elif(CausalityRow[2]=="5"):
                    output["Button"]["Name"]="Have more than "
                    output["Button"]["Name"]+=CausalityRow[3]
                    output["Button"]["Name"]+=" dragon ball orbs been obtained?"

                    output["Slider"]["Name"]="How many dragon ball orbs have been obtained?"
                    output["Slider"]["Logic"]=">"
                    output["Slider"]["Logic"]+=CausalityRow[3]
                    output["Slider"]["Min"]=0
                    output["Slider"]["Max"]=7

                    output["Paragraph Title"]="When " + CausalityRow[3] + "or more dragon ball orbs have been obtained"
                else:
                    output["Button"]["Name"]="UNKNOWN CAUSALITY CONDITION"
                    if(DEVEXCEPTIONS==True):
                        raise Exception("Unknown causality condition")
            elif(CausalityRow[1]=="65"):
                output["Button"]["Name"]=("Has this character entered giant form?")
                output["Paragraph Title"]="When this character has entered giant form"
            elif(CausalityRow[1]=="66"):
                output["Button"]["Name"]=("Has this character's reversible exchange not yet been performed?")
                output["Paragraph Title"]="When this character's reversible exchange has not yet been performed"


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
    output=[]
    binaryId=bin(int(Statusid))[2:]
    binaryId=binaryId.zfill(11)
    if(binaryId[6]=="1"):
        output.append('{passiveImg:atk_down}')
    if(binaryId[5]=="1"):
        output.append('{passiveImg:def_down}')
    if(binaryId[2]=="1"):
        output.append("{passiveImg:stun}")
    if(binaryId[0]=="1"):
        output.append("{passiveImg:astute}")
    
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
    for passiveskillpiece in passive_skills:
        if passiveskillpiece[12]==card[0]:
            #is a transformation
            for passiverelation in passive_skill_set_relations:#
                if passiverelation[2]==passiveskillpiece[0]:
                    #passiveset found
                    for unit in cards:
                        if unit[21][0:-2]==passiverelation[1]:
                            return(unit)
    
def activeSkillTransformationReverseUnit(card,printing=True):
    for possibleactive in active_skills:
        if(possibleactive[6]==card[0]):
            #unit comes from an active skill
            for possibleactivelink in card_active_skills:
                if possibleactivelink[2]==possibleactive[1]:
                    #link found
                    for unit in cards:
                        if unit[0]==possibleactivelink[1]:
                            return(unit)

def activeSkillTransformationUnit(card,printing=True):
    for possibleactivelink in card_active_skills:
        if possibleactivelink[1]==card[0]:
            #they have an active
            for possibleactive in active_skills:
                if possibleactivelink[2]==possibleactive[1]:
                    
                    #has a transforming one, defined in possibleactive
                    for unit in cards:
                        if unit[0]==possibleactive[6]:
                            return(unit)

def dokkanAwakenUnit(card,printing=False):
    possibleAwakening=searchbycolumn(code=card[0],database=card_awakening_routes,column=2)
    possibleDokkanAwakening=searchbycolumn(code="CardAwakeningRoute::Dokkan",database=possibleAwakening, column=1)
    if(possibleDokkanAwakening==[]):
        return(None)
    else:
        return(possibleDokkanAwakening[0][3])


def dokkanreverseunit(card,printing=False):
    for awakenable_unit in card_awakening_routes:
        if awakenable_unit[1]=="CardAwakeningRoute::Dokkan":
            if(card[0])==(awakenable_unit[3]):
                for unit in cards:
                    if unit[0]==awakenable_unit[2]:
                        return(unit)
    return(None)

def qualifyAsDFETUR(card,printing=True):
    if qualifyEncounterable(card) and card[4]=="58" and ((card[29]=="" and card[0][0]=="1")==False):
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
    if qualifyOwnable(card) and (getrarity(card)=="lr"):
        return(True)
    else:
        return(False)
    
def qualifyEZA(card,printing=True):
    directory="data/"
    if qualifyOwnable(card) and (checkEza(card)):
        return(True)
    else:
        return(False)

def qualifySEZA(card,printing=True):
    directory="data/"
    if qualifyOwnable(card) and (checkSeza(card)):
        return(True)
    else:
        return(False)



def qualifyOwnable(card):
    possibleAwakening=searchbycolumn(code=card[0],database=card_awakening_routes,column=2)
    if(not (card[5] in ["5","4"] and card[0][-1]=="0") and
    #card is not awakenable
    searchbycolumn(code="CardAwakeningRoute::Dokkan",database=possibleAwakening, column=1) == [] and
    searchbycolumn(code="CardAwakeningRoute::Zet",database=possibleAwakening, column=1) == [] and
    #card id starts with 1 or 2
    (card[0][0] in ["1","2"] and len(card[0])==7) and
    #card is not "is_selling_only"
    card[46] == "0" and
    #card is either released or set to release within 2 months
    (dateTimeToTimestamp(card[53]) < dateTimeToTimestamp(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + 60*60*24*60) and
    #card max hp is greater than 1
    int(card[7])> 1 and
    #card is trainable
    card[0][:-1] not in [x[1][:-1] for x in card_training_skill_lvs]
    #card stats are not alll 150 min, 500 max
    and not (card[6]=="150" and card[7]=="500" and card[8]=="150" and card[9]=="500" and card[10]=="150" and card[11]=="500")
    ):
        return(True)
    else:
        return(False)

def qualifyEncounterableAsOwnable(card):
    possibleAwakening=searchbycolumn(code=card[0],database=card_awakening_routes,column=2)
    if ((card[0][0] in ["1","2"]) and
    #card is not awakenable
    searchbycolumn(code="CardAwakeningRoute::Dokkan",database=possibleAwakening, column=1) == [] and
    searchbycolumn(code="CardAwakeningRoute::Zet",database=possibleAwakening, column=1) == [] and
    #card is either released or set to release within 2 months
    (dateTimeToTimestamp(card[53]) < dateTimeToTimestamp(datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + 60*60*24*60)):
        return(True)
    else:
        return(False)



def qualifyEncounterable(card):
    if(not (card[5] in ["5","4"] and card[0][-1]=="0") and
    #card id starts with 1,2 or 4
    (card[0][0] in ["1","2","4"] and len(card[0])==7) and
    #card is not "is_selling_only"
    card[46] == "0" and
    #card max hp is greater than 1
    int(card[7])> 1 and
    #card is trainable
    card[0][:-1] not in [x[1][:-1] for x in card_training_skill_lvs]
    #card stats are not alll 150 min, 500 max
    and not (card[6]=="150" and card[7]=="500" and card[8]=="150" and card[9]=="500" and card[10]=="150" and card[11]=="500")
    ):
        return(True)
    else:
        return(False)

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
        kiRequired=int(unitDictionary["Super Attack"][super]["superMinKi"])
        if(kiRequired<lowestKiRequired):
            lowestKiRequired=kiRequired
            lowestConditionSuperID=super
    return(lowestConditionSuperID)


        

        

#def createEZAWallpapers(cards, directory,printing=True):
#    if(printing): print("Creating EZA wallpapers")
#    acquiredlist = os.listdir(r'./assets/EZA wallpapers')
#    leader_skills=storedatabase(directory,"leader_skills.csv")
#    optimal_awakening_growths=storedatabase(directory,"optimal_awakening_growths.csv")
#    total=0
#    for card in cards:
#        if (card[53]!="2030-12-31 23:59:59") and (card[0][0]!="9") and (card[0][-1]=="0") and (card[22]!="") and ((("final_"+card[0]+".png") not in acquiredlist)) and (checkEza(card)):
#            unitid=card[0]
#            if unitid[-1]=="1":
#                unitid=str(int(unitid)-1)
#            mainunit=card
#
#        #background
#            cframeurl=("../frontend/dbManagement/assets/misc/cha_base_0")
#        #element
#            cframeurl+=(mainunit[12][-1])
#            cframeurl+=("_0")
#        #rarity
#            cframeurl+=(mainunit[5])
#            cframeurl+=(".png")


#            cframe = Image.open(cframeurl).convert("RA")
#            cframe=cframe.resize((200,200))

        #character icon
#            ciconurl=("../frontend/dbManagement/assets/thumb/")
#            if card[48]=="" or card[48]=="0.0":
#                ciconurl+=unitid
#            else:
#                ciconurl+=str(int(float(card[48])))
#            ciconurl+=(".png")
#            cicon = Image.open(ciconurl).convert("RA")
#            cicon.resize((250,250))


        #rarity
#            crarityurl=("../frontend/dbManagement/assets/misc/cha_rare_")
#            crarityurl+=(getrarity(mainunit))
#            crarityurl+=(".png")
#            crarity = Image.open(crarityurl).convert("RA")
#            if getrarity(mainunit)=="ssr":
#                crarity=crarity.resize((120,72))
#            else:    
#                crarity=crarity.resize((160,96))

        #element
#            celementurl=("../frontend/dbManagement/assets/misc/cha_type_icon_")
#            if len(mainunit[12])==1:
#                celementurl+=("0")
#            celementurl+=(mainunit[12])
#            celementurl+=(".png")
#            celement = Image.open(celementurl).convert("RA")
#            celement=celement.resize((90,90))
#            if mainunit[12] in ("20","10"):
#                if(printing): print("AGL ",end="")
#            elif mainunit[12] in ("21","11"):
#                if(printing): print("TEQ ",end="")
#            elif mainunit[12] in ("22","12"):
#                if(printing): print("INT ",end="")
#            elif mainunit[12] in ("23","13"):
#                if(printing): print("STR ",end="")
#            elif mainunit[12] in ("24","14"):
#                if(printing): print("PHY ",end="")

#            (width,height)=(cicon.width+10,cicon.height+10)
#            cfinal=Image.new("RA",(width,height))
#            cfinal.paste(cframe, (25,35), cframe)
#            cfinal.paste(cicon, (0,1), cicon)
#            if getrarity(mainunit)=="n":
#                cfinal.paste(crarity, (-37,160),crarity)
#                if(printing): print("N ",end="")
#            elif getrarity(mainunit)=="r":
#                cfinal.paste(crarity, (-42,160), crarity)
#                if(printing): print("R ",end="")
#            elif getrarity(mainunit)=="sr":
#                cfinal.paste(crarity, (-25,158), crarity)
#                if(printing): print("SR ",end="")
#            elif getrarity(mainunit)=="ssr":
#                cfinal.paste(crarity, (-5,171), crarity)
#                if(printing): print("SSR ",end="")
#            elif getrarity(mainunit)=="ur":
#                cfinal.paste(crarity, (-25,160), crarity)
#                if(printing): print("UR ",end="")
#            elif getrarity(mainunit)=="lr" or True:
#                cfinal.paste(crarity, (-25,155),crarity)
#                if(printing): print("LR ",end="")
#            cfinal.paste(celement, (170,5),celement)
            
#            if(printing): print(mainunit[1])
#            wallpapername=("../frontend/dbManagement/assets/EZA wallpapers/final_")
#            wallpapername+=(unitid)
#            wallpapername+=(".png")
#            cfinal.save(wallpapername)
#            total+=1
#            if total%100==0:
#                if(printing): print(total)
#            #print("Created final asset for",total,getfullname(card,leader_skills))
#    if(printing): print("All EZA assets created")

def maxAppearancesInForm(unitPassive,DEVEXCEPTIONS=False):
    maxAppearances=50
    for passiveLine in unitPassive.values():
        if("Transformation" in passiveLine):
            if("First Turn To Activate" in passiveLine and "Condition" not in passiveLine):
                maxAppearances=appearancesBeforeCertainTurn(passiveLine["First Turn To Activate"]-1)[1]
            elif(passiveLine["Transformation"]["Min Turns"]!=None):
                pass
            elif("Condition" in passiveLine):
                pass
            else:
                print("UNKNOWN TRANSFORMATION SETUP",passiveLine)
                if(DEVEXCEPTIONS): 
                    raise Exception("UNKNOWN TRANSFORMATION SETUP")
        elif("Standby" in passiveLine):
            if("Change form" in passiveLine["Standby"]):
                if("First Turn To Activate" in passiveLine and "Condition" not in passiveLine):
                    maxAppearances=appearancesBeforeCertainTurn(passiveLine["First Turn To Activate"]-1)[1]
                elif("Condition" in passiveLine):
                    if("&&" not in passiveLine["Condition"]["Logic"]):
                        for causality in passiveLine["Condition"]["Causalities"]:
                            if(passiveLine["Condition"]["Causalities"][causality]["Button"]["Name"][0:28]=="Is it on or after the first " and passiveLine["Condition"]["Causalities"][causality]["Button"]["Name"][-52:]==" turns from this characters entry turn on this turn?"):
                                maxAppearances=appearancesBeforeCertainTurn(int(passiveLine["Condition"]["Causalities"][causality]["Button"]["Name"][28:-52]))[1]


                else:
                    print("UNKNOWN CHANGE FORM SETUP",passiveLine)
                    if(DEVEXCEPTIONS): 
                        raise Exception("UNKNOWN CHANGE FORM SETUP")

    return(maxAppearances)



def appearancesBeforeCertainTurn(turn):
    if(type(turn)!=int):
        turn=int(turn)
    min=math.floor(turn/3)
    max=math.ceil(turn/2)
    return(min,max)


def articulateAllyType(target):
    if(target["Target"].lower().startswith("allies")):
        output="All "
        if("Class" in target):
            output+=target["Class"]
            output+=" class "
        if("Type" in target):
            for Typing in target["Type"]:
                output+=Typing
                output+=" and "
            output=output[:-4]

        if("Category" in target):
            for Category in target["Category"]["Included"]:
                output+='"' + Category + '"'
                output+=" and "
            output=output[:-5]
            output+=" category "

        output+=" "+target["Target"]+" "


        if("Name" in target):
            output+=" whose name includes "
            for Name in target["Name"]["Included"]:
                output+=Name
                output+=" or "
            output=output[:-4]
        return(output.replace("  "," "))
    

def passiveBriefEffectDescription(parsedLine,DEVEXCEPTIONS=False):
    output=""
    TARGET_WORDING=False
    BASIC_STAT_BUFFS=True
    BASIC_TIMING_WORDING=True


    #Target wording
    if(TARGET_WORDING):
        if(parsedLine["Target"]["Target"]=="Self"):
            pass
        elif(parsedLine["Target"]["Target"]=="Enemies"):
            output+="All enemies "
        elif(parsedLine["Target"]["Target"]=="Enemy"):
            output+="Enemy "
        elif(parsedLine["Target"]["Target"]=="allies" or "allies(self excluded)"):
            output+=articulateAllyType(parsedLine["Target"])



            
        else:
            print("Unknown target",parsedLine["Target"])
            if(DEVEXCEPTIONS):
                raise Exception("Unknown target",parsedLine["Target"])


    #Basic stat buffs
    if(BASIC_STAT_BUFFS):
        if("Ki" in parsedLine):
            output+="Ki +"
            output+=str(parsedLine["Ki"])
        if("ATK" in parsedLine and "DEF" in parsedLine):
            if(parsedLine["ATK"]==parsedLine["DEF"]):
                output+="ATK and DEF "
                output+=str(parsedLine["ATK"])
                if(parsedLine["Buff"]["Type"]=="Percentage"):
                    output+="%"
                if(parsedLine["Buff"]["+ or -"]=="+"):
                    output+="{passiveImg:up_g}"
                elif(parsedLine["Buff"]["+ or -"]=="-"):
                    output+="{passiveImg:down_r}"
            else:
                output+="ATK "
                output+=str(parsedLine["ATK"])
                if(parsedLine["Buff"]["Type"]=="Percentage"):
                    output+="%"
                output+=" and "
                output+="DEF "
                output+=str(parsedLine["DEF"])
                if(parsedLine["Buff"]["Type"]=="Percentage"):
                    output+="%"
                if(parsedLine["Buff"]["+ or -"]=="+"):
                    output+="{passiveImg:up_g}"
                elif(parsedLine["Buff"]["+ or -"]=="-"):
                    output+="{passiveImg:down_r}"
        if("ATK" in parsedLine and "DEF" not in parsedLine):
            output+="ATK "
            output+=str(parsedLine["ATK"])
            if(parsedLine["Buff"]["Type"]=="Percentage"):
                output+="%"
            if(parsedLine["Buff"]["+ or -"]=="+"):
                output+="{passiveImg:up_g}"
            elif(parsedLine["Buff"]["+ or -"]=="-"):
                output+="{passiveImg:down_r}"
        if("DEF" in parsedLine and "ATK" not in parsedLine):
            output+="DEF "
            output+=str(parsedLine["DEF"])
            if(parsedLine["Buff"]["Type"]=="Percentage"):
                output+="%"
            if(parsedLine["Buff"]["+ or -"]=="+"):
                output+="{passiveImg:up_g}"
            elif(parsedLine["Buff"]["+ or -"]=="-"):
                output+="{passiveImg:down_r}"
        if("Heals" in parsedLine):
            output+="Heals "
            output+=str(parsedLine["Buff"]["+ or -"])
            output+=str(parsedLine["Heals"])
            if(parsedLine["Buff"]["Type"]=="Percentage"):
                output+="%"
        if("Ki Change" in parsedLine):
            if(parsedLine["Ki Change"]["Style"]=="Randomly"):
                output+="Randomly changes Ki Spheres of a certain Type"
                if("AGL" not in parsedLine["Ki Change"]["From"]):
                    output+="(AGL excluded)"
                elif("TEQ" not in parsedLine["Ki Change"]["From"]):
                    output+="(TEQ excluded)"
                elif("INT" not in parsedLine["Ki Change"]["From"]):
                    output+="(INT excluded)"
                elif("STR" not in parsedLine["Ki Change"]["From"]):
                    output+="(STR excluded)"
                elif("PHY" not in parsedLine["Ki Change"]["From"]):
                    output+="(PHY excluded)"
                output+=" to "
                output+=parsedLine["Ki Change"]["To"][0]
                output+=" Ki Spheres"
            elif(parsedLine["Ki Change"]["Style"]=="All"):
                output+="Changes all Ki Spheres to "
                output+=parsedLine["Ki Change"]["To"][0]
                output+=" Ki Spheres"
            elif(parsedLine["Ki Change"]["Style"]=="Single"):
                output+="Changes "
                output+=parsedLine["Ki Change"]["From"]
                output+=" Ki Spheres to "
                output+=parsedLine["Ki Change"]["To"]
                output+=" Ki Spheres"
        if("Status" in parsedLine):
            for statusEffect in parsedLine["Status"]:
                output+=statusEffect
                output+=" and "
            output=output[:-5]            
        if("DR" in parsedLine):
            output+="Damage Reduction Rate "
            output+=str(parsedLine["DR"])
            if(parsedLine["Buff"]["Type"]=="Percentage"):
                output+="%"
            if(parsedLine["Buff"]["+ or -"]=="+"):
                output+="{passiveImg:up_g}"
            elif(parsedLine["Buff"]["+ or -"]=="-"):
                output+="{passiveImg:down_r}"
        if("Guard" in parsedLine):
            output+="Guards all attacks "
        if("Transformation" in parsedLine):
            output+="Transforms into "
            output+=parsedLine["Transformation"]["Unit"]
            if(parsedLine["Transformation"]["Giant/Rage"]==True):
                output+=" as a giant form"
            if(parsedLine["Transformation"]["Min Turns"]!=None):
                output+=" for "
                output+=str(parsedLine["Transformation"]["Min Turns"])
                output+=" to "
                output+=str(parsedLine["Transformation"]["Max Turns"])
                output+=" turns"
        if("Crit Chance" in parsedLine):
            if(parsedLine["Crit Chance"]==100):
                output+="Performs a Critical Hit"
            else:
                output+="Chance of performing a critical hit +"
                output+=str(parsedLine["Crit Chance"])
                output+="%"
                if(parsedLine["Buff"]["+ or -"]=="+"):
                    output+="{passiveImg:up_g}"
                elif(parsedLine["Buff"]["+ or -"]=="-"):
                    output+="{passiveImg:down_r}"
            
        if("Additional Attack" in parsedLine):
            if(parsedLine["Additional Attack"]["Chance of another additional"])=="0":
                if(parsedLine["Additional Attack"]["Chance of super"]==100):
                    output+="Performs an additional super attack"
                elif(parsedLine["Additional Attack"]["Chance of super"]==0):
                    output+="Performs an additional attack"
                else:
                    output+="Performs an additional attack with a "
                    output+=str(parsedLine["Additional Attack"]["Chance of super"])
                    output+="% chance of becoming a super attack"
            else:
                if(parsedLine["Additional Attack"]["Chance of another additional"]==100):
                    if(parsedLine["Additional Attack"]["Chance of super"]==100):
                        output+="Performs an additional super attack with a "
                        output+=str(parsedLine["Additional Attack"]["Chance of another additional"])
                        output+="% chance of another additional super attack"
                elif(parsedLine["Additional Attack"]["Chance of super"]==0):
                    output+="Performs an additional attack with a "
                    output+=str(parsedLine["Additional Attack"]["Chance of another additional"])
                    output+="% chance of another additional attack"
                else:
                    output+="Performs an additional attack with a "
                    output+=str(parsedLine["Additional Attack"]["Chance of another additional"])
                    output+="% chance of another additional attack each with a "
                    output+=str(parsedLine["Additional Attack"]["Chance of super"])
                    output+="% chance of becoming a super attack"
        if("Dodge Chance" in parsedLine):
            if(parsedLine["Dodge Chance"]==100):
                output+="Evades enemy attacks"
            else:
                output+="Chance of evading enemy attacks +"
                output+=str(parsedLine["Dodge Chance"])
                output+="%"
        if("Disable Other Line" in parsedLine):
            output+="Disables a different passive line:"
            output+=parsedLine["Disable Other Line"]["Line"]
        if("Effective Against All" in parsedLine):
            output+="Attacks effective against all Types"
        if("Counter" in parsedLine):
            if("DR from normals" in parsedLine["Counter"]):
                output+="Damage received from normal attacks -"
                output+=str(parsedLine["Counter"]["DR from normals"])
                output+="% and "
                output+="counter attacks with a "
            else:
                output+="Counter attacks with a "
            output+=parsedLine["Counter"]["Multiplier"]
            output+="% multiplier"
        if("Forsee Super Attack" in parsedLine):
            output+="Forsee enemy super attack"
        if("Nullification" in parsedLine):
            output+="Nullifies enemy attack"
            if(parsedLine["Nullification"]["Absorbed"]!=0):
                output+=" and absorbs "
                output+=str(parsedLine["Nullification"]["Absorbed"])
                output+="% of damage"
        if("Guaranteed Hit" in parsedLine):
            output+="Attacks guaranteed to hit"
        if("Revive" in parsedLine):
            output+="Revives with "
            output+=str(parsedLine["Revive"]["HP recovered"])
            output+="% HP"
        if("Domain" in parsedLine):
            output+="Opens domain number "
            output+=parsedLine["Domain"]
        if("Standby" in parsedLine):
            if("Change form" in parsedLine["Standby"]):
                output+="Reverts standby to "
                output+=parsedLine["Standby"]["Change form"]["Unit"]


    if(len(output)>0):
        if(output[-1]!=" "):
            output+=" "


    if("Building Stat" in parsedLine):
        if("ki sphere" in parsedLine["Building Stat"]["Cause"]["Cause"].lower()):
            output+="per "
            if("AGL" in parsedLine["Building Stat"]["Cause"]["Type"] and "INT" in parsedLine["Building Stat"]["Cause"]["Type"] and "PHY" in parsedLine["Building Stat"]["Cause"]["Type"] and "TEQ" in parsedLine["Building Stat"]["Cause"]["Type"] and "STR" in parsedLine["Building Stat"]["Cause"]["Type"]):
                if("Rainbow" in parsedLine["Building Stat"]["Cause"]["Type"]):
                    output+=" Ki Sphere obtained"
                else:
                    output+=" Type Ki Sphere obtained"
            else:
                for kiSphere in parsedLine["Building Stat"]["Cause"]["Type"]:
                    output+=kiSphere
                    output+=" and "
                output=output[:-5]
                output+=" Ki Spheres obtained"
            output +="{currentValue} / "+ str(parsedLine["Building Stat"]["Max"])
        else:
            output+="({currentValue} / "
            output+=str(parsedLine["Building Stat"]["Max"])
            if(parsedLine["Buff"]["Type"]=="Percentage"):
                output+="%"
            output+=") based on '"
            output+=parsedLine["Building Stat"]["Slider"][:-1]
            output+="'"
        

    if(len(output)>0):
        if(output[-1]!=" "):
            output+=" "
    
    if(output==""):
        output="None"

    #Basic timing wording
    if(BASIC_TIMING_WORDING):
        if(parsedLine["Timing"]=="Start of turn"):
            #output+="at the start of turn"
            output+=""
        elif(parsedLine["Timing"]=="Right before attack(SOT stat)" or parsedLine["Timing"]=="Right before attack(MOT stat)"):
            output+=" when attacking"
        elif(parsedLine["Timing"]=="Right after attack"):
            output+="after attacking"
        elif(parsedLine["Timing"]=="End of turn"):
            output+="at the end of turn"
        elif(parsedLine["Timing"]=="Right before being hit"):
            output+="right before being hit"
        elif(parsedLine["Timing"]=="Right after being hit"):
            output+="after being hit"
        elif(parsedLine["Timing"]=="After all ki collected"):
            output+="after all ki collected"
        elif(parsedLine["Timing"]=="When ki spheres collected"):
            output+="after this unit collects ki spheres"
        elif(parsedLine["Timing"]=="When final blow delivered"):
            output+="after the final blow is delivered"
        elif(parsedLine["Timing"]=="Activating standby"):
            output+="when activating standby"
        else:
            print("UNKNOWN EFFECT",parsedLine)
            if(DEVEXCEPTIONS):
                raise Exception("UNKNOWN EFFECT TIMING",parsedLine)
        
    if(parsedLine["Target"]["Target"].lower().startswith("allies")):
            output+=" for all "
            if("Class" in parsedLine["Target"]):
                output+=parsedLine["Target"]["Class"]
                output+=" class "
            if("Type" in parsedLine["Target"]):
                for Typing in parsedLine["Target"]["Type"]:
                    output+=Typing
                    output+=" and "
                output=output[:-4]

            if("Category" in parsedLine["Target"]):
                for Category in parsedLine["Target"]["Category"]["Included"]:
                    output+=Category
                    output+=" and "
                output=output[:-5]
                output+=" category "

            output+=" "+parsedLine["Target"]["Target"]+" "


            if("Name" in parsedLine["Target"]):
                output+=" whose name includes "
                for Name in parsedLine["Target"]["Name"]["Included"]:
                    output+=Name
                    output+=" or "
                output=output[:-4]



    while("  " in output):
        output=output.replace("  "," ")
    return(output)

def conditionVital(causalityKey,otherCausalities,logic):
    #Checks if a condition is vital to the passive skill, meaning it is not just a "nice to have" but rather a "must have"
    newLogic=logic.replace(" "+causalityKey+" "," False ")
    for otherCausality in otherCausalities:
        newLogic=newLogic.replace(" "+otherCausality+" "," True ")
    while newLogic!=" True " and newLogic!=" False ":
        newLogic=newLogic.replace("True || True","True")
        newLogic=newLogic.replace("True || False","True")
        newLogic=newLogic.replace("False || True","True")
        newLogic=newLogic.replace("False || False","False")
        newLogic=newLogic.replace("True && True","True")
        newLogic=newLogic.replace("True && False","False")
        newLogic=newLogic.replace("False && True","False")
        newLogic=newLogic.replace("False && False","False")
        newLogic=newLogic.replace("( True )"," True ")
        newLogic=newLogic.replace("( False )"," False ")
        newLogic=newLogic.replace("  "," ")
    return(newLogic==" False ")

def binaryCombinations(sizeOfList, numberOfTrue):
    """
    Generates all binary combinations of a given size with a specified number of True values.

    Args:
        sizeOfList (int): The total number of elements in each binary list.
        numberOfTrue (int): The number of True values in each combination.

    Returns:
        List[List[bool]]: A list of binary combinations (as lists of bools).
    """
    if numberOfTrue > sizeOfList or numberOfTrue < 0:
        return []

    result = []
    indices = range(sizeOfList)

    for true_indices in combinations(indices, numberOfTrue):
        combo = [False] * sizeOfList
        for i in true_indices:
            combo[i] = True
        result.append(combo)

    return result


def bool_logic_reducer(logic):
    newLogic=logic
    #Reduces the logic to a single True or Falsewhile newLogic!=" True " and newLogic!=" False ":
    while not newLogic in [" True ", " False ", "True", "False"]:
        newLogic=newLogic.replace("True || True","True")
        newLogic=newLogic.replace("True || False","True")
        newLogic=newLogic.replace("False || True","True")
        newLogic=newLogic.replace("False || False","False")
        newLogic=newLogic.replace("True && True","True")
        newLogic=newLogic.replace("True && False","False")
        newLogic=newLogic.replace("False && True","False")
        newLogic=newLogic.replace("False && False","False")
        newLogic=newLogic.replace("( True )"," True ")
        newLogic=newLogic.replace("(True)"," True ")
        newLogic=newLogic.replace("( False )"," False ")
        newLogic=newLogic.replace("(False)"," False ")
        newLogic=newLogic.replace("  "," ")
    return (" "+newLogic.strip()+" ")
    

def minimumVital(otherCausalities,logic):
    #Finds the minimum combination of conditions that must be true for the passive skill to work
    #This is used to find the minimum paragraph title that can be used in a passive skill line
    #It returns the paragraph title of the condition that is not vital to the passive skill
    newLogic=logic
    for i in range(1,len(otherCausalities)+1):
        for causalityCombination in binaryCombinations(len(otherCausalities),i):
            exampleLogic=logic
            for j in range(0,len(otherCausalities)):
                if(causalityCombination[j]):
                    exampleLogic=exampleLogic.replace(" "+otherCausalities[j]+" "," False ")
                else:
                    exampleLogic=exampleLogic.replace(" "+otherCausalities[j]+" "," True ")
            exampleLogic=bool_logic_reducer(exampleLogic)
            if(exampleLogic==" False "):
                returnList=[]
                for j in range(0,len(otherCausalities)):
                    if(causalityCombination[j]):
                        returnList.append(otherCausalities[j])
                return(returnList)
            

            
def articulateMultipleCausalities(causalities,causalityDictionaries,andOr):
    output=""
    for causality in causalities:
        if(output==""):
            output+=causalityDictionaries[causality]["Paragraph Title"]
        else:
            output+=" "+andOr+" "
            output+=causalityDictionaries[causality]["Paragraph Title"].replace("When ","")
    return output.replace("  "," ")


def sortParagraphTitles(passiveskill,DEVEXCEPTIONS=False):
    #WIP rework this to properly divide the passive skills, currently only ones included in a "most popular" can achieve anything
    #Create a conditionFrequencyL list to store every appearance of a paragraph Title in a passive skill line
    conditionFrequency={}
    for lineKey in passiveskill:
        line=passiveskill[lineKey]
        if("Condition" in line):
            lineHasParagraphTitle=False
            for conditionKey in line["Condition"]["Causalities"]:
                if(conditionVital(conditionKey,line["Condition"]["Causalities"],line["Condition"]["Logic"])):
                    lineHasParagraphTitle=True
                    condition=line["Condition"]["Causalities"][conditionKey]
                    if(conditionKey not in conditionFrequency):
                        conditionFrequency[conditionKey]={"Lines":[],"Causalities":[conditionKey]}
                    conditionFrequency[conditionKey]["Lines"].append(lineKey)
            if(not lineHasParagraphTitle):
                smallestParagraphTitle=minimumVital(list(line["Condition"]["Causalities"].keys()),line["Condition"]["Logic"])
                if(smallestParagraphTitle!=None):
                    newCondition=""
                    for conditionKey in smallestParagraphTitle:
                        newCondition+=conditionKey+"||"
                    newCondition=newCondition[:-2]
                    if(newCondition not in conditionFrequency):
                        conditionFrequency[newCondition]={"Lines":[],"Causalities":smallestParagraphTitle}
                    conditionFrequency[newCondition]["Lines"].append(lineKey)
                    
        
    linesRemaining=list(passiveskill.keys())
    for lineKey in linesRemaining.copy():
        if("Condition" not in passiveskill[lineKey]):
            linesRemaining.remove(lineKey)
    linesRemaining=list(set(linesRemaining))
    paragraphPriority=[]
    #until every line has a paragraph
    while(len(linesRemaining)>0):
        #find the condition that appears in the most amount of remaining lines
        mostFrequentConditionKey=list(conditionFrequency.keys())[0]
        for conditionKey in conditionFrequency:
            if(len(conditionFrequency[conditionKey]["Lines"])>len(conditionFrequency[mostFrequentConditionKey]["Lines"])):
                mostFrequentConditionKey=conditionKey

        #put it next in the priority of conditions
        paragraphPriority.append(mostFrequentConditionKey)

        #remove any detail of it left within the process
        for line in linesRemaining.copy():
            if(line in conditionFrequency[mostFrequentConditionKey]["Lines"]):
                linesRemaining.remove(line)
                for conditionKey in conditionFrequency:
                    if(line in conditionFrequency[conditionKey]["Lines"]):
                        while(line in conditionFrequency[conditionKey]["Lines"]):
                            conditionFrequency[conditionKey]["Lines"].remove(line)

    causalityDictionary={}
    for lineKey in passiveskill:
        if("Condition" in passiveskill[lineKey]):
            for causalityKey in passiveskill[lineKey]["Condition"]["Causalities"]:
                causalityDictionary[causalityKey]={}
                causalityDictionary[causalityKey]["Paragraph Title"]=passiveskill[lineKey]["Condition"]["Causalities"][causalityKey]["Paragraph Title"]


    for lineKey in passiveskill:
        line=passiveskill[lineKey]
        line["Line description"]=passiveBriefEffectDescription(line,DEVEXCEPTIONS)
        line["Paragraph Title"]="Basic effect(s)"
        if("Condition" in line):
            lineConditions= []
            for conditionKey in line["Condition"]["Causalities"]:
                lineConditions.append(conditionKey)
            if(line["Paragraph Title"]=="Basic effect(s)"):
                if(lineConditions in [conditionFrequency[x]["Causalities"] for x in paragraphPriority]):
                    priorityIndex=[conditionFrequency[x]["Causalities"] for x in paragraphPriority].index(lineConditions)
                    line["Paragraph Title"]=articulateMultipleCausalities(conditionFrequency[paragraphPriority[priorityIndex]]["Causalities"],causalityDictionary,"or")
                    line_logic=line["CausalityLogic"]
                    for causalityKey in conditionFrequency[paragraphPriority[priorityIndex]]["Causalities"]:
                        line_logic=line_logic.replace(causalityKey,"True")
                    line_logic=logicalCausalityExtractor(line_logic)
                else:
                    line_logic=logicalCausalityExtractor(line["CausalityLogic"])
                line_logic=line_logic.replace("(","").replace(")","").replace("||"," or ").replace("&&"," and ")
                line["Line description"]= passiveBriefEffectDescription(line,DEVEXCEPTIONS)
                for conditionKey in line["Condition"]["Causalities"]:
                    line_logic=line_logic.replace(conditionKey,line["Condition"]["Causalities"][conditionKey]["Paragraph Title"])
                while("  " in line_logic):
                    line_logic=line_logic.replace("  "," ")
                if(line_logic!=" True "):
                    line["Line description"]+=(" "+line_logic)
        elif(line["Length"]!="1" and line["Length"]!="99"):
            line["Line description"]+=" for "
            line["Line description"]+=str(line["Length"])
            line["Line description"]+=" turns"
        if(line["Length"]=="99"):
            line["Line description"]+="{passiveImg:forever}"
        else:
            if("Once Only" in line and line["Once Only"]==True):
                if(line["Length"]=="1"):
                    line["Line description"]+=" for 1 turn "
                line["Line description"]=" {passiveImg:once}" + line["Line description"]
        for disablingLine in passiveskill:
            if("Disable Other Line" in passiveskill[disablingLine] and passiveskill[disablingLine]["Disable Other Line"]["Line"]==lineKey):
                line["Line description"]+=" until "+passiveskill[disablingLine]["Brief effect description"].split(lineKey)[1]
        line["Line description"]=line["Line description"].replace("  "," ").replace("right before being hit until after being hit","while being hit").replace("before being hit until after being hit","while being hit").replace("  "," ")

    #check if ithere is an intro condition
    introParagraphSwap={}
    for lineKey in passiveskill:
        line=passiveskill[lineKey]
        if("Has Animation" in line and line["Has Animation"]==True and "Reversible exchange" not in line):
            introParagraphSwap[line["Paragraph Title"]]="Activates the Entrance Animation "+line["Paragraph Title"].replace("When","when").replace("Basic effect(s)","")

    if(introParagraphSwap!={}):
        for lineKey2 in passiveskill:
            line2=passiveskill[lineKey2]
            for replacement in introParagraphSwap:
                line2["Paragraph Title"]=line2["Paragraph Title"].replace(replacement,introParagraphSwap[replacement])
                        
            

    
def firstListOverlap(listToCompare,listToIndex):
    for entry in listToIndex:
        if(entry in listToCompare):
            return(listToIndex.index(entry))
    return(-1)



def parsePassiveSkill(unit,eza=False,seza=False,DEVEXCEPTIONS=False):
    output={}
    passiveIdList=getPassiveIdList(unit,eza,seza)
    if (passiveIdList!=None):
        for passiveskill in passive_skills[1:]:
            if (passiveskill[0] in passiveIdList):
                parsedLine=(extractPassiveLine(unit,passiveskill,printing=False,DEVEXCEPTIONS=DEVEXCEPTIONS))
                parsedLine=shortenPassiveDictionary(parsedLine)
                output[passiveskill[0]]=parsedLine
                if("Building Stat" in parsedLine):
                    if(parsedLine["Building Stat"]["Cause"]["Cause"]=="Look Elsewhere"):
                        parsedLine=removeLookElseWhere(parsedLine,DEVEXCEPTIONS)
                parsedLine=polishPassiveLine(parsedLine)
                parsedLine["Brief effect description"]=passiveBriefEffectDescription(parsedLine,DEVEXCEPTIONS)
                output[passiveskill[0]]=parsedLine
        passiveskill=sortParagraphTitles(output)
    return(output)

def parsePassiveSkillItemizedDescription(unit,eza=False,seza=False,DEVEXCEPTIONS=False):
    unit_passive_id=getPassiveId(unit,eza,seza,DEVEXCEPTIONS)
    passive_skill_itemized_description=searchbyid(unit_passive_id,0,passive_skill_sets,2)
    if(passive_skill_itemized_description!=None):
        return passive_skill_itemized_description[0]
    else:
        return "" 


def polishPassiveLine(parsedLine):
    output=parsedLine.copy()
    if("Building Stat" in parsedLine):
        output["Type"]="Building Stat"
    elif("Disable Other Line" in parsedLine):
        output["Type"]="Disable Other Line"
    else:
        output["Type"]="Single activator"

    
    if("Condition" in parsedLine):
        #full super or full extreme rotation
        if(len(parsedLine["Condition"]["Causalities"])==5):
            superCondition=0
            extremeCondition=0
            for CausalityKey in parsedLine["Condition"]["Causalities"]:
                if ("Is there 1 or more Extreme class " in parsedLine["Condition"]["Causalities"][CausalityKey]["Button"]["Name"] and
                    "on the team?" in parsedLine["Condition"]["Causalities"][CausalityKey]["Button"]["Name"]):
                    extremeCondition+=1
                elif ("Is there 1 or more Super class " in parsedLine["Condition"]["Causalities"][CausalityKey]["Button"]["Name"] and
                    "on the team?" in parsedLine["Condition"]["Causalities"][CausalityKey]["Button"]["Name"]):
                    superCondition+=1
            if(superCondition==5):
                parsedLine["Condition"]={
                    "Logic": CausalityKey+"00000",
                    "Causalities": {
                        CausalityKey+"00000": {
                            "Button": {"Name": "Does the team include 5 Super Types?" },
                            "Paragraph Title": "When the team includes all five Super Types"
                        }
                    }
                }
                output["CausalityLogic"]='{\"source\": \"'+CausalityKey+"00000"+'\", \"compiled\": '+CausalityKey+"00000"+'}'
            elif(extremeCondition==5):
                output["Condition"]={
                    "Logic": " " + CausalityKey+"00000" + " ",
                    "Causalities": {
                        CausalityKey+"00000": {
                            "Button": {"Name": "Does the team include 5 Extreme Types?" },
                            "Paragraph Title": "When the team includes all five Extreme Types"
                        }
                    }
                }
                output["CausalityLogic"]='{\"source\": \"'+CausalityKey+"00000"+'\", \"compiled\": '+CausalityKey+"00000"+'}'

        #1st, 2nd or 3rd attacker in a turn
        if(len(parsedLine["Condition"]["Causalities"])==2):
            slots=[False,False,False]
            for CausalityKey in parsedLine["Condition"]["Causalities"]:
                if("Button" in parsedLine["Condition"]["Causalities"][CausalityKey]):
                    if(parsedLine["Condition"]["Causalities"][CausalityKey]["Button"]["Name"]=="Is this the 1st attacker in the turn?"):
                        slots[0]=True
                    elif(parsedLine["Condition"]["Causalities"][CausalityKey]["Button"]["Name"]=="Is this the 2nd attacker in the turn?"):
                        slots[1]=True
                    elif(parsedLine["Condition"]["Causalities"][CausalityKey]["Button"]["Name"]=="Is this the 3rd attacker in the turn?"):
                        slots[2]=True
            if(slots!=[False,False,False]):
                buttonText="Is this the "
                paragraphText="As the "
                for i in range(3):
                    if(slots[i]):
                        buttonText+=ordinalise(i+1)+" or "
                        paragraphText+=ordinalise(i+1)+" or "
                buttonText=buttonText[:-4]
                buttonText+=" attacker in a turn"
                paragraphText=paragraphText[:-4]
                paragraphText+=" attacker in a turn"
                output["Condition"]={
                    "Logic": " " + CausalityKey+"00000" + " ",
                    "Causalities": {
                        CausalityKey+"00000": {
                            "Button": {"Name": buttonText },
                            "Paragraph Title": paragraphText
                        }
                    }
                }
                output["CausalityLogic"]='{\"source\": \"'+CausalityKey+"00000"+'\", \"compiled\": '+CausalityKey+"00000"+'}'
        
        #Specific enemy debuffs
        debuffs={"{passiveImg:atk_down}": False, 
                   "{passiveImg:def_down}": False,
                   "{passiveImg:stun}" : False,
                   "{passiveImg:astute}" : False,}
        for CausalityKey in parsedLine["Condition"]["Causalities"]:
            if("Button" in parsedLine["Condition"]["Causalities"][CausalityKey]):
                if(parsedLine["Condition"]["Causalities"][CausalityKey]["Button"]["Name"]=='Is the target enemy in {passiveImg:atk_down} status?'):
                    debuffs["{passiveImg:atk_down}"]=True
                elif(parsedLine["Condition"]["Causalities"][CausalityKey]["Button"]["Name"]=='Is the target enemy in {passiveImg:def_down} status?'):
                    debuffs["{passiveImg:def_down}"]=True
                elif(parsedLine["Condition"]["Causalities"][CausalityKey]["Button"]["Name"]=='Is the target enemy {passiveImg:stun}?'):
                    debuffs["{passiveImg:stun}"]=True
                elif(parsedLine["Condition"]["Causalities"][CausalityKey]["Button"]["Name"]=='Is the target enemy sealed?'):
                    debuffs["{passiveImg:astute}"]=True
        if(True in debuffs.values()):
            if("||" in parsedLine["Condition"]["Logic"]):
                logicAndOr=" or "
            else: 
                logicAndOr=" and "
            buttonText="Is the target enemy is :"
            paragraphText="When the target enemy is in the following status :"
            buttonText+=articulateList([key for key,value in debuffs.items() if value],logicAndOr)
            paragraphText+=articulateList([key for key,value in debuffs.items() if value],logicAndOr)
            output["Condition"]={
                "Logic": " " + CausalityKey+"00000" + " ",
                "Causalities": {
                    CausalityKey+"00000": {
                        "Button": {"Name": buttonText },
                        "Paragraph Title": paragraphText
                    }
                }
            }
            output["CausalityLogic"]='{\"source\": \"'+CausalityKey+"00000"+'\", \"compiled\": '+CausalityKey+"00000"+'}'

        if(parsedLine["Timing"]=="End of turn" and ("ATK" in parsedLine or "DEF" in parsedLine) ):
            for CausalityKey in parsedLine["Condition"]["Causalities"]:
                Causality=parsedLine["Condition"]["Causalities"][CausalityKey]
                if("Button" in Causality):
                    Causality["Button"]["Name"]=Causality["Button"]["Name"][:-1].replace("Is ","Was ").replace("Are there","Was there")+" on the last turn?"
                if("Slider" in Causality):
                    Causality["Slider"]["Name"]=Causality["Slider"]["Name"][:-1].replace("Is ","Was ").replace("Are there","Was there")+" on the last turn?"
        
        elif(stupidCondition(parsedLine)):
            del output["Condition"]
        
        elif(enemySuperCondition(parsedLine)):
            for conditionKey in parsedLine["Condition"]["Causalities"]:
                if(parsedLine["Condition"]["Causalities"][conditionKey]["Button"]["Name"]=="Is a super being performed?"):
                    parsedLine["Condition"]["Causalities"][conditionKey]["Button"]["Name"]="Has this character been hit by a super attack?"
                
        else:
            duration=parsedLine["Length"]
            for CausalityKey in parsedLine["Condition"]["Causalities"]:
                Causality=parsedLine["Condition"]["Causalities"][CausalityKey]
                if("Button" in Causality):
                    if("this turn" not in Causality["Button"]["Name"] and "last turn" not in Causality["Button"]["Name"] and "within the first" not in Causality["Button"]["Name"]):
                        if(duration=="1"):
                            Causality["Button"]["Name"]=Causality["Button"]["Name"][:-1]+" on this turn?"
                        elif(duration!="99"):
                            Causality["Button"]["Name"]=Causality["Button"]["Name"][:-1]+" within the last "+duration+" turns?"
                        elif(("Has ") in Causality["Button"]["Name"] and (" Ki Spheres have been obtained?") in Causality["Button"]["Name"]):
                                Causality["Button"]["Name"]=Causality["Button"]["Name"][:-1]+" in one turn?"
                    
                if("Slider" in Causality):
                    if("this turn" not in Causality["Slider"]["Name"] and "last turn" not in Causality["Slider"]["Name"] and "within the first" not in Causality["Slider"]["Name"]):
                        if(duration=="1"):
                            Causality["Slider"]["Name"]=Causality["Slider"]["Name"][:-1]+" on this turn?"
                        elif(duration!="99"):
                            Causality["Slider"]["Name"]=Causality["Slider"]["Name"][:-1]+" within the last "+duration+" turns?"
                        elif(("How many ") in Causality["Slider"]["Name"] and (" Ki Spheres have been obtained?") in Causality["Slider"]["Name"]):
                                Causality["Slider"]["Name"]="What is the most amount of "+ Causality["Slider"]["Name"][9:-1]+" in one turn?"

    elif("Once Only" in parsedLine and parsedLine["Once Only"]==True):
        output["Condition"]={
            "Logic": " "+parsedLine["Length"]+"000000000000 ",
            "Causalities": {
                parsedLine["Length"]+"000000000000": {
                    "Button": {"Name": "Is it within the first "+parsedLine["Length"]+" turn(s) from the character's entry turn?"},
                    "Paragraph Title": "For "+parsedLine["Length"]+" turn(s) from the character's entry turn"
                }
            }
        }
        output["CausalityLogic"]='{\"source\": \"' + parsedLine["Length"] + '000000000000\", \"compiled\": ' + parsedLine["Length"] + '000000000000}'

    elif(parsedLine["Timing"]=="End of turn"):
        if("Condition" in parsedLine):
            for CausalityKey in parsedLine["Condition"]["Causalities"]:
                Causality=parsedLine["Condition"]["Causalities"][CausalityKey]
                if("Button" in Causality):
                    Causality["Button"]["Name"]=Causality["Button"]["Name"][:-1].replace("Is ","Was ").replace("Are there","Was there")+" on the previous turn?"
                if("Slider" in Causality):
                    Causality["Slider"]["Name"]=Causality["Slider"]["Name"][:-1].replace("Is ","Was ").replace("Are there","Was there")+" on previous turns?"

    if(parsedLine["Length"]=="1" and "Building Stat" in parsedLine):
        if(parsedLine["Building Stat"]["Slider"]=="How many attacks has this character performed in battle?"):
            parsedLine["Building Stat"]["Slider"]="How many attacks has this character performed on this turn?"
        if(parsedLine["Building Stat"]["Slider"]=='How many super attacks has this character performed?'):
            parsedLine["Building Stat"]["Slider"]="How many super attacks has this character performed on this turn?"
        
        if(("How many ") in parsedLine["Building Stat"]["Slider"] and (" Ki Spheres have been obtained?") in parsedLine["Building Stat"]["Slider"]):
            parsedLine["Building Stat"]["Slider"]=parsedLine["Building Stat"]["Slider"].replace(" Ki Spheres have been obtained?"," Ki Spheres have been obtained on this turn?")




    return(output)

def articulateList(listToArticulate,andOr):
    #Takes a list and returns a string with the elements of the list articulated
    if(len(listToArticulate)==0):
        return("")
    elif(len(listToArticulate)==1):
        return(listToArticulate[0])
    elif(len(listToArticulate)>1):
        output=""
        for i in range(len(listToArticulate)-1):
            if(i!=len(listToArticulate)-2):
                output+=listToArticulate[i] + ", "
            else:
                output+=listToArticulate[i]
                output+=" "+andOr+" "
        output+=listToArticulate[-1]
    return(output.replace("  "," "))

def stupidCondition(parsedLine,DEVECXEPTION=True):
    causalities=parsedLine.get("Condition", {}).get("Causalities", {})
    if(len(causalities)==1):
        key=next(iter(causalities))
        button_name = causalities[key].get("Button", {}).get("Name", "")
        
        # Check if Button["Name"] matches the required string
        if button_name == 'Is it on or after the first 1 turns from this characters entry turn?':
            return True
    
    return False

def enemySuperCondition(parsedLine,DEVECXEPTION=True):
    causalities=parsedLine.get("Condition", {}).get("Causalities", {})
    if(parsedLine["Timing"]=="Right before being hit" or parsedLine["Timing"]=="Right after being hit"):
        key=next(iter(causalities))
        button_name = causalities[key].get("Button", {}).get("Name", "")
        
        # Check if Button["Name"] matches the required string
        if button_name == 'Is a super being performed?':
            return True
    
    return False

def removeLookElseWhere(parsedLine,DEVECXEPTION=True):
    output=parsedLine
    causalities=[""]
    if("Condition" in parsedLine):
        causalities=[]
        for causalityKey in parsedLine["Condition"]["Causalities"]:
            causalities.append(parsedLine["Condition"]["Causalities"][causalityKey]["Button"]["Name"])

    if(parsedLine["Timing"]=="Right after being hit" and len(causalities)==1 and causalities[0]=="Has this unit evaded an attack?"):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Attacks evaded"
        output["Building Stat"]["Slider"]="How many attacks have been evaded?"

    elif(parsedLine["Timing"]=="Right after being hit" and len(causalities)==1 and causalities[0][:33]=='Has this character recieved their'):
        quantity=causalities[0][34]
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]=quantity+" attacks recieved"
        output["Building Stat"]["Slider"]="How many times has this character recieved "+quantity+" attacks?"
    
    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==1 and causalities[0]=='Is HP 80 % or less?'):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="HP 80% or less"
        output["Building Stat"]["Slider"]="How many times has HP been 80% or less?"

    elif(parsedLine["Timing"]=="Right after being hit" and len(causalities)==1 and causalities[0]=='Has this character been hit?'):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Attacks recieved"
        output["Building Stat"]["Slider"]="How many attacks has this character recieved?"

    elif(parsedLine["Timing"]=="Right after attack" and causalities[0]==""):
        output["Building Stat"]["Cause"]["Cause"]="Attacks performed"
        output["Building Stat"]["Slider"]="How many attacks has this character performed in battle?"

    elif(parsedLine["Timing"]=="Start of turn" and causalities[0]==""):
        output["Building Stat"]["Cause"]["Cause"]="Start of turn"
        output["Building Stat"]["Slider"]="How many turns has this character been on?"

    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==1 and 'allies attacking on this turn whose name includes' in causalities[0]):
        del output["Condition"]
        allyName=causalities[0][64:-1]
        output["Building Stat"]["Cause"]["Cause"]="Turns with ally "+allyName
        output["Building Stat"]["Slider"]="How many turns has this character been on with an ally whose name includes "+allyName+"?"

    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==1 and 'allies on the team whose name includes' in causalities[0]):
        del output["Condition"]
        allyName=causalities[0][49:-1]
        output["Building Stat"]["Cause"]["Cause"]="Turns with ally on the team whose name includes "+allyName
        output["Building Stat"]["Slider"]="How many turns has this character been on with an ally on the team whose name includes "+allyName+"?"

    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==2 and 'allies attacking on this turn whose name includes' in causalities[0] and 'allies attacking on this turn whose name includes' in causalities[1]):
        del output["Condition"]
        ally1Name=causalities[0][59:-1]
        ally2Name=causalities[1][59:-1]
        output["Building Stat"]["Cause"]["Cause"]="Turns with ally "+ally1Name+" or "+ally2Name
        output["Building Stat"]["Slider"]="How many turns has this character been on with an ally whose name includes "+ally1Name+" or "+ally2Name+"?"
    
    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==1 and causalities[0][-18:]=='category enemies ?' and causalities[0][:20]=='Are there 1 or more '):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Turns with a "+causalities[0][20:-18]+" category enemy"
        output["Building Stat"]["Slider"]="How many turns has this character been on with a "+causalities[0][20:-18]+" category enemy?"

    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==2 and 'Are there 1 or more' in causalities[0] and 'category enemies ?' in causalities[0] and 'Are there 1 or more' in causalities[1] and 'category enemies ?' in causalities[1]):
        del output["Condition"]
        enemy1=causalities[0][20:-18]
        enemy2=causalities[1][20:-18]
        output["Building Stat"]["Cause"]["Cause"]="Turns with a "+enemy1+""+" or "+enemy2+" category enemy"
        output["Building Stat"]["Slider"]="How many turns has this character been on with a "+enemy1+" or "+enemy2+" category enemy?"
    
    elif((parsedLine["Timing"]=="Right before being hit" or parsedLine["Timing"]=="Right after being hit") and len(causalities)==1 and causalities[0]=='Has guard been activated?'):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Guard activated"
        output["Building Stat"]["Slider"]="How many times has this character's guard been activated?"
    
    elif(parsedLine["Timing"]=="Right after being hit" and len(causalities)==2 and causalities[0]=='Has this character been hit?' and 'category allies attacking on this turn?' in causalities[1]):
        del output["Condition"]
        category=causalities[1][20:-30]
        quantity=causalities[1][10]
        output["Building Stat"]["Cause"]["Cause"]="Attacks recieved with "+quantity+" or more "+category+" category units on this turn"
        output["Building Stat"]["Slider"]="How many attacks has this character recieved while there was "+quantity+" or more "+category+" category units on this turn?"
    
    elif(parsedLine["Timing"]=="Right after being hit" and len(causalities)==2 and 'Has this character been hit?' in causalities and 'Has this unit evaded an attack?' in causalities):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Attacks recieved or evaded"
        output["Building Stat"]["Slider"]="How many attacks has this unit recieved or evaded?"

    elif(parsedLine["Timing"]=="Right after being hit" and len(causalities)==2 and causalities[0]=="Has this unit evaded an attack?" and 'allies on the team whose name includes' in causalities[1]):
        del output["Condition"]
        allyName=causalities[1][49:-1]
        output["Building Stat"]["Cause"]["Cause"]="Attacks evaded with an ally on the team whose name includes "+allyName
        output["Building Stat"]["Slider"]="How many attacks has this unit evaded with an ally on the team whose name includes "+allyName+"?"

    elif(parsedLine["Timing"]=="Right after being hit" and len(causalities)==2 and causalities[0]=='Has this character been hit?' and causalities[1]=='Has this unit evaded an attack?'):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Attacks recieved or evaded"
        output["Building Stat"]["Slider"]="How many attacks has this unit recieved or evaded?"

    elif(parsedLine["Timing"]=="When final blow delivered" and len(causalities)==1 and causalities[0]=='Has this character delivered the final blow?'):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Final blow delivered"
        output["Building Stat"]["Slider"]="How many times has this character delivered the final blow?"
        
    elif(parsedLine["Timing"]=="Start of turn" and len(causalities)==1 and causalities[0][:9]=='Is there ' and causalities[0][-14:]=='class enemies?'):
        del output["Condition"]
        enemyClass=causalities[0][19:-15]
        output["Building Stat"]["Cause"]["Cause"]="Turns with a "+enemyClass+" class enemy"
        output["Building Stat"]["Slider"]="How many turns has this character been on with a "+enemyClass+" class enemy?"

    elif(parsedLine["Timing"]=="Right after attack" and len(causalities)<=2 and causalities[0][:12]=="Is this the " and causalities[0][-21:]=="attacker in the turn?"):
        del output["Condition"]
        firstSlot=causalities[0][12:-22]
        if(len(causalities)==2):
            secondSlot=causalities[1][12:-22]
            output["Building Stat"]["Cause"]["Cause"]="Attacking as the "+firstSlot+" or "+secondSlot+" attacker in the turn"
            output["Building Stat"]["Slider"]="How many times has this character attacked as the "+firstSlot+" or "+secondSlot+" attacker in the turn?"
        else:
            output["Building Stat"]["Cause"]["Cause"]="Attacking as the "+firstSlot+" attacker in the turn"
            output["Building Stat"]["Slider"]="How many times has this character attacked as the "+firstSlot+" attacker in the turn?"

    elif(parsedLine["Timing"]=="Right after being hit" and causalities[0][:9]=='Are there' and causalities[0][-27:]=='category units on the team ' and causalities[2][:9]=='Are there' and causalities[2][-27:]=='category units on the team ' and causalities[1]=="Has guard been activated?"):
        del output["Condition"]
        quantity1=causalities[0][10]
        quantity2=causalities[2][10]
        category1=causalities[0][20:-28]
        category2=causalities[2][20:-28]
        output["Building Stat"]["Cause"]["Cause"]="Guard activated with "+quantity1+" or more "+category1+" category units on the team or "+quantity2+" or more "+category2+" category units on the team"
        output["Building Stat"]["Slider"]="How many times has this character's guard been activated with "+quantity1+" or more "+category1+" category units on the team or "+quantity2+" or more "+category2+" category units on the team?"

    elif(parsedLine["Timing"]=="Start of turn" and causalities[0][:9]=='Are there' and causalities[0][-17:]=='category allies ?'):
        del output["Condition"]
        quantity=causalities[0][10]
        category=causalities[0][20:-28]
        output["Building Stat"]["Cause"]["Cause"]="Turns with "+quantity+" or more "+category+" category units on the team"
        output["Building Stat"]["Slider"]="How many turns has this character been on with "+quantity+" or more "+category+" category units on the team?"

    elif(parsedLine["Timing"]=="Right after attack" and len(causalities)==1 and 'Is the target enemy in' in causalities[0]):
        del output["Condition"]
        condition=causalities[0][23:-1]
        output["Building Stat"]["Cause"]["Cause"]="Attacking the enemy in "+condition
        output["Building Stat"]["Slider"]="How many times has this character attacked the enemy in "+condition+"?"

    elif(parsedLine["Timing"]=="Right before being hit" and len(causalities)==1 and causalities[0]=="Is a super being performed?"):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Super attack recieved"
        output["Building Stat"]["Slider"]="How many super attacks has this character recieved?"

    elif((parsedLine["Timing"]=="Right after attack" and len(causalities)==1 and causalities[0]=='Is a super being performed?') or ((parsedLine["Timing"]=="Right before attack(SOT stat)" or parsedLine["Timing"]=="Right before attack(MOT stat)") and len(causalities)==1 and causalities[0]=='') or ((parsedLine["Timing"]=="Right before attack(SOT stat)" or parsedLine["Timing"]=="Right before attack(MOT stat)") and len(causalities)==1 and causalities[0]=='Is a super being performed?')):
        if("Condition" in output):
            del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Super being performed"
        output["Building Stat"]["Slider"]="How many super attacks has this character performed?"

    elif((parsedLine["Timing"]=="Right after attack" and len(causalities)==1 and causalities[0][:9]=='Are there' and causalities[0][-17:]=='category allies ?')):
        del output["Condition"]
        quantity=causalities[0][10]
        category=causalities[0][20:-28]
        output["Building Stat"]["Cause"]["Cause"]="Attacks with "+quantity+" or more "+category+" category units on the team"
        output["Building Stat"]["Slider"]="How many attacks has this character performed with "+quantity+" or more "+category+" category units on the team?"
    
    elif(parsedLine["Timing"]=="Right before being hit" and "Has guard been activated?" in causalities):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Guard activated"
        output["Building Stat"]["Slider"]="How many times has this character's guard been activated while the following was true"
        for causality in causalities:
            if(causality!="Has guard been activated?"):
                output["Building Stat"]["Cause"]["Cause"]+=" "+causality+" or"
                output["Building Stat"]["Slider"]+=" "+causality+" or"
        output["Building Stat"]["Cause"]["Cause"]=output["Building Stat"]["Cause"]["Cause"][:-3].replace("?","")+"?"
        output["Building Stat"]["Slider"]=output["Building Stat"]["Slider"][:-3].replace("?","")+"?"

    elif(parsedLine["Timing"]=="Right after being hit" and 'Is this the 1st attacker in the turn?' in causalities and "Is this the 2nd attacker in the turn?" in causalities and 'Has this character been hit?' in causalities and 'Has this unit evaded an attack?' in causalities):
        del output["Condition"]
        output["Building Stat"]["Cause"]["Cause"]="Attacks recieved or dodged in slot 1 or 2"
        output["Building Stat"]["Slider"]="How many attacks has this character recieved or dodged in slot 1 or 2?" 

    else:
        print("LOOK ELSEWHERE NOT ACCOUNTED FOR",parsedLine)
        if(DEVECXEPTION):
            raise Exception("LOOK ELSEWHERE NOT ACCOUNTED FOR",parsedLine)



    return(output)

def parseActiveSkill(unit,DEVEXCEPTIONS=False):
    active_id=searchbyid(unit[0],codecolumn=1,database=card_active_skills,column=2)
    if(active_id!=None):
        active_id=active_id[0]
        active_line=searchbycolumn(code=active_id,column=0,database=active_skill_sets)
        active_line=searchbycolumn(code=active_id,column=0,database=active_skill_sets)
        active_line=active_line[0]

        output={}
        output["Name"]=active_line[1]
        output["Effect Description"]=active_line[2]
        output["Condition Description"]=active_line[3]
        causalityCondition=logicalCausalityExtractor(active_line[6])
        output["Condition"]={}
        output["Condition"]["Logic"]=causalityCondition
        causalityCondition=CausalityLogicalExtractor(unit,causalityCondition,DEVEXCEPTIONS=DEVEXCEPTIONS)
        output["Condition"].update(causalityCondition)
        output["Uses"]=int(active_line[5])
        
        if(active_line[7]!=""):
            special_id=active_line[7][:-2]
            ultimate_row=searchbycolumn(code=special_id,database=ultimate_specials,column=0)
            ultimate_row=ultimate_row[0]
            output["Attack"]={}
            output["Attack"]["Multiplier"]=int(ultimate_row[3])
            if(ultimate_row[4]=="0"):
                output["Attack"]["Target"]="Enemy"
            elif(ultimate_row[4]=="1"):
                output["Attack"]["Target"]="All enemies"
        output["Effects"]={}
        effects_line=searchbycolumn(code=active_id,database=active_skills,column=1)
        domainOpening=searchbyid(code=active_id,codecolumn=2,database=dokkan_field_active_skill_set_relations,column=1)
        #WIP output["Domain"]=""
        if(domainOpening!=None):
            output["Domain"]=domainOpening[0]

        for line in effects_line:
            output["Effects"][line[0]]={}
            output["Effects"][line[0]]["Duration"]=active_line[4]
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

            output["Effects"][line[0]]["Target"]={}
            if(line[2]=="1"):
                output["Effects"][line[0]]["Target"]["Target"]="Self"
            elif(line[2]=="2"):
                output["Effects"][line[0]]["Target"]["Target"]="All allies"
            elif(line[2]=="3"):
                output["Effects"][line[0]]["Target"]["Target"]="Enemy"
            elif(line[2]=="4"):
                output["Effects"][line[0]]["Target"]["Target"]="All enemies"
            elif(line[2]=="12"):
                output["Effects"][line[0]]["Target"]["Target"]="Super class enemies"
            elif(line[2]=="13"):
                output["Effects"][line[0]]["Target"]["Target"]="Extreme class allies"
            elif(line[2]=="16"):
                output["Effects"][line[0]]["Target"]["Target"]="All allies(self excluded)"
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
                output["Effects"][line[0]]["Effect"]["Buff"]="Effective Against All"
            elif(line[5]=="78"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Guard"
            elif(line[5]=="79"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Giant form/Rage"
                output["Effects"][line[0]]["Effect"]["Unit"]=line[6]
                battle_params_list=searchbycolumn(code=line[7],column=1,database=battle_params)
                for param in battle_params_list:
                    if(param[2]=="0"):
                        output["Effects"][line[0]]["Effect"]["Min turns"]=int(param[3])
                    elif(param[2]=="1"):
                        output["Effects"][line[0]]["Effect"]["Max turns"]=int(param[3])
                    elif(param[2]=="2"):
                        output["Effects"][line[0]]["Effect"]["Reverse chance"]=int(param[3])
            elif(line[5]=="90"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Crit Chance"
                output["Effects"][line[0]]["Effect"]["Amount"]=int(line[6])
            elif(line[5]=="91"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Dodge Chance"
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
            elif(line[5]=="129"):
                output["Effects"][line[0]]["Effect"]["Buff"]="Nullifies attacks that are guaranteed to hit"
            else:
                print("UNKNOWN ACTIVE EFFECT")
                if(DEVEXCEPTIONS):
                    raise Exception("Unknown Active")





        return(output)
    






#def createDFEWallpapers(cards, directory,printing=True):
#    if(printing): print("Creating DFE wallpapers")
#    acquiredlist = os.listdir(r'./assets/DFE wallpapers')
#    leader_skills=storedatabase(directory,"leader_skills.csv")
#    total=0
#    for card in cards:
#        if qualifyAsDFE(card) and (((definewith0(card[0])+".png") not in acquiredlist)):
#            unitid=card[0]
#            if unitid[-1]=="1":
#                unitid=str(int(unitid)-1)
#            mainunit=card

        #background
#            cframeurl=("../frontend/dbManagement/assets/misc/cha_base_0")
        #element
#            cframeurl+=(mainunit[12][-1])
#            cframeurl+=("_0")
        #rarity
#            cframeurl+=(mainunit[5])
#            cframeurl+=(".png")


#            cframe = Image.open(cframeurl).convert("RA")
#            cframe=cframe.resize((200,200))

        #character icon
#            ciconurl=("../frontend/dbManagement/assets/thumb/")
#            if card[48]=="" or card[48]=="0.0":
#                ciconurl+=unitid
#            else:
#                ciconurl+=str(int(float(card[48])))
#            ciconurl+=(".png")
#            cicon = Image.open(ciconurl).convert("RA")
#            cicon.resize((250,250))


        #rarity
#            crarityurl=("../frontend/dbManagement/assets/misc/cha_rare_")
#            crarityurl+=(getrarity(mainunit))
#            crarityurl+=(".png")
#            crarity = Image.open(crarityurl).convert("RA")
#            if getrarity(mainunit)=="ssr":
#                crarity=crarity.resize((120,72))
#            else:    
#                crarity=crarity.resize((160,96))

        #element
#            celementurl=("../frontend/dbManagement/assets/misc/cha_type_icon_")
#            if len(mainunit[12])==1:
#                celementurl+=("0")
#            celementurl+=(mainunit[12])
#            celementurl+=(".png")
#            celement = Image.open(celementurl).convert("RA")
#            celement=celement.resize((90,90))
#            if mainunit[12] in ("20","10"):
#                if(printing): print("AGL ",end="")
#            elif mainunit[12] in ("21","11"):
#                if(printing): print("TEQ ",end="")
#            elif mainunit[12] in ("22","12"):
#                if(printing): print("INT ",end="")
#            elif mainunit[12] in ("23","13"):
#                if(printing): print("STR ",end="")
#            elif mainunit[12] in ("24","14"):
#                if(printing): print("PHY ",end="")

#            (width,height)=(cicon.width+10,cicon.height+10)
#            cfinal=Image.new("RA",(width,height))
#            cfinal.paste(cframe, (25,35), cframe)
#            cfinal.paste(cicon, (0,1), cicon)
#            if getrarity(mainunit)=="n":
##                cfinal.paste(crarity, (-37,160),crarity)
#                if(printing): print("N ",end="")
#            elif getrarity(mainunit)=="r":
#                cfinal.paste(crarity, (-42,160), crarity)
#                if(printing): print("R ",end="")
#            elif getrarity(mainunit)=="sr":
#                cfinal.paste(crarity, (-25,158), crarity)
#                if(printing): print("SR ",end="")
#            elif getrarity(mainunit)=="ssr":
#                cfinal.paste(crarity, (-5,171), crarity)
#                if(printing): print("SSR ",end="")
#            elif getrarity(mainunit)=="ur":
#                cfinal.paste(crarity, (-25,160), crarity)
#                if(printing): print("UR ",end="")
#            elif getrarity(mainunit)=="lr" or True:
#                cfinal.paste(crarity, (-25,155),crarity)
#                if(printing): print("LR ",end="")
#            cfinal.paste(celement, (170,5),celement)
#            
            
#            wallpapername=("../frontend/dbManagement/assets/DFE wallpapers/")
#            wallpapername+=(unitid)
#            wallpapername+=(".png")
#            if(printing): print(mainunit[1])
#            cfinal.save(wallpapername)
#            total+=1
#            if total%100==0:
#                if(printing): print(total)
            #print("Created final asset for",total,getfullname(card,leader_skills))
#    if(printing): print("All DFE assets created")

#def createLRWallpapers(cards,directory,printing=True):
#    if(printing): print("Creating LR wallpapers")
#    acquiredlist = os.listdir(r'./assets/LR wallpapers')
#    leader_skills=storedatabase(directory,"leader_skills.csv")
#    total=0
#    for card in cards:
#        if (card[53]!="2030-12-31 23:59:59") and (card[0][0]!="9") and (card[0][-1]=="0") and (card[22]!="") and ((("final_"+card[0]+".png") not in acquiredlist)) and (getrarity(card)=="lr"):
#            unitid=card[0]
#            if unitid[-1]=="1":
#                unitid=str(int(unitid)-1)
#            mainunit=card

        #background
#            cframeurl=("../frontend/dbManagement/assets/misc/cha_base_0")
        #element
#            cframeurl+=(mainunit[12][-1])
#            cframeurl+=("_0")
        #rarity
#            cframeurl+=(mainunit[5])
#            cframeurl+=(".png")

#            cframe = Image.open(cframeurl).convert("RA")
#            cframe=cframe.resize((200,200))

        #character icon
#            ciconurl=("../frontend/dbManagement/assets/thumb/")
#            if card[48]=="" or card[48]=="0.0":
#                ciconurl+=unitid
#            else:
#                ciconurl+=str(int(float(card[48])))
#            ciconurl+=(".png")
#            cicon = Image.open(ciconurl).convert("RA")
#            cicon.resize((250,250))


        #rarity
#            crarityurl=("../frontend/dbManagement/assets/misc/cha_rare_")
#            crarityurl+=(getrarity(mainunit))
#            crarityurl+=(".png")
#            crarity = Image.open(crarityurl).convert("RA")
#            if getrarity(mainunit)=="ssr":
#                crarity=crarity.resize((120,72))
#            else:    
#                crarity=crarity.resize((160,96))

        #element
#            celementurl=("../frontend/dbManagement/assets/misc/cha_type_icon_")
#            if len(mainunit[12])==1:
#                celementurl+=("0")
#            celementurl+=(mainunit[12])
#            celementurl+=(".png")
#            celement = Image.open(celementurl).convert("RA")
#            celement=celement.resize((90,90))
#            if mainunit[12] in ("20","10"):
#                if(printing): print("AGL ",end="")
#            elif mainunit[12] in ("21","11"):
#                if(printing): print("TEQ ",end="")
#            elif mainunit[12] in ("22","12"):
#                if(printing): print("INT ",end="")
#            elif mainunit[12] in ("23","13"):
#                if(printing): print("STR ",end="")
#            elif mainunit[12] in ("24","14"):
#                if(printing): print("PHY ",end="")

#            (width,height)=(cicon.width+10,cicon.height+10)
#            cfinal=Image.new("RA",(width,height))
#            cfinal.paste(cframe, (25,35), cframe)
#            cfinal.paste(cicon, (0,1), cicon)
#            if getrarity(mainunit)=="n":
#                cfinal.paste(crarity, (-37,160),crarity)
#                if(printing): print("N ",end="")
#            elif getrarity(mainunit)=="r":
#                cfinal.paste(crarity, (-42,160), crarity)
#                if(printing): print("R ",end="")
##            elif getrarity(mainunit)=="sr":
#                cfinal.paste(crarity, (-25,158), crarity)
#                if(printing): print("SR ",end="")
#            elif getrarity(mainunit)=="ssr":
#                cfinal.paste(crarity, (-5,171), crarity)
#                if(printing): print("SSR ",end="")
#            elif getrarity(mainunit)=="ur":
#                cfinal.paste(crarity, (-25,160), crarity)
#                if(printing): print("UR ",end="")
#            elif getrarity(mainunit)=="lr" or True:
#                cfinal.paste(crarity, (-25,155),crarity)
#                if(printing): print("LR ",end="")
#            cfinal.paste(celement, (170,5),celement)
            
            
#            if(printing): print(mainunit[1])
#            wallpapername=("../frontend/dbManagement/assets/LR wallpapers/final_")
#            wallpapername+=(unitid)
#            wallpapername+=(".png")
#            cfinal.save(wallpapername)
#            total+=1
#            if total%100==0:
#                if(printing): print(total)
            
#    if(printing): print("All LR wallpapers created")

def qualifyZAwakened(unit):
    if(unit[0][-1]=="0"):
        return False
    if(not qualifyEncounterable(unit)):
        return False
    if(qualifyEncounterable(swapToUnitWith0(unit))):
        return True

def getUnitType(unit,printing=True,DEVEXCEPTIONS=False):
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
        return("None")
    elif unit[12][0]=="1":
        return("Super")
    elif unit[12][0]=="2":
        return("Extreme")
    

#def createFullThumb(card,printing=True):
#    if(card[48]!=""):
#        resource_id=str(int(float(card[48])))
#        if(resource_id[-1]=="1"):
#            resource_id=str(int(resource_id)-1)
#    else:
#        if(card[0][-1]=="1"):
#            resource_id=str(int(card[0])-1)
#        else:
#            resource_id=card[0]
#    unitid=card[0]
#    mainunit=card

#background
#    cframeurl=("../frontend/dbManagement/DokkanFiles/global/en/layout/en/image/character/character_thumb_bg/cha_base_0")
#element
#    cframeurl+=(mainunit[12][-1])
#    cframeurl+=("_0")
#rarity
#    cframeurl+=(mainunit[5])
#    cframeurl+=(".png")


#    cframe = Image.open(cframeurl).convert("RA")
#    cframe=cframe.resize((200,200))

#character icon
#    ciconurl=("../frontend/dbManagement/DokkanFiles/global/en/character/thumb/card_")
#    ciconurl+=resource_id
#    ciconurl+=("_thumb.png")
#    cicon = Image.open(ciconurl).convert("RA")
#    cicon.resize((250,250))


#rarity
#    crarityurl=("../frontend/dbManagement/DokkanFiles/global/en/layout/en/image/character/cha_rare_")
#    crarityurl+=(getrarity(mainunit))
#    crarityurl+=(".png")
#    crarity = Image.open(crarityurl).convert("RA")
#    if getrarity(mainunit)=="ssr":
#        crarity=crarity.resize((120,72))
#    else:    
#        crarity=crarity.resize((160,96))

#element
#    celementurl=("../frontend/dbManagement/DokkanFiles/global/en/layout/en/image/character/cha_type_icon_")
#    if len(mainunit[12])==1:
#        celementurl+=("0")
#    celementurl+=(mainunit[12])
#    celementurl+=(".png")
#    celement = Image.open(celementurl).convert("RA")
#    celement=celement.resize((90,90))

#    (width,height)=(cicon.width+10,cicon.height+10)
#    cfinal=Image.new("RA",(width,height))
#    cfinal.paste(cframe, (25,35), cframe)
#    cfinal.paste(cicon, (0,1), cicon)
#    if getrarity(mainunit)=="n":
#        cfinal.paste(crarity, (-37,160),crarity)
#    elif getrarity(mainunit)=="r":
#        cfinal.paste(crarity, (-42,160), crarity)
#    elif getrarity(mainunit)=="sr":
#        cfinal.paste(crarity, (-25,158), crarity)
#    elif getrarity(mainunit)=="ssr":
#        cfinal.paste(crarity, (-5,171), crarity)
#    elif getrarity(mainunit)=="ur":
#        cfinal.paste(crarity, (-25,160), crarity)
#    elif getrarity(mainunit)=="lr" or True:
#        cfinal.paste(crarity, (-25,155),crarity)
#    cfinal.paste(celement, (170,5),celement)
    
#    cfinal=cfinal.crop((10,10,256,235))
    
#    name=("../frontend/dbManagement/DokkanFiles/global/en/character/card/")
#    name+=unitid
#    name+=("/card_")
#    name+=(unitid)
#    name+=("_full_thumb")
#    name+=(".png")
    
#    cfinal.save(name)


def passivename(unit,printing=True):
    return(listtostr(searchbyid(str(int(float(unit[21]))), 0, passive_skills, 1)))

def floattoint(number,printing=True):
    if(type(number)==str):
        number=float(number)
    if number%1==0:
        return(int(number))
    else:
        return(number)



    
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
            linkid=searchedbyid(link, 1, link_skills, 0)[0]
            linkcode=searchedbyid(linkid, 1, link_skill_lvs, 0)[lvl-1]
            for linkdetails in link_skill_efficacies:
            
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

def getSuperAttackLevel(unit, eza):
    if(eza==False):
        return(int(unit[14]))
    else:
        optimal_awakening_grow_type=unit[16][:-2]
        relevant_Awakenings=searchbycolumn(code=optimal_awakening_grow_type,database=optimal_awakening_growths,column=1)
        relevant_Awakenings.sort(key=lambda x:x[4])
        return(int(relevant_Awakenings[-1][4]))


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
        unitDetails=searchbycolumn(code=unit,column=0,database=cards)[0]
        return(getrarity(unitDetails))

        
    
    return("ERROR IN GETRARITY UNIT MAX LEVEL IS",unit[13])


    

def swapToUnitWith0(unit):
    unitId=definewith0(unit[0])
    for card in cards:
        if card[0]==unitId:
            return(card)
    return(None)

def swapToUnitWith1(unit):
    unitId=definewith1(unit[0])
    for card in cards:
        if card[0]==unitId:
            return(card)
    return(None)

def getPassiveIdList(unit,eza=False,seza=False, printing=False,DEVEXCEPTIONS=False):
    unitPassiveId=unit[21]
    if(eza):
        if(swapToUnitWith1(unit)!=None):
            unitEZA=swapToUnitWith1(unit)
        else:
            return(getPassiveIdList(unit,eza=False, printing=printing))
        unitEZAGrowthId=unitEZA[16][0:-2]
        if(unitEZAGrowthId==""):
            return(getPassiveIdList(unit,eza=False, printing=printing))
        if(seza):
            relevantAwakenings=searchbycolumn(code=unitEZAGrowthId,database=optimal_awakening_growths,column=1)
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
            relevantAwakenings=searchbycolumn(code=unitEZAGrowthId,database=optimal_awakening_growths,column=1)
            #if the unit is an ur
            if(unit[5]=="4"):
                relevantAwakenings=searchbycolumn(code="7",database=relevantAwakenings,column=2)
            #if the unit is an lr
            elif(unit[5]=="5"):
                relevantAwakenings=searchbycolumn(code="3",database=relevantAwakenings,column=2)
            else:
                if(DEVEXCEPTIONS):
                    raise Exception("Unit is not an LR or UR but has a eza")
        unitEZAPassiveId=relevantAwakenings[0][5][:-2]
        
        unitEZAPassiveList=searchbyid(code=unitEZAPassiveId,codecolumn=1,database=passive_skill_set_relations,column=2)
        return(unitEZAPassiveList)
    else:
        unitPassiveId=unitPassiveId[0:-2]
        unitPassiveList=searchbyid(code=unitPassiveId,codecolumn=1,database=passive_skill_set_relations,column=2)
        return(unitPassiveList)
    
def getPassiveId(unit,eza=False,seza=False, printing=False,DEVEXCEPTIONS=False):
    unitPassiveId=unit[21]
    if(eza):
        if(swapToUnitWith1(unit)!=None):
            unitEZA=swapToUnitWith1(unit)
        else:
            return(getPassiveIdList(unit,eza=False, printing=printing))
        unitEZAGrowthId=unitEZA[16][0:-2]
        if(unitEZAGrowthId==""):
            return(getPassiveIdList(unit,eza=False, printing=printing))
        if(seza):
            relevantAwakenings=searchbycolumn(code=unitEZAGrowthId,database=optimal_awakening_growths,column=1)
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
            relevantAwakenings=searchbycolumn(code=unitEZAGrowthId,database=optimal_awakening_growths,column=1)
            #if the unit is an ur
            if(unit[5]=="4"):
                relevantAwakenings=searchbycolumn(code="7",database=relevantAwakenings,column=2)
            #if the unit is an lr
            elif(unit[5]=="5"):
                relevantAwakenings=searchbycolumn(code="3",database=relevantAwakenings,column=2)
            else:
                if(DEVEXCEPTIONS):
                    raise Exception("Unit is not an LR or UR but has a eza")
        unitEZAPassiveId=relevantAwakenings[0][5][:-2]
        
        return(unitEZAPassiveId)
    else:
        unitPassiveId=unitPassiveId[0:-2]
        return(unitPassiveId)

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
    temp+=(listtostr(searchedbyid(unit[22],0,leader_skills,1)))
    temp+=" "
    
    #get unit id
    temp+=(unit[0])
    temp+=" "
    
    #return variable
    return(temp)
    
def getallcategories(unitid,printing=True):
    temp1=searchedbyid(unitid, 1, card_card_categories, 2)
    categoryList=[]
    if temp1!=None:
        for x in temp1:
            globalListedCategory=searchedbyid(x,0,card_categories,1)
            if(globalListedCategory!=None):
                categoryList.append(globalListedCategory[0])
            else:
                categoryList.append(searchedbyid(x,0,card_categories,1)[0])
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
        linkID=searchbyid(code=linkNameOrID,codecolumn=1,database=link_skills,column=0)
    linkID=linkID[0]
    linkLevelIDs=searchbycolumn(code=linkID,column=1,database=link_skill_lvs)
    for levelIDRow in linkLevelIDs:
        levelID=levelIDRow[0]
        efficiacy_rows=searchbycolumn(code=levelID,database=link_skill_efficacies,column=1)
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
        temp1=searchbyid(code,0,link_skills,1)
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

def filter_unit_components(data, components):
    """
    Filters the dictionary to include only the specified components.
    
    :param unit_basics: The original dictionary of unit details.
    :param components: A list of keys to include for each unit (e.g., ["ID", "Name"]).
    :return: A new dictionary with filtered components.
    """
    return {
        unit_id: {key: details[key] for key in components if key in details}
        for unit_id, details in data.items()
    }

def filterSingleComponent(data, component):
    return {unit_id: unit_info.get(component, None) for unit_id, unit_info in data.items()}


def validOrbLimitation(unitDictionary,limitation,cardUniqueInfoSetIds,cardCategories):
    if(limitation[2]=="EquipmentSkillLimitation::ElementLimitation"):
        [unitClass,unitElement]=extractClassType(limitation[3][23:-1])
        classMatch=False
        elementMatch=False
        if(unitClass==[] or unitDictionary["Class"] in unitClass):
            classMatch=True
        if(unitElement==[] or unitDictionary["Type"] in unitElement):
            elementMatch=True
        if(classMatch and elementMatch):
            return(True)
    elif(limitation[2]=="EquipmentSkillLimitation::CardUniqueInfoSetLimitation"):
        validCardUniqueInfoSetIds=limitation[3][31:-2].split(", ")
        validCardUniqueInfoSetIds=limitation[3].replace('{"card_unique_info_set_ids": [',"").replace("]}","").split(", ")
        if any(item in cardUniqueInfoSetIds for item in validCardUniqueInfoSetIds):
            return(True)
    elif(limitation[2]=="EquipmentSkillLimitation::CardCategoryLimitation"):
        validCategories=limitation[3][23:-2].split(", ")
        if any(item in cardCategories for item in validCategories):
            return(True)

    elif(limitation[2]=="EquipmentSkillLimitation::CardLimitation"):
        validCardIds=limitation[3][14:-2].split(", ")
        if(unitDictionary["ID"] in validCardIds):
            return(True)
    else:
        print(limitation)
    return(False)

def calculateOrbs(unit,unitDictionary):
    orbs={
        "gold":{"HP":0,"ATK":0,"DEF":0},
        "silver": {"HP":0,"ATK":0,"DEF":0},
        "bronze": {"HP":0,"ATK":0,"DEF":0},
        "overall":{"HP":0,"ATK":0,"DEF":0}
    }
    validOrbLimitationSets=[]
    cardUniqueInfoSetIds=searchbyid(code=unit[3],codecolumn=1,database=card_unique_info_set_relations,column=2)
    if(cardUniqueInfoSetIds==None): 
        cardUniqueInfoSetIds=[]
    cardCategories=searchedbyid(unit[0], 1, card_card_categories, 2)
    if(cardCategories==None):
        cardCategories=[]
    for limitation in equipment_skill_limitations[1:]:
        if(validOrbLimitation(unitDictionary,limitation,cardUniqueInfoSetIds,cardCategories)):
            validOrbLimitationSets.append(limitation[1])

    for orb in equipment_skill_items[1:]:
        if(orb[8] in validOrbLimitationSets):
            if(orbs[orb[3]]["HP"] < int(orb[5])): orbs[orb[3]]["HP"] = int(orb[5])
            if(orbs[orb[3]]["ATK"] < int(orb[6])): orbs[orb[3]]["ATK"] = int(orb[6])
            if(orbs[orb[3]]["DEF"] < int(orb[7])): orbs[orb[3]]["DEF"] = int(orb[7])
    orbs["overall"]["HP"] = orbs["gold"]["HP"] + orbs["silver"]["HP"] + orbs["bronze"]["HP"]
    orbs["overall"]["ATK"] = orbs["gold"]["ATK"] + orbs["silver"]["ATK"] + orbs["bronze"]["ATK"]
    orbs["overall"]["DEF"] = orbs["gold"]["DEF"] + orbs["silver"]["DEF"] + orbs["bronze"]["DEF"]

    return(orbs)