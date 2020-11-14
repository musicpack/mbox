import sqlite3
from datetime import datetime
import os
from typing import Tuple

class Cache:

    def __init__(self) -> None:
        if not os.path.isdir('cache'):
            os.mkdir('cache')
        self.database_path = os.path.join('cache', 'cache.db')
        self.connection = sqlite3.connect(self.database_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS youtube
             (id text, 
             date_download real, 
             title text, 
             path text, 
             size integer,
             date_hit real,
             user text,
             hits integer)''')
    
    def add_youtube(self, id, date_download, title, path, size, date_hit, user, hits = 0):
        self.cursor.execute("INSERT INTO youtube VALUES (?,?,?,?,?,?,?,?)",(id, date_download, title, path, size, date_hit, user, hits))
        self.connection.commit()

    def find_ytid(self, id) -> Tuple or bool:
        t = (id,)
        self.cursor.execute('SELECT * FROM youtube WHERE id=?', t)
        first_result = self.cursor.fetchone()
        if first_result:
            dbid, date_download, title, path, size, date_hit, user, hits = first_result
            now = datetime.now()
            print(datetime.timestamp(now))
            # set date_hit and hits
            self.cursor.execute('UPDATE youtube SET date_hit = ?, hits = ? WHERE id = ?', (datetime.timestamp(now), hits+1, dbid))
            self.connection.commit()
            return (dbid, date_download, title, path, size, date_hit, user, hits)
        else:
            return False
