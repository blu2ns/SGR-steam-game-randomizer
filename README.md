# Steam Game Randomizer
Welcome to the creatively named Steam Game Randomizer, or SGR for short. 

## Features
  * Shows a random game from your steam library
  * Run the game from the randomizer instead of opening your steam library and finding the game
  * Exclude games from being shown to you
    
## Why use this over something like the steamDB game randomizer?
  * Allows you to pull your game list from the API even with your account being private (if you use the api key assigned to the user id you are using)
  * Faster rerolling
  * Run the game faster, instead of opening your steam library and finding the game
  * Exclude unwanted games from showing up in the randomizer
  * Runs locally
## Prerequisites:
  * Python 3.12 or higher
  * climage
  * requests
  * (follow setup guide for install)
## Setup
   * Clone the repository: git clone https://github.com/blu2ns/SGR-steam-game-randomizer/tree/main
   * Install dependencies with pip install -r ~/path/to/requirements.txt 
   * Run the program, it will automatically prompt you to create the necessary files it needs.
     * The program will prompt you to input a API key and User ID. Input them when requested. Follow the instructions below if you need help with the API Key or User ID.
     * How to find your user ID:
        * Open steam desktop app, website or mobile app.
        * Click on your profile picture in the top right.
        * Click account details.
        * At the top left of the page, under the (usernames)'s account text, your user ID will be shown there.
     * How to set up an API key:
        * Read the [steam api terms](https://steamcommunity.com/dev/apiterms) if you wish.
        * Go to [the api key registration page](https://steamcommunity.com/dev/apikey), and make sure you're logged in.
        * For this application, put in 'localhost' into the field.
        * Agree to the terms and press register.
        * Copy the key. Keep this key private.
     When you have those credentials, paste them into the program when it asks.
  * The first time the program is run, make sure to input Y when it asks to refresh the game list.
  * Once that has been completed, the program should be ready to run! Follow the onscreen prompts when using it.
  * IMPORTANT: The first time a game is rolled, the program has to download the game's image. It slows down the rerolls, and so I recommend just holding down the enter key for a while to get every game's image cached until rerolls go through your games fast.
  For linux users: I recommend creating a .desktop entry with the path to the script, it makes it easier to find and run. For windows users: I recommend switching to linux. 
