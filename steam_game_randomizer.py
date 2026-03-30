import requests,os,json,random,time,subprocess,climage,datetime
from pathlib import Path

api_key = ""
user_id = ""

file_path = r"~/"
file_path = Path(__file__).resolve().parent
file_path = os.path.join(str(file_path), "storage", "")
try:
    os.mkdir(file_path)
except:
    pass
randomized_game_list = []
previous_games = []

def get_games():
    create_storage_files()
    with open(f'{file_path}exclusion_list.json', 'r') as exclusion_file: 
        exclusion_data = json.load(exclusion_file) 
        permanently_excluded = exclusion_data['permanently_excluded']
        temporarily_excluded = ""
    print("-" * 30)
    choice = input("Welcome. Input 'Y' to get a refreshed game list. Any other key uses cached data.\n")
    
    if choice.lower() == 'y' or choice.lower() == 'ydebug':
        try:
            clear_terminal()

            print("Opening file with User ID & API Key..")
            try:
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
            print("API Key and User ID found.")
            print("Making API request...")
            url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={user_id}&format=json&include_appinfo=1&include_played_free_games=1"
            response = requests.get(url)

            print(f"Got response with status code {response.status_code}.")
            time.sleep(1)
            if choice.lower() == 'ydebug':
                print(json.dumps(response.json(), indent=4))
                input("Input any key to continue.")
            game_data = response.json()

            with open(f'{file_path}last_game_data.json', 'w') as game_file:
                json.dump(game_data, game_file, indent=4)

            print(f"Game list refreshed and cached.")
            time.sleep(0.1)
        except Exception as e:
            print(f"Error: {e}")
            input(f'Press any key to continue.\n')
    try:
        with open(f'{file_path}last_game_data.json', 'r') as game_file: 
            data = json.load(game_file) 
        game_num = data['response']['game_count']
        all_game_details = []
    except:
        print('Invalid input and/or Game cache empty and/or cache file not found. Rerun the program and refresh the cache.')
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

    if_go_back = False
    reroll_queue = False

    img_path = os.path.join(str(file_path), "tmp")
    img_path = os.path.join(file_path, "") 
    
    while 1:
        title, playtime,app_url,app_id,last_played = randomize_game(all_game_details,permanently_excluded,temporarily_excluded,if_go_back,reroll_queue)
        

        if os.path.exists(img_path) != True:
            print("Getting game image. The first time a game is rolled may take longer due to this. Once cached, rolls will be faster.")
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
        print("-" * 80,'\n')   
        try: 
            image = climage.convert(img_path,is_unicode=True, is_truecolor=True, is_256color=False, width=80)
            print(image)
        except:
            print("Game image not found.")
        print("-" * 80)
        if last_played == 0:
            last_played = "Never played."
        else:
            last_played = datetime.datetime.fromtimestamp(last_played).strftime("%B %d, %Y at %I:%M %p")
        print(f"{title}\nPlaytime: {playtime}\nLast Played: {last_played}")
        print("-" * 80)

        temporarily_excluded_split = temporarily_excluded.split('|')
        for game in range(len(temporarily_excluded_split)):
            if game == title:
                print(f"{title} has been found in the temporary list.")
        permanently_excluded_split = permanently_excluded.split('|')
        for game in range(len(permanently_excluded_split)):
            if game == title:
                print(f"{title} has been found in the permanent list.")
        choice = input(f"Input 'Run' to launch {title}.\nInput 'X' to add {title} to excluded games list permanently.\nInput 'Z' to add {title} to excluded games list for current session.\nInput 'C' to see excluded games.\nInput 'B' to go back by 1 game.\nInput 'R' to reroll the queue of games.\nInput 'E' to exit.\nPress/Input any other key to reroll.\n")

        if_go_back = False
        reroll_queue = False
        if choice.lower() == 'run': #launch game
            #subprocess.Popen(['steam', '&'])
            try:
                subprocess.Popen(["steam", f"steam://rungameid/{app_id}"])
            except Exception as e:
                print(f"Unable to run game with error {e}.")
        
        if choice.lower() == 'x': #exclude game permanently
            clear_terminal()
            print(f"{title} excluded permanently.")

            if permanently_excluded != "":
                permanently_excluded = str(permanently_excluded) + "|" + str(title)
            else:
                permanently_excluded = title

            time.sleep(1)
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
            choice = str(input("Input the number of a game you would like to reinclude plus first letter for the exclusion pool. Eg. (2p,4t), etc. \nInput/Press any other  key to continue.\n"))
            
            try: 
                number_choice = int(choice[0])
                pool_choice = choice[1]
                if isinstance(number_choice,int) and pool_choice == 'p' or pool_choice == 't':
                    try:
                        if pool_choice == 't': 
                            if temporarily_excluded_split[number_choice] != '':

                                temporarily_excluded_split.pop(number_choice)
                                permanently_excluded = ""

                                for game in range(len(temporarily_excluded_split)):
                                    permanently_excluded = '|'.join(temporarily_excluded_split)

                                print(f"Game removed.")

                            else: print("No game located at that position.")
                        else: 
                            permanently_excluded_split = permanently_excluded.split('|')

                            if permanently_excluded_split[number_choice] != '':

                                permanently_excluded_split.pop(number_choice)
                                permanently_excluded = ""

                                for game in range(len(permanently_excluded_split)):
                                    permanently_excluded = "|".join(permanently_excluded_split)
                                with open(f'{file_path}exclusion_list.json','w') as file:
                                    data = {
                                        "permanently_excluded": f"{permanently_excluded}"
                                    }
                                    json.dump(data,file,indent=4)

                                print(f"Game removed.")

                            else: print("No game located at that position.")
                    except Exception as e:
                        print(f"No game located at that position. {e}")
                        time.sleep(4)
                    time.sleep(1)
                else:
                    print("Invalid Input. Try again later.")
                    time.sleep(2)
            except:
                pass
        
        elif choice.lower() == 'b': # go back by one game
            if_go_back = True

        elif choice.lower() == 'r': #reroll the roll queue
            reroll_queue = True
        elif choice.lower() == 'e': #exit
            exit()
def clear_terminal(): os.system('cls' if os.name == 'nt' else 'clear')
def create_storage_files():
    try:
        os.mkdir(file_path)
    except:
        pass
    try:
        img_path = ''
        img_path = os.path.join(str(file_path), "tmp", "")
        os.mkdir(img_path)
    except Exception as e:
        pass

    #print(os.path.exists(f'{file_path}exclusion_list.json') == False,os.path.exists(f'{file_path}keyids.json') == False,os.path.exists(f'{file_path}last_game_data.json') == False)
    if os.path.exists(f'{file_path}exclusion_list.json') == False or os.path.exists(f'{file_path}keyids.json') == False or os.path.exists(f'{file_path}last_game_data.json') == False:
        choice = input("One or more storage files not found. Create them? (Y)\n")
        clear_terminal()
        if choice.lower() == 'y':
            print("Closing the program during this file creation process could lead to issues when running the program later on.")
            print(f"If so, create the files manually at {file_path} according to the instructions on the github page.")
            input("Press any key to continue.")
            print(f"Creating template file at {file_path}exclusion_list.json.")
            with open(f'{file_path}exclusion_list.json', 'w') as file: 
                data = {
                    "permanently_excluded": ""
                }
                json.dump(data,file,indent=4)
            api_key = input(f"Input API key. These can be changed later by opening {file_path}keyids.json.\n")
            user_id = input(f"Input User ID key. These can be changed later by opening {file_path}keyids.json.\n")
            print(f"Storing credentials at {file_path}keyids.json.")
            with open(f'{file_path}keyids.json', 'w') as file: 
                data = {
                    "api_key": f"{api_key}",
                    "user_id": f"{user_id}"
                }
                json.dump(data,file,indent=4)
            print(f"Creating empty storage file at {file_path}last_game_data.json.")
            with open(f'{file_path}last_game_data.json', 'w') as file: 
                data = ''
                json.dump(data,file,indent=4)
        else:
            exit()
def randomize_game(all_game_details,permanently_excluded,temporarily_excluded,if_go_back,reroll_queue):
    
    global randomized_game_list
    global previous_games

    if len(randomized_game_list) == 0 or reroll_queue == True:
        random.shuffle(all_game_details)
        randomized_game_list = all_game_details.copy()

    permanently_excluded_split = permanently_excluded.split('|')
    temporarily_excluded_split = temporarily_excluded.split('| ')
    game_choice = []
    clear_terminal()
    if if_go_back == False:
        game_choice = randomized_game_list.pop(0)
        previous_games.append(game_choice)
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

    return title, playtime,app_url,app_id,last_played
try:
    get_games()
except KeyboardInterrupt:
    print("\nExiting...")
    exit(0)