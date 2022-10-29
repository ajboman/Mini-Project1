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
                            ('a01', 'Drake', 'Canadian', '0001'),
                            ('a02', 'Celine Dion', 'Canadian', '0002'),
                            ('a03', 'Avril Lavigne', 'caNaDa', '0003'),
                            ('a04', 'Rush', 'CAnaDIAN', '0004'),
                            ('a05', 'The Beatles', 'British', '0005'),
                            ('a06', 'Jimi Hendrix', 'American', '0006'),
                            ('a07', 'PSY', 'Korean', '0007'),
                            ('a08', 'Michael Jackson', 'USA', '0008'),
                            ('a09', 'Pink Floyd', 'United Kingdom', '0009'),
                            ('a10', 'Paul McCartney', 'UK', '0010'),
                            ('adam', 'adam', 'canadian', 'pwd');
                    '''

    insert_songs=   ''' 
                        INSERT INTO songs(sid, title, duration) VALUES
                        -- Drake Songs
                            (0, 'God''s Plan', 198),
                            (1, 'One Dance', 173),
                            (2, 'Hotline Bling', 267),
                            -- Celine Dion Songs
                            (3, 'My Heart Will Go On', 280),
                            (4, 'The Power of Love', 342),
                            (5, 'Because You Loved Me', 273),
                            -- Avril Lavigne Songs
                            (6, 'Complicated', 244),
                            (7, 'Sk8er Boi', 204),
                            (8, 'Girlfriend', 216),
                            -- Rush Songs
                            (9, 'Tom Sawyer', 276),
                            (10, 'Limelight', 259),
                            (11, 'The Spirit of Radio', 299),
                            -- Beatles Songs
                            (12, 'I Am The Walrus', 275),
                            (13, 'Why Don''t We Do It In The Road?', 101),
                            (14, 'Everybody''s Got Something To Hide Except Me And My Monkey', 144),
                            -- Jimi Hendrix Songs
                            (15, 'Purple Haze', 170),
                            (16, 'All Along the Watchtower', 240),
                            (17, 'Hey Joe', 210),
                            -- PSY Songs
                            (18, 'Gangnam Style', 219),
                            (19, 'Gentleman', 194),
                            (20, 'That That', 174),
                            -- Michael Jackson Songs
                            (21, 'This Girl is Mine', 293), -- Alongside Paul McCartney
                            (22, 'Off the Wall', 246),
                            (23, 'Man in the Mirror', 318),
                            (24, 'Who Is It', 393),
                            (25, 'You Rock My World', 337),
                            (26, 'Don''t Matter To Me', 245), -- Alongside Drake
                            -- Pink Floyd Songs
                            (27, 'Dogs', 1026),
                            (28, 'Us and Them', 469),
                            (29, 'Comfortably Numb', 382),
                            -- Paul McCartney Songs
                            (30, 'Maybe I''m Amazed', 229),
                            (31, 'Live and Let Die', 192),
                            -- 'Band on the Run' has NO listeners, and NOT IN ANY PLAYLIST
                            (32, 'Band on the Run', 313);
                    '''

    insert_perform ='''
                        INSERT INTO perform(aid, sid) VALUES
                            -- Drake Songs
                            ('a01', 0),
                            ('a01', 1),
                            ('a01', 2),
                            -- Celine Dion Songs
                            ('a02', 3),
                            ('a02', 4),
                            ('a02', 5),
                            -- Avril Lavigne Songs
                            ('a03', 6),
                            ('a03', 7),
                            ('a03', 8),
                            -- Rush Songs
                            ('a04', 9),
                            ('a04', 10),
                            ('a04', 11),
                            -- Beatles Songs
                            ('a05', 12),
                            ('a05', 13),
                            ('a05', 14),
                            -- Jimi Hendrix Songs
                            ('a06', 15),
                            ('a06', 16),
                            ('a06', 17),
                            -- PSY Songs
                            ('a07', 18),
                            ('a07', 19),
                            ('a07', 20),
                            -- Michael Jackson Songs
                            ('a08', 22),
                            ('a08', 23),
                            ('a08', 24),
                            ('a08', 25),
                            -- Pink Floyd Songs
                            ('a09', 27),
                            ('a09', 28),
                            ('a09', 29),
                            -- Paul McCartney Songs
                            ('a10', 30),
                            ('a10', 31),
                            ('a10', 32),
                            -- COLLAB SONGS (2 artists)
                            -- 'This Girl is Mine' by Michael Jackson & Paul McCartney
                            ('a08', 21),
                            ('a10', 21),
                            -- 'Don't Matter To Me' by Drake & Michael Jackson
                            ('a01', 26),
                            ('a08', 26);
                    '''

    cursor.execute(insert_users)
    cursor.execute(insert_artists)
    cursor.execute(insert_songs)
    cursor.execute(insert_perform)
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


def search_artists(keywords):
    global connection, cursor
    # get LIKE artists
    keys = []
    counter = 0
    for word in keywords:
        keys.append(f"SELECT art.name, art.nationality, {counter + 1} as n FROM artists art WHERE art.name LIKE '%{word}%'")
        keys.append(f"SELECT art.name, art.nationality, {counter + len(keywords) + 1} as n FROM songs s, artists art, perform p WHERE s.sid = p.sid AND p.aid = art.aid AND s.title LIKE '%{word}%'")
        counter += 1
    keywords_query = (' UNION ').join(keys)
    query = ''' 
                SELECT name, nationality, COUNT(n) as cnt
                FROM (''' + keywords_query + ''')
                GROUP BY name, nationality
                ORDER BY cnt DESC
            '''
    final_query = ''' 
                        SELECT q1.name, q1.nationality, COUNT(s.title)
                        FROM (''' + query + ''') q1, songs s, perform p, artists a
                        WHERE q1.name = a.name
                        AND a.aid = p.aid
                        AND p.sid = s.sid
                        GROUP BY q1.name, q1.nationality
                        ORDER BY q1.cnt DESC
                     '''
    cursor.execute(final_query)
    artists = cursor.fetchall()
    return artists


def get_artist_info(artist):
    artist_info_query = ''' 
                            SELECT s.sid, s.title, s.duration 
                            FROM artists a, songs s, perform p
                            WHERE a.aid = p.aid
                            AND p.sid = s.sid
                        '''
    cursor.execute(artist_info_query)
    artist_info = cursor.fetchall()
    return artist_info