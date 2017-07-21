# -*- coding: utf-8 -*-

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
		self.base_link = 'https://fmovies.io'
		self.search_link = '/sitemap'
		self.search_link2 = 'https://fmovies.io/search.html?keyword=%s'
		self.link_server_f1 = "https://player.fmovies.io/bk/embed.php?id=%s"
		self.link_server_f2 = "https://player.fmovies.io/embed.php?id=%s"
		self.hash_link = '/ajax/episode/info'
		self.MainPageValidatingContent = 'Watch Free Movies Online -  Streaming MoviesFast - Fmovies'
		self.type_filter = ['movie', 'show', 'anime']
		self.ssl = False
		self.name = 'FMovies.io'
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
			
	def setNewCookies(self):
		try:
			ua = client.randomagent()
			self.headers['User-Agent'] = ua
			self.cookie = proxies.request(url=self.base_link, headers=self.headers, output='cookie', use_web_proxy=self.proxyrequired)
			self.headers['Cookie'] = self.cookie
		except Exception as e:
			self.log('ERROR','setNewCookies', '%s' % e, dolog=True)
		
			
	def testSite(self):
		try:
			ua = client.randomagent()
			self.headers['User-Agent'] = ua
			x1 = time.time()
			http_res, content = proxies.request(url=self.base_link, headers=self.headers, output='response', use_web_proxy=False, httpsskip=True)
			self.speedtest = time.time() - x1
			if content != None and content.find(self.MainPageValidatingContent) >-1:
				x1 = time.time()
				self.cookie = proxies.request(url=self.base_link, headers=self.headers, output='cookie', use_web_proxy=False, httpsskip=True)
				self.speedtest = time.time() - x1
				self.headers['Cookie'] = self.cookie
				self.log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,self.base_link), dolog=True)
				self.log('SUCCESS', 'testSite', 'Cookie Resp : %s for %s' % (self.cookie,self.base_link), dolog=True)
				return True
			else:
				self.log('ERROR', 'testSite', 'HTTP Resp : %s for %s' % (http_res,self.base_link), dolog=True)
				x1 = time.time()
				http_res, content = proxies.request(url=self.base_link, headers=self.headers, output='response', use_web_proxy=True, httpsskip=True)
				self.speedtest = time.time() - x1
				if content != None and content.find(self.MainPageValidatingContent) >-1:
					self.proxyrequired = True
					x1 = time.time()
					self.cookie = proxies.request(url=self.base_link, headers=self.headers, output='cookie', use_web_proxy=True, httpsskip=True)
					self.speedtest = time.time() - x1
					self.headers['Cookie'] = self.cookie
					self.log('SUCCESS', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,self.base_link), dolog=True)
					self.log('SUCCESS', 'testSite', 'Cookie Resp : %s for %s' % (self.cookie,self.base_link), dolog=True)
					return True
				else:
					time.sleep(2.0)
					x1 = time.time()
					http_res, content = proxies.request(url=self.base_link, headers=self.headers, output='response', use_web_proxy=True, httpsskip=True)
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
			if self.siteonline == False:
				self.log('ERROR', 'testParser', 'testSite returned False', dolog=True)
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
			title = title.replace('&','and')
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


	def get_episode(self, url, imdb, tvdb, title, year, season, episode, proxy_options=None, key=None, testing=False):

		try:
			url = {'year':year, 'imdb': imdb, 'tvdb': tvdb, 'title': title, 'season': season, 'episode': episode}
			url = urllib.urlencode(url)
			return url
		except:
			return

	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):

		try:
			sources = []
			
			if url == None: return sources
			urls = []
			
			if not str(url).startswith('http'):
				try:
					data = urlparse.parse_qs(url)
					data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
					
					#print data

					title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

					if 'year' in data:
						year = data['year']
					try: episode = data['episode']
					except: pass

					query = {'keyword': title}
					search_url = urlparse.urljoin(self.base_link, '/search.html')
					search_url = search_url + '?' + urllib.urlencode(query)
					#print search_url
					
					result = proxies.request(search_url, headers=self.headers, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
					
					#self.log('GRABBER','get_sources-2', '%s' % search_url, dolog=False)
					r = client.parseDOM(result, 'div', attrs = {'class': 'wrapper'})
					try:
						r = r[1]
					except:
						raise Exception()
					
					#print r
					r1 = client.parseDOM(r, 'figure')
					r2 = []
					for res in r1:
						l = client.parseDOM(res, 'a', ret='href')[0]
						t = client.parseDOM(res, 'div', attrs = {'class': 'title'})[0]
						r = (l,t)
						r2.append(r)
					
					r = r2
					#print data
					
					if 'season' in data:
						r = [(i[0], re.sub(' \(\w*\)', '', i[1])) for i in r]
						#print r
						#title += '%01d' % int(data['season'])
						url = [(i[0], re.findall('(.+?) (\d+)$', i[1])) for i in r]
						url = [(i[0], i[1][0][0], i[1][0][1]) for i in url if len(i[1]) > 0]
						url = [i for i in url if cleantitle.get(title) in cleantitle.get(i[1])]
						#for i in url:
						#	print i[2],i[0],i[1]
						#	print '%01d' % int(data['season']) == '%01d' % int(i[2])

						url = [i for i in url if '%01d' % int(data['season']) == '%01d' % int(i[2])]
						for i in url:
							urls.append(urlparse.urljoin(self.base_link, i[0]))
					else:
						for i in r:
							if cleantitle.get(title) in cleantitle.get(i[1]):
								urls.append(urlparse.urljoin(self.base_link, i[0]))	

				except:
					urls == [self.base_link]
			
			links_m = []
			#print urls
			
			for url in urls:
				try:
					result = proxies.request(url, headers=self.headers, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
					
					quality = '480p'
					type = 'BRRIP'
					
					try:
						atr = client.parseDOM(result, 'span', attrs = {'class': 'quanlity'})[0]
						q, t = cleantitle.getQuality(atr)
						if q != None:
							quality = q
							type = t
					except:
						pass
					
					try:
						atr = client.parseDOM(result, 'span', attrs = {'class': 'year'})[0]
					except:
						atr = ''
					#print atr
					try:
						atr_release = client.parseDOM(result, 'div', attrs = {'class': 'meta'})[1]
					except:
						atr_release = ''
					#print atr_release
					
					if 'season' in data:
						pass
					else:
						resultx = result if str(int(year)) in atr or str(int(year)+1) in atr or str(int(year)-1) in atr else None
						if resultx == None:
							resultx = result if str(int(year)) in atr_release or str(int(year)+1) in atr_release or str(int(year)-1) in atr_release else None
						if resultx == None:
							raise Exception()
							
					#print url

					r = client.parseDOM(result, 'article', attrs = {'class': 'player current'})[0]
					result = client.parseDOM(r, 'iframe', ret='src')[0]
					result = result.split('?')
					data = urlparse.parse_qs(result[1])
					
					id = data['id'][0]
					
					try:
						server_f1 = self.link_server_f1 % id
						result = proxies.request(server_f1, headers=self.headers, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)

						ss = client.parseDOM(result, 'source', ret='src')
						for s in ss:
							#print s
							links_m = resolvers.createMeta(s, self.name, self.logo, quality, links_m, key)
							if testing and len(links_m) > 0:
								break
					except:
						pass
					
					try:
						server_f2 = self.link_server_f2 % id
						result = proxies.request(server_f2, headers=self.headers, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
						ss = client.parseDOM(result, 'source', ret='src')
						for s in ss:
							#print s
							if testing and len(links_m) > 0:
								break
							links_m = resolvers.createMeta(s, self.name, self.logo, quality, links_m, key)
						if testing and len(links_m) > 0:
								break
					except:
						pass
				except:
					pass

			#print links_m
			for link in links_m:
				sources.append(link)
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

def logger(msg):
	control.log(msg)
