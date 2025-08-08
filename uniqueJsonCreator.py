from dokkanfunctions import *


CALCLINKS=True
CALCCATEGORIES=True
CALCDOMAINS=True
CALCALLUNITS=True
CALCUNITBASICS=True
DEVEXCEPTIONS=os.getenv('DEVEXCEPTIONS')  == "True"
print("DEVEXCEPTIONS",DEVEXCEPTIONS)


if(CALCLINKS):
    print("Creating links json")

    link_skills=storedatabase("data/","link_skills.csv")[1:]
    link_skills_name=[name[1] for name in link_skills]
    link_skills_id=[name[0] for name in link_skills]

    links_dictionary={}

    for link in link_skills_name:
        linkBuffs=getlinkBuffsAtAllLevel(link)
        for level in linkBuffs:
            for buff in linkBuffs[level].copy():
                if(linkBuffs[level][buff]==0):
                    del linkBuffs[level][buff]
        links_dictionary[link]=linkBuffs

    turnintoJson(links_dictionary, "links",directoryName="temp_jsons/uniqueJsons")

if(CALCCATEGORIES):
    print("Creating categories json")

    categories=storedatabase("data/","card_categories.csv")[1:]
    categories_dictionary={}
    for category in categories:
        categories_dictionary[category[0]]={}
        categories_dictionary[category[0]]["ID"]=category[0]
        categories_dictionary[category[0]]["Name"]=category[1]
        categories_dictionary[category[0]]["Priority"]=category[3]

    turnintoJson(categories_dictionary, "categories",directoryName="temp_jsons/uniqueJsons")


if(CALCDOMAINS):
    print("Creating domains json")
    domains_json={}
    dokkan_fields=storedatabase("data/","dokkan_fields.csv")[1:]
    dokkan_field_efficiacies=storedatabase("data/","dokkan_field_efficacies.csv")[1:]

    for domain in dokkan_fields:
        domain_dictionary={}
        domain_dictionary["ID"]=domain[1]
        domain_dictionary["Name"]=domain[2]
        domain_dictionary["Description"]=domain[3]
        domain_dictionary["Efficiacies"]={}
        relevant_efficiacies=searchbycolumn(domain[1],dokkan_field_efficiacies,1)
        for efficiacy in relevant_efficiacies:
            domain_dictionary["Efficiacies"][efficiacy[0]]=parse_domain_efficiacy(efficiacy,DEVEXCEPTIONS)

        domains_json[domain[1]]=domain_dictionary
        domain_dictionary["Resource ID"]=domain[4]


    turnintoJson(domains_json, "domains",directoryName="temp_jsons/uniqueJsons")


if(CALCALLUNITS):
    print("Creating all units json")
    unitCount=0
    maxUnitCount=len(cards)-1
allUnitsDictionary=[]
encounterableCards=[]
for unit in cards[1:]:
    if(CALCALLUNITS):
        if(unitCount%100==0):
            print(unitCount,"/",maxUnitCount)
        unitCount+=1
    if qualifyEncounterable(unit):
        encounterableCards.append(unit)


if(CALCUNITBASICS):
    unitBasics={}
    print("Creating all units basics")
    unitCount=0
    maxUnitCount=len(encounterableCards)
    for unit in encounterableCards:
        ezaTrueFalse=["None"]
        if(checkEza(unit[0])):
            ezaTrueFalse.append("EZA")
        if(checkSeza(unit[0])):
            ezaTrueFalse.append("SEZA")
        for ezaCheck in ezaTrueFalse:
            if(ezaCheck)=="None":
                eza=False
                seza=False
            elif(ezaCheck)=="EZA":
                eza=True
                seza=False
            elif(ezaCheck)=="SEZA":
                eza=False
                seza=True
            unit1=swapToUnitWith1(unit)
            unitDictionary={}

            #Sort conditions
            unitDictionary["ID"]=int(unit[0])
            unitDictionary["Ownable"]=qualifyEncounterableAsOwnable(unit)
            unitDictionary["Name"]=unit[1]
            unitDictionary["Type"]=getUnitType(unit)
            unitDictionary["Rarity"]=getrarity(unit)
            unitDictionary["Max Level"]=getMaxLevel(unit,eza or seza)
            unitDictionary["Cost"]=int(getUnitCost(unit))
            unitDictionary["Eza"]=eza
            unitDictionary["Seza"]=seza
            unitDictionary["Dokkan Awakened"]=False
            relevant_awakenings=searchbycolumn(code=unit[0],database=card_awakening_routes,column=3)
            relevant_awakenings+=searchbycolumn(code=unit1[0],database=card_awakening_routes,column=3)
            relevant_awakenings=searchbycolumn(code="CardAwakeningRoute::Dokkan",database=relevant_awakenings,column=1)
            if(relevant_awakenings!=[]):
                unitDictionary["Dokkan Awakened"]=True
            intUnit = [int(x) for x in unit[6:14]]
            growthInfo=searchbycolumn(code=unit[15],column=1,database=card_growths)
            coef=float(searchbyid(code=str(unitDictionary["Max Level"]),codecolumn=2,database=growthInfo,column=3)[0])
            maxLevelStats=getUnitStats(intUnit,unitDictionary["Max Level"],coef)
            unitDictionary["HP"]=maxLevelStats["HP"]
            unitDictionary["Attack"]=maxLevelStats["ATK"]
            unitDictionary["Defense"]=maxLevelStats["DEF"]
            if(eza):
                unitDictionary["Release"]=getEzaReleaseTime(unit,DEVEXCEPTIONS)
            elif(seza):
                unitDictionary["Release"]=getSezaReleaseTime(unit,DEVEXCEPTIONS)
            else:
                unitDictionary["Release"]=getUnitReleaseTime(unit)
            unitDictionary["Character"]=int(getCharacterNameID(unit))
            unitDictionary["Sp Atk Lv"]=getSuperAttackLevel(unit,eza)
            if(eza):
                unitDictionary["Sp ATK Lv"]=str(5+int(unit[14]))
            if(unitDictionary["Rarity"]=="ur" or unitDictionary["Rarity"]=="lr"):
                unitDictionary["Activation"]=1


            unitDictionary["Resource ID"]=unit[0]
            if(unit[48]!=""):
                unitDictionary["Resource ID"]=str(int(float(unit[48])))
            if(unitDictionary["Resource ID"][-1]=="1"):
                unitDictionary["Resource ID"]=(unitDictionary["Resource ID"][:-1]+"0")
            
            #filter conditions(many are within sort)
            unitDictionary["Class"]=getUnitClass(unit)
            unitDictionary["Categories"]=getallcategories(unit[0],printing=True)

            unitDictionary["Awakening"]={"Dokkan Awakening":False, "Awakening to LR":False, "Extreme Z-Awakening":False, "Super Extreme Z-Awakening":False}
            relevant_awakenings=searchbycolumn(code=unit1[0],database=card_awakening_routes,column=2)
            relevant_awakenings=searchbycolumn(code="CardAwakeningRoute::Dokkan",database=relevant_awakenings,column=1)
            if(len(relevant_awakenings)>0):
                unitDictionary["Awakening"]["Dokkan Awakening"]=True


            for awakening in relevant_awakenings:
                if(getrarity(awakening[3])=="lr"):
                    unitDictionary["Awakening"]["Awakening to LR"]=True

            if("EZA" in ezaTrueFalse and eza==False):
                unitDictionary["Awakening"]["Extreme Z-Awakening"]=True
            if("SEZA" in ezaTrueFalse and seza==False):
                unitDictionary["Awakening"]["Super Extreme Z-Awakening"]=True

            superAttackTypes=getSuperAttackTypes(unit,eza)

            unitDictionary["Super Attack Types"]=superAttackTypes
            if(eza):
                unitBasics[unit[0]+"EZA"]=unitDictionary
            elif(seza):
                unitBasics[unit[0]+"SEZA"]=unitDictionary
            else:
                unitBasics[unit[0]]=unitDictionary

            unitDictionary["Leader Skill"]= parseLeaderSkill(unit,eza)

            unitDictionary["Links"]=getalllinks(unit)

        print(unitCount,"/",maxUnitCount)
        unitCount+=1
            

    print("Turning unitBasics into json seperated by component")
    for component in unitDictionary:
        turnintoJson(filterSingleComponent(unitBasics,component), component,directoryName="temp_jsons/uniqueJsons/unitBasics")
        print("Finished:" + component)


