import time
from func import *

# Main logic

start_time = time.perf_counter() # performance check

# variables definition
api_key = get_text_from_file("C:/Users/48885/Documents/Python Knowledge/service_folder/key.txt")
if api_key is None:
    raise ValueError("API key could not be retrieved. Please check the file and try again.")
region = "EUW"
summoner_name = get_text_from_file("C:/Users/48885/Documents/Python Knowledge/service_folder/summoner.txt")
if api_key is None:
    raise ValueError("API key could not be retrieved. Please check the file and try again.")

# collect main data

# fetching data from api
acc_data = get_account_data_api(api_key, region, summoner_name)
if acc_data != None:
    puuid = acc_data.get('puuid')
    matchid_list = get_matchid_list_api(api_key, puuid, 3) # for debugging purposes amount of processed matches is limited to 3
    current_game_data = get_current_game_data(api_key, puuid)


    # debugging starts here
    if current_game_data == None:
        current_game_data = get_json_from_file("C:/Users/48885/Documents/Python Knowledge/service_folder/participants.json") # replace the file with current game json from spectator api
    # debugging ends here 


    if current_game_data != None:
        #loop through the list of matches and adding match data to a dictionary
        dic_all_matches_data = {matchid: get_match_data_api(api_key, matchid) for matchid in matchid_list}

        # local data processing
        dic_all_matches_participants = {key: value["metadata"]["participants"] for key, value in dic_all_matches_data.items()}
        matching_participants = get_matching_participants(dic_all_matches_data, current_game_data, puuid)

        # results output
        if matching_participants is not None:
            for p in matching_participants:
                print(p)
        else: print('No matches')

end_time = time.perf_counter() # performance check
elapsed_time = end_time - start_time # performance check
print(f"Elapsed time: {elapsed_time:.4f} seconds")



