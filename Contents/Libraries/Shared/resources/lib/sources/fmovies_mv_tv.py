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
from __builtin__ import ord, format

class source:
	def __init__(self):
		self.disabled = False
		self.TOKEN_KEY = []
		self.base_link = 'https://fmovies.is'
		self.search_link = '/sitemap'
		self.ALL_JS = "/assets/min/public/all.js"
		self.TOKEN_KEY_PASTEBIN_URL = "https://pastebin.com/raw/VNn1454k"
		self.hash_link = '/ajax/episode/info'
		self.hash_menu_link = "/user/ajax/menu-bar"
		self.token_link = "/token"
		self.MainPageValidatingContent = 'FMovies'
		self.type_filter = ['movie', 'show', 'anime']
		self.ssl = False
		self.name = 'FMovies'
		self.headers = {}
		self.cookie = None
		self.loggertxt = []
		self.logo = 'http://i.imgur.com/li8Skjf.jpg'
		self.speedtest = 0
		if len(proxies.sourceProxies)==0:
			proxies.init()
		self.proxyrequired = False
		self.siteonline = self.testSite()
		self.testparser = 'Unknown'
		self.testparser = self.testParser()
		self.initAndSleepThread()
		
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
			
			t_base_link = self.base_link
			self.headers = {'X-Requested-With': 'XMLHttpRequest'}
			self.headers['Referer'] = t_base_link
			ua = client.randomagent()
			self.headers['User-Agent'] = ua
			
			#get cf cookie
			cookie1 = proxies.request(url=t_base_link, headers=self.headers, output='cookie', use_web_proxy=self.proxyrequired)
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
			tk = self.__get_token(query)
			query.update(tk)
			hash_url = urlparse.urljoin(t_base_link, self.hash_menu_link)
			hash_url = hash_url + '?' + urllib.urlencode(query)

			r1, headers, content, cookie2 = proxies.request(hash_url, headers=self.headers, limit='0', output='extended', httpsskip=True)
			
			cookie = cookie1 + '; ' + cookie2 + '; user-info=null; reqkey=' + reqkey
			self.headers['Cookie'] = cookie
			self.log('SUCCESS', 'initAndSleep', 'Cookies : %s for %s' % (cookie,self.base_link), dolog=True)
		except Exception as e:
			self.log('ERROR','initAndSleep', '%s' % e, dolog=True)
				
			
	def testSite(self):
		try:
			if self.disabled:
				self.log('INFO','testSite', 'Plugin Disabled', dolog=True)
				return False
			self.initAndSleep()
			x1 = time.time()
			http_res, content = proxies.request(url=self.base_link, headers=self.headers, output='response', use_web_proxy=False)
			self.speedtest = time.time() - x1
			if content != None and content.find(self.MainPageValidatingContent) >-1:
				self.log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,self.base_link), dolog=True)
				return True
			else:
				self.log('ERROR', 'testSite', 'HTTP Resp : %s for %s' % (http_res,self.base_link), dolog=True)
			return False
		except Exception as e:
			self.log('ERROR','testSite', '%s' % e, dolog=True)
			return False
		
	def testParser(self):
		try:
			if self.disabled:
				self.log('INFO','testParser', 'Plugin Disabled', dolog=True)
				return False
			for movie in testparams.test_movies:
				getmovieurl = self.get_movie(title=movie['title'], year=movie['year'], imdb=movie['imdb'], testing=True)
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

	def get_show(self, imdb, tvdb, tvshowtitle, year, season, proxy_options=None, key=None, testing=False):

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
			
			if url == None or self.testparser == False: return sources
			
			myts = str(((int(time.time())/3600)*3600))
			#self.log('GRABBER','get_sources-1', '%s' % url, dolog=False)
			
			if not str(url).startswith('http'):
				try:
					data = urlparse.parse_qs(url)
					data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

					title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

					year = re.findall('(\d{4})', data['premiered'])[0] if 'tvshowtitle' in data else data['year']
					try: episode = data['episode']
					except: pass

					query = {'keyword': title}
					search_url = urlparse.urljoin(self.base_link, '/search')
					search_url = search_url + '?' + urllib.urlencode(query)
					result = proxies.request(search_url, headers=self.headers, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
					
					#self.log('GRABBER','get_sources-2', '%s' % search_url, dolog=False)
					
					#print result

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
						#for i in url:
							#print i[2],i[0],i[1]
							#print '%01d' % int(data['season']) == '%01d' % int(i[2])

						url = [i for i in url if '%01d' % int(data['season']) == '%01d' % int(i[2])]
					else:
						url = [i for i in r if cleantitle.get(title) in cleantitle.get(i[1])]
					#print("r1", cleantitle.get(title),url,r)

					url = url[0][0]

					url = urlparse.urljoin(self.base_link, url)
					r2 = url.split('.')[-1]

				except:
					raise Exception()


			try: url, episode = re.compile('(.+?)\?episode=(\d*)$').findall(url)[0]
			except: pass
			
			#self.log('GRABBER','get_sources-3', '%s' % url, dolog=False)

			referer = url
			#result = client.request(url, limit='0')
			result = proxies.request(url, headers=self.headers, limit='0', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			
			try:
				myts = re.findall(r'data-ts="(.*?)"', result)[0]
				#print myts
				#myts = result.xpath(".//body[@class='watching']//@data-ts")[0]
			except:
				print "could not parse ts ! will use generated one."
				print myts
				
			trailers = []
			links_m = []
			
			if testing == False:
				try:
					matches = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+').findall(result)
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
					links_m = resolvers.createMeta(trailer, self.name, self.logo, '720p', links_m, key, vidtype='Trailer')
			
			#self.log('GRABBER','get_sources-3.1', '%s' % url, dolog=False)

			#hash_url = urlparse.urljoin(self.base_link, '/user/ajax/menu-bar')
			# int(time.time())
			#query = {'ts': myts}
			#query.update(self.__get_token(query))
			#hash_url = hash_url + '?' + urllib.urlencode(query)
			#r1, headers, content, cookie2 = proxies.request(hash_url, headers=self.headers, limit='0', output='extended', cookie=cookie1, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			
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
			
			for s in servers[:4]:
				try:

					headers = {'X-Requested-With': 'XMLHttpRequest'}
					hash_url = urlparse.urljoin(self.base_link, self.hash_link)
					query = {'ts': myts, 'id': s[0], 'update': '0'}

					query.update(self.__get_token(query))
					hash_url = hash_url + '?' + urllib.urlencode(query)
					headers['Referer'] = urlparse.urljoin(url, s[0])
					headers['Cookie'] = self.headers['Cookie']
					
					#self.log('GRABBER','get_sources-3.9', '%s' % hash_url, dolog=False)
					result = proxies.request(hash_url, headers=headers, limit='0', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
					#self.log('GRABBER','get_sources-4', '%s' % result, dolog=False)
					result = json.loads(result)
					
					if 'error' in result and result['error'] == True:
						query.update(self.__get_token(query, token_error=True))
						hash_url = hash_url + '?' + urllib.urlencode(query)
						result = proxies.request(hash_url, headers=headers, limit='0', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
						result = json.loads(result)
						
						query = {'id': s[0], 'update': '0'}
						query.update(self.__get_token(query, token_error=True))
					else:
						query = {'id': s[0], 'update': '0'}
						query.update(self.__get_token(query))
					
					url = url + '?' + urllib.urlencode(query)
					#result = client2.http_get(url, headers=headers)
					
					quality = 'SD'
					if s[1] == '1080': quality = '1080p'
					if s[1] == '720': quality = 'HD'
					if s[1] == 'CAM': quality == 'CAM'

					if result['target'] != "":
						pass
					else:
						query = {'id':result['params']['id'], 'token':result['params']['token']}
						grabber = result['grabber'] 
						if '?' in grabber:
							grabber += '&' + urllib.urlencode(query)
						else:
							grabber += '?' + urllib.urlencode(query)
					
						if grabber!=None and not grabber.startswith('http'):
							grabber = 'http:'+grabber
							
						#self.log('GRABBER','url', '%s' % grabber, dolog=False)

						result = proxies.request(grabber, headers=headers, referer=url, limit='0', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)

						result = json.loads(result)
						
					#print result
					
					if 'data' in result.keys():
						result = [i['file'] for i in result['data'] if 'file' in i]

						for i in result:
							links_m = resolvers.createMeta(i, self.name, self.logo, quality, links_m, key)
					else:
						target = result['target']
						
						if target!=None and not target.startswith('http'):
							target = 'http:' + target
							
						links_m = resolvers.createMeta(target, self.name, self.logo, quality, links_m, key)
							
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


	def __get_token(self, n, token_error=False):
		try:
			d = self.TOKEN_KEY[0]
			s = self.a01(d, token_error)
			for i in n: 
				s += self.a01(self.r01(d + i, n[i]), token_error)
			return {'_': str(s)}
		except Exception as e:
			print("fmovies.py > get_token > %s" % e)
			
	def decodeJSFCookie(self, token):
		dec = jsfdecoder.JSFDecoder(token).ca_decode()
		dec = dec.split('reqkey=')
		dec = dec[1].split(';')
		dec = dec[0]
		return dec
		
	def getVidToken(self):
		try:
			all_js_url = urlparse.urljoin(self.base_link, self.ALL_JS)
			if len(self.TOKEN_KEY) == 0:
				all_js_pack_code = proxies.request(all_js_url, use_web_proxy=self.proxyrequired, httpsskip=True)
				unpacked_code = jsunpack.unpack(all_js_pack_code)
				cch = re.findall(r'%s' % client.b64decode('ZnVuY3Rpb25cKHQsZSxpXCl7XCJ1c2Ugc3RyaWN0XCI7ZnVuY3Rpb24gblwoXCl7cmV0dXJuICguKj8pfWZ1bmN0aW9uIHJcKHRcKQ=='), unpacked_code)[0]
				token_key = re.findall(r'%s=.*?\"(.*?)\"' % cch, unpacked_code)[0]
				if token_key !=None and token_key != '':
					#cookie_dict.update({'token_key':token_key})
					self.TOKEN_KEY.append(token_key)
		except Exception as e:
			self.log('ERROR', 'getVidToken-1','%s' % e)

		try:
			if len(self.TOKEN_KEY) == 0:
				token_key = proxies.request(self.TOKEN_KEY_PASTEBIN_URL, use_web_proxy=self.proxyrequired, httpsskip=True)
				if token_key !=None and token_key != '':
					#cookie_dict.update({'token_key':token_key})
					self.TOKEN_KEY.append(token_key)
		except Exception as e:
			self.log('ERROR', 'getVidToken-2','%s' % e)

def logger(msg):
	control.log(msg)
