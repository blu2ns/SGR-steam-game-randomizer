import requests,os,json,random,time,subprocess,climage,datetime,textwrap
from pathlib import Path

def main():
    api_key = ""; user_id = ""; randomized_game_list = []; previous_games = []

    file_path,img_path = create_storage_files()
    with open(f'{file_path}exclusion_list.json', 'r') as exclusion_file: 
        exclusion_data = json.load(exclusion_file) 
        permanently_excluded = exclusion_data['permanently_excluded']
        temporarily_excluded = ""

    show_images = True; show_developers = True; show_publishers = True; show_genres = True; show_release_date = True; show_description = True
    try:
        show_images, show_developers,show_publishers,show_genres,show_release_date,show_description = settings.load_settings(file_path,show_images,show_developers,show_publishers,show_genres,show_release_date,show_description)    
    except Exception as e:
        print(f"Unable to load settings with error {e}. Using default values.")
        show_images = True; show_developers = True; show_publishers = True; show_genres = True; show_release_date = True; show_description = True
    get_games(file_path,api_key,user_id)
    permanently_excluded_split,all_game_details,game_num = parse_game_data(file_path, permanently_excluded)

    if_go_back = False; reroll_queue = False

    clear_terminal()
    choice = input("Refresh game image cache? This step is only necessary to do once. It may take a while but rolls will happen faster after.\n[R] Refresh all images [G] Get missing images [Other] Continue without refresh.\n")
    if choice.lower() == 'r':
        refresh_img_cache(file_path,img_path,all_game_details,permanently_excluded,refresh_all=True)
    elif choice.lower() == 'g':
        refresh_img_cache(file_path,img_path,all_game_details,permanently_excluded,refresh_all=False)
    while 1:
        
        title, playtime, app_url, app_id, last_played, randomized_game_list, previous_games, developers, publishers, platforms, genres, release_date, short_description = randomize_game(all_game_details, permanently_excluded, temporarily_excluded,if_go_back, reroll_queue, randomized_game_list, previous_games,file_path)
        if show_images == True: print_game_image(file_path,app_id,img_path,title)
        #else: print("-" * 80,'\n')
        
        print("-" * 80)
        if last_played != 0:
            last_played = datetime.datetime.fromtimestamp(last_played).strftime("%B %d, %Y at %I:%M %p")
        else:
            last_played = "Never played."
        if len(title) > 80:
            title = title[0:78]+'..'         
        
        print(f"{title if title else 'N/A'}\nPlaytime: {playtime if playtime else 'N/A'}\nLast Played: {last_played if last_played else 'N/A'}")
        
        if show_developers == True or show_publishers == True or show_genres == True or show_release_date == True: print("-" * 80)

        if len(developers) > 1:
            developers = [developers[0],developers[1]]
        if len(publishers) > 1:
            publishers = [publishers[0],publishers[1]]
        if len(genres) > 2:
            genres = [genres[0],genres[1],genres[2]]

        if show_developers == True: print(f'Developed by: {', '.join(developers) if developers else 'N/A'}')
        if show_publishers == True: print(f'Published By: {', '.join(publishers) if publishers else 'N/A'}')
        if show_genres == True: print(f'Genres: {', '.join(genres) if genres else 'N/A'}')
        if show_release_date == True: print(f'Release Date: {release_date if release_date else 'N/A'}')
        
        if show_description == True:
            if short_description != '':
                print("-" * 80)
                print(textwrap.fill(short_description, width=80))
        if len(title) > 65:
            title = title[0:65]+'..'        

        print(f'''{"-" * 80}
[ENTER] Reroll   [R] Reroll Queue   [V] View On Steam     [F] Filters
[C] Exclusions   [X] Exclude Perm   [Z] Exclude Session
[B] Go Back      [S] Settings       [E] Exit
[RUN] Launch {title}''')
        choice = input("Choice: ")

        if_go_back = False; reroll_queue = False

        if choice.lower() == 'run': #launch game
            try:
                subprocess.Popen(["steam", f"steam://rungameid/{app_id}"])
            except Exception as e:
                print(f"Unable to run game with error {e}.")
        
        elif choice.lower() == 'v': #see game page in desktop app:
            try:
                subprocess.Popen(['steam', f'steam://nav/games/details/{app_id}'])
            except Exception as e:
                print(f"Unable to open game page with error {e}.")
        
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
                    except Exception as e:
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
                except Exception as e:
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

        elif choice.lower() == 's': #view settings
            show_images,show_developers,show_publishers,show_genres,show_release_date,show_description = settings.view_settings(file_path,show_images, show_developers,show_publishers,show_genres,show_release_date,show_description)

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
            pass

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

def refresh_img_cache(file_path,img_path,all_game_details,permanently_excluded,refresh_all):
    parse_game_data(file_path,permanently_excluded)
    images_added = 0
    for game in range(len(all_game_details)):
        title = all_game_details[game][0]
        id = all_game_details[game][3]
        img_path = os.path.join(str(file_path), "images", f"{id}.jpg")
        if refresh_all == False and os.path.exists(img_path) == True:
            print(f"Image already exists for {title}. Skipping.")
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
            images_added += 1
        except:
            print(f"Game image and backup game image for {title} not found.")
    #this sometimes has an inaccurate number
    input(f"{images_added} new images successfully cached. [Enter] Continue\n")

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
    choice = input(f"{"-" * 80}\nWelcome to the Steam Game Randomizer.\n[Y] Refresh game cache. [YD] Refresh Game Cache & Store Details [C] Change stored API Key and User ID [Other] Continue without refresh.\n")
    
    if choice.lower() == 'y' or choice.lower() == 'ydebug' or choice.lower() == 'yd':
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
                choice = input("API Key and/or User ID not found. [A] Add Credentials [Other] Exit\n")
                if choice.lower() != 'a':
                    exit()
                else:
                    create_keyids(file_path)
                    main()

            print("API Key and User ID found.\nMaking API request...")
            url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={user_id}&format=json&include_appinfo=1&include_played_free_games=1&skip_unvetted_apps=false"
            response = requests.get(url)

            print(f"Got response with status code {response.status_code}.")
            time.sleep(0.5)
            if choice.lower() == 'ydebug':
                print(json.dumps(response.json(), indent=4))
                input("[Enter] Continue")
            
            game_num = 0
            game_data = response.json()
            with open(f'{file_path}last_game_data.json', 'w') as game_file:
                json.dump(game_data, game_file, indent=4)
                game_num = game_data['response']['game_count']
            appid = 0
            store_details = {}
            if choice.lower() == 'yd':
                for game in range(game_num):
                    try:
                        # get this to show the game name not just ID
                        app_id = game_data['response']['games'][game]['appid']
                        print(f"Getting game store page data for {app_id}")
                        url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
                        response = requests.get(url)
                        data = response.json()
                        #print(json.dumps(response.json(), indent=4))
                        price_overview = data[str(app_id)]['data'].get('price_overview', {})
                        relevant_data = {
                            'success':    data[str(app_id)]['success'],
                            'short_description': data[str(app_id)]['data'].get('short_description', 'N/A'),
                            'developers': data[str(app_id)]['data'].get('developers', 'N/A'),
                            'publishers': data[str(app_id)]['data'].get('publishers', 'N/A'),
                            'platforms':  data[str(app_id)]['data'].get('platforms', 'N/A'),
                            'genres':     data[str(app_id)]['data'].get('genres', 'N/A'),
                            'release_date': data[str(app_id)]['data'].get('release_date', {}).get('date', 'N/A'),
                        }
                        clear_terminal()
                        if data[str(app_id)]['success'] == False:
                            raise ValueError(f"Unable to get game store page data for {app_id}")
                        store_details[app_id] = relevant_data
                        
                    except Exception as e:
                        print(f"Failed with error {e}. Skipping.")
                        input()
                try:
                    with open(f'{file_path}game_store_data.json', 'w') as game_file:
                        json.dump(store_details, game_file, indent=4)
                    print("Game Store data successfully stored.")
                except Exception as e:
                    print(f"Error Occurred. {e}")
            print(f"Game list successfully refreshed and cached.")
            time.sleep(0.5)

        except Exception as e:
            print(f"Error: {e}")
            print("Make sure stored API Key and User ID is correct and try again.")
            input("[Enter] Continue")
    
    if choice.lower() == 'c':
        clear_terminal()
        create_keyids(file_path)
        get_games(file_path,api_key,user_id)

def create_storage_files():
    file_path = r"~/"
    file_path = Path(__file__).resolve().parent
    file_path = os.path.join(str(file_path), "storage", "")

    try:
        os.mkdir(file_path)
    except FileExistsError:
        pass

    img_path = ''
    img_path = os.path.join(str(file_path), "images", "")

    try:
        os.mkdir(img_path)
    except FileExistsError:
        pass
    
    if os.path.exists(f'{file_path}exclusion_list.json') == False or os.path.exists(f'{file_path}keyids.json') == False or os.path.exists(f'{file_path}last_game_data.json') == False or os.path.exists(f'{file_path}settings.json') == False:
        
        choice = input("One or more storage files not found. [Y] Create Files [Other] Close Program\n")
        clear_terminal()

        if choice.lower() == 'y':

            choice = ''
            if os.path.exists(f'{file_path}exclusion_list.json') == True: 
                choice = input("Exclusion List found. Recreate? [Y] Yes [Other] No\n")
            if choice.lower() == 'y' or os.path.exists(f'{file_path}exclusion_list.json') == False:
                with open(f'{file_path}exclusion_list.json', 'w') as file: 
                    data = {
                        "permanently_excluded": ""
                    }
                    json.dump(data,file,indent=4)
                clear_terminal()
                print(f"Created game exclusion storage file at {file_path}exclusion_list.json.")
                time.sleep(2.5)
            
            clear_terminal()
            choice = ''
            if os.path.exists(f'{file_path}keyids.json') == True:
                choice = input("Credentials file found. Recreate? [Y] Yes [Other] No\n")
            if choice.lower() == 'y' or os.path.exists(f'{file_path}keyids.json') == False:
                create_keyids(file_path)
            
            clear_terminal()
            choice = ''
            if os.path.exists(f'{file_path}last_game_data.json') == True:
                choice = input("Game data file found. Recreate? [Y] Yes [Other] No\n")
            if choice.lower() == 'y' or os.path.exists(f'{file_path}last_game_data.json') == False:
                with open(f'{file_path}last_game_data.json', 'w') as file: 
                    data = {}
                    json.dump(data,file,indent=4)
                clear_terminal()
                print(f"Created empty storage file at {file_path}last_game_data.json.")
                time.sleep(2.5)
            clear_terminal()

            choice = ''
            if os.path.exists(f'{file_path}settings.json') == True: 
                choice = input("Settings file found. Recreate? [Y] Yes [Other] No\n")
            if choice.lower() == 'y' or os.path.exists(f'{file_path}settings.json') == False:
                with open(f'{file_path}settings.json', 'w') as file: 
                    data = {
                        "show_images": True,
                        "show_developers": True,
                        "show_publishers": True,
                        "show_genres": True,
                        "show_release_date": True,
                        "show_description": True
                    }
                    json.dump(data,file,indent=4)
                clear_terminal()
                print(f"Created settings file at {file_path}settings.json")
                time.sleep(2.5)
            clear_terminal()
        else:
            exit()
    
    return file_path,img_path

def create_keyids(file_path):
    clear_terminal()
    api_key = input(f"Input API key. This can be changed later by opening {file_path}keyids.json,\n or running the program again and following the prompt.\nA guide to getting this can be found on the github page or in the README.\n")
    clear_terminal()
    print("API key added.")
    time.sleep(2)
    clear_terminal()

    user_id = input(f"Input User ID. This can be changed later by opening {file_path}keyids.json,\n or running the program again and following the prompt.\nA guide to finding this can be found on the github page or in the README.\n")
    clear_terminal()
    print("User ID added.")
    time.sleep(2)
    clear_terminal()

    
    with open(f'{file_path}keyids.json', 'w') as file: 
        data = {
            "api_key": f"{api_key}",
            "user_id": f"{user_id}"
        }
        json.dump(data,file,indent=4)
    clear_terminal()
    print(f"Stored credentials at {file_path}keyids.json.")
    time.sleep(2.5)
    clear_terminal()

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
    developers = []; publishers = []; platforms = []; genres = []; release_date = None; short_description = ''
    try:
        with open(f'{file_path}game_store_data.json','r') as file:
            data = json.load(file)
            for i in range(len(data[str(app_id)]['developers'])): 
                developers.append(data[str(app_id)]['developers'][i])
            for i in range(len(data[str(app_id)]['publishers'])): 
                publishers.append(data[str(app_id)]['publishers'][i])
            genres = [item['description'] for item in data[str(app_id)]['genres']]
            release_date = data[str(app_id)]['release_date']
            short_description = data[str(app_id)]['short_description']
    except Exception as e:
        pass

    return title, playtime, app_url, app_id, last_played, randomized_game_list, previous_games, developers, publishers, platforms, genres, release_date,short_description

class settings: 
    def view_settings(file_path,show_images,show_developers,show_publishers,show_genres,show_release_date,show_description):
        if os.path.exists(f'{file_path}settings.json') == True: 
            clear_terminal()
            print(f"{'-'*6}   Settings   {'-'*6}")
            
            setting_list = [["Show Game Images",show_images], ["Show Developer(s)",show_developers], ["Show Publisher(s)",show_publishers],["Show Genre(s)",show_genres],["Show Release Date",show_release_date],["Show Description",show_description]]
            for setting in range(len(setting_list)):
                print(f'{setting}) {setting_list[setting][0]}: {settings.bool_to_symbol(setting_list[setting][1])}')
            choice = None
            try: choice = int(input(f"[1-{len(setting_list)}] Toggle Setting [ENTER] Return\n"))
            except: return show_images,show_developers,show_publishers,show_genres,show_release_date,show_description
            if -1 < choice <= len(setting_list):
                try:
                    setting_list[choice][1] = not setting_list[choice][1]

                    with open(f'{file_path}settings.json', 'w') as file: 
                        data = {
                            "show_images": setting_list[0][1],
                            "show_developers": setting_list[1][1],
                            "show_publishers": setting_list[2][1],
                            "show_genres": setting_list[3][1],
                            "show_release_date": setting_list[4][1],
                            "show_description": setting_list[5][1]
                        }
                        json.dump(data,file,indent=4)   

                    clear_terminal()
                    print(f"{settings.bool_to_symbol(not setting_list[choice][1])} changed to {settings.bool_to_symbol(setting_list[choice][1])} for {setting_list[choice][0]}.")
                    time.sleep(1)
                    settings.view_settings(file_path,setting_list[0][1], setting_list[1][1], setting_list[2][1], setting_list[3][1], setting_list[4][1], setting_list[5][1])
                except Exception as e:
                    print(f"Unable to save settings with error {e}.")
                    input()
                
            return setting_list[0][1], setting_list[1][1], setting_list[2][1], setting_list[3][1], setting_list[4][1], setting_list[5][1]
    def load_settings(file_path,show_images,show_developers,show_publishers,show_genres,show_release_date,show_description):
        try:
            if os.path.exists(f'{file_path}settings.json') == True: 
                with open(f'{file_path}settings.json', 'r') as settings_file: 
                    settings_data = json.load(settings_file) 
                    show_images = settings_data['show_images']
                    
                    show_developers = settings_data['show_developers']
                    show_publishers = settings_data['show_publishers']
                    show_genres = settings_data['show_genres']
                    show_release_date = settings_data['show_release_date']
                    show_description = settings_data['show_description']
            else:
                print("Settings file does not exist. Using default values.")
            return show_images,show_developers,show_publishers,show_genres,show_release_date,show_description
        except Exception as e:
            print(f"Unable to load settings with error {e}")
            
    def bool_to_symbol(bool): return '✓' if bool else '✗'

def clear_terminal(): os.system('cls' if os.name == 'nt' else 'clear')
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
        exit()