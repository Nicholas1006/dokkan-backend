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