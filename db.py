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

def commit_connection():
    # commits to the connection
    connection.commit()
    return

def close_connection():
    # closes the connection
    connection.close()  
    return


def check_username_and_password(username, password):
    global connection, cursor
    # check if username and password are in the db
    cursor.execute("SELECT uid FROM users WHERE uid = :username AND pwd = :password;", 
                    {'username': username, 'password': password})
    if (cursor.fetchone()) == None:
        # then user does not exist so check if they are an artist
        cursor.execute("SELECT aid FROM artists WHERE aid = :username AND pwd =:password",
                    {'username': username, 'password': password})
        if (cursor.fetchone()) == None:
            # 0 = no account found
            return 0
        else:
            # 1 = artist
            return 1
    else:
        # then user exists so check if they are also an artist
        cursor.execute("SELECT aid FROM artists WHERE aid = :username AND pwd =:password",
                    {'username': username, 'password': password})
        if (cursor.fetchone()) == None:
            return 2 # 2 = user
        else:
            return 3 # 3 = user + artist


def check_unique_user(username):
    global connection, cursor
    # check if the userid is already in the db
    cursor.execute('SELECT * FROM users WHERE uid = :username', {'username': username})
    if cursor.fetchone() == None:
        return True
    else:
        return False

def insert_new_user(uid, name, pwd):
    # insert the new user's information into the db
    global connection, cursor
    cursor.execute('''INSERT INTO users(uid, name, pwd) Values 
                            (:uid, :name, :pwd)''',
                            {'uid': uid, 'name': name, 'pwd': pwd})
    return # add error check here like a try except

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
        # append a query for each key into keys
        keys.append(f"SELECT art.name, art.nationality, {counter + 1} as n FROM artists art WHERE art.name LIKE '%{word}%'")
        keys.append(f"SELECT art.name, art.nationality, {counter + len(keywords) + 1} as n FROM songs s, artists art, perform p WHERE s.sid = p.sid AND p.aid = art.aid AND s.title LIKE '%{word}%'")
        counter += 1
    # join keys by UNION
    keywords_query = (' UNION ').join(keys)
    # query to get the number of matching keywords as cnt
    query = ''' 
                SELECT name, nationality, COUNT(n) as cnt
                FROM (''' + keywords_query + ''')
                GROUP BY name, nationality
                ORDER BY cnt DESC
            '''
    # query to get the song number of songs performed with the info from query before
    final_query = ''' 
                        SELECT q1.name, q1.nationality, COUNT(s.title) as songcnt
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
    global connection, cursor
    # gets the artists info
    cursor.execute(''' SELECT s.sid, s.title, s.duration 
                            FROM artists a, songs s, perform p
                            WHERE a.name = :artist_name
                            AND a.aid = p.aid
                            AND p.sid = s.sid
                            GROUP BY s.sid
                        ''', {'artist_name': artist[0]})
    artist_info = cursor.fetchall()
    return artist_info


def check_unique_title_dur(title, duration, username):
    global connection, cursor
    # checks if title and duration are in the table already
    cursor.execute('''
                SELECT s.title, s.duration
                FROM songs s, artists a, perform p
                WHERE s.title = :title
                AND s.duration = :duration
                AND s.sid = p.sid
                AND p.aid = a.aid
                AND a.aid = :aid
                ''', {'title':title, 'duration':duration, 'aid': username})
    result = cursor.fetchone()
    if result == None:
        return True
    else:
        return False


def generate_sid():
    # takes max sid and adds 1
    global connection, cursor
    max_sid_query = '''
                SELECT MAX(sid) + 1
                FROM songs
            '''
    cursor.execute(max_sid_query)
    max_sid = cursor.fetchone()[0]
    new_sid = max_sid + 1
    return new_sid

def add_new_song(sid, title, duration, aid, features):
    global connection, cursor
    # need to add to songs table and perform table
    # artist info from current login
    # add try and except error check here
    counter = 0
    cursor.execute( ''' 
                        INSERT INTO songs(sid, title, duration) VALUES
                            (:sid, :title, :duration);
                    ''', {'sid':sid, 'title':title, 'duration':duration}
                    )
    cursor.execute( '''
                        INSERT INTO perform(aid, sid) VALUES
                            (:aid, :sid);
                    ''', {'aid': aid, 'sid':sid}
                    )
    # insert the featuring artists into to the perform table
    if len(features) != 0:
        features_query = ''' INSERT INTO perform(aid, sid) VALUES '''
        # generates string for adding values
        for item in features:
            if len(features) == 1:
                features_query += "('" + item + "', '"+ str(sid) + "');"
            elif counter == len(features) - 1:
                features_query += "('" + item + "', '" + str(sid) + "');"
            else:
                features_query += "('" + item + "', '"+ str(sid) + "'),"
            counter += 1 
        cursor.execute(features_query)

    connection.commit()
    return

def check_artist_aid(aid):
    global connection, cursor
    # check if artist id exists already
    cursor.execute( '''
                        SELECT aid FROM artists WHERE aid = :aid
                    ''', {'aid': aid})
    result = cursor.fetchone()
    if result == None:
        return False
    else:
        return True

def find_top_fans(aid):
    global connection, cursor
    # finds the top fans based on the total listen duration
    cursor.execute('''
                    SELECT q.uid, q.name FROM (
                        SELECT u.uid, u.name, SUM(l.cnt*s.duration) as rank
                        FROM users u, artists a, perform p, listen l, songs s
                        WHERE l.sid = s.sid
                        AND p.aid = a.aid
                        AND p.sid = s.sid
                        AND l.uid = u.uid
                        AND a.aid = :aid
                        GROUP BY u.uid, u.name
                        ORDER BY rank DESC
                        LIMIT 3) q
            ''', {'aid':aid})
    fans = cursor.fetchall()
    return fans


def find_top_playlists(aid):
    # finds the top playlists based on the number of songs that are in the playlist by that artist
    global connection, cursor
    cursor.execute( '''
                        SELECT q.pid, q.title FROM (
                        SELECT pl.pid, pl.title, COUNT(s.sid) as rank
                        FROM playlists pl, plinclude pli, artists a, songs s, perform p
                        WHERE pl.pid = pli.pid
                        AND pli.sid = s.sid
                        AND s.sid = p.sid
                        AND p.aid = a.aid
                        AND a.aid = :aid
                        GROUP BY pl.pid
                        ORDER BY rank DESC
                        LIMIT 3) q
                    ''', {'aid':aid}
    )
    playlists = cursor.fetchall()
    return playlists

def get_artists(song):
    global connection, cursor
    # get the artists that perform this song
    cursor.execute('''
                        SELECT a.name 
                        FROM artists a, songs s, perform p
                        WHERE a.aid = p.aid
                        AND p.sid = s.sid
                        AND s.sid = :sid
                    ''', {'sid': song[0]})
    artists = cursor.fetchall()
    return artists

def get_playlists_including(song):
    global connection, cursor
    # get the playlists that include this song
    cursor.execute( '''
                        SELECT pl.title 
                        FROM playlists pl, songs s, plinclude pli
                        WHERE pl.pid = pli.pid
                        AND pli.sid = s.sid
                        AND s.sid = :sid
                    ''', {'sid':song[0]})
    playlists = cursor.fetchall()
    return playlists

#=========================================================================
#
# SEARCH FOR SONGS AND PLAYLISTS
#
#=========================================================================

def songs_and_playlists(keywords)
    global connection, cursor

    # === get the songs query ===
    keys = []
    counter = 0
    
    for word in keywords:
        keys.append(f"SELECT s.id, s.title, s.duration, {counter + 1} as n FROM songs s WHERE s.title LIKE '%{word}%'")
        counter += 1
    
    keywords_query1 = (' UNION ').join(keys)
    songs_query = '''
                    SELECT sid, title, duration, COUNT(n) as cnt
                    FROM (''' + keywords_query1 + ''')
                    GROUP BY name, title, duration
                    ORDER BY cnt DESC
                '''
    
    # === get the playlists query ===
    keys = []
    counter = 0

    for word in keywords:
        keys.append(f"SELECT p.pid, p.title, {counter + 1} as n FROM playlists p WHERE p.title LIKE '%{word}%'")
        counter += 1

    keywords_query2 = (' UNION ').join(keys)
    playlist_query1 = '''
                        SELECT pid, title, COUNT(n) as cnt
                        FROM (''' + keywords_query2 + ''')
                        GROUP BY pid, title
                        ORDER BY cnt DESC
                      '''
    
    playlist_query2 = '''
                        SELECT q.pid, q.title, sum(s.duration) as duration
                        FROM (''' + playlist_query1 + ''') q, songs s, playlists p, plinclude pl
                        WHERE p.pid = pl.pid AND pl.sid = songs.sid
                        GROUP BY q.pid, q.title, s.duration
                        ORDER BY q.cnt DESC
                      '''
    
    # === combine songs and playlists ===
    songs_and_playlists = '''
                            SELECT qs.sid, qs.title, qs.duration, qp.pid, qp.title, qp.duration
                            FROM (''' + songs_query + ''') qs, (''' + playlist_query2 + ''') as qp
                            ORDER BY qs.cnt DESC
                          '''
    
    cursors.execute(songs_and_playlists)
    songs_and_playlists_list = cursor.fetchall()
    return songs_and_playlists_list

#=========================================================================
#
# END SESSION
#
#=========================================================================

def end_session(username):
    global connection, cursor
    
    # get uid
    cursor.execute('SELECT uid FROM users WHERE name = :username', {'username': username})
    uid = cursor.fetchone()
    
    cursor.execute('''
                        UPDATE session 
                        SER end = Time('now')
                        WHERE uid = :uid
                   ''', {'uid': uid})
    connection.commit()

#=========================================================================
