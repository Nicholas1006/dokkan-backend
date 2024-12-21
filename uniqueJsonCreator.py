from dokkanfunctions import *
from progress.bar import Bar

print("Creating links json")

link_skills=storedatabase("dataGB/","link_skills.csv")
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

turnintoJson(links_dictionary, "links",directoryName="../frontend/dbManagement/uniqueJsons")




print("Creating domains json")
domains_json={}
dokkan_fields=storedatabase("dataGB/","dokkan_fields.csv")[1:]
dokkan_field_efficiacies=storedatabase("dataGB/","dokkan_field_efficacies.csv")[1:]

for domain in dokkan_fields:
    domain_dictionary={}
    domain_dictionary["ID"]=domain[1]
    domain_dictionary["Name"]=domain[2]
    domain_dictionary["Description"]=domain[3]
    domain_dictionary["Efficiacies"]={}
    relevant_efficiacies=searchbycolumn(domain[1],dokkan_field_efficiacies,1)
    for efficiacy in relevant_efficiacies:
        domain_dictionary["Efficiacies"][efficiacy[0]]=parse_domain_efficiacy(efficiacy)

    domains_json[domain[1]]=domain_dictionary


turnintoJson(domains_json, "domains",directoryName="../frontend/dbManagement/uniqueJsons")

bar = Bar("Creating all units json",max=len(cardsGB))
allUnitsDictionary=[]
relevantCards=[]
for unit in cardsGB:
    bar.next()    
    if qualifyUsable(unit):
        relevantCards.append(unit)
        allUnitsDictionary.append(unit[0])
        if(checkEza(unit[0])):
            allUnitsDictionary.append(unit[0]+"EZA")
        if(checkSeza(unit[0])):
            allUnitsDictionary.append(unit[0]+"SEZA")
    


turnintoJson(allUnitsDictionary, "allUnits",directoryName="../frontend/dbManagement/uniquejsons")

unitBasics={}
bar1 = Bar('Creating all unit basics', max=len(relevantCards))
for unit in relevantCards:
    bar1.next()
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
        unitDictionary["ID"]=unit[0]
        unitDictionary["Name"]=unit[1]
        unitDictionary["Type"]=getUnitTyping(unit)
        unitDictionary["Rarity"]=getrarity(unit)
        unitDictionary["Max Level"]=getMaxLevel(unit,eza)
        unitDictionary["Cost"]=getUnitCost(unit)
        unitDictionary["Eza"]=eza
        unitDictionary["Seza"]=seza
        unitDictionary["Dokkan Awakened"]=False
        relevant_awakenings=searchbycolumn(code=unit[0],database=card_awakening_routesGB,column=3)
        relevant_awakenings+=searchbycolumn(code=unit1[0],database=card_awakening_routesGB,column=3)
        relevant_awakenings=searchbycolumn(code="CardAwakeningRoute::Dokkan",database=relevant_awakenings,column=1)
        if(relevant_awakenings!=[]):
            unitDictionary["Dokkan Awakened"]=True
        intUnit = [int(x) for x in unit[6:14]]
        growthInfo=searchbycolumn(code=unit[15],column=1,database=card_growthsGB)
        coef=float(searchbyid(code=str(unitDictionary["Max Level"]),codecolumn=2,database=growthInfo,column=3)[0])
        maxLevelStats=getUnitStats(intUnit,unitDictionary["Max Level"],coef)
        unitDictionary["HP"]=maxLevelStats["HP"]
        unitDictionary["Attack"]=maxLevelStats["ATK"]
        unitDictionary["Defense"]=maxLevelStats["DEF"]
        if(eza):
            unitDictionary["Acquired"]=getEzaReleaseTime(unit)
        elif(seza):
            unitDictionary["Acquired"]=getSezaReleaseTime(unit)
        else:
            unitDictionary["Acquired"]=getUnitReleaseTime(unit)
        unitDictionary["Character"]=getCharacterNameID(unit)
        unitDictionary["Sp Atk Lv"]=unit[14]
        if(eza):
            unitDictionary["Sp ATK Lv"]=str(5+int(unit[14]))
        unitDictionary["Activation"]=0
        if(unitDictionary["Rarity"]=="ur" or unitDictionary["Rarity"]=="lr"):
            unitDictionary["Activation"]=1

        
        #filter conditions(many are within sort)
        unitDictionary["Class"]=getUnitClass(unit)
        unitDictionary["Categories"]=getallcategories(unit[0],printing=True)

        unitDictionary["Awakening"]={"Dokkan Awakening":False, "Awakening to LR":False, "Extreme Z-Awakening":False, "Super Extreme Z-Awakening":False}
        relevant_awakenings=searchbycolumn(code=unit1[0],database=card_awakening_routesGB,column=2)
        relevant_awakenings=searchbycolumn(code="CardAwakeningRoute::Dokkan",database=relevant_awakenings,column=1)
        if(len(relevant_awakenings)>0):
            unitDictionary["Awakening"]["Dokkan Awakening"]=True


        for awakening in relevant_awakenings:
            if(getrarity(awakening[3])=="lr"):
                unitDictionary["Awakening"]["Awakening to LR"]=True

        if("EZA" in ezaTrueFalse):
            unitDictionary["Awakening"]["Extreme Z-Awakening"]=True
        if("SEZA" in ezaTrueFalse):
            unitDictionary["Awakening"]["Super Extreme Z-Awakening"]=True

        superAttackTypes=getSuperAttackTypes(unit,eza)
        superAttackTypes=list(set(superAttackTypes))

        unitDictionary["Super Attack Types"]=superAttackTypes
        if(eza):
            unitBasics[unit[0]+"EZA"]=unitDictionary
        elif(seza):
            unitBasics[unit[0]+"SEZA"]=unitDictionary
        else:
            unitBasics[unit[0]]=unitDictionary

        unitDictionary["Links"]=getalllinks(unit)
        
bar.finish()
print("Turning unitBasics into json")
turnintoJson(unitBasics, "unitBasics",directoryName="../frontend/dbManagement/uniqueJsons")