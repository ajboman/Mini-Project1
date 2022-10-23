import sqlite3
import os


connection = None
cursor = None

def connect(path):
    # connects to the database
    global connection, cursor

    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA forteign_keys=ON; ')
    connection.commit()
    return

def define_tables():
    # defines the tables to be used for this project
    global connection, cursor

    users_query =   ''' 
                        CREATE TABLE users (
                                uid CHAR(4),
                                name TEXT,
                                pwd TEXT,
                                PRIMARY KEY (uid)
                                );
                    '''

    songs_query =   ''' 
                        CREATE TABLE songs (
                                sid INTEGER,
                                title TEXT,
                                duration INTEGER,
                                PRIMARY KEY (sid)
                                );
                    '''
    
    sessions_query= ''' 
                        CREATE TABLE sessions (
                                uid CHAR(4),
                                sno INTEGER,
                                start DATE,
                                end DATE,
                                PRIMARY KEY(uid, sno),
                                FOREIGN KEY (uid) REFERENCES users(uid)
                                ON DELETE CASCADE
                                );
                    '''
    
    listen_query=   '''
                        CREATE TABLE listen (
                                uid CHAR(4),
                                sno INTEGER,
                                sid INTEGER,
                                cnt REAL,
                                PRIMARY KEY (uid, sno, sid),
                                FOREIGN KEY (uid, sno) REFERENCES sessions(uid, sno),
                                FOREIGN KEY (sid) REFERENCES songs(sid)
                                );
                    '''

    playlists_query='''
                        CREATE TABLE playlists (
                                pid INTEGER,
                                title TEXT,
                                uid CHAR(4),
                                PRIMARY KEY (pid),
                                FOREIGN KEY (uid) REFERENCES users(uid)
                                );
                    '''

    plinclude_query='''
                        CREATE TABLE plinclude(
                                pid INTEGER,
                                sid INTEGER,
                                sorder INTEGER,
                                PRIMARY KEY (pid, sid),
                                FOREIGN KEY (pid) REFERENCES playlists(pid),
                                FOREIGN KEY (sid) REFERENCES songs(sid)
                                );
                    '''

    artists_query=  '''
                        CREATE TABLE artists(
                                aid CHAR(4),
                                name TEXT,
                                nationality TEXT,
                                pwd TEXT,
                                PRIMARY KEY (aid)
                                );
                    '''

    perform_query=  '''
                        CREATE TABLE perform(
                                aid CHAR(4),
                                sid INTEGER,
                                PRIMARY KEY (aid, sid),
                                FOREIGN KEY (aid) REFERENCES artists(aid),
                                FOREIGN KEY (sid) REFERENCES songs(sid)
                                );
                    '''
    cursor.execute(users_query)
    cursor.execute(songs_query)
    cursor.execute(sessions_query)
    cursor.execute(listen_query)
    cursor.execute(playlists_query)
    cursor.execute(plinclude_query)
    cursor.execute(artists_query)
    cursor.execute(perform_query)
    connection.commit()
    return


def drop_tables():
    # drops tables if they exist
    global connection, cursor

    drop_users = "DROP TABLE IF EXISTS users; "
    drop_songs = "DROP TABLE IF EXISTS songs; "
    drop_sessions = "DROP TABLE IF EXISTS sessions; "
    drop_listen = "DROP TABLE IF EXISTS listen; "
    drop_playlists = "DROP TABLE IF EXISTS playlists; "
    drop_plinclude = "DROP TABLE IF EXISTS plinclude ; "
    drop_artists = "DROP TABLE IF EXISTS artists; "
    drop_perform = "DROP TABLE IF EXISTS perform; "

    cursor.execute(drop_users)
    cursor.execute(drop_songs)
    cursor.execute(drop_sessions)
    cursor.execute(drop_listen)
    cursor.execute(drop_playlists)
    cursor.execute(drop_plinclude)
    cursor.execute(drop_artists)
    cursor.execute(drop_perform)
    return


def insert_data(): 
    global connection, cursor

    insert_users =  '''
                        INSERT INTO users(uid, name, pwd) VALUES
                            ('adam', 'adam', 'pwd'),
                            ('kyle', 'kyle', 'password');
                    '''


    insert_artists= '''
                        INSERT INTO artists(aid, name, nationality, pwd) VALUES
                            ('anna', 'anna', 'german', 'pass'),
                            ('adam', 'adam', 'canadian', 'pwd');
                    '''

    cursor.execute(insert_users)
    cursor.execute(insert_artists)
    connection.commit()
    return

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')
    return

def draw_login_screen():
    clear_terminal()
    print("---UAtify---")
    return

def draw_user_screen():
    clear_terminal()
    print('Select an option: ')
    print('1. Start a session.')
    print('2. Search for songs and playlists.')
    print('3. Search for artists.')
    print('4. End session.')
    user_choice = input('')
    if user_choice == '1': # start a session
        return
    elif user_choice == '2': # search for songs and playlists
        return
    elif user_choice == '3': # search for artists
        return
    else: # user choice == 4 # end session and return to login screen
        return
    return

def draw_artist_screen():
    clear_terminal()
    print('Select an option: ')
    print('1. Add a song.')
    print('2. Find top fans and playlists.')
    artist_choice = input('')
    if artist_choice == '1':
        return
    elif artist_choice == '2':
        return
    return


def create_account():
    global connection, cursor
    clear_terminal()
    print('Account not found. Must create a new account.')
    new_user_id = input("Enter a unique user ID: ")
    cursor.execute('SELECT * FROM users WHERE uid = :new_user_id', {'new_user_id': new_user_id})
    while (cursor.fetchone() != None):
        # if cursor.fetchone() != none then the user id is not unique
        clear_terminal()
        print('Account not found. Must create a new account.')
        print("Error: User ID not unique")
        new_user_id = input("Enter a unique user ID: ")
        cursor.execute('SELECT * FROM users WHERE uid = :new_user_id', {'new_user_id': new_user_id})
    clear_terminal()
    print('Account not found. Must create a new account.')
    new_user_name = input("Successful Unique User ID\nEnter a name:")
    new_user_pwd = input("Enter a password: ")
    cursor.execute('''INSERT INTO users(uid, name, pwd) Values 
                            (:id, :name, :pwd)''',
                            {'id': new_user_id, 'name': new_user_name, 'pwd': new_user_pwd})
    return

def login_check():
    # verifies the login information
    global connection, cursor
    username = input("Enter a Username: ")
    password = input("Enter a Password: ")
    # check if they are a user
    cursor.execute("SELECT uid FROM users WHERE uid = :username AND pwd = :password;", 
                    {'username': username, 'password': password})
    if (cursor.fetchone()) == None:
        # then user does not exist so check if they are an artist
        cursor.execute("SELECT aid FROM artists WHERE aid = :username AND pwd =:password",
                    {'username': username, 'password': password})
        if (cursor.fetchone()) == None:
            # they are neither artist nor user so ask to create account then display user screen
            create_account()
            draw_user_screen()
            return
        else:
            #display artist screen
            draw_artist_screen()
            return
    else:
        # then user exists so check if they are also an artist
        cursor.execute("SELECT aid FROM artists WHERE aid = :username AND pwd =:password",
                    {'username': username, 'password': password})
        if (cursor.fetchone()) == None:
            # then user is not an artist
            draw_user_screen()
            return
        else:
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
                draw_user_screen()

            return
    return



def main():
    global connection, cursor
    path = "./project.db"
    connect(path)

    drop_tables()
    define_tables()
    insert_data()

    draw_login_screen()

    login_check()

    connection.commit()
    connection.close()
    return 

if __name__ == "__main__":
    main()