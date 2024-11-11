import csv
def storedatabase(directory,name,printing=True):
    directory+=name
    file = open(directory, encoding="utf-8-sig")
    dbtemp=csv.reader(file)
    name=[]
    for row in dbtemp:
        name.append(row)
    return(name)

directoryGB="dataGB/"

active_skillsGB=storedatabase(directoryGB,"active_skills.csv")
active_skill_setsGB=storedatabase(directoryGB,"active_skill_sets.csv")
battle_paramsGB=storedatabase(directoryGB,"battle_params.csv")

cardsGB=storedatabase(directoryGB,"cards.csv")
card_active_skillsGB=storedatabase(directoryGB,"card_active_skills.csv")
card_awakening_routesGB=storedatabase(directoryGB,"card_awakening_routes.csv")
card_card_categoriesGB=storedatabase(directoryGB,"card_card_categories.csv")
card_categoriesGB=storedatabase(directoryGB,"card_categories.csv")
card_finish_skill_set_relationsGB=storedatabase(directoryGB,"card_finish_skill_set_relations.csv")
card_growthsGB=storedatabase(directoryGB,"card_growths.csv")
card_specialsGB=storedatabase(directoryGB,"card_specials.csv")
card_standby_skill_set_relationsGB=storedatabase(directoryGB,"card_standby_skill_set_relations.csv")
card_unique_info_set_relationsGB=storedatabase(directoryGB,"card_unique_info_set_relations.csv")

dokkan_fieldsGB=storedatabase(directoryGB,"dokkan_fields.csv")
dokkan_field_passive_skill_relationsGB=storedatabase(directoryGB,"dokkan_field_passive_skill_relations.csv")

finish_skill_setsGB=storedatabase(directoryGB,"finish_skill_sets.csv")
finish_skillsGB=storedatabase(directoryGB,"finish_skills.csv")
finish_specialsGB=storedatabase(directoryGB,"finish_specials.csv")

leader_skillsGB=storedatabase(directoryGB,"leader_skills.csv")
leader_skill_setsGB=storedatabase(directoryGB,"leader_skill_sets.csv")
link_skillsGB=storedatabase(directoryGB,"link_skills.csv")
link_skill_efficaciesGB=storedatabase(directoryGB,"link_skill_efficacies.csv")
link_skill_lvsGB=storedatabase(directoryGB,"link_skill_lvs.csv")

optimal_awakening_growthsGB=storedatabase(directoryGB,"optimal_awakening_growths.csv")

passive_skillsGB=storedatabase(directoryGB,"passive_skills.csv")
passive_skill_setsGB=storedatabase(directoryGB,"passive_skill_sets.csv")
passive_skill_set_relationsGB=storedatabase(directoryGB,"passive_skill_set_relations.csv")
potential_eventsGB=storedatabase(directoryGB,"potential_events.csv")
potential_squaresGB=storedatabase(directoryGB,"potential_squares.csv")
potential_square_relationsGB=storedatabase(directoryGB,"potential_square_relations.csv")

skill_causalitiesGB=storedatabase(directoryGB,"skill_causalities.csv")
specialsGB=storedatabase(directoryGB,"specials.csv")
special_bonusesGB=storedatabase(directoryGB,"special_bonuses.csv")
special_setsGB=storedatabase(directoryGB,"special_sets.csv")
special_viewsGB=storedatabase(directoryGB,"special_views.csv")
standby_skillsGB=storedatabase(directoryGB,"standby_skills.csv")
standby_skill_setsGB=storedatabase(directoryGB,"standby_skill_sets.csv")
sub_target_typesGB=storedatabase(directoryGB,"sub_target_types.csv")
ultimate_specialsGB=storedatabase(directoryGB,"ultimate_specials.csv")
