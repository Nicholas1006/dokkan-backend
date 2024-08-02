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

directoryJP="dataJP/"

active_skillsJP=storedatabase(directoryJP,"active_skills.csv")
active_skill_setsJP=storedatabase(directoryJP,"active_skill_sets.csv")
battle_paramsJP=storedatabase(directoryJP,"battle_params.csv")

cardsJP=storedatabase(directoryJP,"cards.csv")
card_active_skillsJP=storedatabase(directoryJP,"card_active_skills.csv")
card_awakening_routesJP=storedatabase(directoryJP,"card_awakening_routes.csv")
card_card_categoriesJP=storedatabase(directoryJP,"card_card_categories.csv")
card_categoriesJP=storedatabase(directoryJP,"card_categories.csv")
card_finish_skill_set_relationsJP=storedatabase(directoryJP,"card_finish_skill_set_relations.csv")  
card_growthsJP=storedatabase(directoryJP,"card_growths.csv")
card_specialsJP=storedatabase(directoryJP,"card_specials.csv")
card_standby_skill_set_relationsJP=storedatabase(directoryJP,"card_standby_skill_set_relations.csv")
card_unique_info_set_relationsJP=storedatabase(directoryJP,"card_unique_info_set_relations.csv")

dokkan_fieldsJP=storedatabase(directoryJP,"dokkan_fields.csv")
dokkan_field_passive_skill_relationsJP=storedatabase(directoryJP,"dokkan_field_passive_skill_relations.csv")

finish_skillsJP=storedatabase(directoryJP,"finish_skills.csv")
finish_skill_setsJP=storedatabase(directoryJP,"finish_skill_sets.csv")
finish_specialsJP=storedatabase(directoryJP,"finish_specials.csv")

leader_skillsJP=storedatabase(directoryJP,"leader_skills.csv")
leader_skill_setsJP=storedatabase(directoryJP,"leader_skill_sets.csv")
link_skillsJP=storedatabase(directoryJP,"link_skills.csv")
link_skill_efficaciesJP=storedatabase(directoryJP,"link_skill_efficacies.csv")
link_skill_lvsJP=storedatabase(directoryJP,"link_skill_lvs.csv")

optimal_awakening_growthsJP=storedatabase(directoryJP,"optimal_awakening_growths.csv")

passive_skillsJP=storedatabase(directoryJP,"passive_skills.csv")
passive_skill_setsJP=storedatabase(directoryJP,"passive_skill_sets.csv")
passive_skill_set_relationsJP=storedatabase(directoryJP,"passive_skill_set_relations.csv")
potential_eventsJP=storedatabase(directoryJP,"potential_events.csv")
potential_squaresJP=storedatabase(directoryJP,"potential_squares.csv")
potential_square_relationsJP=storedatabase(directoryJP,"potential_square_relations.csv")

skill_causalitiesJP=storedatabase(directoryJP,"skill_causalities.csv")
specialsJP=storedatabase(directoryJP,"specials.csv")
special_bonusesJP=storedatabase(directoryJP,"special_bonuses.csv")
special_setsJP=storedatabase(directoryJP,"special_sets.csv")
special_viewsJP=storedatabase(directoryJP,"special_views.csv")
standby_skillsJP=storedatabase(directoryJP,"standby_skills.csv")
standby_skill_setsJP=storedatabase(directoryJP,"standby_skill_sets.csv")
sub_target_typesJP=storedatabase(directoryJP,"sub_target_types.csv")

ultimate_specialsJP=storedatabase(directoryJP,"ultimate_specials.csv")