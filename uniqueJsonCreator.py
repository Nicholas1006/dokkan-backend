from dokkanfunctions import *
import sqlite3

GLOBAL_DB_LOC=os.path.dirname(os.path.abspath(__file__))+"/Dokkan_Asset_Downloader/card_assets/global/en/sqlite/current/en/database.db"
connection = sqlite3.connect(GLOBAL_DB_LOC)
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
ownableCards=[]
for unit in cards[1:]:
    if(CALCALLUNITS):
        if(unitCount%100==0):
            print(unitCount,"/",maxUnitCount)
        unitCount+=1
    if qualifyOwnableSQL(connection,unit[0]):
        ownableCards.append(unit)



idTime=0.0
maxedTime=0.0
nameTime=0.0
typeTime=0.0
rarityTime=0.0
maxLevelTime=0.0
costTime=0.0
ezaTime=0.0
dokkanAwakenTime=0.0
dokkanAwakenTime=0.0
statsTime=0.0
releaseTime=0.0
maxLevelStatsTime=0.0
characterTime=0.0
spAtkLevelTime=0.0
resourceIDTime=0.0
classTime=0.0
categoriesTime=0.0
awakeningTime=0.0
superAttackTypesTime=0.0
leaderSkillTime=0.0
linksTime=0.0
totalTime=0.0

if(CALCUNITBASICS):
    totalTimeStart=time.time()
    unitBasics={}
    print("Creating all units basics")
    unitCount=0
    maxUnitCount=len(ownableCards)
    for unit in ownableCards:
        try:
            ezaTimeStart=time.time()
            ezaTrueFalse=["None"]
            if(checkEzaSQL(connection,unit[0])):
                ezaTrueFalse.append("EZA")
            if(checkSezaSQL(connection,unit[0])):
                ezaTrueFalse.append("SEZA")
            ezaTime+=time.time()-ezaTimeStart
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
                idStart=time.time()
                unitDictionary["ID"]=int(unit[0])
                idTime+=time.time()-idStart

                maxedStart=time.time()
                unitDictionary["Maxed"]=qualifyMaxedSQL(connection,unit[0])
                maxedTime+=time.time()-maxedStart

                nameStart=time.time()
                unitDictionary["Name"]=getNameSQL(connection,unit[0])
                nameTime+=time.time()-nameStart

                typeStart=time.time()
                unitDictionary["Type"]=getUnitTypeSQL(connection,unit[0])
                typeTime+=time.time()-typeStart

                rarityStart=time.time()
                unitDictionary["Rarity"]=getRaritySQL(connection,unit[0])
                rarityTime+=time.time()-rarityStart

                maxLevelStart=time.time()
                unitDictionary["Max Level"]=getMaxLevelSQL(connection,unit[0],eza or seza)
                maxLevelTime+=time.time()-maxLevelStart

                costStart=time.time()
                unitDictionary["Cost"]=int(unit[4])
                costTime+=time.time()-costStart

                ezaTimeStart=time.time()
                unitDictionary["Eza"]=eza
                unitDictionary["Seza"]=seza
                ezaTime+=time.time()-ezaTimeStart

                dokkanAwakenTimeStart=time.time()
                unitDictionary["Dokkan Awakened"]=canDokkanAwakenSQL(connection,unit[0])
                dokkanAwakenTime+=time.time()-dokkanAwakenTimeStart

                maxLevelStatsStart=time.time()
                maxLevelStats=getStatsAtHighestSQL(connection,unit[0],eza or seza)
                unitDictionary["HP"]=maxLevelStats["HP"]
                unitDictionary["Attack"]=maxLevelStats["ATK"]
                unitDictionary["Defense"]=maxLevelStats["DEF"]
                maxLevelStatsTime+=time.time()-maxLevelStatsStart
                
                releaseStart=time.time()
                if(eza):
                    unitDictionary["Release"]=getEzaReleaseTimeSQL(connection,unit[0],False)
                elif(seza):
                    unitDictionary["Release"]=getEzaReleaseTimeSQL(connection,unit[0],True)
                else:
                    unitDictionary["Release"]=getUnitReleaseTimeSQL(connection,unit[0])
                releaseTime+=time.time()-releaseStart

                characterStart=time.time()
                unitDictionary["Character"]=int(getCharacterNameID(unit))
                characterTime+=time.time()-characterStart

                spAtkLevelStart=time.time()
                unitDictionary["Sp Atk Lv"]=getSuperAttackLevel(unit,eza)
                if(eza):
                    unitDictionary["Sp ATK Lv"]=str(5+int(unit[14]))
                spAtkLevelTime+=time.time()-spAtkLevelStart
                
                activationTimeStart=time.time()
                if(unitDictionary["Rarity"]=="ur" or unitDictionary["Rarity"]=="lr"):
                    unitDictionary["Activation"]=1
                activationTime=round(time.time()-activationTimeStart,2)

                resourceIDStart=time.time()
                unitDictionary["Resource ID"]=unit[0]
                if(unit[48]!=""):
                    unitDictionary["Resource ID"]=str(int(float(unit[48])))
                if(unitDictionary["Resource ID"][-1]=="1"):
                    unitDictionary["Resource ID"]=(unitDictionary["Resource ID"][:-1]+"0")
                resourceIDTime+=time.time()-resourceIDStart
                
                classStart=time.time()
                unitDictionary["Class"]=getUnitClass(unit)
                classTime+=time.time()-classStart

                categoriesStart=time.time()
                #unitDictionary["Categories"]=getallcategories(unit[0],printing=True)
                unitDictionary["Categories"]=getAllCategoriesSQL(connection,unit[0])
                categoriesTime+=time.time()-categoriesStart

                awakeningStart=time.time()
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
                    unitDictionary["Maxed"]=False
                if("SEZA" in ezaTrueFalse and seza==False):
                    unitDictionary["Awakening"]["Super Extreme Z-Awakening"]=True
                    unitDictionary["Maxed"]=False
                awakeningTime+=time.time()-awakeningStart

                superAttackTypesStart=time.time()
                superAttackTypes=getSuperAttackTypesSQL(connection,unit[0],eza)
                unitDictionary["Super Attack Types"]=superAttackTypes
                superAttackTypesTime+=time.time()-superAttackTypesStart

                leaderSkillStart=time.time()
                unitDictionary["Leader Skill"]= parseLeaderSkill(unit,eza)
                leaderSkillTime+=time.time()-leaderSkillStart

                linksStart=time.time()
                unitDictionary["Links"]=getalllinks(unit)
                linksTime+=time.time()-linksStart

                if(eza):
                    unitBasics[unit[0]+"EZA"]=unitDictionary
                elif(seza):
                    unitBasics[unit[0]+"SEZA"]=unitDictionary
                else:
                    unitBasics[unit[0]]=unitDictionary

            print(unitCount,"/",maxUnitCount)
            unitCount+=1
        except Exception as e:
            print(unitCount,"/",maxUnitCount)
            print("FAIELD" , str(unit[0]) , str(e))
            unitCount+=1
    totalTimeEnd=time.time()
    totalTime=totalTimeEnd-totalTimeStart
            

    print("Turning unitBasics into json seperated by component")
    for component in unitDictionary:
        turnintoJson(filterSingleComponent(unitBasics,component), component,directoryName="temp_jsons/uniqueJsons/unitBasics")
        print("Finished:" + component)
print("Total time to calculate all unit basics:",round(totalTime,2),"seconds")
print("ID time:",round(idTime,2),"seconds")
print("Maxed time:",round(maxedTime,2),"seconds")
print("Name time:",round(nameTime,2),"seconds")
print("Type time:",round(typeTime,2),"seconds")
print("Rarity time:",round(rarityTime,2),"seconds")
print("Max Level time:",round(maxLevelTime,2),"seconds")
print("Cost time:",round(costTime,2),"seconds")
print("Eza time:",round(ezaTime,2),"seconds")
print("Dokkan Awaken time:",round(dokkanAwakenTime,2),"seconds")
print("Stats time:",round(statsTime,2),"seconds")
print("Release time:",round(releaseTime,2),"seconds")
print("Max Level Stats time:",round(maxLevelStatsTime,2),"seconds")
print("Character time:",round(characterTime,2),"seconds")
print("Sp Atk Level time:",round(spAtkLevelTime,2),"seconds")
print("Resource ID time:",round(resourceIDTime,2),"seconds")
print("Class time:",round(classTime,2),"seconds")
print("Categories time:",round(categoriesTime,2),"seconds")
print("Awakening time:",round(awakeningTime,2),"seconds")
print("Super Attack Types time:",round(superAttackTypesTime,2),"seconds")
print("Leader Skill time:",round(leaderSkillTime,2),"seconds")
print("Links time:",round(linksTime,2),"seconds")
print("Other time",round(totalTime-(idTime+maxedTime+nameTime+typeTime+rarityTime+maxLevelTime+costTime+ezaTime+dokkanAwakenTime+statsTime+releaseTime+maxLevelStatsTime+characterTime+spAtkLevelTime+resourceIDTime+classTime+categoriesTime+awakeningTime+superAttackTypesTime+leaderSkillTime+linksTime),2),"seconds")


