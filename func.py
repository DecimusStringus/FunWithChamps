import requests
import json
import datetime

class matching_player:
    def __init__(self, puuid, match, date, username):
        self.puuid = puuid
        self.match = match
        self.date = date
        self.username = username

    def __repr__(self):
        return f"{self.puuid}, {self.match}, {self.date}, {self.username}"


# get text from file
def get_text_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            api_key = file.readline().strip()
            return api_key
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_json_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} is not a valid JSON file.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# get a user information by summoner name
def get_account_data_api(api_key, region, summoner_name):
    """
    Fetch account data from the Riot Games API.
    
    Parameters:
        api_key (str): The API key for authentication.
        region (str): The region of the summoner (e.g., "euw", "na1").
        summoner_name (str): The summoner's name.
    Returns:
        dict: The JSON data from the API response if successful.
        None: If the request fails.
    """
    url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{region}"
    headers = {"X-Riot-Token": api_key}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()  # Return the data if the request is successful
    else:
        print(f"get_account_data_api error: {response.status_code}")
        return None
    
# get a list of match ids by puuid
def get_matchid_list_api(api_key, puuid, count):
    """
    Fetch a list of match ids from the Riot Games API.
    
    Parameters:
        api_key (str): The API key for authentication.
        puuidr (str): The summoner's puuid
    Returns:
        list: list from JSON data from the API response if successful.
        None: If the request fails.
    """
    url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}"
    headers = {"X-Riot-Token": api_key}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, list):  # Check if the response is a list
            return data
        else:
            print("get_matchid_list_api error: expected a list but got something else.")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None

# get a match data by match id
def get_match_data_api(api_key, matchid):
    """
    Fetch match data from the Riot Games API.
    
    Parameters:
        api_key (str): The API key for authentication.
        region (str): The region of the summoner (e.g., "euw", "na1").
        summoner_name (str): The summoner's name.
    Returns:
        dict: The JSON data from the API response if successful.
        None: If the request fails.
    """
    url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{matchid}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Return the data if the request is successful
    else:
        print(f"get_match_data_api error: {response.status_code}")
        return None

# get a list of a match participants
def get_match_participants(dic_all_matches_data, matchid):
    """
    Fetch match data from the local dictionary.
    
    Parameters:
        dic_all_matches_data (dic): dictionary with matches data.
        matchid (str): ID of a match (e.g., "EUW1_7274848114").
    Returns:
        list: list of the match participants.
        None: If the request fails.
    """
    lv_match_data = dic_all_matches_data.get(matchid, "not found")
    if lv_match_data != "not found":
        return lv_match_data["metadata"]["participants"]
    else:
        return None

def get_match_participants_excl(dic_all_matches_data, matchid, excluding):
    """
    Fetch match data from the local dictionary, excluding selected players' puuids.
    
    Parameters:
        dic_all_matches_data (dic): dictionary with matches data.
        matchid (str): ID of a match (e.g., "EUW1_7274848114").
        excluding (list): List of excluded users (e.g. own user)
        
    Returns:
        list: list of the match participants.
        None: If the request fails.
    """
    lv_match_data = dic_all_matches_data.get(matchid, "not found")

    #for player_puuid in lv_match_data["metadata"]["participants"]:
    if lv_match_data != "not found":
        return [player_puuid for player_puuid in lv_match_data["metadata"]["participants"] if player_puuid not in excluding]
    else:
        return None

# get a list of a match participants
def get_matching_participants(dic_all_matches_data, current_game_data, excluding):
    """
    Fetch a match data from the local dictionary.
    
    Parameters:
        dic_all_matches_data (dic): dictionary with all matches data.
        current_game_data (?): current game data.
        excluding (list): List of excluded users (e.g. own user)
    Returns:
        list: list of the matching participants with additional info.
        None: If the request fails.
    Notes:
        Function uses custom class matching_player(self, puuid, username, match, date)
    """
    lv_temp_list = [] # define temporary list
    current_players = []
    dic_current_players = {}
    current_players = [player.get('puuid','') for player in current_game_data.get("participants", ['nothing']) if player.get('puuid','') not in excluding]
    dic_current_players = {player.get('puuid',''): player.get('riotId','XXX') for player in current_game_data.get("participants", ['nothing']) if player.get('puuid','') not in excluding}

    # for player_puuid in current_players:
    for player_puuid in dic_current_players.keys():
        for value in dic_all_matches_data.items():
            if player_puuid in value[1]["metadata"]["participants"]:
                time_str = value[1]["info"]["gameStartTimestamp"]
                
                lv_temp_list.append(matching_player(player_puuid, value[1]["metadata"]["matchId"],datetime.datetime.fromtimestamp(time_str/1000).strftime('%Y-%m-%d %H:%M:%S'), get_text_before_hash(dic_current_players[player_puuid])))

    if lv_temp_list == None:
        lv_temp_list = ['Karamba'] # dummy value
    return lv_temp_list

# get current game information for the given puuid
# https://euw1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/u_jO0B5BACHmW8GnMOQ9gLoGFKkh4TwDxr7v9dZhIBO00Jg04QXol765K-fu0cGJiTP4lJu2ANBvsw
def get_current_game_data(api_key, puuid):
    """
    Fetch account data from the Riot Games API.
    
    Parameters:
        api_key (str): The API key for authentication.
        puuid (str): The summoner's puuid.

    Returns:
        json: The json data from the API response if successful.
        None: If the request fails.
    """
    url = f"https://euw1.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"
    headers = {"X-Riot-Token": api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()  # Return the data if the request is successful
    else:
        print(f"Error: {response.status_code}")
        return None

# return the text before the hash symbol 
def get_text_before_hash(input_string):
    # split by #
    parts = input_string.split('#')
    # return first part (before #)
    return parts[0]