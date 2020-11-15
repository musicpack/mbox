import sqlite3
from datetime import datetime
import os
from typing import Tuple

TEMP_DIR = os.path.join('cache','temp')
class Cache:
    def __init__(self) -> None:
        if not os.path.isdir('cache'):
            os.mkdir('cache')
        if not os.path.isdir(TEMP_DIR):
            os.mkdir(TEMP_DIR)
        for f in os.listdir(TEMP_DIR):
            os.remove(os.path.join(TEMP_DIR, f))

        self.database_path = os.path.join('cache', 'cache.db')
        self.connection = sqlite3.connect(self.database_path)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS youtube
             (id text,
             date_download real,
             date_hit real,
             hits integer,
             file_name text,
             title text
             description text,
             uploader text,
             uploader_url text,
             thumbnail_url text,
             user_requested text)''')
    
    def cleanup(self):
        for f in os.listdir('temp'):
            os.remove(os.path.join('temp', f))
    
    def add_youtube(self, id, date_download, date_hit, hits, file_name, title, description, uploader, uploader_url, thumbnail_url, user_requested):
        if not self.find_ytid(id):
            self.cursor.execute("INSERT INTO youtube VALUES (?,?,?,?,?,?,?,?,?,?,?)",(id, date_download, date_hit, hits, file_name, title, description, uploader, uploader_url, thumbnail_url, user_requested))
            self.connection.commit()
        else:
            raise FileExistsError('Cannot add ID {0}: already exists'.format(id))

    def find_ytid(self, id) -> Tuple or bool:
        t = (id,)
        self.cursor.execute('SELECT * FROM youtube WHERE id=?', t)
        for row in self.cursor:
            dbid, date_download, date_hit, hits, file_name, title, description, uploader, uploader_url, thumbnail_url, user_requested = row
            
            # Check if database file_name exists on disk, delete if not found
            if os.path.isfile(os.path.join('cache', 'youtube', file_name)):
                # set date_hit and hits
                self.cursor.execute('UPDATE youtube SET date_hit = ?, hits = ? WHERE id = ?', (self.timenow(), hits+1, dbid))
                self.connection.commit()
                return (dbid, date_download, date_hit, hits, file_name, title, description, uploader, uploader_url, thumbnail_url, user_requested)
            else:
                self.remove_ytid(id)
                
        return False

    def remove_ytid(self, id):
        t = (id,)
        self.cursor.execute('DELETE FROM youtube WHERE id=?', t)
        self.connection.commit()

    def timenow(self):
        now = datetime.now()
        return datetime.timestamp(now)