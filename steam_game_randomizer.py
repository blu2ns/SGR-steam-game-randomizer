import requests,os,json,random,time,subprocess,climage,datetime
from pathlib import Path

def main():
    api_key = ""
    user_id = ""
    randomized_game_list = []
    previous_games = []

    file_path,img_path = create_storage_files()
    with open(f'{file_path}exclusion_list.json', 'r') as exclusion_file: 
        exclusion_data = json.load(exclusion_file) 
        permanently_excluded = exclusion_data['permanently_excluded']
        temporarily_excluded = ""
        
    get_games(file_path,api_key,user_id)
    permanently_excluded_split,all_game_details,game_num = parse_game_data(file_path, permanently_excluded)

    if_go_back = False
    reroll_queue = False

    clear_terminal()
    choice = input("Refresh game image cache? This step is only necessary to do once. It may take a while but rolls will happen faster after.\n[R] Refresh all images [G] Get missing images [Other] Continue without refresh.\n")
    if choice.lower() == 'r':
        refresh_img_cache(file_path,img_path,all_game_details,permanently_excluded,refresh_all=True)
    elif choice.lower() == 'g':
        refresh_img_cache(file_path,img_path,all_game_details,permanently_excluded,refresh_all=False)
    while 1:
        title, playtime, app_url, app_id, last_played, randomized_game_list, previous_games = randomize_game(all_game_details, permanently_excluded, temporarily_excluded,if_go_back, reroll_queue, randomized_game_list, previous_games,file_path)
        
        print_game_image(file_path,app_id,img_path,title)

        if last_played != 0:
            last_played = datetime.datetime.fromtimestamp(last_played).strftime("%B %d, %Y at %I:%M %p")
        else:
            last_played = "Never played."

        print(f"{title}\nPlaytime: {playtime}\nLast Played: {last_played}")
        print("-" * 80)

        print(f"[ENTER] Reroll   [R] Reroll Queue   [RUN] Launch {title}\n[C] Exclusions   [X] Exclude Perm   [Z] Exclude Session\n[B] Go Back      [E] Exit    ")
        choice = input("Choice: ")
        if_go_back = False
        reroll_queue = False

        if choice.lower() == 'run': #launch game
            try:
                subprocess.Popen(["steam", f"steam://rungameid/{app_id}"])
            except Exception as e:
                print(f"Unable to run game with error {e}.")
        
        elif choice.lower() == 'x': #exclude game permanently
            clear_terminal()
            
            permanently_excluded_split = permanently_excluded.split('|')
            if title in permanently_excluded_split:
                print("Game already in exclusion list.")
            else:
                print(f"{title} excluded permanently.")
                if permanently_excluded != "":
                    permanently_excluded = str(permanently_excluded) + "|" + str(title)
                else:
                    permanently_excluded = title

                
                with open(f'{file_path}exclusion_list.json','w') as file:
                    data = {
                        "permanently_excluded": f"{permanently_excluded}"
                    }
                    json.dump(data,file,indent=4)
                for game in range(len(all_game_details)):
                    try:
                        if all_game_details[game][0] == title:
                            all_game_details.pop(game)
                            break
                    except:
                        print(f"Error {e}.")
                        input()
            time.sleep(1)
        elif choice.lower() == 'z': #exclude game temporarily
            clear_terminal()
            print(f"{title} excluded temporarily.")

            if temporarily_excluded != "":
                temporarily_excluded = str(temporarily_excluded) + "|" + str(title)
            else:
                temporarily_excluded = title

            for game in range(len(all_game_details)):
                try:
                    if all_game_details[game][0] == title:
                        all_game_details.pop(game)
                        break
                except:
                    print(f"Error {e}.")
                    input()
            time.sleep(1)

        elif choice.lower() == 'c': #see list of excluded games
            clear_terminal()

            permanently_excluded_split = permanently_excluded.split('|')
            temporarily_excluded_split = temporarily_excluded.split('|')

            if permanently_excluded_split[0] != '':
                print("List of permanently excluded items:")
                for n in range(len(permanently_excluded_split)):
                    print(f"{n}) {permanently_excluded_split[n]}")
            else:
                print("No permanently excluded games.")
            print('')
            if temporarily_excluded_split[0] != '':
                print("List of temporarily excluded items:")
                for n in range(len(temporarily_excluded_split)):
                    print(f"{n}) {temporarily_excluded_split[n]}")
            else:
                print("No temporarily excluded games.")
            print('')
            choice = str(input("Input the first letter of the exclusion pool you would like to remove from, followed by the number associated with the game you would like to remove. Eg. (p2,t4), etc. \n[Clear P] Clear Permanently Excluded list. [Clear T] Clear Temporarily Excluded list. [Enter] Continue.\n"))
            
            try: 
                if choice != '':
                    if choice[0:7].lower() != 'clear p' and choice[0:7].lower() != 'clear t':
                        try:
                            pool_choice = choice[0]
                            number_choice = int(choice[1:len(choice)])
                        except:
                            clear_terminal()
                            print("Invalid Input. Try again later.")
                            time.sleep(3)
                    if choice[0:7].lower() == 'clear p' or choice[0:7].lower() == 'clear t':
                        if choice[6] == 'p':
                            permanently_excluded = ''
                            permanently_excluded_split = []
                            with open(f'{file_path}exclusion_list.json','w') as file:
                                data = {
                                    "permanently_excluded": f"{permanently_excluded}"
                                }
                                json.dump(data,file,indent=4)
                                
                            print("Rerolling game queue based on new exclusion list..")
                            time.sleep(1.5)
                            randomize_game(all_game_details, permanently_excluded, temporarily_excluded,if_go_back, True, randomized_game_list, previous_games,file_path)
                            
                        elif choice[6] == 't':
                            temporarily_excluded = ''
                            temporarily_excluded_split = []

                            print("Rerolling game queue based on new exclusion list..")
                            time.sleep(1.5)
                            randomize_game(all_game_details, permanently_excluded, temporarily_excluded,if_go_back, True, randomized_game_list, previous_games,file_path)
                        permanently_excluded_split,all_game_details,game_num = parse_game_data(file_path, permanently_excluded)    
                    elif isinstance(number_choice, int) and (pool_choice == 'p' or pool_choice == 't'):
                        try:
                            if pool_choice == 't': 
                                if temporarily_excluded_split[number_choice] != '':

                                    removed_title = temporarily_excluded_split.pop(number_choice)
                                    temporarily_excluded = ""

                                    for game in range(len(temporarily_excluded_split)):
                                        temporarily_excluded = '|'.join(temporarily_excluded_split)
                                    clear_terminal()
                                    print(f"{removed_title} removed.")
                                    time.sleep(1)
                                else: print("No game located at that position.")
                            else: 
                                permanently_excluded_split = permanently_excluded.split('|')

                                if permanently_excluded_split[number_choice] != '':

                                    removed_title = permanently_excluded_split.pop(number_choice)
                                    permanently_excluded = ""

                                    for game in range(len(permanently_excluded_split)):
                                        permanently_excluded = "|".join(permanently_excluded_split)
                                    with open(f'{file_path}exclusion_list.json','w') as file:
                                        data = {
                                            "permanently_excluded": f"{permanently_excluded}"
                                        }
                                        json.dump(data,file,indent=4)
                                    clear_terminal()
                                    print(f"{removed_title} removed.")
                                    time.sleep(1)
                                else: print("No game located at that position.")
                        except Exception as e:
                            print(f"No game located at that position. {e}")
                            time.sleep(4)
                        permanently_excluded_split,all_game_details,game_num = parse_game_data(file_path, permanently_excluded)
                        time.sleep(1)
                    else:
                        print("Invalid Input. Try again later.")
                        time.sleep(3)
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(3)
        
        elif choice.lower() == 'b': # go back by one game
            if_go_back = True

        elif choice.lower() == 'r': #reroll the roll queue
            reroll_queue = True

        elif choice.lower() == 'e': #exit
            exit()

def print_game_image(file_path,app_id,img_path,title):

    img_path = os.path.join(str(file_path), "images", f"{app_id}.jpg")
    #print(img_path)
    if os.path.exists(img_path) != True:
        print(f"Getting image for {title}. The first time a game is rolled may take longer due to this. Once images are cached, rolls will be faster.")

        try:
            url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/library_hero.jpg"
            response = requests.get(url)

            if response.status_code != 200:
                url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{app_id}/header.jpg"
                response = requests.get(url)    

            with open(img_path, "wb") as f:
                f.write(response.content)
            clear_terminal()
            
        except:
            print("Game image not found.")

    try: 
        print("-" * 80,'\n') 
        image = climage.convert(img_path,is_unicode=True, is_truecolor=True, is_256color=False, width=80)
        rows = image.split('\n')

        for index, row in enumerate(rows):
            print(f'{row}')
            if index >= 11: break
        print()
    except:
        print("Game image not found.")

    print("-" * 80)

def refresh_img_cache(file_path,img_path,all_game_details,permanently_excluded,refresh_all):
    parse_game_data(file_path,permanently_excluded)

    for game in range(len(all_game_details)):
        title = all_game_details[game][0]
        id = all_game_details[game][3]
        img_path = os.path.join(str(file_path), "images", f"{id}.jpg")
        if refresh_all == False and os.path.exists(img_path) == True:
            print(f"Image already exists for {title}. Skipping.")
            time.sleep(0.01)
            clear_terminal()
            continue
        try:
            clear_terminal()
            print(f"Getting image for {title}. [{game + 1}/{len(all_game_details)}]")
            url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{id}/library_hero.jpg"
            response = requests.get(url)

            if response.status_code != 200:
                url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{id}/header.jpg"
                response = requests.get(url)    

            with open(img_path, "wb") as f:
                f.write(response.content)
            clear_terminal()
            print(f"Image found for {title}. [{game + 1}/{len(all_game_details)}]")
        except:
            print(f"Game image and backup game image for {title} not found.")

    input("Game images successfully cached. [Enter] Continue\n")

def parse_game_data(file_path,permanently_excluded):
    try:
        with open(f'{file_path}last_game_data.json', 'r') as game_file: 
            data = json.load(game_file) 
        game_num = data['response']['game_count']
        all_game_details = []
    except Exception as e:
        print(f'Game cache empty and/or cache file not found. Rerun the program and refresh the cache. {e}')
        time.sleep(5)
        exit()

    for game in range(game_num):
        try:
            game_details = [
                data['response']['games'][game]['name'],
                data['response']['games'][game]['playtime_forever'] + data['response']['games'][game]['playtime_disconnected'],
                data['response']['games'][game]['img_icon_url'],
                data['response']['games'][game]['appid'],
                data['response']['games'][game]['rtime_last_played']
            ]
            all_game_details.append(game_details)
        except:
            break

    permanently_excluded_split = permanently_excluded.split('|')
    all_game_details = [game for game in all_game_details if game[0] not in permanently_excluded_split]
    return permanently_excluded_split, all_game_details,game_num

def get_games(file_path,api_key,user_id):
    choice = input(f"{"-" * 80}\nWelcome to the Steam Game Randomizer.\n[Y] Refresh game cache. (required for first ever program run) [Other] Continue without refresh.\n")
    
    if choice.lower() == 'y' or choice.lower() == 'ydebug':
        try:
            clear_terminal()

            try:
                print("Opening file with User ID & API Key..")
                with open(f'{file_path}keyids.json', 'r') as ids_file: 
                    data = json.load(ids_file) 
                    api_key = data['api_key']
                    user_id = data['user_id']
            except:
                create_storage_files()

            if api_key == '' or user_id == '':
                print("API Key and/or User ID not found.")
                time.sleep(5)
                exit()

            print("API Key and User ID found.\nMaking API request...")
            url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={user_id}&format=json&include_appinfo=1&include_played_free_games=1&skip_unvetted_apps=false"
            response = requests.get(url)

            print(f"Got response with status code {response.status_code}.")
            time.sleep(0.5)
            if choice.lower() == 'ydebug':
                print(json.dumps(response.json(), indent=4))
                input("[Enter] Continue")

            game_data = response.json()
            with open(f'{file_path}last_game_data.json', 'w') as game_file:
                json.dump(game_data, game_file, indent=4)
            print(f"Game list successfully refreshed and cached.")
            time.sleep(0.5)

        except Exception as e:
            print(f"Error: {e}")
            input("[Enter] Continue")
    
def clear_terminal(): os.system('cls' if os.name == 'nt' else 'clear')

def create_storage_files():

    file_path = r"~/"
    file_path = Path(__file__).resolve().parent
    file_path = os.path.join(str(file_path), "storage", "")

    try:
        os.mkdir(file_path)
    except:
        pass

    try:
        img_path = ''
        img_path = os.path.join(str(file_path), "images", "")
        os.mkdir(img_path)
    except Exception as e:
        pass

    if os.path.exists(f'{file_path}exclusion_list.json') == False or os.path.exists(f'{file_path}keyids.json') == False or os.path.exists(f'{file_path}last_game_data.json') == False:
        
        choice = input("One or more storage files not found. [Y] Create Files [Other] Close Program\n")
        clear_terminal()

        if choice.lower() == 'y':
            print(f"Closing the program during this file creation process could lead to issues when running the program later on.\nIf so, delete the files manually at {file_path} and try again.")
            sleep(3)
            input("[Enter] Continue\n")
            clear_terminal()

            print(f"Creating game exlusion storage file at {file_path}exclusion_list.json.")
            time.sleep(3)
            clear_terminal()
            with open(f'{file_path}exclusion_list.json', 'w') as file: 
                data = {
                    "permanently_excluded": ""
                }
                json.dump(data,file,indent=4)

            api_key = input(f"Input API key. This can be changed later by opening {file_path}keyids.json.\nA guide to getting this can be found on the github page.\n")
            clear_terminal()
            print("API key added.")
            time.sleep(1)
            clear_terminal()
            user_id = input(f"Input User ID. This can be changed later by opening {file_path}keyids.json.\nA guide to finding this can be found on the github page.\n")
            clear_terminal()
            print("User ID added.")
            time.sleep(1)
            print(f"Storing credentials at {file_path}keyids.json.")
            with open(f'{file_path}keyids.json', 'w') as file: 
                data = {
                    "api_key": f"{api_key}",
                    "user_id": f"{user_id}"
                }
                json.dump(data,file,indent=4)
            time.sleep(3)
            clear_terminal()
            print(f"Creating empty storage file at {file_path}last_game_data.json.")
            time.sleep(3)
            clear_terminal()
            with open(f'{file_path}last_game_data.json', 'w') as file: 
                data = {}
                json.dump(data,file,indent=4)
            
        else:
            exit()
    return file_path,img_path

def randomize_game(all_game_details, permanently_excluded, temporarily_excluded, if_go_back, reroll_queue, randomized_game_list, previous_games,file_path):

    if len(randomized_game_list) == 0 or reroll_queue == True:
        random.shuffle(all_game_details)
        randomized_game_list = all_game_details.copy()

    permanently_excluded_split = permanently_excluded.split('|')
    temporarily_excluded_split = temporarily_excluded.split('|')

    game_choice = []
    clear_terminal()

    if if_go_back == False:
        try:
            game_choice = randomized_game_list.pop(0)
            previous_games.append(game_choice)
        except:
            choice = input("No games found in list. Either you're very picky or you own no steam games. [Y] Clear exclusion preferences. [Other] Close program\n")
            if choice.lower() == 'y':
                permanently_excluded = ''
                temporarily_excluded = ''
                with open(f'{file_path}exclusion_list.json','w') as file:
                    json.dump({"permanently_excluded": ""}, file, indent=4)

                _, all_game_details, _ = parse_game_data(file_path, permanently_excluded)
                random.shuffle(all_game_details)
                randomized_game_list = all_game_details.copy()
                game_choice = randomized_game_list.pop(0)
                previous_games.append(game_choice)
            else:
                exit()
    else:
        try:
            randomized_game_list.insert(0, previous_games.pop()) 
            game_choice = previous_games[len(previous_games) - 1]  
        except:
            print("No previous games.")
            game_choice = randomized_game_list.pop(0)
            previous_games.append(game_choice)

    try:
        title = game_choice[0]; app_url = game_choice[2]; app_id = game_choice[3]; last_played = game_choice[4]
    except Exception as e:
        print(f"Error reading game data: {e}")

    total_minutes = int(game_choice[1])

    if total_minutes >= 60:
        hours = total_minutes // 60
        minutes = total_minutes % 60
        if minutes == 0:
            playtime = f"{hours} hr{'s' if hours > 1 else ''}"
        else:
            playtime = f"{hours} hr{'s' if hours > 1 else ''}, {minutes} min"
    else:
        playtime = f"{total_minutes} min" if total_minutes > 0 else "Never played."

    return title, playtime, app_url, app_id, last_played, randomized_game_list, previous_games

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        exit()