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


import re,urllib,urlparse,json,random,time,base64
from resources.lib.libraries import control
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import testparams
from resources.lib import resolvers
from resources.lib import proxies
from __builtin__ import ord, format

class source:
	def __init__(self):
		self.base_link = 'https://fmovies.unlockpro.top'
		self.search_link = '/sitemap'
		self.search_link2 = 'https://fmovies.unlockpro.top/ajax/film/search?sort=year%3Adesc&funny=1&keyword=%s'
		self.hash_link = '/ajax/episode/info'
		self.MainPageValidatingContent = 'FMovies'
		self.ssl = False
		self.name = 'FMovies'
		self.loggertxt = []
		self.logo = 'http://i.imgur.com/li8Skjf.jpg'
		self.speedtest = 0
		if len(proxies.sourceProxies)==0:
			proxies.init()
		self.proxyrequired = False
		self.siteonline = self.testSite()
		self.testparser = 'Unknown'
		self.testparser = self.testParser()
		
	def info(self):
		return {
			'url': self.base_link,
			'name': self.name,
			'speed': round(self.speedtest,3),
			'logo': self.logo,
			'ssl' : self.ssl,
			'online': self.siteonline,
			'online_via_proxy' : self.proxyrequired,
			'parser': self.testparser
		}
		
	def log(self, type, method, err, dolog=False, disp=True):
		msg = '%s : %s>%s - : %s' % (type, self.name, method, err)
		if dolog == True:
			self.loggertxt.append(msg)
		if disp == True:
			logger(msg)
			
	def testSite(self):
		try:
			x1 = time.time()
			http_res, content = proxies.request(url=self.base_link, output='response', use_web_proxy=False)
			self.speedtest = time.time() - x1
			if content != None and content.find(self.MainPageValidatingContent) >-1:
				self.log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,self.base_link), dolog=True)
				return True
			else:
				self.log('ERROR', 'testSite', 'HTTP Resp : %s for %s' % (http_res,self.base_link), dolog=True)
				x1 = time.time()
				http_res, content = proxies.request(url=self.base_link, output='response', use_web_proxy=True)
				self.speedtest = time.time() - x1
				if content != None and content.find(self.MainPageValidatingContent) >-1:
					self.proxyrequired = True
					self.log('SUCCESS', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,self.base_link), dolog=True)
					return True
				else:
					time.sleep(2.0)
					x1 = time.time()
					http_res, content = proxies.request(url=self.base_link, output='response', use_web_proxy=True)
					self.speedtest = time.time() - x1
					if content != None and content.find(self.MainPageValidatingContent) >-1:
						self.proxyrequired = True
						self.log('SUCCESS', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,self.base_link), dolog=True)
						return True
					else:
						self.log('ERROR', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,self.base_link), dolog=True)
						self.log('ERROR', 'testSite', content, dolog=True)
			return False
		except Exception as e:
			self.log('ERROR','testSite', '%s' % e, dolog=True)
			return False
		
	def testParser(self):
		try:
			getmovieurl = self.get_movie(title=testparams.movie, year=testparams.movieYear, imdb=testparams.movieIMDb, testing=True)
			movielinks = self.get_sources(url=getmovieurl, testing=True)
			
			if movielinks != None and len(movielinks) > 0:
				self.log('SUCCESS', 'testParser', 'links : %s' % len(movielinks), dolog=True)
				return True
			else:
				self.log('ERROR', 'testParser', 'getmovieurl : %s' % getmovieurl, dolog=True)
				self.log('ERROR', 'testParser', 'movielinks : %s' % movielinks, dolog=True)
				return False
		except Exception as e:
			self.log('ERROR', 'testParser', '%s' % e, dolog=True)
			return False

	def get_movie(self, imdb, title, year, proxy_options=None, key=None, testing=False):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			#X - Requested - With:"XMLHttpRequest"
			return url
		except:
			return

	def get_show(self, imdb, tvdb, tvshowtitle, year, proxy_options=None, key=None, testing=False):

		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return None


	def get_episode(self, url, imdb, tvdb, title, date, season, episode, proxy_options=None, key=None, testing=False):

		try:
			if url == None: return

			url = urlparse.parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'],  url['season'], url['episode'], url['premiered'] = title, season, episode, date
			url = urllib.urlencode(url)
			return url
		except:
			return

	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):

		try:
			sources = []
			myts = str(((int(time.time())/3600)*3600))
			
			#self.log('GRABBER','get_sources-1', '%s' % url, dolog=False)

			if url == None: return sources

			if not str(url).startswith('http'):
				try:
					data = urlparse.parse_qs(url)
					data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

					title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

					year = re.findall('(\d{4})', data['premiered'])[0] if 'tvshowtitle' in data else data['year']
					try: episode = data['episode']
					except: pass

					query = {'keyword': title, 's':''}
					search_url = urlparse.urljoin(self.base_link, '/search')
					search_url = search_url + '?' + urllib.urlencode(query)
					result = proxies.request(search_url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
					
					#self.log('GRABBER','get_sources-2', '%s' % search_url, dolog=False)

					r = client.parseDOM(result, 'div', attrs = {'class': '[^"]*movie-list[^"]*'})[0]
					r = client.parseDOM(r, 'div', attrs = {'class': 'item'})
					r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', attrs = {'class': 'name'})) for i in r]
					r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and  len(i[1]) > 0]
					r = [(re.sub('http.+?//.+?/','/', i[0]), re.sub('&#\d*;','', i[1])) for i in r]

					if 'season' in data:
						r = [(i[0], re.sub(' \(\w*\)', '', i[1])) for i in r]
						#title += '%01d' % int(data['season'])
						url = [(i[0], re.findall('(.+?) (\d+)$', i[1])) for i in r]
						url = [(i[0], i[1][0][0], i[1][0][1]) for i in url if len(i[1]) > 0]
						url = [i for i in url if cleantitle.get(title) in cleantitle.get(i[1])]
						for i in url:
							print i[2],i[0],i[1]
							print '%01d' % int(data['season']) == '%01d' % int(i[2])

						url = [i for i in url if '%01d' % int(data['season']) == '%01d' % int(i[2])]
					else:
						url = [i for i in r if cleantitle.get(title) in cleantitle.get(i[1])]
					#print("r1", cleantitle.get(title),url,r)


					url = url[0][0]

					url = urlparse.urljoin(self.base_link, url)
					r2 = url.split('.')[-1]


				except:
					url == self.base_link


			try: url, episode = re.compile('(.+?)\?episode=(\d*)$').findall(url)[0]
			except: pass
			
			#self.log('GRABBER','get_sources-3', '%s' % url, dolog=False)

			referer = url
			#result = client.request(url, limit='0')
			result, headers, content, cookie1 = proxies.request(url, limit='0', output='extended', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			
			#self.log('GRABBER','get_sources-3.1', '%s' % url, dolog=False)

			hash_url = urlparse.urljoin(self.base_link, '/user/ajax/menu-bar')
			# int(time.time())
			query = {'ts': myts}
			query.update(self.__get_token(query))
			hash_url = hash_url + '?' + urllib.urlencode(query)
			r1, headers, content, cookie2 = proxies.request(hash_url, limit='0', output='extended', cookie=cookie1, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			
			#print "%s" % cookie1
			#print "%s" % cookie2
			
			#self.log('GRABBER','get_sources-3.2', '%s' % hash_url, dolog=False)

			alina = client.parseDOM(result, 'title')[0]

			atr = [i for i in client.parseDOM(result, 'title') if len(re.findall('(\d{4})', i)) > 0][-1]
			if 'season' in data:
				years = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1)]
				mychk = False
				for y in years:
					if y in atr: mychk = True
				result = result if mychk ==True else None
			else:
				result = result if year in atr else None

			#print("r3",result)

			try: quality = client.parseDOM(result, 'span', attrs = {'class': 'quality'})[0].lower()
			except: quality = 'hd'
			if quality == 'cam' or quality == 'ts': quality = 'CAM'
			elif quality == 'hd' or 'hd ' in quality: quality = 'HD'
			else: quality = 'SD'

			result = client.parseDOM(result, 'ul', attrs = {'data-range-id':"0"})

			#print result
			servers = []
			#servers = client.parseDOM(result, 'li', attrs = {'data-type': 'direct'})
			servers = zip(client.parseDOM(result, 'a', ret='data-id'), client.parseDOM(result, 'a'))
			servers = [(i[0], re.findall('(\d+)', i[1])) for i in servers]
			servers = [(i[0], ''.join(i[1][:1])) for i in servers]
			#print("r3",servers)

			try: servers = [i for i in servers if '%01d' % int(i[1]) == '%01d' % int(episode)]
			except: pass
			
			#print servers

			links_m = []
			for s in servers[:4]:
				try:

					headers = {'X-Requested-With': 'XMLHttpRequest'}
					hash_url = urlparse.urljoin(self.base_link, self.hash_link)
					query = {'ts': myts, 'id': s[0], 'update': '0'}

					query.update(self.__get_token(query))
					hash_url = hash_url + '?' + urllib.urlencode(query)
					headers['Referer'] = urlparse.urljoin(url, s[0])
					headers['Cookie'] = cookie1 + '; ' + cookie2 + '; user-info=null;  MarketGidStorage=%7B%220%22%3A%7B%22svspr%22%3A%22%22%2C%22svsds%22%3A1%2C%22TejndEEDj%22%3A%22MTQ5MzIzMTk1Mzc5MzExMDAxMjk1NDE%3D%22%7D%2C%22C110012%22%3A%7B%22page%22%3A1%2C%22time%22%3A1493231954827%7D%7D'
					
					#self.log('GRABBER','get_sources-3.9', '%s' % hash_url, dolog=False)
					result = proxies.request(hash_url, headers=headers, limit='0', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
					#self.log('GRABBER','get_sources-4', '%s' % result, dolog=False)

					query = {'id': s[0], 'update': '0'}
					query.update(self.__get_token(query))
					url = url + '?' + urllib.urlencode(query)
					#result = client2.http_get(url, headers=headers)
					result = json.loads(result)
					quality = 'SD'
					if s[1] == '1080': quality = '1080p'
					if s[1] == '720': quality = 'HD'
					if s[1] == 'CAM': quality == 'CAM'

					query = {'id':result['params']['id'], 'token':result['params']['token']}
					grabber = result['grabber'] + '?' + urllib.urlencode(query)
				
					if not grabber.startswith('http'):
						grabber = 'http:'+grabber
						
					#self.log('GRABBER','url', '%s' % grabber, dolog=False)

					result = proxies.request(grabber, headers=headers, referer=url, limit='0', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)

					result = json.loads(result)

					print result
					if 'data' in result.keys():
						result = [i['file'] for i in result['data'] if 'file' in i]

						for i in result:
							links_m = resolvers.createMeta(i, self.name, self.logo, quality, links_m, key)
					else:
						links_m = resolvers.createMeta(result['target'], self.name, self.logo, quality, links_m, key)
							
					if testing and len(links_m) > 0:
						break

				except Exception as e:
					print e
					pass

			sources += [l for l in links_m]
			self.log('SUCCESS', 'get_sources','links : %s' % len(sources), dolog=testing)
			return sources
		except Exception as e:
			self.log('ERROR', 'get_sources','%s' % e, dolog=testing)
			return sources


	def resolve(self, url):
		try:
			return url
		except:
			return
	
	def r01(self, t, e):
		i = 0
		n = 0
		for i in range(0, max(len(t), len(e))):
			if i < len(e):
				n += ord(e[i])
			if i < len(t):
				n += ord(t[i])
		h = format(int(hex(n),16),'x')
		return h

	def a01(self, t):
		i = 0
		for e in range(0, len(t)): 
			i += ord(t[e])
		return i


	def __get_token(self, n):
		try:
			d = base64.decodestring("bG9jYXRpb24=")
			s = self.a01(d)
			for i in n: 
				s += self.a01(self.r01(d + i, n[i]))
			return {'_': str(s)}
		except Exception as e:
			print("fmovies.py > get_token > %s" % e)

def logger(msg):
	control.log(msg)
