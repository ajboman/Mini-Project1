import sqlite3
import os
import db
import sys


def draw_screen(user):
    if user['user_type'] == 0:
        create_account()
        draw_user_screen(user['username'])
    elif user['user_type'] == 1:
        draw_artist_screen()
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
            draw_artist_screen()
        else:
            #draw user screen
            draw_user_screen(user['username'])
    return

def create_account():
    clear_terminal()
    print('Account not found. Must create a new account.')
    new_user_id = input("Enter a unique user ID: ")
    user_check = db.check_unique_user(new_user_id)
    
    while (user_check == False):
        # if cursor.fetchone() != none then the user id is not unique
        clear_terminal()
        print('Account not found. Must create a new account.')
        print("Error: User ID not unique")
        new_user_id = input("Enter a unique user ID: ")
        user_check = db.check_unique_user(new_user_id)    
    clear_terminal()
    print('Account not found. Must create a new account.')
    new_user_name = input("Successful Unique User ID\nEnter a name:")
    new_user_pwd = input("Enter a password: ")
    db.insert_new_user(new_user_id, new_user_name, new_user_pwd)


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
            db.start_session(username)
            continue 
        elif user_choice == '2': # search for songs and playlists
            continue
        elif user_choice == '3': # search for artists
            continue
        elif user_choice == '4': # end session and return to login screen
            continue 
        elif user_choice == '5': # logout
            continue 
        elif user_choice == '6': # exit
            exit(0)
    return 


def draw_artist_screen():
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
            continue 
        elif artist_choice == '2':
            continue 
        elif artist_choice == '3': # logout
            continue 
        else: # artist_choice == '4' #exit
            exit(0)
    return 



def login():
    # verifies the login information
    clear_terminal()
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

    db.drop_tables()
    db.define_tables()
    db.insert_data()

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
