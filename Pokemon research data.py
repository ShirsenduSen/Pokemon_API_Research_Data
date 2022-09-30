##################################
#  Pokemon research API Data Generator 1.0 #
##################################

# This code will coomplete the following tasks a csv file will be generated and can be saved in the same location
# This code is developed using Pycharm IDE and python 3.9. developed by Shirsendu Sen
#1.The name, id, base_experience, weight, height and order of all Pokémon that appear in the any of the games red, blue, leafgreen or white.
#2. The name of the slot 1 (and if available 2) type of each of the Pokémon's types.
#3. The Body Mass Index of the Pokémon (hint: The formula for BMI is weight (kg) / height (m2))
#4. The first letter of names of the Pokémon should be capitalized.
#5. The url of the front_default sprite.
#6. Prepare the data in an appropriate data format. Consider if it should be multiple or a single file.

#import required packages
import requests
import configparser
import json
import re
import pandas as pd
import ast

# read the config file using configparser
config = configparser.ConfigParser()
config.read("pokemon_config.ini")
# read the pokeapi pokemon url
pokemon_url = config.get('pokemon', 'pokemon_url')
# read the pokeapi pokemon games url
pokemon_games_url = config.get('pokemon','pokemon_games_url')
# Data collection list
pokemon_data_list = []
# Construct the dictionary
pokemon_dic = {"Pokemon_name": [], "Pokemon_id": [], "Pokemon_base_experience": [],
               "Pokemon_weight": [], "Pokemon_height": [],
               "Pokemon_order": [], "Pokemon_body_mass_index": [],
               "Pokemon_sprite_front_default": [], "Pokemon_slot_type_name": []}

# Function to call the pokeapi


def pokemon_req():

    # first we need to check the mentioned games and the pokemon species
    pokemon_species = []
    games_version = ast.literal_eval(config.get('pokemon', 'games_version'))
    games_url_response = requests.get(pokemon_games_url)
    # find the limit for the games url
    games_url_limit = games_url_response.json()
    games_url_limit_count = games_url_limit ["count"]
    # now we need to search and filter the pokemons based on the pokemon games
    for generation in range(1, games_url_limit_count):
        get_games_and_species = requests.get(pokemon_games_url+str(generation))
        games_and_species_json = get_games_and_species.json()
        for versions in games_and_species_json["version_groups"]:
            v_name = versions["name"]
            # this flag will determine the match of the games_version
            flag = 0
            # wildcard search for the specified games_version
            for each_games_version in games_version:
                if re.search(each_games_version+".", v_name) and flag == 0:
                    flag = 1
                    for each_species in games_and_species_json["pokemon_species"]:
                        # this is to ensure that we do not collect duplicate pokemon names
                        pokemon_species.append(each_species["name"]) if each_species["name"] not in pokemon_species else None

    # we have now selected species to find the attributes
    # We need to get the attributes data
    for pokemon_name in pokemon_species:
        pokemon_response = requests.get(pokemon_url+pokemon_name + "/")

        # check if the response status code is 200 then collect all the information/ attributes
        if pokemon_response.status_code == 200:
            pokemon_response = pokemon_response.text
            pokemon_entities_data = json.loads(pokemon_response)
            # capitalize the first letter of the Pokemon name
            pokemon_dic["Pokemon_name"] = pokemon_name.capitalize()
            pokemon_dic["Pokemon_id"] = pokemon_entities_data["id"]
            pokemon_dic["Pokemon_base_experience"] = pokemon_entities_data["base_experience"]
            pokemon_dic["Pokemon_weight"] = pokemon_entities_data["weight"]
            pokemon_dic["Pokemon_height"] = pokemon_entities_data["height"]
            pokemon_dic["Pokemon_order"] = pokemon_entities_data["order"]
            # calculate the BMI
            pokemon_dic["Pokemon_body_mass_index"] = format((pokemon_entities_data["weight"]/(pokemon_entities_data["height"])**2), '.2f')
            # collect the url for the front_default sprite
            pokemon_dic["Pokemon_sprite_front_default"] = pokemon_entities_data["sprites"]["front_default"]
            pokemon_slot_type_name = []
            # collect the slots name
            for slots in pokemon_entities_data["types"]:
                pokemon_slot_type_name.append(slots["type"]["name"])
            pokemon_dic["Pokemon_slot_type_name"] = pokemon_slot_type_name
            # collect all the dictionary in to the final list
            pokemon_data_list.append(pokemon_dic.copy())
    # Normalize the slot list with df.explode method
    pokemon_df = pd.DataFrame(pokemon_data_list)
    pokemon_df = pokemon_df.explode('Pokemon_slot_type_name')

    # save the file in CSV file
    pokemon_df.to_csv("Pokemon_research_data.csv")

# Create the object
Pokemon_research_API_data = pokemon_req()