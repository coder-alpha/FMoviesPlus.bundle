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
from resources.lib.libraries import jsfdecoder
from resources.lib.libraries import jsunpack
from resources.lib.libraries import testparams
from resources.lib.libraries import workers
from resources.lib import resolvers
from resources.lib import proxies
from __builtin__ import ord, format, eval

name = 'FMovies'
loggertxt = []

ENCRYPTED_URLS = False

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.2'
		self.update_date = 'Nov. 18, 2017'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.disabled = False
		self.TOKEN_KEY = []
		self.base_link_alts = ['https://bmovies.is','https://bmovies.to','https://bmovies.pro','https://bmovies.club','https://bmovies.online','https://bmovies.ru'] #['https://fmovies.to','https://fmovies.is','https://fmovies.se']
		self.base_link = self.base_link_alts[0]
		self.grabber_api = "grabber-api/"
		self.search_link = '/sitemap'
		self.ALL_JS = "/assets/min/public/all.js"
		self.TOKEN_KEY_PASTEBIN_URL = "https://pastebin.com/raw/VNn1454k"
		self.hash_link = '/ajax/episode/info'
		self.hash_menu_link = "/user/ajax/menu-bar"
		self.token_link = "/token"
		self.MainPageValidatingContent = ['bmovies','fmovies']
		self.type_filter = ['movie', 'show', 'anime']
		self.ssl = False
		self.name = name
		self.headers = {}
		self.cookie = None
		self.loggertxt = []
		self.logo = 'http://i.imgur.com/li8Skjf.jpg'
		self.speedtest = 0
		if len(proxies.sourceProxies)==0:
			proxies.init()
		self.proxyrequired = False
		self.msg = ''
		self.siteonline = self.testSite()
		self.testparser = 'Unknown'
		self.testparser = self.testParser()
		self.initAndSleepThread()
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
		for site in self.base_link_alts:
			bool = self.testSiteAlts(site)
			if bool == True:
				return bool
				
		self.base_link = self.base_link_alts[0]
		return False
		
	def testSiteAlts(self, site):
		try:
			self.base_link = site
			if self.disabled:
				log('INFO','testSite', 'Plugin Disabled')
				return False
			self.initAndSleep()
			x1 = time.time()
			http_res, content = proxies.request(url=site, headers=self.headers, output='response', use_web_proxy=False, httpsskip=True)
			self.speedtest = time.time() - x1
			for valcon in self.MainPageValidatingContent:
				if content != None and content.find(valcon) >-1:
					log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,site))
					return True
			log('FAIL', 'testSite', 'Validation content Not Found. HTTP Resp : %s for %s' % (http_res,site))
			return False
		except Exception as e:
			log('ERROR','testSite', '%s' % e)
			return False
			
	def initAndSleepThread(self):
		thread_i = workers.Thread(self.InitSleepThread)
		thread_i.start()
		
	def InitSleepThread(self):
		while True:
			time.sleep(60*100)
			self.initAndSleep()
			
	def initAndSleep(self):
		try:
			self.TOKEN_KEY = []
			self.getVidToken()
			if len(self.TOKEN_KEY) > 0:
				log('SUCCESS', 'initAndSleep', 'Vid Token: %s' % client.b64encode(self.TOKEN_KEY[0]))
			else:
				log('FAIL', 'initAndSleep', 'Vid Token Not retrieved !')
			
			t_base_link = self.base_link
			self.headers = {'X-Requested-With': 'XMLHttpRequest'}
			self.headers['Referer'] = t_base_link
			ua = client.randomagent()
			self.headers['User-Agent'] = ua
			
			#get cf cookie
			cookie1 = proxies.request(url=t_base_link, headers=self.headers, output='cookie', use_web_proxy=self.proxyrequired, httpsskip=True)
			self.headers['Cookie'] = cookie1
			
			# get reqkey cookie
			try:
				token_url = urlparse.urljoin(t_base_link, self.token_link)
				r1 = proxies.request(token_url, headers=self.headers, httpsskip=True)
				reqkey = self.decodeJSFCookie(r1)
			except:
				reqkey = ''
			
			# get session cookie
			serverts = str(((int(time.time())/3600)*3600))
			query = {'ts': serverts}
			try:
				tk = self.__get_token(query)
			except:
				tk = self.__get_token(query, True)

			query.update(tk)
			hash_url = urlparse.urljoin(t_base_link, self.hash_menu_link)
			hash_url = hash_url + '?' + urllib.urlencode(query)

			r1, headers, content, cookie2 = proxies.request(hash_url, headers=self.headers, limit='0', output='extended', httpsskip=True)

			#cookie = cookie1 + '; ' + cookie2 + '; user-info=null; reqkey=' + reqkey
			cookie = '%s; %s; user-info=null; reqkey=%s' % (cookie1 , cookie2 , reqkey)
			
			self.headers['Cookie'] = cookie
			log('SUCCESS', 'initAndSleep', 'Cookies : %s for %s' % (cookie,self.base_link))
		except Exception as e:
			log('ERROR','initAndSleep', '%s' % e)
		
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
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			#X - Requested - With:"XMLHttpRequest"
			return url
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
			if url == None: return
			url = urlparse.parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'],  url['season'], url['episode'], url['premiered'] = title, season, episode, year
			url = urllib.urlencode(url)
			return url
		except Exception as e: 
			log('ERROR', 'get_episode','%s: %s' % (title,e), dolog=self.init)
			return

	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):
		try:
			sources = []
			if url == None: 
				log('FAIL','get_sources','Could not find a matching title: %s' % cleantitle.title_from_key(key), dolog=not testing)
				return sources
			
			myts = str(((int(time.time())/3600)*3600))
			log('INFO','get_sources-1', 'url: %s' % url, dolog=False)
			token_error = False
			urls = []
			
			if not str(url).startswith('http'):
				try:
					data = urlparse.parse_qs(url)
					data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

					title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

					try:
						year = re.findall('(\d{4})', data['premiered'])[0] if 'tvshowtitle' in data else data['year']
					except:
						try:
							year = data['year']
						except:
							year = None
					try: episode = data['episode']
					except: pass

					query = {'keyword': title}
					search_url = urlparse.urljoin(self.base_link, '/search')
					search_url = search_url + '?' + urllib.urlencode(query)
					result = proxies.request(search_url, headers=self.headers, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
					
					log('INFO','get_sources-2', '%s' % search_url, dolog=False)
					
					rs = client.parseDOM(result, 'div', attrs = {'class': '[^"]*movie-list[^"]*'})[0]
					r = client.parseDOM(rs, 'div', attrs = {'class': 'item'})
					r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', attrs = {'class': 'name'})) for i in r]
					r = [(i[0][0], i[1][0]) for i in r if len(i[0]) > 0 and  len(i[1]) > 0]
					r = [(re.sub('http.+?//.+?/','/', i[0]), re.sub('&#\d*;','', i[1])) for i in r]
					
					if 'season' in data:
						r = [(i[0], re.sub(' \(\w*\)', '', i[1])) for i in r]
						
						possible_hits = []
						for i in r:
							if cleantitle.get(title).lower() == cleantitle.get(i[1]).lower():
								possible_hits.append((i[0], [[i[1], u'1']]))
							
						#title += '%01d' % int(data['season'])
						url = [(i[0], re.findall('(.+?) (\d+)$', i[1])) for i in r]

						for i in possible_hits:
							url.append(i)
							
						url = [(i[0], i[1][0][0], i[1][0][1]) for i in url if len(i[1]) > 0]
						
						url = [i for i in url if cleantitle.get(title) in cleantitle.get(i[1])]

						url = [i for i in url if '%01d' % int(data['season']) == '%01d' % int(i[2])]
						
						if len(url) == 0:
							url = [i for i in r if cleantitle.get(title) == cleantitle.get(i[1])]
						if len(url) == 0:
							url = [i for i in r if cleantitle.get(title) == cleantitle.get(i[1]+str(season))]
					else:
						url = [i for i in r if cleantitle.get(title) in cleantitle.get(i[1])]
					
					if len(url) == 0:
						log('FAIL','get_sources','Could not find a matching title: %s' % cleantitle.title_from_key(key))
						return sources
					
					for urli in url:
						url = urli[0]
						url = urlparse.urljoin(self.base_link, url)
						urls.append(url)
					
				except Exception as e:
					raise Exception(e)

			for url in urls:
				try:
					try: url, episode = re.compile('(.+?)\?episode=(\d*)$').findall(url)[0]
					except: pass
					
					log('INFO','get_sources-3', url, dolog=False)

					referer = url
					result = resultT = proxies.request(url, headers=self.headers, limit='0', proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
					
					alina = client.parseDOM(result, 'title')[0]

					atr = [i for i in client.parseDOM(result, 'title') if len(re.findall('(\d{4})', i)) > 0][-1]
					if 'season' in data:
						years = ['%s' % str(year), '%s' % str(int(year) + 1), '%s' % str(int(year) - 1)]
						mychk = False
						for y in years:
							if y in atr: 
								mychk = True
						result = result if mychk == True else None
						if mychk == True:
							break
					else:
						result = result if year in atr else None
						
					if result != None:
						break
				except Exception as e:
					log('FAIL','get_sources-3', '%s : %s' % (url,e), dolog=False)
					
			if result == None:
				log('FAIL','get_sources','Could not find a matching title: %s' % cleantitle.title_from_key(key))
				return sources

			try:
				myts = re.findall(r'data-ts="(.*?)"', result)[0]
			except:
				log('INFO','get_sources-3', 'could not parse ts ! will use generated one : %s' % myts, dolog=False)
				
			trailers = []
			links_m = []
			
			if testing == False:
				try:
					matches = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+').findall(result)
					for match in matches:
						try:
							if 'youtube.com' in match:
								match = match.replace('embed/','watch?v=')
								trailers.append(match)
						except:
							pass
				except Exception as e:
					pass
					
				for trailer in trailers:
					links_m = resolvers.createMeta(trailer, self.name, self.logo, '720p', links_m, key, vidtype='Trailer', testing=testing)
			
			riptype = None
			try: quality = client.parseDOM(result, 'span', attrs = {'class': 'quality'})[0].lower()
			except: quality = 'hd'
			if quality == 'cam' or quality == 'ts': 
				quality = '480p'
				riptype = 'CAM'
			elif quality == 'hd' or 'hd ' in quality: 
				quality = '720p'
				riptype = 'BRRIP'
			else: 
				quality = '480p'
				riptype = 'BRRIP'

			result = client.parseDOM(result, 'ul', attrs = {'data-range-id':"0"})

			servers = []
			#servers = client.parseDOM(result, 'li', attrs = {'data-type': 'direct'})
			servers = zip(client.parseDOM(result, 'a', ret='data-id'), client.parseDOM(result, 'a'))
			
			servers = [(i[0], re.findall('(\d+)', i[1])) for i in servers]
			servers = [(i[0], ''.join(i[1][:1])) for i in servers]
			
			try: servers = [i for i in servers if '%01d' % int(i[1]) == '%01d' % int(episode)]
			except: pass
			
			for s in servers[:len(servers)]:
				try:

					headers = {'X-Requested-With': 'XMLHttpRequest'}
					hash_url = urlparse.urljoin(self.base_link, self.hash_link)
					query = {'ts': myts, 'id': s[0], 'update': '0', 'server':'36'}

					query.update(self.__get_token(query))
					hash_url = hash_url + '?' + urllib.urlencode(query)
					headers['Referer'] = urlparse.urljoin(url, s[0])
					headers['Cookie'] = self.headers['Cookie']
					
					log('INFO','get_sources-4', '%s' % hash_url, dolog=False)
					result = proxies.request(hash_url, headers=headers, limit='0', proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
					result = json.loads(result)
					
					if 'error' in result and result['error'] == True:
						token_error = True
						query.update(self.__get_token(query, token_error=token_error))
						hash_url = hash_url + '?' + urllib.urlencode(query)
						result = proxies.request(hash_url, headers=headers, limit='0', proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
						result = json.loads(result)
						
						query = {'id': s[0], 'update': '0'}
						query.update(self.__get_token(query, token_error=token_error))
					else:
						token_error = False
						queryx = {'id': s[0], 'update': '0'}
						query.update(self.__get_token(queryx))
					
					url = url + '?' + urllib.urlencode(query)
					#result = client2.http_get(url, headers=headers)
					
					#quality = '360p'
					if '1080' in s[1]: 
						quality = '1080p'
						#riptype = 'BRRIP'
					elif '720' in s[1] or 'hd' in s[1].lower(): 
						quality = '720p'
						#riptype = 'BRRIP'
					elif '480' in s[1]: 
						quality = '480p'
						#riptype = 'BRRIP'
					elif 'cam' in s[1].lower() or 'ts' in s[1].lower(): 
						quality = '480p'
						#riptype = 'CAM'
					else:
						quality = '480p'
						#riptype = 'CAM'
						
					log('INFO','get_sources-5', result, dolog=False)
					
					if result['target'] != "":
						pass
					else:
						grabber = result['grabber']
						grab_data = grabber
						grabber_url = urlparse.urljoin(self.base_link, self.grabber_api)
						
						if '?' in grabber:
							grab_data = grab_data.split('?')
							grabber_url = grab_data[0]
							grab_data = grab_data[1]
							
						print grab_data
						grab_server = str(urlparse.parse_qs(grab_data)['server'][0])
						
						b, resp = self.decode_t(result['params']['token'], -18)
						if b == False:
							raise Exception(resp)
						token = resp
						b, resp = self.decode_t(result['params']['options'], -18)
						if b == False:
							raise Exception(resp)
						options = resp
						
						grab_query = {'ts':myts, grabber_url:'','id':result['params']['id'],'server':grab_server,'mobile':'0','token':token,'options':options}
						tk = self.__get_token(grab_query, token_error)

						if tk == None:
							raise Exception('video token algo')
						grab_info = {'token':token,'options':options}
						del query['server']
						query.update(grab_info)
						query.update(tk)
						
						sub_url = result['subtitle']
						if sub_url==None or len(sub_url) == 0:
							sub_url = None
						
						if '?' in grabber:
							grabber += '&' + urllib.urlencode(query)
						else:
							grabber += '?' + urllib.urlencode(query)
					
						if grabber!=None and not grabber.startswith('http'):
							grabber = 'http:'+grabber
							
						log('INFO','get_sources-6', grabber, dolog=False)

						result = proxies.request(grabber, headers=headers, referer=url, limit='0', proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)

						result = json.loads(result)
					
					if 'data' in result.keys():
						result = [i['file'] for i in result['data'] if 'file' in i]
						
						for i in result:
							links_m = resolvers.createMeta(i, self.name, self.logo, quality, links_m, key, riptype, sub_url=sub_url, testing=testing)
					else:
						target = result['target']
						b, resp = self.decode_t(target, -18)
						if b == False:
							raise Exception(resp)
						target = resp
						sub_url = result['subtitle']
						if sub_url==None or len(sub_url) == 0:
							sub_url = None
						
						if target!=None and not target.startswith('http'):
							target = 'http:' + target
							
						links_m = resolvers.createMeta(target, self.name, self.logo, quality, links_m, key, riptype, sub_url=sub_url, testing=testing)

				except Exception as e:
					log('FAIL', 'get_sources-7','%s' % e, dolog=False)

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
		try:
			return url
		except:
			return
	
	def r01(self, t, e, token_error=False):
		i = 0
		n = 0
		for i in range(0, max(len(t), len(e))):
			if i < len(e):
				n += ord(e[i])
			if i < len(t):
				n += ord(t[i])
		h = format(int(hex(n),16),'x')
		return h

	def a01(self, t, token_error=False):
		i = 0
		for e in range(0, len(t)):
			if token_error == False:
				i += ord(t[e]) + e
			else:
				i += ord(t[e]) * e + e
		return i

	def decode_t(self, t, i):
		n = [] 
		e = []
		r = ''
		
		if ENCRYPTED_URLS == False:
			return True, t
		
		try:
			for n in range(0, len(t)):
				if n == 0 and t[n] == '.':
					pass
				else:
					c = ord(t[n])
					if c >= 97 and c <= 122:
						e.append((c - 71 + i) % 26 + 97)
					elif c >= 65 and c <= 90:
						e.append((c - 39 + i) % 26 + 65)
					else:
						e.append(c)
			for ee in e:
				r += chr(ee)
				
			return True, r
		except Exception as e:
			log('ERROR', 'decode_t','%s' % e, dolog=False)
			False, 'Error in decoding'

	def __get_token(self, n, token_error=False):
		try:
			if token_error == True and len(self.TOKEN_KEY) > 1:
				d = self.TOKEN_KEY[1]
			else:
				d = self.TOKEN_KEY[0]
			s = self.a01(d, token_error)
			for i in n: 
				s += self.a01(self.r01(d + i, n[i]), token_error)
			return {'_': str(s)}
		except Exception as e:
			log('ERROR', '__get_token','%s' % e, dolog=False)
			
	def decodeJSFCookie(self, token):
		dec = jsfdecoder.JSFDecoder(token).ca_decode()
		dec = dec.split('reqkey=')
		dec = dec[1].split(';')
		dec = dec[0]
		return dec
		
	def getVidToken(self):
		try:
			all_js_url = urlparse.urljoin(self.base_link, self.ALL_JS)
			unpacked_code = ''
			cch = ''
			if len(self.TOKEN_KEY) == 0:
				try:
					all_js_pack_code = proxies.request(all_js_url, use_web_proxy=self.proxyrequired, httpsskip=True)
					unpacked_code = jsunpack.unpack(all_js_pack_code)
					cch = re.findall(r'%s' % common.client.b64decode('ZnVuY3Rpb25cKHQsaSxuXCl7XCJ1c2Ugc3RyaWN0XCI7ZnVuY3Rpb24gZVwoXCl7cmV0dXJuICguKj8pfWZ1bmN0aW9uIHJcKHRcKQ=='), unpacked_code)[0]
					token_key = re.findall(r'%s=.*?\"(.*?)\"' % cch, unpacked_code)[0]
					if token_key !=None and token_key != '':
						self.TOKEN_KEY.append(token_key)
				except Exception as e:
					log('ERROR', 'getVidToken-1.1','%s' % e, dolog=False)
					
			if len(self.TOKEN_KEY) == 0:
				try:
					cch = re.findall(r'%s' % common.client.b64decode('ZnVuY3Rpb25cKFthLXpdLFthLXpdLFthLXpdXCl7XCJ1c2Ugc3RyaWN0XCI7ZnVuY3Rpb24gW2Etel1cKFwpe3JldHVybiAoLio/KX1mdW5jdGlvbiBbYS16XVwoW2Etel1cKQ=='), unpacked_code)[0]
					token_key = re.findall(r'%s=.*?\"(.*?)\"' % cch, unpacked_code)[0]
					if token_key !=None and token_key != '':
						#cookie_dict.update({'token_key':token_key})
						self.TOKEN_KEY.append(token_key)
				except Exception as e:
					log('ERROR', 'getVidToken-1.2','%s' % e, dolog=False)
		except Exception as e:
			log('ERROR', 'getVidToken-1','%s' % e, dolog=False)
			log('ERROR', 'getVidToken-1','%s' % unpacked_code, dolog=False)
			log('ERROR', 'getVidToken-1','%s' % cch, dolog=False)

		try:
			if len(self.TOKEN_KEY) == 0 or True:
				token_key = proxies.request(self.TOKEN_KEY_PASTEBIN_URL, use_web_proxy=self.proxyrequired, httpsskip=True)
				if token_key !=None and token_key != '':
					#cookie_dict.update({'token_key':token_key})
					self.TOKEN_KEY.append(token_key)
		except Exception as e:
			log('ERROR', 'getVidToken-2','%s' % e, dolog=False)

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
