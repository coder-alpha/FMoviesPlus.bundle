# -*- coding: utf-8 -*-

import re,urllib,urlparse,json,random,time,base64
from resources.lib.libraries import client, control, cleantitle, source_utils, testparams
from resources.lib import resolvers, proxies
from __builtin__ import ord, format

name = 'FMovies.io'
loggertxt = []

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.1.2'
		self.update_date = 'March 01, 2019'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.base_link_alts = ['https://fmovies.io','https://www3.fmovies.pe','https://www.fmovies.pe','https://www4.fmovies.pe']
		self.base_link = self.base_link_alts[0]
		self.search_link = '/sitemap'
		self.link_server_f1 = "https://vidnode.net/streaming.php?id=%s"
		self.link_server_f2 = "https://player.fmovie.io/embed.php?id=%s"
		self.hash_link = '/ajax/episode/info'
		self.MainPageValidatingContent = 'Watch movies online free'
		self.type_filter = ['movie', 'show', 'anime']
		self.ssl = False
		self.disabled = False
		self.name = 'FMovies.io'
		self.headers = {}
		self.cookie = None
		self.loggertxt = []
		self.logo = 'https://i.imgur.com/jsD6b0O.png'
		self.speedtest = 0
		if len(proxies.sourceProxies)==0:
			proxies.init()
		self.proxyrequired = False
		self.msg = ''
		self.siteonline = self.testSite()
		self.testparser = 'Unknown'
		self.testparser = self.testParser()
		self.firstRunDisabled = False
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
			'frd' : self.firstRunDisabled,
			'online': self.siteonline,
			'online_via_proxy' : self.proxyrequired,
			'parser': self.testparser
		}
			
	def getLog(self):
		self.loggertxt = loggertxt
		return self.loggertxt
			
	def setNewCookies(self):
		try:
			ua = client.randomagent()
			self.headers['User-Agent'] = ua
			self.cookie = proxies.request(url=self.base_link, headers=self.headers, output='cookie', use_web_proxy=self.proxyrequired)
			self.headers['Cookie'] = self.cookie
		except Exception as e:
			log('ERROR','setNewCookies', '%s' % e)
		
	def testSite(self):
		for site in self.base_link_alts:
			bool = self.testSiteAlts(site)
			if bool == True:
				self.base_link = site
				return bool
				
		self.base_link = self.base_link_alts[0]
		return False
			
	def testSiteAlts(self, site):
		try:
			ua = client.randomagent()
			self.headers['User-Agent'] = ua
			self.base_link = proxies.request(url=site, headers=self.headers, output='geturl', use_web_proxy=False, httpsskip=True).strip("/")
			x1 = time.time()
			http_res, content = proxies.request(url=self.base_link, headers=self.headers, output='response', use_web_proxy=False, httpsskip=True)
			self.speedtest = time.time() - x1
			if content != None and content.find(self.MainPageValidatingContent) >-1:
				x1 = time.time()
				self.cookie = proxies.request(url=self.base_link, headers=self.headers, output='cookie', use_web_proxy=False, httpsskip=True)
				self.speedtest = time.time() - x1
				self.headers['Cookie'] = self.cookie
				log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,self.base_link))
				log('SUCCESS', 'testSite', 'Cookie Resp : %s for %s' % (self.cookie,self.base_link))
				return True
			else:
				log('FAIL', 'testSite', 'Validation content Not Found. HTTP Resp : %s for %s' % (http_res,self.base_link))
				x1 = time.time()
				http_res, content = proxies.request(url=self.base_link.replace('https:','http:'), headers=self.headers, output='response', use_web_proxy=True, httpsskip=True)
				self.speedtest = time.time() - x1
				if content != None and content.find(self.MainPageValidatingContent) >-1:
					self.proxyrequired = True
					x1 = time.time()
					self.cookie = proxies.request(url=self.base_link, headers=self.headers, output='cookie', use_web_proxy=True, httpsskip=True)
					self.speedtest = time.time() - x1
					self.headers['Cookie'] = self.cookie
					log('SUCCESS', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,self.base_link))
					log('SUCCESS', 'testSite', 'Cookie Resp : %s for %s' % (self.cookie,self.base_link))
					return True
				else:
					time.sleep(2.0)
					x1 = time.time()
					http_res, content = proxies.request(url=self.base_link, headers=self.headers, output='response', use_web_proxy=True, httpsskip=True)
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
			if control.setting('Provider-%s' % name) == False:
				log('INFO','testParser', 'Plugin Disabled by User - cannot test parser')
				return False
			if control.setting('use_quick_init') == True:
				log('INFO','testParser', 'Disabled testing - Using Quick Init setting in Prefs.')
				return False
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

	def get_movie(self, imdb=None, title=None, year=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_movie','Provider Disabled by User')
				return None
			if self.siteonline == False:
				log('INFO','get_movie','Provider is Offline')
				return None
				
			title = title.replace('&','and')
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
			if self.siteonline == False:
				log('INFO','get_show','Provider is Offline')
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
			url = {'year':year, 'imdb': imdb, 'tvdb': tvdb, 'title': title, 'season': season, 'episode': episode}
			url = urllib.urlencode(url)
			return url
		except Exception as e: 
			log('ERROR', 'get_episode','%s: %s' % (title,e), dolog=self.init)
			return

	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):
		try:
			sources = []
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_sources','Provider Disabled by User')
				log('INFO', 'get_sources', 'Completed')
				return sources
			if url == None: 
				log('FAIL','get_sources','url == None. Could not find a matching title: %s' % cleantitle.title_from_key(key), dolog=not testing)
				log('INFO', 'get_sources', 'Completed')
				return sources
			
			urls = []
			vidtype = 'Movie'
			
			if not str(url).startswith('http'):
				try:
					data = urlparse.parse_qs(url)
					data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
					
					title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

					if 'year' in data:
						year = data['year']
					
					if 'season' in data:
						query = {'keyword': '%s %s %s' % (title, 'season', data['season'])}
					else:
						query = {'keyword': title}
						
					search_url = urlparse.urljoin(self.base_link, '/search.html')
					search_url = search_url + '?' + urllib.urlencode(query)
					
					result = proxies.request(search_url, headers=self.headers, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
					r = client.parseDOM(result, 'div', attrs = {'class': 'wrapper'})
					
					try:
						r = r[1]
					except:
						raise Exception()
					
					r1 = client.parseDOM(r, 'figure')
					r2 = []
					for res in r1:
						l = client.parseDOM(res, 'a', ret='href')[0]
						t = client.parseDOM(res, 'div', attrs = {'class': 'title'})[0]
						r = (l,t)
						r2.append(r)
						
					r = r2
					
					if 'season' in data:
						vidtype = 'Show'
						episode = int(data['episode'])
						
						r = [(i[0], re.sub(' \(\w*\)', '', i[1])) for i in r]
						url = [(i[0], re.findall('(.+?) (\d+)$', i[1])) for i in r]
						url = [(i[0], i[1][0][0], i[1][0][1]) for i in url if len(i[1]) > 0]
						url = [i for i in url if cleantitle.get(title) in cleantitle.get(i[1])]
						url = [i for i in url if '%01d' % int(data['season']) == '%01d' % int(i[2])]
						
						ep_url = []
						for i in url:
							result = proxies.request(urlparse.urljoin(self.base_link, i[0]), headers=self.headers, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
							t = client.parseDOM(result, 'div', attrs = {'class': 'eps'})
							for tt in t:
								if 'watch' in tt:
									tt = client.parseDOM(tt, 'div', attrs = {'class': 'server'})[0]
									section_links = client.parseDOM(tt, 'a', ret='href')
									for a_link in section_links:
										if episode < 100:
											f_key = '-episode-%02d-' % episode
										else:
											f_key = '-episode-%03d-' % episode
										if f_key in a_link:
											log('INFO','get_sources','episode url = %s' % a_link)
											ep_url.append(a_link)
											break
						for i in ep_url:
							urls.append(urlparse.urljoin(self.base_link, i))
					else:
						for i in r:
							if cleantitle.get(title) in cleantitle.get(i[1]):
								urls.append(urlparse.urljoin(self.base_link, i[0]))	

				except:
					urls == [self.base_link]
			
			links_m = []

			page = None
			for url in urls:
				try:
					log('INFO','get_sources','url == %s' % url, dolog=False, doPrint=True)
					page_url = url
					page = result = proxies.request(url, headers=self.headers, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
					
					quality = '480p'
					type = 'BRRIP'
					
					atr = ''
					qtr = ''
					
					try:
						qtr = client.parseDOM(result, 'span', attrs = {'class': 'quanlity'})[0]
						# q, t = cleantitle.getQuality(atr)
						# if q != None:
							# quality = q
							# type = t
					except:
						try:
							qtr = client.parseDOM(result, 'span', attrs = {'class': 'quality'})[0]
							# q, t = cleantitle.getQuality(atr)
							# if q != None:
								# quality = q
								# type = t
						except:
							pass
							
					try:
						quality = source_utils.check_sd_url(qtr)
						type = source_utils.check_sd_url_rip(qtr)
					except Exception as e:
						quality = '480p'
						type = 'BRRIP'
						
					try:
						atr = client.parseDOM(result, 'span', attrs = {'class': 'year'})[0]
					except:
						atr = ''

					try:
						atr_release = client.parseDOM(result, 'div', attrs = {'class': 'meta'})[1]
					except:
						atr_release = ''
					
					if 'season' in data:
						vidtype = 'Show'
						pass
					else:
						vidtype = 'Movie'
						resultx = result if str(int(year)) in atr else None
						if resultx == None:
							resultx = result if str(int(year)) in atr_release else None
						if resultx == None:
							raise Exception()
							
					try:
						poster = client.parseDOM(page, 'div', attrs = {'class': 'detail-l'})[0]
						poster = client.parseDOM(poster, 'img', ret='src')[0]
						if 'http' not in poster:
							poster = 'http:' + poster
					except:
						poster = None
					#print result

					#r = client.parseDOM(result, 'article', attrs = {'class': 'player current'})[0]
					#r = client.parseDOM(r, 'iframe', ret='src')[0]
					#r = r.split('?')
						
					try:
						servers = re.findall(r'link_server_.*\"(.*)\";', page)
						servers = list(set(servers))
						for server in servers:
							try:
								if 'http' not in server:
									server = 'http:' + server

								result = proxies.request(server, headers=self.headers, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
								
								server = client.parseDOM(result, 'iframe', ret='src')[0]
								if len(server) > 0:
									if 'http' not in server:
										server = 'http:' + server
									
									l = resolvers.createMeta(server, self.name, self.logo, quality, [], key, poster=poster, riptype=type, vidtype=vidtype, testing=testing, page_url=page_url)
									for ll in l:
										if ll != None and 'key' in ll.keys():
											links_m.append(ll)
							except Exception as e:
								pass
							if testing and len(links_m) > 0:
								break
					except Exception as e:
						pass
						
					try:
						servers = re.findall(r'link_server_.*\"(.*)\";', page)
						servers = list(set(servers))
						for server in servers:
							if server != None:
								if 'http' not in server:
									server = 'http:' + server

								try:
									l = resolvers.createMeta(server, self.name, self.logo, quality, [], key, poster=poster, riptype=type, vidtype=vidtype, testing=testing, page_url=page_url)
									for ll in l:
										if ll != None and 'key' in ll.keys():
											links_m.append(ll)
								except:
									pass
					except:
						pass
						
					break
				except:
					pass
				
			for link in links_m:
				if link != None and 'key' in link.keys():
					sources.append(link)
				
			if len(sources) == 0:
				log('FAIL','get_sources','Could not find a matching title: %s' % cleantitle.title_from_key(key))
			else:
				log('SUCCESS', 'get_sources','%s sources : %s' % (cleantitle.title_from_key(key), len(sources)))
				
			log('INFO', 'get_sources', 'Completed')
			
			return sources
		except Exception as e:
			log('ERROR', 'get_sources', '%s' % e)
			log('INFO', 'get_sources', 'Completed')
			return sources

	def resolve(self, url):
		try:
			return url
		except:
			return

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
