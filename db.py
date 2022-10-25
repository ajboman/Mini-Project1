import sqlite3

cursor = None
connection = None


def connect(path):
    global cursor, connection
    # connects to the database
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA forteign_keys=ON; ')
    connection.commit()
    return


def get_cursor():
    return cursor

def get_connection():
    return connection

def commit_connection():
    connection.commit()
    return

def close_connection():
    connection.close()  
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


def check_username_and_password(username, password):
    global connection, cursor
    cursor.execute("SELECT uid FROM users WHERE uid = :username AND pwd = :password;", 
                    {'username': username, 'password': password})
    if (cursor.fetchone()) == None:
        # then user does not exist so check if they are an artist
        cursor.execute("SELECT aid FROM artists WHERE aid = :username AND pwd =:password",
                    {'username': username, 'password': password})
        if (cursor.fetchone()) == None:
            return 0
        else:
            #display artist screen
            return 1
    else:
        # then user exists so check if they are also an artist
        cursor.execute("SELECT aid FROM artists WHERE aid = :username AND pwd =:password",
                    {'username': username, 'password': password})
        if (cursor.fetchone()) == None:
            # then user is not an artist
            return 2
        else:
            # then they are an artist and user let them choose
            return 3


def check_unique_user(username):
    global connection, cursor
    cursor.execute('SELECT * FROM users WHERE uid = :username', {'username': username})
    if cursor.fetchone() == None:
        return True
    else:
        return False

def insert_new_user(uid, name, pwd):
    global connection, cursor
    cursor.execute('''INSERT INTO users(uid, name, pwd) Values 
                            (:uid, :name, :pwd)''',
                            {'uid': uid, 'name': name, 'pwd': pwd})
    return # add error check here

# starts a session by appending new values to the sessions table
# a username is passed
def start_session(username):
    global connection, cursor
    
    # get uid
    cursor.execute('SELECT uid FROM users WHERE name = :username', {'username': username})
    uid = cursor.fetchone()
    
    cursor.execute('''
                    INSERT INTO sessions(uid, sno, start, end)
                    VALUES (:uid, ROWID, DATE('now'), NULL); 
                   ''', {'uid': uid})
    connection.commit()
    return # I DIDNT TEST THIS YET
