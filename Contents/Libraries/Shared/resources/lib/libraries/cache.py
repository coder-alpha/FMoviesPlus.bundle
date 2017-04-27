# -*- coding: utf-8 -*-

'''
    Specto Add-on
    Copyright (C) 2015 lambda

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re,hashlib,time, json

# try:
    # from sqlite3 import dbapi2 as database
# except:
    # from pysqlite2 import dbapi2 as database

from resources.lib.libraries import control



def get(function, timeout, *args, **table):
    try:
        response = None

        f = repr(function)
        f = re.sub('.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', f)

        a = hashlib.md5()
        for i in args: a.update(str(i))
        a = str(a.hexdigest())
    except:
        pass

    try:
        table = table['table']
    except:
        table = 'rel_list'

    try:
        control.makeFile(control.dataPath)
        dbcon = database.connect(control.cacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM %s WHERE func = '%s' AND args = '%s'" % (table, f, a))
        match = dbcur.fetchone()

        response = eval(match[2].encode('utf-8'))

        t1 = int(match[3])
        t2 = int(time.time())
        update = (abs(t2 - t1) / 3600) >= int(timeout)
        if update == False:
            return response
    except:
        pass

    try:
        r = function(*args)
        if (r == None or r == []) and not response == None:
            return response
        elif (r == None or r == []):
            return r
    except:
        return

    try:
        r = repr(r)
        t = int(time.time())
        dbcur.execute("CREATE TABLE IF NOT EXISTS %s (""func TEXT, ""args TEXT, ""response TEXT, ""added TEXT, ""UNIQUE(func, args)"");" % table)
        dbcur.execute("DELETE FROM %s WHERE func = '%s' AND args = '%s'" % (table, f, a))
        dbcur.execute("INSERT INTO %s Values (?, ?, ?, ?)" % table, (f, a, r, t))
        dbcon.commit()
    except:
        pass

    try:
        return eval(r.encode('utf-8'))
    except:
        pass


def timeout(function, *args, **table):
    try:
        response = None

        f = repr(function)
        f = re.sub('.+\smethod\s|.+function\s|\sat\s.+|\sof\s.+', '', f)

        a = hashlib.md5()
        for i in args: a.update(str(i))
        a = str(a.hexdigest())
    except:
        pass

    try:
        table = table['table']
    except:
        table = 'rel_list'

    try:
        control.makeFile(control.dataPath)
        dbcon = database.connect(control.cacheFile)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT * FROM %s WHERE func = '%s' AND args = '%s'" % (table, f, a))
        match = dbcur.fetchone()
        return int(match[3])
    except:
        return


def clear(table=None):
    try:
        control.idle()

        if table == None: table = ['rel_list', 'rel_lib']
        elif not type(table) == list: table = [table]

        yes = control.yesnoDialog(control.lang(30401).encode('utf-8'), '', '')
        if not yes: return

        dbcon = database.connect(control.cacheFile)
        dbcur = dbcon.cursor()

        for t in table:
            try:
                dbcur.execute("DROP TABLE IF EXISTS %s" % t)
                dbcur.execute("VACUUM")
                dbcon.commit()
            except:
                pass

        control.infoDialog(control.lang(30402).encode('utf-8'))
    except:
        pass


#def getMovieSource(self, title, year, imdb, source, call):
def get_cached_url(self, url, data='', cache_limit=8):
    try:
        dbcon = database.connect(control.sourcescachedUrl)
        dbcur = dbcon.cursor()

        #dbcur.execute(
        #    "CREATE TABLE IF NOT EXISTS rel_url (""source TEXT, ""imdb_id TEXT, ""season TEXT, ""episode TEXT, ""rel_url TEXT, ""UNIQUE(source, imdb_id, season, episode)"");")
        dbcur.execute(
        "CREATE TABLE IF NOT EXISTS url_cache (url VARCHAR(255) NOT NULL, data VARCHAR(255), response, res_header, timestamp, PRIMARY KEY(url, data))")
    except:
        pass

    try:
        if data is None: data = ''
        html = ''
        res_header = []
        created = 0
        now = time.time()
        age = now - created
        limit = 60 * 60 * cache_limit
        dbcur.execute('SELECT timestamp, response, res_header FROM url_cache WHERE url = %s and data=%s' % (url,data))
        rows =  dbcur.fetchall()
        control.log('DB ROWS: Url: %s, ' % (rows))

        if rows:
            created = float(rows[0][0])
            res_header = json.loads(rows[0][2])
            age = now - created
            if age < limit:
                html = rows[0][1]
        control.log('DB Cache: Url: %s, Data: %s, Cache Hit: %s, created: %s, age: %.2fs (%.2fh), limit: %ss' % (
        url, data, bool(html), created, age, age / (60 * 60), limit))
        return created, res_header, html
    except:
        return


def cache_url(self, url, body, data=None, res_header=None):
    try:
        dbcon = database.connect(control.sourcescachedUrl)
        dbcur = dbcon.cursor()
        dbcur.execute(
            "CREATE TABLE IF NOT EXISTS url_cache (url VARCHAR(255) NOT NULL, data VARCHAR(255), response, res_header, timestamp, PRIMARY KEY(url, data))")
    except:
        pass
    try:
        now = time.time()
        if data is None: data = ''
        if res_header is None: res_header = []
        res_header = json.dumps(res_header)
        # truncate data if running mysql and greater than col size
        sql = "REPLACE INTO url_cache (url, data, response, res_header, timestamp) VALUES(?, ?, ?, ?, ?)" % (url, data, body, res_header, now)
        #dbcur.execute("DELETE FROM url_cache WHERE func = '%s' AND args = '%s'" % (table, f, a))
        #dbcur.execute("INSERT INTO %s Values (?, ?, ?, ?)" % table, (f, a, r, t))
        dbcur.execute(sql)
        dbcon.commit()
    except:
        pass

