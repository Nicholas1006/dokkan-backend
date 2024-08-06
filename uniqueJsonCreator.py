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

    domains_json[domain[2]]=domain_dictionary


turnintoJson(domains_json, "domains",directoryName="../frontend/dbManagement/uniqueJsons")