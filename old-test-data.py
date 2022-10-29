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
                            ('kyle', 'kyle', 'password'),
                            ('u01', 'user1', 'password'),
                            ('u02', 'user2', 'password'),
                            ('u03', 'user3', 'password'),
                            ('u04', 'user4', 'password'),
                            ('u05', 'user5', 'password'),
                            ('u06', 'user6', 'password'),
                            ('u07', 'user7', 'password'),
                            ('u08', 'user8', 'password'),
                            ('u09', 'user9', 'password'),
                            ('u10', 'user10', 'password');
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

    insert_playlists =  '''
                            INSERT INTO playlists(pid, title, uid) VALUES
                                (0, 'All Songs', 'u01'),
                                (1, 'Canadian Songs', 'u02'),
                                (2, 'British Invasion', 'u03'),
                                (3, 'Boomer Rock', 'u04'),
                                (4, 'New Songs', 'u05'),
                                (5, 'Solo Artists', 'u06'),
                                (6, 'Songs by Bands', 'u07'),
                                (7, 'Female Artists', 'u08'),
                                (8, 'All American', 'u09'),
                                (9, 'One of Each Artist', 'u10');
                        '''

    insert_plinclude =  '''
                            INSERT INTO plinclude(pid, sid, sorder) VALUES
                                (0, 0, 1),
                                (0, 1, 2),
                                (0, 2, 3),
                                (0, 3, 4),
                                (0, 4, 5),
                                (0, 5, 6),
                                (0, 6, 7),
                                (0, 7, 8),
                                (0, 8, 9),
                                (0, 9, 10),
                                (0, 10, 11),
                                (0, 11, 12),
                                (0, 12, 13),
                                (0, 13, 14),
                                (0, 14, 15),
                                (0, 15, 16),
                                (0, 16, 17),
                                (0, 17, 18),
                                (0, 18, 19),
                                (0, 19, 20),
                                (0, 20, 21),
                                (0, 21, 22),
                                (0, 22, 23),
                                (0, 23, 24),
                                (0, 24, 25),
                                (0, 25, 26),
                                (0, 26, 27),
                                (0, 27, 28),
                                (0, 28, 29),
                                (0, 29, 30),
                                (0, 30, 31),
                                (0, 31, 32),
                                (1, 0, 1),
                                (1, 1, 2),
                                (1, 2, 3),
                                (1, 3, 4),
                                (1, 26, 5),
                                (1, 4, 6),
                                (1, 5, 7),
                                (1, 6, 8),
                                (1, 7, 9),
                                (1, 8, 10),
                                (1, 9, 11),
                                (1, 10, 12),
                                (1, 11, 13),
                                (2, 12, 1),
                                (2, 13, 2),
                                (2, 14, 3),
                                (2, 21, 4),
                                (2, 27, 5),
                                (2, 28, 6),
                                (2, 29, 7),
                                (2, 30, 8),
                                (2, 31, 9),
                                (3, 9, 1),
                                (3, 10, 2),
                                (3, 11, 3),
                                (3, 12, 4),
                                (3, 13, 5),
                                (3, 14, 6),
                                (3, 15, 7),
                                (3, 16, 8),
                                (3, 17, 9),
                                (3, 27, 10),
                                (3, 28, 11),
                                (3, 29, 12),
                                (4, 0, 1),
                                (4, 1, 2),
                                (4, 2, 3),
                                (4, 26, 4),
                                (4, 6, 5),
                                (4, 7, 6),
                                (4, 8, 7),
                                (4, 18, 8),
                                (4, 19, 9),
                                (4, 20, 10),
                                (5, 0, 1),
                                (5, 1, 2),
                                (5, 2, 3),
                                (5, 3, 4),
                                (5, 4, 5),
                                (5, 5, 6),
                                (5, 6, 7),
                                (5, 7, 8),
                                (5, 8, 9),
                                (5, 15, 10),
                                (5, 16, 11),
                                (5, 17, 12),
                                (5, 18, 13),
                                (5, 19, 14),
                                (5, 20, 15),
                                (5, 22, 16),
                                (5, 23, 17),
                                (5, 24, 18),
                                (5, 25, 19),
                                (5, 30, 20),
                                (5, 31, 21),
                                (6, 9, 1),
                                (6, 10, 2),
                                (6, 11, 3),
                                (6, 12, 4),
                                (6, 13, 5),
                                (6, 14, 6),
                                (6, 27, 7),
                                (6, 28, 8),
                                (6, 29, 9),
                                (7, 3, 1),
                                (7, 4, 2),
                                (7, 5, 3),
                                (7, 6, 4),
                                (7, 7, 5),
                                (7, 8, 6),
                                (8, 15, 1),
                                (8, 16, 2),
                                (8, 17, 3),
                                (8, 21, 4),
                                (8, 22, 5),
                                (8, 23, 6),
                                (8, 24, 7),
                                (8, 25, 8),
                                (8, 26, 9),
                                (9, 0, 1), -- God's Plan, Drake
                                (9, 3, 2), -- My Heart Will Go On, Celine Dion
                                (9, 6, 3), -- Complicated, Avril Lavigne
                                (9, 9, 4), -- Tom Sawyer, Rush
                                (9, 12, 5), -- I Am The Walrus, The Beatles
                                (9, 15, 6), -- Purple Haze, Jimi Hendrix
                                (9, 18, 7), -- Gangnam Style, PSY
                                (9, 22, 8), -- Off the Wall, Michael Jackson
                                (9, 27, 9), -- Dogs, Pink Floyd
                                (9, 30, 10); -- Maybe I'm Amazed, Paul McCartney
                        '''

    insert_sessions =   '''
                            INSERT INTO sessions(uid, sno, start, end) VALUES

                        '''

    cursor.execute(insert_users)
    cursor.execute(insert_artists)
    cursor.execute(insert_songs)
    cursor.execute(insert_perform)
    cursor.execute(insert_playlists)
    cursor.execute(insert_plinclude)
    connection.commit()
    return
