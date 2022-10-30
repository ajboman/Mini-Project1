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
    global connection, cursor
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
    global connection, cursor
    max_sid_query = '''
                SELECT MAX(sid)
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
    if len(features) != 0:
        features_query = ''' INSERT INTO perform(aid, sid) VALUES '''
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
    cursor.execute('''
                    SELECT q.uid, q.name FROM (
                        SELECT u.uid, u.name, SUM(l.cnt) as rank
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
    global connection, cursor
    cursor.execute( '''
                        SELECT pl.pid, pl.title, COUNT(s.sid) as rank
                        FROM playlists pl, plinclude pli, artists a, songs s, perform p
                        WHERE pl.pid = pli.pid
                        AND pli.sid = s.sid
                        AND s.sid = p.sid
                        AND p.aid = a.aid
                        AND a.aid = :aid
                        GROUP BY pl.pid
                        ORDER BY rank DESC
                        LIMIT 3
                    ''', {'aid':aid}
    )
    playlists = cursor.fetchall()
    return playlists