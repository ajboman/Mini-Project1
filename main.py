import sqlite3
import os
import db
import sys


def find_top(aid):
    # find the top fans and playlists
    top_fans = db.find_top_fans(aid)
    top_playlists = db.find_top_playlists(aid)
    
    return

def check_valid_features(features):
    if len(features) == 0:
        return True
    for item in features:
        if len(item) > 4:
            return False
        elif not db.check_artist_aid(item):
            return False
    return True
            

def add_song(username):
    # TO DO: add featuring artists
    user_input = ''
    features = []
    valid_features = False
    unique = False
    clear_terminal()
    print('Adding a Song.')
    while (not unique):
        title = input('Title: ')
        duration = input('Duration: ')
        while not duration.isdigit(): # make sure an integer is input
            clear_terminal()
            print('Adding a Song.')
            print('Title: ' + title)
            print('Error: Must be an integer.')
            duration = input('Duration: ')
        unique = db.check_unique_title_dur(title, duration)
        if not unique:
            print("Error: Song Title and Duration not Unique.\n Please Try Again.")
    while (not valid_features):
        feature_input = input("Enter Contributing Artist's IDs.\nPress Enter To Skip.\n ")
        features = feature_input.split()
        valid_features = check_valid_features(features)
        if not valid_features:
            print("ERROR: Invalid Artist ID. Please Try Again.")
    song_id = db.generate_sid()
    db.add_new_song(song_id, title, duration, username, features)
    return

def get_song_action(songs, index):
    # SONG ACTIONS
    # JUST THE CHOICE SELECTION SCREEN can call functions here
    # NOT DONE. JUST PLACEHOLDER.
    choice = ''
    clear_terminal()
    print(songs[int(index) - 1][0],songs[int(index) - 1][1],songs[int(index) - 1][2])
    print('1. Listen to this song.')
    print('2. More information.')
    print('3. Add to playlist.')
    print('4. Menu')
    while choice not in ['1','2','3','4']:
        choice = input('Select an option: ')
        if choice.upper() == 'EXIT':
            return
    if choice == '1':
        return
    elif choice == '2':
        return
    elif choice == '3':
        return
    elif choice == '4':
        return
    return

def draw_artist_info(artist):
    index = []
    counter = 1
    artist_info = db.get_artist_info(artist)
    clear_terminal()
    print('Songs performed by:', artist[0])
    for song in artist_info:
        print(str(counter) + '.', song[0], song[1], song[2])
        counter += 1
    for i in range(len(artist_info)):
        index += str(i + 1)
    choice = '-1'
    while choice not in index:
        choice = input('Select a Song or Type Exit: ')
        if choice.upper() == 'EXIT':
            return
    get_song_action(artist_info, choice)
    return  


def draw_artist_list(artists, page_num):
    counter = page_num * 5
    for item in [1,2,3,4,5]:
        if counter == page_num*5 + 5:
            continue
        if counter + 1 > len(artists):
            continue
        print(str(counter+1) + '.', artists[counter][0], artists[counter][1], artists[counter][2])
        counter += 1
    


def search_for_artist():
    # currently returns the artists without order
    exit_str = 'exit'
    page_num = 0
    clear_terminal()
    print('Searching For Artists:')
    user_input = input('Enter Keywords to Search or Exit to leave: \n')
    user_keywords = user_input.split()
    if (len(user_keywords) == 1 and user_input.upper() == exit_str.upper()):
        searching = False
        return
    artists = db.search_artists(user_keywords)
    draw_artist_list(artists, page_num)
    choice = '-1'
    index = []
    for i in range(len(artists)):
        index += str(i + 1)
    while (choice not in index):
        choice = input('Select an Artists or Type Next for the Next Page: ')
        if choice.upper() == 'NEXT':
            page_num += 1
            draw_artist_list(artists, page_num)
    draw_artist_info(artists[int(choice)-1])
    return

def draw_screen(user):
    if user['user_type'] == 0:
        create_account()
        draw_user_screen(user['username'])
    elif user['user_type'] == 1:
        draw_artist_screen(user['username'])
    elif user['user_type'] == 2:
        draw_user_screen(user['username'])
    elif user['user_type'] == 3:
        # then they are an artist and user let them choose
        clear_terminal()
        print('Would you like to login as user or artist?')
        choice = ''
        while (choice.upper() != 'ARTIST') and (choice.upper() != 'USER'):
            choice = input('')
        if choice.upper() == 'ARTIST':
            #draw artist screen
            draw_artist_screen(user['username'])
        else:
            #draw user screen
            draw_user_screen(user['username'])
    return

def create_account():
    clear_terminal()
    print('Account not found. Must create a new account.')
    new_user_id = input("Enter a unique user ID: ")
    user_check = db.check_unique_user(new_user_id)
    
    while (user_check == False or len(new_user_id) > 4):
        # if cursor.fetchone() != none then the user id is not unique
        clear_terminal()
        print('Account not found. Must create a new account.')
        print("Error: Must be 4 or less characters and unique.")
        new_user_id = input("Enter a unique user ID: ")
        user_check = db.check_unique_user(new_user_id)    
    clear_terminal()
    print('Account not found. Must create a new account.')
    new_user_name = input("Successful Unique User ID\nEnter a name:")
    new_user_pwd = input("Enter a password: ")
    db.insert_new_user(new_user_id, new_user_name, new_user_pwd)

def start_session(username):
    db.start_session(username)
    return


def draw_user_screen(username):
    user_choice = ''
    while (user_choice not in ['4','5']):
        clear_terminal()
        print('Select an option: ')
        print('1. Start a session.')
        print('2. Search for songs and playlists.')
        print('3. Search for artists.')
        print('4. End session.')
        print('5. Logout.')
        print('6. Exit.')
        user_choice = input('')
        if user_choice == '1': # start a session
            start_session(username)
            continue
        elif user_choice == '2': # search for songs and playlists
            continue
        elif user_choice == '3': # search for artists
            search_for_artist()
            continue
        elif user_choice == '4': # end session and return to login screen
            continue 
        elif user_choice == '5': # logout
            continue 
        elif user_choice == '6': # exit
            exit(0)
    return 


def draw_artist_screen(username):
    artist_choice = ''
    while (artist_choice not in ['3','4']):
        clear_terminal()
        print('Select an option: ')
        print('1. Add a song.')
        print('2. Find top fans and playlists.')
        print('3. Logout.')
        print('4. Exit.')
        artist_choice = input('')
        if artist_choice == '1':
            add_song(username)
            continue 
        elif artist_choice == '2':
            find_top(username)
            continue 
        elif artist_choice == '3': # logout
            continue 
        else: # artist_choice == '4' #exit
            exit(0)
    return 



def login():
    # verifies the login information
    clear_terminal()
    username = '12345'
    username = input("Enter a Username: ")
    while len(username) > 4:
        clear_terminal()
        print("ERROR: Must be 4 characters or less.")
        username = input("Enter a Username: ")
    password = input("Enter a Password: ")
    # check if they are a user
    result = db.check_username_and_password(username, password)
    return {'user_type':result, 'username':username, 'password':password}


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    return


def main():
    path = sys.argv[1]
    db.connect(path)


    playing = True
    while (playing):
        # user ={'user_type':result, 'username':username, 'password':password}
        user = login() 
        draw_screen(user)


    db.commit_connection()
    db.close_connection()
    return

if __name__ == '__main__':
    main()
