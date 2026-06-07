import requests,os,json,random,time,subprocess,climage,datetime,textwrap
from pathlib import Path

class game_selections:
    api_key = ""; user_id = ""; randomized_game_list = []; previous_games = []; permanently_excluded = []; temporarily_excluded = [] 
    show_images = True; show_developers = True; show_publishers = True; show_genres = True; show_release_date = True; show_description = True
    file_path = ''; img_path = ''; all_game_details = []; if_go_back = False; reroll_queue = False; 

    @staticmethod
    def main():
        game_selections.file_path,game_selections.img_path = game_selections.create_storage_files()
        
        with open(f'{game_selections.file_path}exclusion_list.json', 'r') as exclusion_file: 
            exclusion_data = json.load(exclusion_file) 
            game_selections.permanently_excluded = exclusion_data.get('permanently_excluded', [])
            game_selections.temporarily_excluded = [] 
        try:
            game_selections.show_images, game_selections.show_developers,game_selections.show_publishers,game_selections.show_genres,game_selections.show_release_date,game_selections.show_description = settings.load_settings(game_selections.file_path,game_selections.show_images,game_selections.show_developers,game_selections.show_publishers,game_selections.show_genres,game_selections.show_release_date,game_selections.show_description)    
        except Exception as e:
            general.clear_terminal()
            print(f"Unable to load settings with error {e}. Using default values.")
            time.sleep(2)

        game_selections.get_games(game_selections.file_path,game_selections.api_key,game_selections.user_id)
        _, game_selections.all_game_details, _ = game_selections.parse_game_data(game_selections.file_path, game_selections.permanently_excluded)

        general.clear_terminal()
        print('-' * 80)

        choice = input("Refresh game image cache? This step is only necessary to do once.\nIt may take a while but rolls will happen faster after.\n[R] Refresh all images [G] Get missing images [Other] Continue without refresh.\n")
        if choice.lower() == 'r':
            game_selections.refresh_img_cache(game_selections.file_path,game_selections.img_path,game_selections.all_game_details,game_selections.permanently_excluded,refresh_all=True)
        elif choice.lower() == 'g':
            game_selections.refresh_img_cache(game_selections.file_path,game_selections.img_path,game_selections.all_game_details,game_selections.permanently_excluded,refresh_all=False)
        
        while 1:
            game_selections.show_game()
    
    @staticmethod        
    def show_game():
        title, playtime, app_url, app_id, last_played, game_selections.randomized_game_list, game_selections.previous_games, developers, publishers, platforms, genres, release_date, short_description, playtime_2weeks, playtime_2weeks_HR = game_selections.randomize_game(game_selections.all_game_details, game_selections.permanently_excluded, game_selections.temporarily_excluded,game_selections.if_go_back, game_selections.reroll_queue,game_selections.randomized_game_list, game_selections.previous_games,game_selections.file_path, settings.current_filter, settings.current_playtime_threshold)
        game_selections.if_go_back = False; game_selections.reroll_queue = False

        if last_played != 0:
            last_played = datetime.datetime.fromtimestamp(last_played).strftime("%B %d, %Y at %I:%M %p")
        else:
            last_played = "Never played."
        if len(title) > 80:
            title = title[0:78]+'..'   

        if len(developers) > 1:
            developers = [developers[0],developers[1]]
        if len(publishers) > 1:
            publishers = [publishers[0],publishers[1]]
        if len(genres) > 5:
            genres = [genres[0],genres[1],genres[2],genres[3],genres[4]]      
        if len(title) > 65:
            title = title[0:65]+'..'

        if game_selections.show_images == True: game_selections.print_game_image(game_selections.file_path, app_id, game_selections.img_path, title)
        print("-" * 80)

        print(f"{title if title else 'N/A'}\nPlaytime: {playtime if playtime else 'N/A'}\nLast Played: {last_played if last_played else 'N/A'}\nPlaytime 2 Weeks: {playtime_2weeks_HR if playtime_2weeks_HR else '0'}")
        
        if game_selections.show_developers == True or game_selections.show_publishers == True or game_selections.show_genres == True or game_selections.show_release_date == True: print("-" * 80)

        if game_selections.show_developers == True: print(f'Developed by: {', '.join(developers) if developers else 'N/A'}')
        if game_selections.show_publishers == True: print(f'Published By: {', '.join(publishers) if publishers else 'N/A'}')
        if game_selections.show_genres == True: print(f'Genres: {', '.join(genres) if genres else 'N/A'}')
        if game_selections.show_release_date == True: print(f'Release Date: {release_date if release_date else 'N/A'}')
        
        if game_selections.show_description == True:
            if short_description != '':
                print("-" * 80)
                general.printw(short_description)  

        game_selections.get_input_choice(title, app_id)

    @staticmethod
    def get_input_choice(title, app_id):
        file_path = game_selections.file_path
        all_game_details = game_selections.all_game_details
        permanently_excluded = game_selections.permanently_excluded
        temporarily_excluded = game_selections.temporarily_excluded
        directions = "\n".join([
            "[ENTER] Reroll   [R] Reroll Queue   [V] View On Steam",
            "[C] Exclusions   [X] Exclude Perm   [Z] Exclude Session",
            "[B] Go Back      [S] Settings       [E] Exit",
            f"[RUN] Launch {title}",
        ])
        print(f'{"-" * 80}\n{directions}')

        choice = input("Choice: ")

        match choice: 
            case 'run': #launch the game
                game_selections.run_command(title=title,app_id=app_id,list_indx=1)
            case 'v': #view in desktop app
                game_selections.run_command(title=title,app_id=app_id,list_indx=0)
            case 'x': #exclude game permanently
                exclusions.add_exclusion(exclusion_type=0,title=title) #permanent
            case 'z': #exclude game temporarily
                exclusions.add_exclusion(exclusion_type=1,title=title) #temp
            case 'c': #see list of excluded games
                exclusions.view_excluded()
            case 'b': #go back by one game
                game_selections.if_go_back = True
            case 'r': #reroll the roll queue
                game_selections.reroll_queue = True
            case 's': #view setttings
                pre_filter = settings.current_filter; pre_playtime_threshold = settings.current_playtime_threshold
                settings.view_settings(file_path, game_selections.all_game_details, game_selections.permanently_excluded, game_selections.temporarily_excluded)
                if pre_filter != settings.current_filter or pre_playtime_threshold != settings.current_playtime_threshold:
                    game_selections.reroll_queue = True        
            case 'e': #exit
                exit()

    @staticmethod
    def run_command(title,app_id,list_indx):
        command_list = [[f'steam://nav/games/details/{app_id}', f"open game page for {title}"],[f"steam://rungameid/{app_id}", f"run {title}"]]
        try:
            print("Launching. It may take a moment.")
            subprocess.Popen(['steam', str(command_list[list_indx][0])],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,stdin=subprocess.DEVNULL,start_new_session=True)
            time.sleep(1)
        except Exception as e:
            general.clear_terminal()
            print(f"Unable to {str(command_list[list_indx][1])} with error: {e}.")
            input("[Enter] Continue\n")

    @staticmethod
    def print_game_image(file_path,app_id,img_path,title):
        img_path = os.path.join(str(file_path), "images", f"{app_id}.jpg")
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
                general.clear_terminal()
            except:
                pass
        print("-" * 80) 
        try: 
            image = climage.convert(img_path,is_unicode=True, is_truecolor=True, is_256color=False, width=80)
            rows = image.split('\n')
            for index, row in enumerate(rows):
                print(f'{row}\033[0m')
                if index >= 11: break
        except:
            print("Game image not found.")
    
    @staticmethod
    def refresh_img_cache(file_path,img_path,all_game_details,permanently_excluded,refresh_all):
        game_selections.parse_game_data(file_path,permanently_excluded)
        images_added = 0
        for game in range(len(all_game_details)):
            title = all_game_details[game][0]
            id = all_game_details[game][3]
            img_path = os.path.join(str(file_path), "images", f"{id}.jpg")
            if refresh_all == False and os.path.exists(img_path) == True:
                print(f"Image already exists for {title}. Skipping.")
                general.clear_terminal()
                continue
            try:
                general.clear_terminal()
                print(f"Getting image for {title}. [{game + 1}/{len(all_game_details)}]")
                url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{id}/library_hero.jpg"
                response = requests.get(url)

                if response.status_code != 200:
                    url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{id}/header.jpg"
                    response = requests.get(url)    

                with open(img_path, "wb") as f:
                    f.write(response.content)
                general.clear_terminal()
                print(f"Image found for {title}. [{game + 1}/{len(all_game_details)}]")
                images_added += 1
            except:
                print(f"Game image and backup game image for {title} not found.")
        input(f"{images_added} new images successfully cached. [Enter] Continue\n")
    
    @staticmethod
    def parse_game_data(file_path,permanently_excluded):
        try:
            with open(f'{file_path}last_game_data.json', 'r') as game_file: 
                data = json.load(game_file) 
            game_num = data['response']['game_count']
            all_game_details = []
        except Exception as e:
            print(f'Game cache empty and/or cache file not found. Rerun the program and request the game data from the API. Error: {e}')
            time.sleep(5)
            exit()

        for game in range(game_num):
            try:
                game_details = [
                    data['response']['games'][game]['name'],
                    data['response']['games'][game]['playtime_forever'] + data['response']['games'][game]['playtime_disconnected'],
                    data['response']['games'][game]['img_icon_url'],
                    data['response']['games'][game]['appid'],
                    data['response']['games'][game]['rtime_last_played'],
                    data['response']['games'][game].get('playtime_2weeks', 0)
                ]   
                all_game_details.append(game_details)
            except:
                break

        all_game_details = [game for game in all_game_details if game[0] not in game_selections.permanently_excluded]
        return game_selections.permanently_excluded, all_game_details,game_num
    
    @staticmethod
    def get_games(file_path,api_key,user_id): #still needs rewrite
        choice = input(f"{"-" * 80}\nWelcome to the Steam Game Randomizer.\n[Y] Refresh game cache. [YS] Refresh Game Cache & Store Details \n[YSM] Refresh Game Cache & missing Store Details\n[C] Change stored API Key and User ID [Other] Continue without refresh.\n")

        if choice.lower() == 'c':
            general.clear_terminal()
            game_selections.create_keyids(file_path)
            game_selections.get_games(file_path,api_key,user_id)

        if choice.lower() == 'y' or choice.lower() == 'ys' or choice.lower() == 'ysm' or choice.lower() == 'ysdebug' or choice.lower() == 'ysmdebug' or choice.lower() == 'ydebug':
            try:
                general.clear_terminal()

                try:
                    print("Opening file with User ID & API Key..")
                    with open(f'{file_path}keyids.json', 'r') as ids_file: 
                        data = json.load(ids_file) 
                        api_key = data['api_key']
                        user_id = data['user_id']
                except:
                    game_selections.create_storage_files()

                if api_key == '' or user_id == '':
                    choice = input("API Key and/or User ID not found. [A] Add Credentials [Other] Exit\n")
                    if choice.lower() != 'a':
                        exit()
                    else:
                        game_selections.create_keyids(file_path)
                        game_selections.main()

                print("API Key and User ID found.\nMaking API request...")
                url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={user_id}&format=json&include_appinfo=1&include_played_free_games=1&skip_unvetted_apps=false"
                response = requests.get(url)

                print(f"Got response with status code {response.status_code}.")
                time.sleep(0.5)
                if choice.lower() == 'ydebug' or choice.lower() == 'ysdebug' or choice.lower() == 'ysmdebug':
                    print(json.dumps(response.json(), indent=4))
                    input("[Enter] Continue")
                
                game_num = 0
                game_data = response.json()
                if choice.lower() == 'ydebug' or choice.lower() == 'ysdebug' or choice.lower() == 'ysmdebug':
                    print(game_data)
                    input("[Enter] Continue")

                if 'game_count' not in game_data.get('response', {}):
                    print("Account ID invalid. User ID might be wrong or library is set to private.")
                    print('[Enter] Continue')
                    return

                with open(f'{file_path}last_game_data.json', 'w') as game_file:
                    json.dump(game_data, game_file, indent=4)
                    game_num = game_data['response']['game_count']

                if choice.lower() == 'ys' or choice.lower() == 'ysm' or choice.lower() == 'ysdebug' or choice.lower() == 'ysmdebug':
                    game_selections.get_storepg_data(choice,game_data) 

                print(f"Game list successfully refreshed and cached.")
                time.sleep(0.5)

            except Exception as e:
                print(f"Error: {e}")
                print("Make sure stored API Key and User ID is correct and try again.")
                input("[Enter] Continue")

    @staticmethod
    def get_storepg_data(choice,game_data):
        appid = 0
        store_details = {}
        
        if choice.lower() == 'ysm' or choice.lower() == 'ysmdebug':
            existing_game_list = []

            with open(f'{game_selections.file_path}game_store_data.json', 'r') as game_file:
                data = json.load(game_file)        
            for game_id, temp_game_data in data.items():
                existing_game_list.append(game_id)
                print(f"Game store page data already exists for {temp_game_data['name']}.")
                time.sleep(0.001)
                general.clear_terminal()

            game_data['response']['games'] = [
                game for game in game_data['response']['games']
                if str(game['appid']) not in existing_game_list
            ]
        game_details_fetched = 0
        game_num = len(game_data['response']['games'])
        for game in range(game_num):
            try:
                app_id = game_data['response']['games'][game]['appid']
                game_name = game_data['response']['games'][game]['name']
                print(f"Getting game store page data for {game_name}.")
                url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
                response = requests.get(url)
                data = response.json()
                if choice.lower() == 'ysdebug' or choice.lower() == 'ysmdebug':
                    print(json.dumps(data, indent=4))
                if data[str(app_id)]['success'] == False:
                    print(f"Unable to retreive game data for {game_name}, skipping.")
                    continue
                price_overview = data[str(app_id)]['data'].get('price_overview', {})
                relevant_data = {
                    'success':    data[str(app_id)]['success'],
                    'short_description': data[str(app_id)]['data'].get('short_description', 'N/A'),
                    'developers': data[str(app_id)]['data'].get('developers', 'N/A'),
                    'publishers': data[str(app_id)]['data'].get('publishers', 'N/A'),
                    'platforms':  data[str(app_id)]['data'].get('platforms', 'N/A'),
                    'genres':     data[str(app_id)]['data'].get('genres', 'N/A'),
                    'release_date': data[str(app_id)]['data'].get('release_date', {}).get('date', 'N/A'),
                    'name': data[str(app_id)]['data'].get('name', 'N/A'),
                }

                general.clear_terminal()
                store_details[app_id] = relevant_data
                game_details_fetched += 1
            except Exception as e:
                print(f"Failed with error {e}. Skipping. If this happens a lot, you might have gotten rate limited, so try again in a few minutes.")
                time.sleep(3)
        print(f"Retrieved new data for {game_details_fetched} {'games' if game_details_fetched != 1 else 'game'}.")
        time.sleep(1)
        if choice.lower() == 'ysdebug' or choice.lower() == 'ysmdebug':
            input("[Enter] Continue")
        try:
            try:
                with open(f'{game_selections.file_path}game_store_data.json', 'r') as game_file:
                    existing_game_data = json.load(game_file)
            except (json.JSONDecodeError, FileNotFoundError):
                existing_game_data = {}

            existing_game_data.update(store_details)

            with open(f'{game_selections.file_path}game_store_data.json', 'w') as game_file:
                json.dump(existing_game_data, game_file, indent=4)
            print("Game Store data successfully stored.")
        except Exception as e:
            print(f"Error occurred when storing store page data: {e}")
            input()  
    @staticmethod
    def create_keyids(file_path):
        general.clear_terminal()
        api_key = input(f"Input API key. This can be changed later by running\nthe program again and following the prompt.\nA guide to getting this can be found on the github page or in the README.\n")
        general.clear_terminal()
        print("API key added.")
        time.sleep(2)

        general.clear_terminal()
        user_id = input(f"Input User ID. This can be changed later by running\nthe program again and following the prompt.\nA guide to getting this can be found on the github page or in the README.\n")
        general.clear_terminal()
        print("User ID added.")
        time.sleep(2)

        with open(f'{file_path}keyids.json', 'w') as file: 
            data = {
                "api_key": f"{api_key}",
                "user_id": f"{user_id}"
            }
            json.dump(data,file,indent=4)

        general.clear_terminal()
        print(f"Stored credentials at {file_path}keyids.json.")
        time.sleep(2.5)
        general.clear_terminal()
    
    @staticmethod #still needs rewrite
    def randomize_game(all_game_details, permanently_excluded, temporarily_excluded, if_go_back, reroll_queue, randomized_game_list, previous_games,file_path,filter_type,playtime_threshold):
        if len(randomized_game_list) == 0 or reroll_queue == True:
            print("Rerolling queue...")
            time.sleep(0.2)
            randomized_game_list = game_selections.shuffle_games(all_game_details)

        game_choice = []
        general.clear_terminal()

        if if_go_back == False:
            try:
                game_choice = randomized_game_list.pop(0)
                previous_games.append(game_choice)
            except Exception as e:
                print('-' *80)
                choice = input(f"No games found in list. Either you're very picky or you own no steam games.\n[Y] Clear exclusion preferences. [Other] Close program\n {e}")
                if choice.lower() == 'y':
                    permanently_excluded = []
                    temporarily_excluded = []
                    with open(f'{file_path}exclusion_list.json','w') as file:
                        json.dump({"permanently_excluded": []}, file, indent=4)

                    _, all_game_details, _ = game_selections.parse_game_data(file_path, permanently_excluded)
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
        playtime_2weeks = 0
        try:
            title = game_choice[0]; app_url = game_choice[2]; app_id = game_choice[3]; last_played = game_choice[4]; playtime_2weeks = game_choice[5]
        except Exception as e:
            print(f"Error reading game data: {e}")

        playtime = general.time_convert(int(game_choice[1]))
        playtime_2weeks_HR = general.time_convert(playtime_2weeks)

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
        return title, playtime, app_url, app_id, last_played, randomized_game_list, previous_games, developers, publishers, platforms, genres, release_date, short_description, playtime_2weeks, playtime_2weeks_HR

    @staticmethod
    def shuffle_games(all_game_details):
        randomized_game_list = all_game_details.copy()
        random.shuffle(randomized_game_list)        
        filter_conditions = {
            'playtime': lambda game: int(game[1]) <= settings.current_playtime_threshold,
            'norecent': lambda game: int(game[5]) == 0,
        }

        if settings.current_filter in filter_conditions:
            try:
                condition = filter_conditions[settings.current_filter]
                temp_randomized_game_list = []
                for game in randomized_game_list:
                    try:
                        if condition(game):
                            temp_randomized_game_list.append(game)
                    except Exception:
                        pass
                randomized_game_list = temp_randomized_game_list.copy()
            except Exception as e:
                choice = input(f"No games fit criteria of current filter with error {e}. Clear and try again? [Y] Yes [Other] Close Program")
                if choice.lower() == 'y':
                    game_selections.randomize_game(all_game_details, game_selections.permanently_excluded, game_selections.temporarily_excluded, game_selections.if_go_back, game_selections.reroll_queue, randomized_game_list, game_selections.previous_games, game_selections.file_path, "default", game_selections.playtime_threshold)
                else:
                    exit()
        return randomized_game_list

    @staticmethod
    def create_storage_files():
        
        file_path = Path(__file__).resolve().parent
        file_path = os.path.join(str(file_path), "storage", "")

        try:
            os.mkdir(file_path)
        except FileExistsError:
            pass

        img_path = os.path.join(str(file_path), "images", "")

        try:
            os.mkdir(img_path)
        except FileExistsError:
            pass
        
        if os.path.exists(f'{file_path}exclusion_list.json') == False or os.path.exists(f'{file_path}keyids.json') == False or os.path.exists(f'{file_path}last_game_data.json') == False or os.path.exists(f'{file_path}settings.json') == False or os.path.exists(f'{file_path}game_store_data.json') == False:
            
            choice = input("One or more storage files not found. [Y] Create Files [Other] Close Program\n")

            if choice.lower() == 'y':
                file_list = [
                    ("Exclusion List",      "exclusion_list.json",  {"permanently_excluded": []}),
                    ("Game Data",           "last_game_data.json",  {}),
                    ("Game Store Data",     "game_store_data.json", {}),
                    ("Settings",            "settings.json",        {
                        "show_images": True,
                        "show_developers": True,
                        "show_publishers": True,
                        "show_genres": True,
                        "show_release_date": True,
                        "show_description": True,
                        "current_filter": "default",
                        "current_playtime_threshold": 120
                    }),
                ]

                for game_indx in range(len(file_list)):
                    storage_file_path = f'{file_path}{file_list[game_indx][1]}'
                    choice = ''
                    general.clear_terminal()
                    if os.path.exists(storage_file_path) == True: 
                        choice = input(f"{file_list[game_indx][0]} storage file found. Recreate? [Y] Yes [Other] No\n")
                    if choice.lower() == 'y' or os.path.exists(storage_file_path) == False:
                        with open(storage_file_path, 'w') as file: 
                            json.dump(file_list[game_indx][2],file,indent=4)
                        general.clear_terminal()
                        print(f"Created {file_list[game_indx][0]} storage file at {storage_file_path}.")
                        time.sleep(2.5)
                        
                choice = ''
                if os.path.exists(f'{file_path}keyids.json') == True:
                    choice = input("Credentials file found. Recreate? [Y] Yes [Other] No\n")
                if choice.lower() == 'y' or os.path.exists(f'{file_path}keyids.json') == False:
                    game_selections.create_keyids(file_path)
                general.clear_terminal()
            else:
                exit()
        
        return file_path,img_path

class exclusions:
    @staticmethod
    def view_excluded(): 
        general.clear_terminal()
        print("-" * 80)

        var_list = [[game_selections.permanently_excluded,"Permanently"],[game_selections.temporarily_excluded,"Temporarily"]]
        for i in range(len(var_list)):
            if var_list[i][0]:
                print(f"{var_list[i][1]} excluded games:")
                        
                for n in range(len(var_list[i][0])):
                    print(f"{n}) {var_list[i][0][n]}")
                print('')
            else:
                print(f"{var_list[i][1]} excluded list is empty.")
                print('')
        
        choice = str(input("Input the first letter of the exclusion pool you would like to remove from,\nfollowed by the number for game you would like to remove. Eg. (p2,t4), etc.\n[Clear P] Clear Permanently Excluded list.\n[Clear T] Clear Temporarily Excluded list. [Enter] Continue.\n"))
        if choice == '': return
        try: 
            if choice.lower() == 'clear p' or choice.lower() == 'clear t':
                exclusions.clear_exclusion_list(choice)
            else:
                exclusions.exclude_game(choice)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(3)

    @staticmethod
    def exclude_game(choice):
        pool_choice = choice[0]
        number_choice = int(choice[1:len(choice)])
        if isinstance(number_choice, int) and (pool_choice == 'p' or pool_choice == 't'):
            try:
                if pool_choice == 't': 
                    if game_selections.temporarily_excluded[number_choice]:
                        removed_title = game_selections.temporarily_excluded.pop(number_choice)
                        general.clear_terminal()
                        print(f"{removed_title} removed.")
                        time.sleep(1)
                    else: print("No game located at that position.")
                else: 
                    if game_selections.permanently_excluded[number_choice]:
                        removed_title = game_selections.permanently_excluded.pop(number_choice)
                        with open(f'{game_selections.file_path}exclusion_list.json','w') as file:
                            data = {
                                "permanently_excluded": game_selections.permanently_excluded
                            }
                            json.dump(data,file,indent=4)
                        general.clear_terminal()
                        print(f"{removed_title} removed.")
                        time.sleep(1)
                    else: print("No game located at that position.")
            except Exception as e:
                print(f"No game located at that position. {e}")
                time.sleep(4)
            _, game_selections.all_game_details, _ = game_selections.parse_game_data(game_selections.file_path, game_selections.permanently_excluded)
            time.sleep(1)
        else:
            print("Invalid Input. Try again later.")
            time.sleep(3)

    @staticmethod
    def clear_exclusion_list(choice):
        if choice[6] == 'p':
            game_selections.permanently_excluded = []
            with open(f'{game_selections.file_path}exclusion_list.json','w') as file:
                data = {
                    "permanently_excluded": game_selections.permanently_excluded
                }
                json.dump(data,file,indent=4)

        elif choice[6] == 't':
            game_selections.temporarily_excluded = []

        game_selections.randomized_game_list, game_selections.previous_games = game_selections.randomize_game(game_selections.all_game_details, game_selections.permanently_excluded, game_selections.temporarily_excluded, False, True, game_selections.randomized_game_list, game_selections.previous_games, game_selections.file_path, settings.current_filter, settings.current_playtime_threshold)[5:7]
        print("Rerolled game queue based on new exclusion list.")
        time.sleep(1.5)
        _, game_selections.all_game_details, _ = game_selections.parse_game_data(game_selections.file_path, game_selections.permanently_excluded)

    @staticmethod
    def add_exclusion(exclusion_type,title):
        general.clear_terminal()
        var_list = [[game_selections.permanently_excluded,"permanently","permanently_excluded"],[game_selections.temporarily_excluded,"temporarily","temporarily_excluded"]]
        if title in var_list[exclusion_type][0]:
            print(f"Game is already in selected exclusion list.")
        else:
            print(f"{title} excluded {var_list[exclusion_type][1]}.")

            var_list[exclusion_type][0].append(title)
            setattr(game_selections, var_list[exclusion_type][2], var_list[exclusion_type][0])
            if exclusion_type == 0:
                with open(f'{game_selections.file_path}exclusion_list.json','w') as file:
                    data = {
                        "permanently_excluded": var_list[exclusion_type][0]
                    }
                    json.dump(data,file,indent=4)
            for game in range(len(game_selections.all_game_details)):
                try:
                    if game_selections.all_game_details[game][0] == title:
                        game_selections.all_game_details.pop(game)
                        break
                except Exception as e:
                    print(f"Error {e}.")
                    input()
        time.sleep(1)

class settings: 
    #'default', 'norecent', 'playtime'
    current_filter = "default"
    current_playtime_threshold = 120
    #what is displayed to the user, variable
    settings_list = [
        ["Show Game Images",game_selections.show_images], ["Show Developer(s)",game_selections.show_developers],["Show Publisher(s)",game_selections.show_publishers],
        ["Show Genre(s)",game_selections.show_genres],["Show Release Date",game_selections.show_release_date],["Show Description",game_selections.show_description],
        ["Current Filter",current_filter],["Playtime Threshold",current_playtime_threshold]
        ]
    #name,description,how it is stored
    filter_list = [["Default", "No games filtered out.", "default"],
        ["No Recent Games", "No games played in the last 2 weeks shown.", "norecent"],
        ["Low Played Games", "No games with playtime above _ mins. Current: {} mins.", "playtime"]
    ]
                    
    @staticmethod
    def view_settings(file_path, all_game_details, permanently_excluded, temporarily_excluded):
        if os.path.exists(f'{file_path}settings.json') == True: 
            general.clear_terminal()
            print(f"{'-'*6}   Settings   {'-'*6}")

            for setting in range(len(settings.settings_list)):
                print(f'{setting}) {settings.settings_list[setting][0]}: {settings.bool_to_symbol(settings.settings_list[setting][1])}')
                
            choice = None
            try: choice = int(input(f"[0-{len(settings.settings_list)-2}] Toggle Setting [ENTER] Return\n"))
            except: 
                game_selections.show_images = settings.settings_list[0][1]; game_selections.show_developers = settings.settings_list[1][1]
                game_selections.show_publishers = settings.settings_list[2][1]; game_selections.show_genres = settings.settings_list[3][1]
                game_selections.show_release_date = settings.settings_list[4][1]; game_selections.show_description = settings.settings_list[5][1]
                return
            
            if -1 < choice <= len(settings.settings_list):
                try:
                    setting_name = settings.settings_list[choice][0]
                    match setting_name:
                        case 'Playtime Threshold':
                            settings.change_playtime_threshold(choice=choice)
                        case 'Current Filter':
                            settings.change_filter_type(choice=choice)
                        case _:
                            settings.change_misc_setting(choice=choice)

                    settings.save_settings()
                except Exception as e:
                    print(f"Unable to modify settings with error {e}.")
                    time.sleep(3)
                
            game_selections.show_images = settings.settings_list[0][1]; game_selections.show_developers = settings.settings_list[1][1]
            game_selections.show_publishers = settings.settings_list[2][1]; game_selections.show_genres = settings.settings_list[3][1]
            game_selections.show_release_date = settings.settings_list[4][1]; game_selections.show_description = settings.settings_list[5][1]
        else: print("Settings file not found."); time.sleep(2)
    
    @staticmethod
    def change_filter_type(choice):
        general.clear_terminal()
        previous_filter = settings.current_filter
        print(f"{'-'*6}   Filters   {'-'*6}")
        
        for filterindx in range(len(settings.filter_list)):
            name = settings.filter_list[filterindx][0]
            description = settings.filter_list[filterindx][1]
            
            if "{}" in description:
                description = description.format(settings.current_playtime_threshold)
            print(f"{filterindx}) {name} - {description}")
        filter_choice = input(f"[0-{len(settings.filter_list) - 1}] Choose Filter Type [Other] Return\n")

        try:
            if -1 < int(filter_choice) <= len(settings.filter_list):
                settings.current_filter = str(settings.filter_list[int(filter_choice)][2])
                settings.settings_list[choice][1] = settings.current_filter 
                general.clear_terminal()
                print(f"{previous_filter} changed to {settings.current_filter}.")
                time.sleep(0.4)
                print(f"Rerolling game queue based on new filter...")
                time.sleep(1)
            elif isinstance(filter_choice, int):
                print("Invalid number.")
        except ValueError:
            pass

    @staticmethod
    def change_misc_setting(choice):
        settings.settings_list[choice][1] = not settings.settings_list[choice][1]
        general.clear_terminal()
        print(f"{settings.bool_to_symbol(not settings.settings_list[choice][1])} changed to {settings.bool_to_symbol(settings.settings_list[choice][1])} for {settings.settings_list[choice][0]}.")
        time.sleep(1)

    @staticmethod
    def save_settings():
        try:
            with open(f'{game_selections.file_path}settings.json', 'w') as file: 
                data = {
                    "show_images": settings.settings_list[0][1],
                    "show_developers": settings.settings_list[1][1],
                    "show_publishers": settings.settings_list[2][1],
                    "show_genres": settings.settings_list[3][1],
                    "show_release_date": settings.settings_list[4][1],
                    "show_description": settings.settings_list[5][1],
                    "current_filter": settings.current_filter,
                    "current_playtime_threshold": settings.current_playtime_threshold
                }
                json.dump(data,file,indent=4)   
        except Exception as e:
            print(f"Unable to save settings with error {e}")
            time.sleep(3)

    @staticmethod
    def change_playtime_threshold(choice):
        general.clear_terminal()
        try: 
            num = int(input(f"Input Playtime threshold in minutes. Low Played Games will hide games with\nplaytime above this number. Current: {settings.current_playtime_threshold} mins.\n"))
            if isinstance(num,int) and num >= 0:
                settings.current_playtime_threshold = num
                settings.settings_list[choice][1] = settings.current_playtime_threshold
                general.clear_terminal()
                print(f"Playtime threshold changed to {num} mins.")
                time.sleep(1.5) 
            else:
                print("Invalid input")
                time.sleep(2)
                
        except Exception as e: 
            print(f"Error: {e}")
            time.sleep(2)

    @staticmethod
    def load_settings(file_path,show_images,show_developers,show_publishers,show_genres,show_release_date,show_description):
        try:
            if os.path.exists(f'{file_path}settings.json') == True: 
                with open(f'{file_path}settings.json', 'r') as settings_file: 
                    settings_data = json.load(settings_file) 
                    game_selections.show_images = settings_data['show_images']
                    game_selections.show_developers = settings_data['show_developers']
                    game_selections.show_publishers = settings_data['show_publishers']
                    game_selections.show_genres = settings_data['show_genres']
                    game_selections.show_release_date = settings_data['show_release_date']
                    game_selections.show_description = settings_data['show_description']
                    settings.current_filter = settings_data['current_filter']
                    settings.current_playtime_threshold = settings_data['current_playtime_threshold']
                    settings.settings_list[6][1] = settings.current_filter
                    settings.settings_list[7][1] = settings.current_playtime_threshold
            else:
                print(f"Settings file does not exist/cannot load. Using default values.")
            return game_selections.show_images,game_selections.show_developers,game_selections.show_publishers,game_selections.show_genres,game_selections.show_release_date,game_selections.show_description
        except Exception as e:
            print(f"Unable to load settings with error {e}. Try deleting the file and recreating it if the error continues.")
    
    @staticmethod      
    def bool_to_symbol(input): 
        match input:
            case bool():
                return '✓' if input else '✗'
            case int():
                return general.time_convert(input)
            case str():
                match input:
                    case "default":
                        return "Default"
                    case "norecent":
                        return "No Recent Games"
                    case "playtime":
                        return "Less than _ Playtime"
                    case _:
                        return input
            case _:
                return input
        
class general:
    @staticmethod
    def clear_terminal(): os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def printw(text): print(textwrap.fill(text, width=80))
    
    @staticmethod
    def time_convert(timeint):
        if timeint >= 60:
            hours = timeint // 60
            minutes = timeint % 60
            if minutes == 0:
                return f"{hours} hr{'s' if hours > 1 else ''}"
            else:
                return f"{hours} hr{'s' if hours > 1 else ''}, {minutes} min"
        else:
            return f"{timeint} min"
        
if __name__ == "__main__":
    try:
        game_selections.main()
    except KeyboardInterrupt:
        print("\nExiting.")
        exit()