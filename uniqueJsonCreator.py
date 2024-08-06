from dokkanfunctions import *

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

print("Creating all units json")
relevantCards=[]
for unit in cardsJP:
        if qualifyUsable(unit):
            relevantCards.append(unit)
allUnitsDictionary=[]
for unit in relevantCards:
    allUnitsDictionary.append(unit[0])
turnintoJson(allUnitsDictionary, "allUnits",directoryName="jsons")

print("Creating all unit basics")
unitBasics={}
for unit in relevantCards:
    unitGB=switchUnitToGlobal(unit)
    unitDictionary={}
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
    unitDictionary["Categories"]=getallcategories(unit[0],printing=True)
    unitBasics[unit[0]]=unitDictionary

turnintoJson(unitBasics, "unitBasics",directoryName="../frontend/dbManagement/uniqueJsons")