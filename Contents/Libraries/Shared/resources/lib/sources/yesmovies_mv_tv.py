# -*- coding: utf-8 -*-

'''
	Specto Add-on
	Copyright (C) 2016 mrknow

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

# TODO: Check gvideo resolving

import re,urllib,urlparse,json,hashlib,base64,time

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import testparams
from resources.lib.libraries import cache
from resources.lib import resolvers
from resources.lib import proxies
from resources.lib.libraries import control
from resources.lib.libraries import jsunfuck

CODE = '''def retA():
	class Infix:
		def __init__(self, function):
			self.function = function
		def __ror__(self, other):
			return Infix(lambda x, self=self, other=other: self.function(other, x))
		def __or__(self, other):
			return self.function(other)
		def __rlshift__(self, other):
			return Infix(lambda x, self=self, other=other: self.function(other, x))
		def __rshift__(self, other):
			return self.function(other)
		def __call__(self, value1, value2):
			return self.function(value1, value2)
	def my_add(x, y):
		try: return x + y
		except Exception: return str(x) + str(y)
	x = Infix(my_add)
	return %s
param = retA()'''

name = 'YesMovies'
loggertxt = []

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'Nov. 13, 2017'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.base_link = 'https://yesmovies.to'
		self.MainPageValidatingContent = 'Yesmovies - Watch FREE Movies Online & TV shows'
		self.ssl = False
		self.disabled = False
		self.name = name
		self.type_filter = ['movie', 'show', 'anime']
		self.loggertxt = []
		self.logo = 'http://i.imgur.com/4g0iJ8Y.png'
		self.info_link = '/ajax/movie_info/%s.html'
		self.episode_link = '/ajax/v4_movie_episodes/%s'
		self.playlist_link = '/ajax/v2_get_sources/%s.html?hash=%s'
		self.server_link = '/ajax/v4_movie_episodes/%s'
		self.embed_link = '/ajax/movie_embed/%s'
		self.token_link = '/ajax/movie_token?eid=%s&mid=%s'
		self.sourcelink = '/ajax/movie_sources/%s?x=%s&y=%s'
		self.speedtest = 0
		if len(proxies.sourceProxies)==0:
			proxies.init()
		self.proxyrequired = False
		self.msg = ''
		self.siteonline = self.testSite()
		self.testparser = 'Unknown'
		self.testparser = self.testParser()
		self.init = True
		log(type='INFO', method='init', err=' -- Initializing %s %s %s End --' % (name, self.ver, self.update_date))
		
	def info(self):
		return {
			'url': self.base_link,
			'name': self.name,
			'msg' : self.msg,
			'speed': round(self.speedtest,3),
			'logo': self.logo,
			'ssl' : self.ssl,
			'online': self.siteonline,
			'online_via_proxy' : self.proxyrequired,
			'parser': self.testparser
		}
		
	def getLog(self):
		self.loggertxt = loggertxt
		return self.loggertxt
		
	def testSite(self):
		try:
			x1 = time.time()
			http_res, content = proxies.request(url=self.base_link, output='response', use_web_proxy=False)
			self.speedtest = time.time() - x1
			if content != None and content.find(self.MainPageValidatingContent) >-1:
				log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,self.base_link))
				return True
			else:
				log('FAIL', 'testSite', 'Validation content Not Found. HTTP Resp : %s for %s' % (http_res,self.base_link))
				x1 = time.time()
				http_res, content = proxies.request(url=self.base_link, output='response', use_web_proxy=True)
				self.speedtest = time.time() - x1
				if content != None and content.find(self.MainPageValidatingContent) >-1:
					self.proxyrequired = True
					log('SUCCESS', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,self.base_link))
					return True
				else:
					time.sleep(2.0)
					x1 = time.time()
					http_res, content = proxies.request(url=self.base_link, output='response', use_web_proxy=True)
					self.speedtest = time.time() - x1
					if content != None and content.find(self.MainPageValidatingContent) >-1:
						self.proxyrequired = True
						log('SUCCESS', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,self.base_link))
						return True
					else:
						log('FAIL', 'testSite', 'Validation content Not Found. HTTP Resp : %s via proxy for %s' % (http_res,self.base_link))
			return False
		except Exception as e:
			log('ERROR','testSite', '%s' % e)
			return False
		
	def testParser(self):
		try:
			if self.disabled == True:
				log('INFO','testParser', 'Plugin Disabled - cannot test parser')
				return False
			if self.siteonline == False:
				log('INFO', 'testParser', '%s is offline - cannot test parser' % self.base_link)
				return False
		
			for movie in testparams.test_movies:
				getmovieurl = self.get_movie(title=movie['title'], year=movie['year'], imdb=movie['imdb'])
				movielinks = self.get_sources(url=getmovieurl, testing=True)
				
				if movielinks != None and len(movielinks) > 0:
					log('SUCCESS', 'testParser', 'Parser is working')
					return True
					
			log('FAIL', 'testParser', 'Parser NOT working')
			return False
		except Exception as e:
			log('ERROR', 'testParser', '%s' % e)
			return False

	def get_movie(self, imdb, title, year, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_movie','Provider Disabled by User')
				return None
			variations = [title, title.replace('&','and')]
			
			for title in variations:
				try:
					t = cleantitle.get(title)

					q = '/search/%s.html' % (urllib.quote_plus(cleantitle.query(title)))
					q = urlparse.urljoin(self.base_link, q)
					
					for i in range(3):
						r = client.request(q, IPv4=True)
						if not r == None: break

					r = client.parseDOM(r, 'div', attrs = {'class': 'ml-item'})
					r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in r]
					r = [(i[0][0], i[1][0]) for i in r if i[0] and i[1]]
					r = [i[0] for i in r if t == cleantitle.get(i[1])][:2]
					r = [(i, re.findall('(\d+)', i)[-1]) for i in r]

					for i in r:
						try:
							y, q = cache.get(self.ymovies_info, 9000, i[1])
							if not y == year: raise Exception()
							return urlparse.urlparse(i[0]).path, ''
						except:
							pass
				except:
					pass
		except Exception as e: 
			log('ERROR', 'get_movie','%s: %s' % (title,e), dolog=self.init)
			return

	def get_show(self, imdb=None, tvdb=None, tvshowtitle=None, year=None, season=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_show','Provider Disabled by User')
				return None
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urllib.urlencode(url)
			return url
		except Exception as e: 
			log('ERROR', 'get_show','%s: %s' % (tvshowtitle,e), dolog=self.init)
			return

	def get_episode(self, url=None, imdb=None, tvdb=None, title=None, year=None, season=None, episode=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				return None
			if url != None:
				data = urlparse.parse_qs(url)
				data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			else:
				data = {}
				data['tvshowtitle'] = title
			
			t1 = data['tvshowtitle']
			#t2 = cleantitle.get(data['tvshowtitle'])
			titles = [t1]
			if '\'s' in t1:
				t0 = t1.replace('\'s','')
				titles.append(t0)
				if ' ' in t0:
					t0 = t0.split(' ')
					t0 = t0[0]
					titles.append(t0)
			elif '\'' in t1:
				t0 = t1.replace('\'','')
				titles.append(t0)
				if ' ' in t0:
					t0 = t0.split(' ')
					t0 = t0[0]
					titles.append(t0)
			
			for title in titles:
				#print title
				try:
					season = '%01d' % int(season) ; episode = '%01d' % int(episode)
					#year = re.findall('(\d{4})', date)[0]
					years = [str(year), str(int(year)+1), str(int(year)-1)]

					r = cache.get(self.ymovies_info_season, 720, title, season)
					if r == None or len(r) == 0: raise Exception()
					#print r
					
					r = [(i[0], re.findall('(.+?)\s+(?:-|)\s+season\s+(\d+)$', i[1].lower())) for i in r]
					#print r
					
					r = [(i[0], i[1][0][0], i[1][0][1]) for i in r if i[1]]
					#print r
					
					r1 = []
					try:
						r1 = [i[0] for i in r if title == cleantitle.get(i[1]) and int(season) == int(i[2])][:2]
					except:
						pass
					if len(r1) == 0:
						r = [i[0] for i in r if int(season) == int(i[2])][:2]
					else:
						r = r1

					#print r
						
					r = [(i, re.findall('(\d+)', i)[-1]) for i in r]					
					#print r

					for i in r:
						try:
							y, q = cache.get(self.ymovies_info, 9000, i[1])
							mychk = False
							years = [str(year),str(int(year) + 1),str(int(year) - 1)]
							for x in years:
								if str(y) == x: mychk = True
							if mychk == False: raise Exception()
							return urlparse.urlparse(i[0]).path, (episode)
						except:
							pass
							
					# yr variation for shows
					try:
						year = int(year) - int(season)
						for i in r:
							try:
								y, q = cache.get(self.ymovies_info, 9000, i[1])
								mychk = False
								years = [str(year),str(int(year) + 1),str(int(year) - 1)]
								for x in years:
									if str(y) == x: mychk = True
								if mychk == False: raise Exception()
								return urlparse.urlparse(i[0]).path, (episode)
							except:
								pass
					except:
						pass
						
					# yr ignore for shows
					for i in r:
						return urlparse.urlparse(i[0]).path, (episode)
				except:
					pass		
			return
		except Exception as e: 
			log('ERROR', 'get_episode','%s: %s' % (title,e), dolog=self.init)
			return

	def ymovies_info_season(self, title, season):
		try:
			qs = []
			q = '%s Season %s' % (cleantitle.query(title), season)
			qs.append(q)
			q = cleantitle.query(title)
			qs.append(q)
			
			#print qs
			for qm in qs:
				try:
					q = '/search/%s.html' % (urllib.quote_plus(qm))
					q = urlparse.urljoin(self.base_link, q)
					#print q
					for i in range(3):
						r = client.request(q, IPv4=True)
						if not r == None: break
					
					r = client.parseDOM(r, 'div', attrs = {'class': 'ml-item'})
					r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in r]
					r = [(i[0][0], i[1][0]) for i in r if i[0] and i[1]]
					if not r == None and len(r) > 0: break
				except:
					pass

			return r
		except:
			return

	def ymovies_info(self, url):
		try:
			u = urlparse.urljoin(self.base_link, self.info_link)

			for i in range(3):
				r = client.request(u % url, IPv4=True)
				if not r == None: break

			q = client.parseDOM(r, 'div', attrs = {'class': 'jtip-quality'})[0]

			y = client.parseDOM(r, 'div', attrs = {'class': 'jt-info'})
			y = [i.strip() for i in y if i.strip().isdigit() and len(i.strip()) == 4][0]

			return (y, q)
		except:
			return

	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):
		#try:
		try:
			sources = []
			if url == None: 
				log('FAIL','get_sources','Could not find a matching title: %s' % cleantitle.title_from_key(key), dolog=not testing)
				return sources
			
			base_link = self.base_link
			
			try:
				if url[0].startswith('http'):
					base_link = url[0]
				mid = re.findall('-(\d+)', url[0])[-1]
			except:
				if url.startswith('http'):
					base_link = url
				mid = re.findall('-(\d+)', url)[-1]

			try:
				if len(url[1]) > 0:
					episode = url[1]
				else:
					episode = None
			except:
				episode = None

			#print mid

			links_m = []
			trailers = []
			headers = {'Referer': self.base_link}
			
			if testing == False:
				try:		
					u = urlparse.urljoin(self.base_link, url[0])
					#print u
					r = client.request(u, headers=headers, IPv4=True)
					#regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
					#matches = re.finditer(regex, r, re.MULTILINE)
					matches = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+').findall(r)
					for match in matches:
						try:
							#print match
							if 'youtube.com' in match:
								match = match.replace('embed/','watch?v=')
								trailers.append(match)
						except:
							pass
				except Exception as e:
					pass
					
				for trailer in trailers:
					links_m = resolvers.createMeta(trailer, self.name, self.logo, '720p', links_m, key, vidtype='Trailer', testing=testing)
			
			try:
				u = urlparse.urljoin(self.base_link, self.server_link % mid)
				#print u
				r = client.request(u, headers=headers, XHR=True, IPv4=True)
				r = json.loads(r)['html']
				r = client.parseDOM(r, 'div', attrs = {'class': 'pas-list'})
				ids = client.parseDOM(r, 'li', ret='data-id')
				servers = client.parseDOM(r, 'li', ret='data-server')
				labels = client.parseDOM(r, 'a', ret='title')
				r = zip(ids, servers, labels)
				
				for eid in r:
					#print r
					try:
						sub_url = None
						try:
							ep = re.findall('episode.*?(\d+):.*?',eid[2].lower())[0]
						except:
							ep = 0
						
						if (episode is None) or (int(ep) == int(episode)):
							
							url = urlparse.urljoin(self.base_link, self.token_link % (eid[0], mid))
							script = client.request(url, IPv4=True)
							#print script
							
							if '$_$' in script:
								params = self.uncensored1(script)
							elif script.startswith('[]') and script.endswith('()'):
								params = self.uncensored2(script)
							elif '_x=' in script and '_y=' in script:
								params = self.uncensored3(script)
							else:
								raise Exception()
							u = urlparse.urljoin(self.base_link, self.sourcelink % (eid[0], params['x'], params['y']))
							
							#print u
							
							r = client.request(u, IPv4=True)
							url = json.loads(r)['playlist'][0]['sources']
							#print url
							
							try:
								url = [i['file'] for i in url]
							except:
								url = [url['file']]
								
							#print url
							
							#url = [client.googletag(i) for i in url]
							#print url
							
							#url = [i[0] for i in url if i]
							#print url
							
							try:
								sub_url = json.loads(r)['playlist'][0]['tracks'][0]['file']
							except:
								pass
							
							for s in url:
								links_m = resolvers.createMeta(s, self.name, self.logo, '720p', links_m, key, vidtype='Movie', sub_url=sub_url, testing=testing)
					except:
						pass
			except:
				pass
				
			sources += [l for l in links_m]
			
			if len(sources) == 0:
				log('FAIL','get_sources','Could not find a matching title: %s' % cleantitle.title_from_key(key))
				return sources
			
			log('SUCCESS', 'get_sources','%s sources : %s' % (cleantitle.title_from_key(key), len(sources)), dolog=not testing)
			return sources
		except Exception as e:
			log('ERROR', 'get_sources', '%s' % e, dolog=not testing)
			return sources

	def resolve(self, url):
		return client.googlepass(url)


	def uncensored1(self, script):
		try:
			script = '(' + script.split("(_$$)) ('_');")[0].split("/* `$$` */")[-1].strip()
			script = script.replace('(__$)[$$$]', '\'"\'')
			script = script.replace('(__$)[_$]', '"\\\\"')
			script = script.replace('(o^_^o)', '3')
			script = script.replace('(c^_^o)', '0')
			script = script.replace('(_$$)', '1')
			script = script.replace('($$_)', '4')

			vGlobals = {"__builtins__": None, '__name__': __name__, 'str': str, 'Exception': Exception}
			vLocals = {'param': None}
			exec (CODE % script.replace('+', '|x|'), vGlobals, vLocals)
			#js_ret = js2py.eval_js(CODE % script.replace('+', '|x|'))
			
			data = vLocals['param'].decode('string_escape')
			x = re.search('''_x=['"]([^"']+)''', data).group(1)
			y = re.search('''_y=['"]([^"']+)''', data).group(1)
			return {'x': x, 'y': y}
		except Exception as e:
			log(type='ERROR', method='uncensored1', err='%s' % e)
			pass

	def uncensored2(self, script):
		try:
			js = jsunfuck.JSUnfuck(script).decode()
			x = re.search('''_x=['"]([^"']+)''', js).group(1)
			y = re.search('''_y=['"]([^"']+)''', js).group(1)
			return {'x': x, 'y': y}
		except Exception as e:
			log(type='ERROR', method='uncensored2', err='%s' % e)
			pass
			
	def uncensored3(self, script):
		try:
			js = script
			x = re.search('''_x=['"]([^"']+)''', js).group(1)
			y = re.search('''_y=['"]([^"']+)''', js).group(1)
			return {'x': x, 'y': y}
		except Exception as e:
			log(type='ERROR', method='uncensored3', err='%s' % e)
			pass

def log(type='INFO', method='undefined', err='', dolog=True, logToControl=False, doPrint=True):
	try:
		msg = '%s: %s > %s > %s : %s' % (time.ctime(time.time()), type, name, method, err)
		if dolog == True:
			loggertxt.append(msg)
		if logToControl == True:
			control.log(msg)
		if control.doPrint == True and doPrint == True:
			print msg
	except Exception as e:
		control.log('Error in Logging: %s >>> %s' % (msg,e))
