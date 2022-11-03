import sqlite3
import os
import db
import sys

#=========================================================================
#
# SEARCH FOR SONGS AND PLAYLISTS
#
#=========================================================================

def search_for_song_playlist(username):
    clear_terminal()
    index = []
    page_num = 0
    choice = ''
    user_in = ''
    search_res = ''
    while user_in == '' or user_in.isspace():
        user_in = input("Enter keywords\n")
        clear_terminal()
        
        if user_in.upper() != 'EXIT' and user_in != '' and (not user_in.isspace()):
            keywords = user_in.split()
            keywords = set(keywords)
            search_res = db.songs_and_playlists(keywords)

    if len(search_res) == 0:
        print("No Results Found.")
        input("Press Enter To Continue.\n")
        return
        
    if search_res is not None:
        # create list of index strings based on the number of songs and playlists
        for i in range(len(search_res)):
            index.append(str(i + 1))  
        # get the user's choice for which song or playlist
        while (choice not in index):
            clear_terminal()
            print('Page:', str(page_num + 1))
            print('Type Next or Back to Change Pages.\nType Menu to Leave.\n')
            draw_songs_and_playlists(search_res, page_num)
            choice = input('\nSelect a Song or Playlist:')
            if choice.upper() == 'NEXT':
                if ((((page_num + 1) *5) + 1) > len(search_res)):
                    pass
                else:
                    page_num += 1
            elif choice.upper() == 'BACK':
                if page_num == 0:
                    pass
                else:
                    page_num -=1
            elif choice.upper() == 'MENU' or choice.upper() == 'EXIT':
                return

        song_or_playlist = search_res[int(choice)-1]
        # result = 1 if song, 2 if playlist, 3 if both, 0 if neither
        result = db.check_song_or_playlist(song_or_playlist) 
        if result is not None:
            if result == 1: # song
                get_song_action(song_or_playlist, username)
            elif result == 2: # playlist
                get_playlist_action(song_or_playlist, username)
            elif result == 3: # both(unlikely as duration must equal a user id) just print the song
                get_song_action(song_or_playlist, username)
            else: # result == 4: neither
                print('ERROR: Selection Not a Song or Playlist.')
            return
        else:
            print("ERROR: Could Not Verify Song or Playlist.")
    else:
        print("ERROR: Songs and Playlists Not Found.")


def get_playlist_action(playlist, username):
    index = []
    counter = 1
    # get playlist info from database
    playlist_info = db.get_playlist_info(playlist)
    if playlist_info is not None:
        clear_terminal()
        # print the songs in the playlist
        print('Songs in the Playlist:', playlist[1])
        for song in playlist_info:
            print(str(counter) + '.', song[0], song[1], song[2])
            counter += 1
        # create an list of string index of the number of songs
        for i in range(len(playlist_info)):
            index.append(str(i + 1))
        choice = '-1'
        # loop until valid choice or 'exit' is entered
        while choice not in index:
            choice = input('Select a Song or Type Exit: ')
            if choice.upper() == 'EXIT':
                return
        # user must choose what to do with song
        get_song_action(playlist_info[int(choice) - 1], username)
        return 
    else:
        print("ERROR: Could Not Get Playlist Info.")
        return


def draw_songs_and_playlists(songs_and_playlists, page_num):
    # draws the requested page of songs and playlists 
    # if no page exists nothing is drawn
    counter = page_num * 5
    identifier_string = ''
    # prints 5 items
    for item in [0,1,2,3,4]:
        if counter == page_num*5 + 5:
            break
        if counter + 1 > len(songs_and_playlists):
            break
        song_or_playlist = db.check_song_or_playlist(songs_and_playlists[item])
        if song_or_playlist is not None:
            if song_or_playlist == 1:
                identifier_string = 'Song:'
            elif song_or_playlist == 2:
                identifier_string = 'Playlist:'
            elif song_or_playlist == 3:
                identifier_string = 'Both:'
            else:
                song_identifer = 'Neither:'
            
            print(str(counter+1) + '. ' + identifier_string, songs_and_playlists[counter][0], songs_and_playlists[counter][1], songs_and_playlists[counter][2])
            counter += 1
        else:
            print('ERROR: Could Not Check Song or Playlist.')
    return

#=========================================================================
#
# SONG ACTIONS (LISTEN, MORE INFO, ADD TO PLAYLIST)
#
#=========================================================================

def get_song_action(song, username):
    # SONG ACTIONS
    choice = ''
    clear_terminal()
    print(song[0],song[1],song[2])
    print('1. Listen to this song.')
    print('2. More information.')
    print('3. Add to playlist.')
    print('4. Menu')
    while choice not in ['1','2','3','4']:
        choice = input('Select an option: ')
        if choice.upper() == 'EXIT':
            return
    if choice == '1': # listen
        listen_to(song, username)
        return
    elif choice == '2': # more info
        get_song_info(song)
        return
    elif choice == '3': # add to playlist
        add_to_playlist(song, username)
        return
    elif choice == '4': # menu
        return
    return

def get_song_info(song):
    # names of artists who performed
    # id title duration
    # names of any playlists that include this song
    viewing = True
    contributing_artists = db.get_artists(song)
    if contributing_artists is not None:
        included_playlists = db.get_playlists_including(song)
        if included_playlists is not None:
            clear_terminal()
            print('Viewing More Information. Press Enter to Leave')
            print('Song ID, Title, Duration:\n', song[0], song[1], song[2])
            print('\nContributing Artists:')
            for artist in contributing_artists:
                print(artist[0])
            if len(included_playlists) == 0:
                print('\nNot Included in Any Playlists.')
            else:
                print('\nPlaylists including', song[1], ':')
                for playlist in included_playlists:
                    print(playlist[0])

            while viewing:
                user_input = input()
                if user_input == '':
                    viewing = False
            return
        else:
            print("ERROR: Could Not Get Included Playlists.")
            return
    else:
        print("ERROR: Could Not Get Song Info.")
        return
def listen_to(song, username):
    # add a listening event or increase listen cnt is event already exists
    session_exists = db.check_sessions(username)
    if session_exists:
        db.listen_to_song(song, username)
    else:
        start_session(username)
        db.listen_to_song(song, username)
    print('Listening To:', song[1], '\nPress Enter to Finish Listening.')
    input()
    return

def add_to_playlist(song, username):
    # must insert to playlists and plinclude
    # first get user's current playlists
    index = []
    owned_playlists = db.get_owned_playlists(username)
    if owned_playlists is not None:
        for i in range(len(owned_playlists)):
            index.append(str(i + 1))
        index.append('NEW')
        # then ask if they wanna put in those or a new playlist
        user_input = ''
        counter = 1
        while user_input.upper() not in index:
            if len(owned_playlists) != 0:
                for playlist in owned_playlists:
                    print(str(counter) + '. ', playlist)
                    counter += 1
                user_input = input('Select a Playlist or Type NEW to create a new playlist.\n')
            else:
                print('No Playlists Owned By This User. Creating Playlist.')
                user_input = 'NEW'
        if user_input.upper() == 'NEW':
            # create new playlist
            # need unique pid
            pid = db.generate_pid(username)
            if pid is not None:
                unique = db.check_plinclude(song, pid)
                if unique:
                    # title from input
                    title = ''
                    while title == '' or title.isspace():
                        clear_terminal()
                        title = input('Enter a Title: ')
                    db.create_playlist(pid, title, username)
                    sorder = db.get_sorder(pid)
                    if sorder is not None:
                        db.insert_into_playlist(song, pid, sorder)
                    else:
                        print("ERROR: Can Not Find Song Order")
                else:
                    print('Song is Already in the Playlist.')
                    input('Press Enter to Continue.\n')
            else:
                print("ERROR: Could Not Generate Unique Playlist ID.")
                return
        else: # insert into chosen playlist
            unique = db.check_plinclude(song, owned_playlists[int(user_input)-1][0])
            if unique:
                sorder = db.get_sorder(owned_playlists[int(user_input)-1][0])
                if sorder is not None:
                    db.insert_into_playlist(song, owned_playlists[int(user_input)-1][0], sorder)
                    print("Added To Playlist.")
                    input("Press Enter To Continue")
                else:
                    print("ERROR: Can Not Find Song Order")    
            else:
                print('Song is Already in the Playlist.')
                input('Press Enter to Continue.\n')
        return 
    else:
        print("ERROR: Could Not Find Owned Playlists.")
        return

#=========================================================================
#
# FIND TOP FANS AND PLAYLISTS
#
#=========================================================================


def find_top(aid):
    # find the top fans and playlists
    top_fans = db.find_top_fans(aid)
    if top_fans is not None:
        top_playlists = db.find_top_playlists(aid)
        if top_playlists is not None:
            clear_terminal()

            print('Top Fans:')
            for item in top_fans:
                print(item[0], item[1])

            print('\nTop Playlists:')
            for item in top_playlists:
                print(item[0], item[1])

            user_input = '-1'
            while user_input != '':
                # return when they are satisfied
                user_input = input('\nPress Enter To Return\n')
            return
        else:
            print("ERROR: Could Not Find Top Playlists.")
            return
    else:
        print('ERROR: Could Not Find Top Fans.')
        return
            
#=========================================================================
#
# ADD SONG
#
#=========================================================================

def add_song(username):
    # TO DO: add featuring artists
    user_input = ''
    features = []
    valid_features = False
    unique = False
    clear_terminal()
    print('Adding a Song.')
    # check that the song is not already in the table from the current artist
    while (not unique):
        title = input('Title: ')
        duration = input('Duration: ')
        # make sure input is an integer
        while not duration.isdigit(): 
            clear_terminal()
            # reprint info
            print('Adding a Song.')
            print('Title: ' + title)
            print('Error: Must be an integer.')
            duration = input('Duration: ')
        # unique title and duration check in database
        unique = db.check_unique_title_dur(title, duration, username)
        if not unique:
            print("Error: Song Title and Duration not Unique.\n Please Try Again.")
    # ask for featuring artists and check that they exist in the database
    while (not valid_features):
        feature_input = input("Enter Contributing Artist's IDs.\nPress Enter To Skip.\n ")
        features = feature_input.split()
        valid_features = check_valid_features(features)
        if not valid_features:
            print("ERROR: Invalid Artist ID. Please Try Again.")
    # generate a unique song id
    song_id = db.generate_sid()
    # add the song to the required tables
    db.add_new_song(song_id, title, duration, username, features)
    return

def check_valid_features(features):
    if len(features) == 0: # if no features then valid by default
        return True
    for item in features: # check that each aid is 4 characters or less
        if len(item) > 4:
            return False
        elif not db.check_artist_aid(item): # check that the artist exists
            return False
    return True # if all pass then all valid

#=========================================================================
#
# SEARCH FOR ARTISTS
#
#=========================================================================

def search_for_artist(username):
    exit_str = 'exit'
    page_num = 0
    clear_terminal()
    print('Searching For Artists:')
    user_input = ''
    while user_input == '' or user_input.isspace():
        clear_terminal()
        print('Searching For Artists:')
        user_input = input('Enter Keywords to Search:\n')
    # split the user_input into a list of the keywords
    user_keywords = user_input.split()
    user_keywords = set(user_keywords)
    artists = db.search_artists(user_keywords) # search db for artists like keywords
    if len(artists) == 0:
        clear_terminal()
        print("No Results Found.")
        input("Press Enter To Continue.\n")
        return
    if artists is not None:
        choice = '-1'
        index = []
        # create list of index strings based on the number of artists
        for i in range(len(artists)):
            index.append(str(i + 1))
        # ask to select an artist or see another page
        while (choice not in index):
            clear_terminal()
            print('Page:', str(page_num + 1))
            print('Type Next or Back to Change Pages.\nType Menu to Leave.\n')
            draw_artist_list(artists, page_num)
            choice = input('\nSelect an Artist:')
            if choice.upper() == 'NEXT':
                if ((((page_num + 1) *5) + 1) > len(artists)):
                    pass
                else:
                    page_num += 1
            elif choice.upper() == 'BACK':
                if page_num == 0:
                    pass
                else:
                    page_num -=1
            elif choice.upper() == 'MENU' or choice.upper() == 'EXIT':
                return
        # display the chosen artists info
        draw_artist_info(artists[int(choice)-1], username)
        return
    else:
        print('Could not find artists')
        return

def draw_artist_list(artists, page_num):
    # draws the requested page of artists 
    # if no page exists nothing is drawn
    counter = page_num * 5
    # prints 5 items
    for item in [1,2,3,4,5]:
        if counter == page_num*5 + 5:
            continue
        if counter + 1 > len(artists):
            continue
        print(str(counter+1) + '.', artists[counter][0], artists[counter][1], artists[counter][2])
        counter += 1
    return

def draw_artist_info(artist,username):
    index = []
    counter = 1
    # get artist info from database
    artist_info = db.get_artist_info(artist)
    if artist_info is not None:
        clear_terminal()
        # print the songs performed by the artist
        print('Songs performed by:', artist[0])
        for song in artist_info:
            print(str(counter) + '.', song[0], song[1], song[2])
            counter += 1
        # create an list of string index of the number of songs
        for i in range(len(artist_info)):
            index.append(str(i + 1))
        choice = '-1'
        # loop until valid choice or 'exit' is entered
        while choice not in index:
            choice = input('Select a Song or Type Exit: ')
            if choice.upper() == 'EXIT':
                return
        # user must choose what to do with song
        get_song_action(artist_info[int(choice) - 1], username)
        return  
    else:
        print('ERROR: Could Not Find Artist Info.')
        return

#=========================================================================
#
# START AND END SESSION
#
#=========================================================================

def start_session(username):
    # check if session already started
    session_exist = db.check_sessions(username)
    user_input = ''
    if session_exist:
        print('Session Already Started.\n Would you like to end current and start another?')
        while (user_input.upper() != 'YES' or user_input.upper()!='NO'):
            user_input = input('')
            if user_input.upper() == 'YES':
                end_session(username)
                db.start_session(username)
                input('Session Started.\nPress Enter To Continue.')
                return
            elif user_input.upper() == 'NO':
                return
    else:
        db.start_session(username)
        input('Session Started.\nPress Enter To Continue.')
    return

def end_session(username):
    # check if session already started
    session_exist = db.check_sessions(username)
    if session_exist:
        db.end_session(username)
        input('Session Ended.\nPress Enter To Continue.\n')
    else:
        print('No Session To End.')
        input('Press Enter To Continue.\n')
    return

#=========================================================================
#
# DRAW USER AND ARTIST SCREENS OR CREATE ACCOUNT
#
#=========================================================================

def draw_screen(user):
    if user['user_type'] == 0: # account does not exist
        create_account()
        draw_user_screen(user['username'])
    elif user['user_type'] == 1: # artist account
        draw_artist_screen(user['username'])
    elif user['user_type'] == 2: # user account
        draw_user_screen(user['username'])
    elif user['user_type'] == 3: # user and artist account
        # Give a choice of which type to login as
        clear_terminal()
        print('Would you like to login as user or artist?')
        choice = ''
        # case insensitive check must type 'artist' or 'user'
        while (choice.upper() != 'ARTIST') and (choice.upper() != 'USER'):
            choice = input('')
        if choice.upper() == 'ARTIST': # artist chosen
            draw_artist_screen(user['username'])
        elif choice.upper() == 'USER': # user chosen
            draw_user_screen(user['username']) 
    return

def draw_user_screen(username):
    user_choice = ''
    # print the options and act upon a valid choice being input
    while (user_choice not in ['5','6']):
        clear_terminal()
        print('Select an option: ')
        print('1. Start a session.')
        print('2. Search for songs and playlists.')
        print('3. Search for artists.')
        print('4. End session.')
        print('5. Logout.')
        print('6. Exit.')
        user_choice = input('')
        if user_choice == '1' or user_choice.upper() == 'START': # start a session
            start_session(username)
            continue
        elif user_choice == '2': # search for songs and playlists
            search_for_song_playlist(username)
            continue
        elif user_choice == '3': # search for artists
            search_for_artist(username)
            continue
        elif user_choice == '4' or user_choice.upper() == 'END': # end session and return to login screen
            end_session(username)
            continue 
        elif user_choice == '5' or user_choice.upper() == 'LOGOUT': # logout
            session_exist = db.check_sessions(username)
            if session_exist:
                end_session(username)
            continue
        elif user_choice == '6' or user_choice.upper() == 'EXIT': # exit
            session_exist = db.check_sessions(username)
            if session_exist:
                end_session(username)
            db.commit_connection()
            db.close_connection()
            exit(0)
    return 

def draw_artist_screen(username):
    artist_choice = ''
    # print the options and act upon a valid choice being input
    while (artist_choice not in ['3','4']):
        clear_terminal()
        print('Select an option: ')
        print('1. Add a song.')
        print('2. Find top fans and playlists.')
        print('3. Logout.')
        print('4. Exit.')
        artist_choice = input('')
        if artist_choice == '1' or artist_choice.upper() == 'ADD': # add song
            add_song(username)
            continue 
        elif artist_choice == '2' or artist_choice.upper() == 'FIND': # find top users and playlists
            find_top(username)
            continue 
        elif artist_choice == '3' or artist_choice.upper() == 'LOGOUT': # logout
            continue 
        elif artist_choice == '4' or artist_choice.upper() == 'EXIT': #exit
            # must implement if session: end_session()
            db.commit_connection()
            db.close_connection()
            exit(0)
    return 

def create_account():
    # Create a new account with valid credentials
    clear_terminal()
    print('Account not found. Must create a new account.')
    new_user_id = input("Enter a unique user ID: ")
    user_check = db.check_unique_user(new_user_id)
    if user_check is not None:
        while (user_check == False or len(new_user_id) > 4):
            # if user_check == False then the user id is not unique
            clear_terminal()
            print('Account not found. Must create a new account.')
            print("Error: Must be 4 or less characters and unique.")
            new_user_id = input("Enter a unique user ID: ")
            user_check = db.check_unique_user(new_user_id)  
            if user_check is not None:
                continue  
            else:
                print("ERROR: Cannot Check If User Is Unique.")
                break
        clear_terminal()
        # reprint 
        print('Account not found. Must create a new account.')
        new_user_name = input("Successful Unique User ID\nEnter a name:")
        new_user_pwd = input("Enter a password: ")
        # insert data into the tables
        
        db.insert_new_user(new_user_id, new_user_name, new_user_pwd)
    else:
        print("ERROR: Cannot Check If User Is Unique.")

#=========================================================================
#
# LOGIN
#
#=========================================================================

def login():
    # verifies the login information
    clear_terminal()
    username = ''
    username = input("Enter a Username: ")
    # make sure username is 4 characters
    while len(username) > 4 or username == '':
        clear_terminal()
        print("ERROR: Must be 4 characters or less.")
        username = input("Enter a Username: ")

    password = ''
    password = input("Enter a Password: ")
    while password == '':
        clear_terminal()
        print("Enter a Username:", username)
        password = input("Enter a Password: ")
    result = db.check_username_and_password(username, password) # check if they are a user
    if result is not None:
        return {'user_type':result, 'username':username, 'password':password}
    else:
        print('ERROR: Could Not Check If User.')
#=========================================================================


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
