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


import re,json,base64

from resources.lib.libraries import cache
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import control



class alterepisode:
    def __init__(self):
        self.tvrage_link = 'http://www.tvrage.com/shows/id-%s/episode_list/all'
        self.epguides_link = 'http://epguides.com/common/exportToCSV.asp?rage=%s'

        self.tmdb_key = control.tmdb_key
        self.tmdb_info_link = 'http://api.themoviedb.org/3/tv/%s?api_key=%s&append_to_response=external_ids' % ('%s', self.tmdb_key)
        self.tmdb_by_imdb = 'http://api.themoviedb.org/3/find/%s?api_key=%s&external_source=imdb_id' % ('%s', self.tmdb_key)
        self.tmdb_by_tvdb = 'http://api.themoviedb.org/3/find/%s?api_key=%s&external_source=tvdb_id' % ('%s', self.tmdb_key)


    def get(self, imdb, tmdb, tvdb, tvrage, season, episode, alter, title, date):
        try:
            alt = False
            if alter == '1': alt = True
            elif any(x in alter for x in ['Documentary', 'Reality', 'Game Show', 'Talk Show']): alt = True
            if len(season) > 3: alt = True
            block = ['73141']
            if tvdb in block: alt = True
            if alt == False: raise Exception()

            if tvrage == '0': tvrage = cache.get(self.tvrageId, 8640, imdb, tmdb, tvdb)
            if tvrage == None: raise Exception()

            result = cache.get(self.tvrageEpisode, 8640, tvrage, title, date, season, episode)
            if result == None: raise Exception()
            return (result[0], result[1])
        except:
            return (season, episode)


    def tvrageId(self, imdb, tmdb, tvdb):
        try:
            if tmdb == '0' and not imdb == '0':
                url = self.tmdb_by_imdb % imdb
                result = client.request(url, timeout='5')

                tmdb = json.loads(result)
                tmdb = tmdb['tv_results'][0]['id']
                if tmdb == '' or tmdb == None: tmdb = '0'
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')


            if tmdb == '0' and not tvdb == '0':
                url = self.tmdb_by_tvdb % tvdb
                result = client.request(url, timeout='5')

                tmdb = json.loads(result)
                tmdb = tmdb['tv_results'][0]['id']
                if tmdb == '' or tmdb == None: tmdb = '0'
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                tmdb = tmdb.encode('utf-8')

            if tmdb == '0': raise Exception()

            url = self.tmdb_info_link % tmdb

            result = client.request(url, timeout='5')
            result = json.loads(result)

            tvrage = result['external_ids']['tvrage_id']
            if tvrage == '' or tvrage == None: raise Exception()
            tvrage = re.sub('[^0-9]', '', str(tvrage))
            tvrage = tvrage.encode('utf-8')
            return tvrage
        except:
            pass


    def tvrageEpisode(self, tvrage, title, date, season, episode):
        monthMap = {'01':'Jan', '02':'Feb', '03':'Mar', '04':'Apr', '05':'May', '06':'Jun', '07':'Jul', '08':'Aug', '09':'Sep', '10':'Oct', '11':'Nov', '12':'Dec'}
        title = cleantitle.tv(title)

        try:
            url = self.tvrage_link % tvrage
            result = client.request(url, timeout='5')
            search = re.compile('<td.+?><a.+?title=.+?season.+?episode.+?>(\d+?)x(\d+?)<.+?<td.+?>(\d+?/.+?/\d+?)<.+?<td.+?>.+?href=.+?>(.+?)<').findall(result.replace('\n',''))
            d = '%02d/%s/%s' % (int(date.split('-')[2]), monthMap[date.split('-')[1]], date.split('-')[0])
            match = [i for i in search if d == i[2]]
            if len(match) == 1: return (str('%01d' % int(match[0][0])), str('%01d' % int(match[0][1])))
            match = [i for i in search if title == cleantitle.tv(i[3])]
            if len(match) == 1: return (str('%01d' % int(match[0][0])), str('%01d' % int(match[0][1])))
        except:
            pass

        try:
            url = self.epguides_link % tvrage
            result = client.request(url, timeout='5')
            search = re.compile('\d+?,(\d+?),(\d+?),.+?,(\d+?/.+?/\d+?),"(.+?)",.+?,".+?"').findall(result)
            d = '%02d/%s/%s' % (int(date.split('-')[2]), monthMap[date.split('-')[1]], date.split('-')[0][-2:])
            match = [i for i in search if d == i[2]]
            if len(match) == 1: return (str('%01d' % int(match[0][0])), str('%01d' % int(match[0][1])))
            match = [i for i in search if title == cleantitle.tv(i[3])]
            if len(match) == 1: return (str('%01d' % int(match[0][0])), str('%01d' % int(match[0][1])))
        except:
            pass


