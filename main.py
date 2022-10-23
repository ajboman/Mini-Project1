import sqlite3


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
                            ('adam', 'adam', 'boman');
                    '''


    insert_artists= '''
                        INSERT INTO artists(aid, name, nationality, pwd) VALUES
                            ('anna', 'anna', 'german', 'poop');
                    '''

    cursor.execute(insert_users)
    cursor.execute(insert_artists)
    connection.commit()
    return


def loginCheck():
    global connection, cursor
    username = input("Username: ")
    password = input("Password: ")
    # check if they are a user
    cursor.execute("SELECT uid FROM users WHERE uid = :username AND pwd = :password;", 
                    {'username': username, 'password': password})
    if (cursor.fetchone()) == None:
        # then user does not exist so check if they are an artist
        cursor.execute("SELECT aid FROM artists WHERE aid = :username AND pwd =:password",
                    {'username': username, 'password': password})
        if (cursor.fetchone()) == None:
            # they are neither artist nor user so ask to create account
        else:
            #display artist screen
    else:
        # then user exists so check if they are also an artist
        cursor.execute("SELECT aid FROM artists WHERE aid = :username AND pwd =:password",
                    {'username': username, 'password': password})
        if (cursor.fetchone()) == None:
            # then user is not an artist
        else:
            # then they are an artist and user let them choose 
    return



def main():
    global connection, cursor
    path = "./project.db"
    connect(path)

    drop_tables()
    define_tables()
    insert_data()

    loginCheck()

    connection.commit()
    connection.close()
    return 

if __name__ == "__main__":
    main()
