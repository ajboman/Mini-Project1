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

#=========================================================================
#
# LOGIN
#
#=========================================================================

def check_username_and_password(username, password):
    global connection, cursor
    try:
        # check if username and password are in the db
        cursor.execute("SELECT uid FROM users WHERE UPPER(uid) = :username AND pwd = :password;", 
                        {'username': username.upper(), 'password': password})
        if (cursor.fetchone()) == None:
            # then user does not exist so check if they are an artist
            cursor.execute("SELECT aid FROM artists WHERE UPPER(aid) = :username AND pwd =:password",
                        {'username': username.upper(), 'password': password})
            if (cursor.fetchone()) == None:
                # 0 = no account found
                return 0
            else:
                # 1 = artist
                return 1
        else:
            # then user exists so check if they are also an artist
            cursor.execute("SELECT aid FROM artists WHERE UPPER(aid) = :username AND pwd =:password",
                        {'username': username.upper(), 'password': password})
            if (cursor.fetchone()) == None:
                return 2 # 2 = user
            else:
                return 3 # 3 = user + artist
    except:
        return None

def check_unique_user(username):
    global connection, cursor
    # check if the userid is already in the db
    try:
        cursor.execute('SELECT * FROM users WHERE UPPER(uid) = :username', {'username': username.upper()})
        if cursor.fetchone() == None:
            return True
        else:
            return False
    except:
        return None

def insert_new_user(uid, name, pwd):
    # insert the new user's information into the db
    global connection, cursor
    cursor.execute('''INSERT INTO users(uid, name, pwd) Values 
                            (:uid, :name, :pwd)''',
                            {'uid': uid, 'name': name, 'pwd': pwd})
    return

#=========================================================================
#
# START AND END SESSION
#
#=========================================================================

def start_session(username):
    global connection, cursor
    # get unique session number
    unique_sno = get_unique_sno(username)
    if unique_sno is not None:
        cursor.execute( '''
                            INSERT INTO sessions(uid, sno, start, end) VALUES
                                (:uid, :sno, DATE('now'), NULL)
                        ''', {'uid':username, 'sno':unique_sno})
        connection.commit()
        return 
    else:
        print("ERROR: Could Not Get Unique Session Number.")
        return
        
def end_session(username):
    global connection, cursor

    cursor.execute('''
                        UPDATE sessions
                        SET end = TIME('now')
                        WHERE UPPER(uid) = :uid 
                        AND end IS NULL
                    ''', {'uid':username.upper()})
    connection.commit()
    return

def check_sessions(username):
    global connection, cursor
    session_exist = None
    cursor.execute( ''' SELECT s.end
                        FROM sessions s
                        WHERE UPPER(s.uid) = :uid
                        AND s.end IS NULL
                        ''', {'uid':username.upper()})
    results = cursor.fetchall()
    if len(results) == 0:
        session_exist = False
    else:
        session_exist = True
    return session_exist

def get_unique_sno(username):
    # get unique session number
    global connection, cursor
    try:
        unique_sno = None
        cursor.execute( '''
                            SELECT MAX(s.sno)
                            FROM sessions s, users u
                            WHERE s.uid = u.uid
                            AND UPPER(u.uid) = :uid
                        ''', {'uid':username.upper()})

        max_sno = cursor.fetchone()[0]

        if max_sno == None:
            unique_sno = 1
        else:
            unique_sno = max_sno + 1
        return unique_sno
    except:
        return None

#=========================================================================
#
# SEARCH FOR ARTISTS
#
#=========================================================================

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
    try:
        cursor.execute(final_query)
        artists = cursor.fetchall()
        return artists
    except:
        return None


def get_artist_info(artist):
    global connection, cursor
    # gets the artists info
    try:
        cursor.execute(''' SELECT s.sid, s.title, s.duration 
                                FROM artists a, songs s, perform p
                                WHERE a.name = :artist_name
                                AND a.aid = p.aid
                                AND p.sid = s.sid
                                GROUP BY s.sid
                            ''', {'artist_name': artist[0]})
        artist_info = cursor.fetchall()
        return artist_info
    except:
        return None

#=========================================================================
#
# ADD SONG
#
#=========================================================================

def check_unique_title_dur(title, duration, username):
    global connection, cursor
    # checks if title and duration are in the table already
    cursor.execute('''
                SELECT s.title, s.duration
                FROM songs s, artists a, perform p
                WHERE UPPER(s.title) = :title
                AND s.duration = :duration
                AND s.sid = p.sid
                AND p.aid = a.aid
                AND UPPER(a.aid) = :aid
                ''', {'title':title.upper(), 'duration':duration, 'aid':username.upper()})
    result = cursor.fetchone()
    if result == None:
        return True
    else:
        return False

def generate_sid():
    # takes max sid and adds 1
    global connection, cursor
    max_sid_query = '''
                SELECT MAX(sid)
                FROM songs
            '''
    cursor.execute(max_sid_query)
    max_sid = cursor.fetchone()[0]
    if max_sid is None:
        new_sid = 1
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
                        SELECT aid FROM artists WHERE UPPER(aid) = :aid
                    ''', {'aid': aid.upper()})
    result = cursor.fetchone()
    if result == None:
        return False
    else:
        return True

#=========================================================================
#
# FIND TOP FANS AND PLAYLISTS
#
#=========================================================================

def find_top_fans(aid):
    global connection, cursor
    # finds the top fans based on the total listen duration
    try:
        cursor.execute('''
                        SELECT q.uid, q.name FROM (
                            SELECT u.uid, u.name, SUM(l.cnt*s.duration) as rank
                            FROM users u, artists a, perform p, listen l, songs s
                            WHERE l.sid = s.sid
                            AND p.aid = a.aid
                            AND p.sid = s.sid
                            AND l.uid = u.uid
                            AND UPPER(a.aid) = :aid
                            GROUP BY u.uid, u.name
                            ORDER BY rank DESC
                            LIMIT 3) q
                ''', {'aid':aid.upper()})
        fans = cursor.fetchall()
        return fans
    except:
        return None

def find_top_playlists(aid):
    # finds the top playlists based on the number of songs that are in the playlist by that artist
    global connection, cursor
    try:
        cursor.execute( '''
                            SELECT q.pid, q.title FROM (
                            SELECT pl.pid, pl.title, COUNT(s.sid) as rank
                            FROM playlists pl, plinclude pli, artists a, songs s, perform p
                            WHERE pl.pid = pli.pid
                            AND pli.sid = s.sid
                            AND s.sid = p.sid
                            AND p.aid = a.aid
                            AND UPPER(a.aid) = :aid
                            GROUP BY pl.pid
                            ORDER BY rank DESC
                            LIMIT 3) q
                        ''', {'aid':aid.upper()}
        )
        playlists = cursor.fetchall()
        return playlists
    except:
        return None
#=========================================================================
#
# SONG ACTIONS (LISTEN, MORE INFO, ADD TO PLAYLIST)
#
#=========================================================================

# GET MORE INFO FUNCTIONS
def get_artists(song):
    global connection, cursor
    # get the artists that perform this song
    try:
        cursor.execute('''
                            SELECT a.name 
                            FROM artists a, songs s, perform p
                            WHERE a.aid = p.aid
                            AND p.sid = s.sid
                            AND s.sid = :sid
                        ''', {'sid': song[0]})
        artists = cursor.fetchall()
        return artists
    except:
        return None


def get_playlists_including(song):
    global connection, cursor
    # get the playlists that include this song
    try:
        cursor.execute( '''
                            SELECT pl.title 
                            FROM playlists pl, songs s, plinclude pli
                            WHERE pl.pid = pli.pid
                            AND pli.sid = s.sid
                            AND s.sid = :sid
                        ''', {'sid':song[0]})
        playlists = cursor.fetchall()
        return playlists
    except:
        return None

# LISTEN TO SONG FUNCTION
def listen_to_song(song, username):
    global connection, cursor
    # get sno and listen cnt
    current_sno = get_current_sno(username) 
    if current_sno is not None:
        listen_cnt = get_listen_cnt(username, current_sno, song)
        if listen_cnt is not None:
            new_cnt = listen_cnt + 1
            insert_listen_event(username, current_sno, song[0], new_cnt)
            return
        else:
            print("ERROR: Could Not Find Listen Count.")
            return
    else:
        print('ERROR: Could Not Find Current Session Number.')
        return

def get_current_sno(username):
    global connection, cursor
    try: 
        cursor.execute('''
                        SELECT sno 
                        FROM sessions
                        WHERE UPPER(uid) = :uid
                        AND end IS NULL
                        ''', {'uid':username.upper()})
        sno = cursor.fetchone()[0]
        return sno
    except:
        return None

def get_listen_cnt(username, sno, song):
    global connection, cursor
    try:
        cursor.execute(''' 
                            SELECT cnt
                            FROM listen
                            WHERE UPPER(uid) = :uid
                            AND sno = :sno
                            AND sid = :sid
                        ''', {'uid':username.upper(), 'sno':sno, 'sid':song[0]})
        cnt = cursor.fetchone()
        if cnt == None:
            # no listen events created so create first
            cnt = 1
        else:
            cnt = cnt[0]
        return cnt
    except:
        return None

def insert_listen_event(uid, sno, sid, cnt):
    global connection, cursor
    listen_event_exists = check_listen_event(uid, sno, sid, cnt)
    if listen_event_exists: # update cnt    
        cursor.execute( ''' 
                            UPDATE listen
                            SET cnt = :cnt
                            WHERE UPPER(uid) = :uid
                            AND sno = :sno
                            AND sid = :sid
                        ''', {'uid':uid.upper(), 'sno':sno, 'sid':sid, 'cnt':cnt}) 
    else: # insert new listen event
        cursor.execute( ''' 
                            INSERT INTO listen(uid, sno, sid, cnt) VALUES
                                (:uid, :sno, :sid, :cnt)
                        ''', {'uid':uid, 'sno':sno, 'sid':sid, 'cnt':cnt})

    connection.commit()
    return

def check_listen_event(uid, sno, sid, cnt):
    global connection, cursor
    cursor.execute('''SELECT * FROM listen
                        WHERE UPPER(uid) = :uid
                        AND sno = :sno
                        AND sid = :sid
                        AND cnt = :cnt
                    ''', {'uid':uid.upper(), 'sno':sno, 'sid':sid, 'cnt':cnt})
    if cursor.fetchall() == None:
        return False
    else:
        return True

# ADD TO PLAYLIST FUNCTIONS
def get_owned_playlists(uid):
    global connection, cursor
    try:
        cursor.execute( '''
                            SELECT * 
                            FROM playlists
                            WHERE UPPER(uid) = :uid
                        ''', {'uid':uid.upper()})
        playlists = cursor.fetchall()
        return playlists
    except:
        return None

def generate_pid(uid):
    global connection, cursor
    try:
        unique_pid = -1
        cursor.execute(''' 
                        SELECT MAX(pid) 
                        FROM playlists
                        ''')
        max_pid = cursor.fetchone()
        if max_pid[0] == None:
            unique_pid = 1
        else:
            unique_pid = max_pid[0] + 1
        return unique_pid
    except:
        return None

def create_playlist(pid, title, uid):
    global connection, cursor
    cursor.execute(''' INSERT INTO playlists VALUES
                        (:pid, :title, :uid) 
                    ''', {'pid':pid, 'title':title, 'uid':uid})
    connection.commit()
    return

def get_sorder(pid):
    global connection, cursor
    try:
        sorder = -1
        cursor.execute('''
                            SELECT MAX(sorder) 
                            FROM plinclude pli
                            WHERE pid = :pid
                        ''', {'pid':pid})
        max_sorder = cursor.fetchone()[0]
        if max_sorder == None:
            sorder = 1
        else:
            sorder = max_sorder + 1
        return sorder
    except:
        return None

def insert_into_playlist(song, pid, sorder):
    global connection, cursor
    cursor.execute(''' 
                        INSERT INTO plinclude VALUES
                            (:pid, :sid, :sorder)
                    ''', {'pid':pid, 'sid':song[0], 'sorder':sorder})
    connection.commit()
    return

def check_plinclude(song, pid):
    global connection, cursor
    cursor.execute(''' SELECT * FROM plinclude
                       WHERE pid = :pid
                       AND sid = :sid 
                     ''', {'pid':pid, 'sid':song[0]})
    if cursor.fetchone() == None:
        return True
    else:
        return False


#=========================================================================
#
# SEARCH FOR SONGS AND PLAYLISTS
#
#=========================================================================

def songs_and_playlists(keywords):
    global connection, cursor
    try:
        # === get the songs query ===
        keys = []
        counter = 0
        
        for word in keywords:
            keys.append(f"SELECT s.sid, s.title, s.duration, {counter + 1} as n FROM songs s WHERE s.title LIKE '%{word}%'")
            counter += 1
        
        keywords_query1 = (' UNION ').join(keys)
        songs_query = '''
                        SELECT sid, title, duration, COUNT(n) as cnt
                        FROM (''' + keywords_query1 + ''')
                        GROUP BY sid, title, duration
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
                        '''
        
        playlist_query2 = '''
                            SELECT q.pid, q.title, sum(s.duration) as duration, q.cnt
                            FROM (''' + playlist_query1 + ''') q, songs s, playlists p, plinclude pl
                            WHERE p.pid = pl.pid 
                            AND pl.sid = s.sid
                            AND q.pid = p.pid
                            AND q.title = p.title
                            GROUP BY q.pid, q.title
                        '''
        
        # === combine songs and playlists ===
        union_query = songs_query + ''' UNION ''' + playlist_query2 + ''' ORDER BY cnt DESC '''
        final_query = '''
                        SELECT sid, title, duration 
                        FROM (''' + union_query + ''')
                        GROUP BY sid, title
                        ORDER BY cnt DESC'''
                        
        cursor.execute(final_query)
        songs_and_playlists_list = cursor.fetchall()
        return songs_and_playlists_list
    except:
        return None

#=========================================================================
#
# SEARCH FOR SONGS AND PLAYLISTS
#
#=========================================================================

def check_song_or_playlist(song_or_playlist):
    global connection, cursor
    # checks if the item exists as a song or as a playlist
    # returns 1 if song, 2 if playlist, 3 if both, 0 if neither
    try:
        results = 0
        cursor.execute(''' 
                            SELECT sid, title, duration
                            FROM songs
                            WHERE sid = :sid
                            AND title = :title
                            
                        ''', {'sid':song_or_playlist[0], 'title':song_or_playlist[1]})
        if cursor.fetchone() != None:
            return results + 1
        else:
            cursor.execute('''  
                                SELECT pid, title, uid
                                FROM playlists
                                WHERE pid = :pid
                                AND title = :title
                            ''', {'pid':song_or_playlist[0], 'title':song_or_playlist[1]})
            if cursor.fetchone() != None:
                return results + 2
        # songs have a duration 
        # playlists have a uid
        return results
    except:
        return None

def get_playlist_info(playlist):
    global connection, cursor
    try:
        # gets the playlist's info
        cursor.execute(''' SELECT s.sid, s.title, s.duration 
                                FROM songs s, playlists p, plinclude pli
                                WHERE p.pid = :pid
                                AND p.pid = pli.pid
                                AND pli.sid = s.sid
                                GROUP BY s.sid
                            ''', {'pid': playlist[0]})
        playlist_info = cursor.fetchall()
        return playlist_info
    except:
        return None