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


import re,urllib,urlparse,base64,time,json

from resources.lib.libraries import cleantitle, jsunpack, client, testparams, control
from resources.lib import resolvers, proxies

name = 'CmoviesHD'
loggertxt = []

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.3'
		self.update_date = 'Feb. 07, 2019'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.base_link_alts = ['http://cmovieshd.net']
		self.base_link = self.base_link_alts[0]
		self.MainPageValidatingContent = 'Watch movies online-Free movies to watch online/CMoviesHD'
		self.type_filter = ['movie', 'show', 'anime']
		self.name = name
		self.aliases = []
		self.disabled = False
		self.loggertxt = []
		self.ssl = False
		self.logo = 'https://i.imgur.com/OEgxiyP.png'
		self.search_link = 'search/?q=%s'
		self.headers = {'Connection' : 'keep-alive'}
		self.speedtest = 0
		if len(proxies.sourceProxies)==0:
			proxies.init()
		self.proxyrequired = False
		self.msg = ''
		self.siteonline = self.testSite()
		self.testparser = 'Unknown'
		self.testparser = self.testParser()
		self.firstRunDisabled = True
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
			x1 = time.time()
			http_res, content = proxies.request(url=site, output='response', use_web_proxy=False)
			self.speedtest = time.time() - x1
			if content != None and content.find(self.MainPageValidatingContent) >-1:
				log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,site))
				return True
			else:
				log('FAIL', 'testSite', 'Validation content Not Found. HTTP Resp : %s for %s' % (http_res,site))
				x1 = time.time()
				http_res, content = proxies.request(url=site, output='response', use_web_proxy=True)
				self.speedtest = time.time() - x1
				if content != None and content.find(self.MainPageValidatingContent) >-1:
					self.proxyrequired = True
					log('SUCCESS', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,site))
					return True
				else:
					time.sleep(2.0)
					x1 = time.time()
					http_res, content = proxies.request(url=site, output='response', use_web_proxy=True)
					self.speedtest = time.time() - x1
					if content != None and content.find(self.MainPageValidatingContent) >-1:
						self.proxyrequired = True
						log('SUCCESS', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,site))
						return True
					else:
						log('FAIL', 'testSite', 'Validation content Not Found. HTTP Resp : %s via proxy for %s' % (http_res,site))			
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
				getmovieurl = self.get_movie(title=movie['title'], year=movie['year'], imdb=movie['imdb'], testing=True)
				movielinks = self.get_sources(url=getmovieurl, testing=True)
				
				if movielinks != None and len(movielinks) > 0:
					log('SUCCESS', 'testParser', 'Parser is working')
					return True
					
			log('FAIL', 'testParser', 'Parser NOT working')
			return False
		except Exception as e:
			log('ERROR', 'testParser', '%s' % e)
			return False

	def get_movie(self, imdb, title, year, proxy_options=None, key=None, testing=False):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_movie','Provider Disabled by User')
				return None
			
			del self.aliases[:]
			self.aliases.append({'country': 'us', 'title': title})
			url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': self.aliases}
			url = urllib.urlencode(url)
			return url
			
		except Exception as e: 
			log('ERROR', 'get_movie','%s: %s' % (title,e), dolog=self.init)
			return

	def get_show(self, imdb=None, tvdb=None, tvshowtitle=None, year=None, season=None, proxy_options=None, key=None, testing=False):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_show','Provider Disabled by User')
				return None
			
			del self.aliases[:]
			self.aliases.append({'country': 'us', 'title': tvshowtitle})
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': self.aliases}
			url = urllib.urlencode(url)
			return url
			
		except Exception as e: 
			log('ERROR', 'get_show','%s: %s' % (tvshowtitle,e), dolog=self.init)
			return

	def get_episode(self, url=None, imdb=None, tvdb=None, title=None, year=None, season=None, episode=None, proxy_options=None, key=None, testing=False):
		try:
			if control.setting('Provider-%s' % name) == False:
				return None
			
			if url == None: return
			url = urlparse.parse_qs(url)
			url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
			url['title'], url['premiered'], url['season'], url['episode'] = title, None, season, episode
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
				return sources
			if url == None: 
				log('FAIL','get_sources','url == None. Could not find a matching title: %s' % cleantitle.title_from_key(key), dolog=not testing)
				return sources
			
			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
			year = data['year']
			aliases = eval(data['aliases'])
			#cookie = '; approve_search=yes'
			query = self.search_link % (urllib.quote_plus(title))
			query = urlparse.urljoin(self.base_link, query)
			
			log(type='INFO', method='get_sources', err='Searching - %s' % query, dolog=False, logToControl=False, doPrint=True)
			result = client.request(query) #, cookie=cookie)
			
			links_m = []
			
			try:
				if 'episode' in data:
					r = client.parseDOM(result, 'div', attrs={'class': 'ml-item'})
					r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'))
					r = [(i[0], i[1], re.findall('(.*?)\s+-\s+Season\s+(\d+)', i[1])) for i in r]
					r = [(i[0], i[1], i[2][0]) for i in r if len(i[2]) > 0]
					url = [i[0] for i in r if self.matchAlias(i[2][0], aliases) and i[2][1] == data['season']][0]

					url = '%swatch' % url
					result = client.request(url)

					url = re.findall('a href=\"(.+?)\" class=\"btn-eps first-ep \">Episode %02d' % int(data['episode']), result)[0]

				else:
					r = client.parseDOM(result, 'div', attrs={'class': 'ml-item'})
					r = zip(client.parseDOM(r, 'a', ret='href'), client.parseDOM(r, 'a', ret='title'), client.parseDOM(r, 'img', ret='data-original'))
					
					results = [(i[0], i[1], re.findall(r'images/(.*?)-', i[2])) for i in r]
					
					try:
						r = [(i[0], i[1], i[2][0]) for i in results if len(i[2]) > 0]
						url = [i[0] for i in r if self.matchAlias(i[1], aliases) and (year == i[2])][0]
					except Exception as e:
						print e
						url = None
						pass
						
					if (url == None):
						url = [i[0] for i in results if self.matchAlias(i[1], aliases)][0]
					url = urlparse.urljoin(url, 'watch')

				#url = client.request(url, output='geturl')
				if url == None: raise Exception()
			except Exception as e:
			  raise Exception('Step 1 Failed: %s > %s' % (url,e))

			url = url if 'http' in url else urlparse.urljoin(self.base_link, url)
			log(type='INFO', method='get_sources', err='Match found - %s' % url, dolog=False, logToControl=False, doPrint=True)
			
			result = client.request(url)
			try:
				poster = client.parseDOM(result, 'img', attrs={'itemprop':'image'}, ret='src')[0]
			except:
				poster = None
				
			Juicy = False
			ss = []
			riptype = 'BRRIP'
			
			if 'streamdor' in result and Juicy == True:
				src = re.findall('src\s*=\s*"(.*streamdor.co\/video\/\d+)"', result)[0]
				if src.startswith('//'):
					src = 'http:'+src
				episodeId = re.findall('.*streamdor.co/video/(\d+)', src)[0]
				p = client.request(src, referer=url)
				
				try:
					#log(type='INFO', method='get_sources', err='Juicy Code', dolog=False, logToControl=False, doPrint=True)
					p = re.findall(r'JuicyCodes.Run\(([^\)]+)', p, re.IGNORECASE)[0]
					p = re.sub(r'\"\s*\+\s*\"','', p)
					p = re.sub(r'[^A-Za-z0-9+\\/=]','', p)
					p = base64.b64decode(p)
					p = jsunpack.unpack(p)
					p = unicode(p, 'utf-8')

					post = client.encodePostData({'id': episodeId})
					
					p2 = client.request('https://embed.streamdor.co/token.php?v=5', post=post, referer=src, XHR=True, timeout=60)
					
					js = json.loads(p2)
					tok = js['token']
					quali = 'SD'
					try:
						quali = re.findall(r'label:"(.*?)"',p)[0]
					except:
						pass
					
					p = re.findall(r'var\s+episode=({[^}]+});',p)[0]
					js = json.loads(p)
					
					try:
						rtype = js['eName']
						if '0p' in rtype.lower() or 'sd' in rtype.lower() or 'hd' in rtype.lower():
							raise
						riptype = rtype
					except:
						pass

					if 'fileEmbed' in js and js['fileEmbed'] != '':
						ss.append([js['fileEmbed'], quali, riptype])
					if 'filePlaylist' in js and js['filePlaylist'] != '':
						js_data = client.request('https://embed.streamdor.co/play/sources?hash=%s&token=%s'%(js['filePlaylist'],tok), referer=src, XHR=True)
						
						js = json.loads(js_data)
						m_srcs = js['playlist'][0]['sources']
						if 'error' not in m_srcs:
							for m_src in m_srcs:
								ss.append([m_src['file'], m_src['label'], riptype])
					if 'fileHLS' in js and js['fileHLS'] != '':
						ss.append(['https://hls.streamdor.co/%s%s'%(tok, js['fileHLS']), quali, riptype])
						
				except Exception as e:
					raise Exception('Step 2 Failed: %s > %s' % (url,e))
			else:
				#log(type='INFO', method='get_sources', err='Embed Code', dolog=False, logToControl=False, doPrint=True)
				div_s = client.parseDOM(result, 'div', attrs={'id': 'list-eps'})[0]
				pages = client.parseDOM(div_s, 'a', ret='href')
				#print pages
				quals = re.findall(r'>(.*?)</a>',div_s)
				#print quals
				c=0
				for p in pages:
					p1 = client.request(p, referer=url)
					file_id = re.findall(r'load_player\.html\?e=(.*?)\"',p1)[0]
					file_loc = 'https://api.streamdor.co/episode/embed/%s' % file_id
					js_data = client.request(file_loc, referer=p)
					js = json.loads(js_data)
					m_srcs = js['embed']
					try:
						rtype = quals[c]
						if '0p' in rtype.lower() or 'sd' in rtype.lower() or 'hd' in rtype.lower():
							raise
						riptype = 'CAM'
					except:
						pass
					ss.append([m_srcs, file_quality(quals[c]), riptype])
					c=c+1

			for link in ss:
				#print link
				try:
					if 'google' in url:
						xs = client.googletag(url)
						for x in xs:
							try:
								links_m = resolvers.createMeta(x['url'], self.name, self.logo, x['quality'], links_m, key, riptype, poster=poster, testing=testing)
								if testing == True and len(links_m) > 0:
									break
							except:
								pass
					else:
						try:
							links_m = resolvers.createMeta(link[0], self.name, self.logo, link[1], links_m, key, link[2], poster=poster, testing=testing)
							if testing == True and len(links_m) > 0:
								break
						except:
							pass
				except:
					pass
			
			for l in links_m:
				sources.append(l)

			if len(sources) == 0:
				log('FAIL','get_sources','Could not find a matching title: %s' % cleantitle.title_from_key(key))
				return sources
			
			log('SUCCESS', 'get_sources','%s sources : %s' % (cleantitle.title_from_key(key), len(sources)), dolog=not testing)
			return sources
		except Exception as e:
			log('ERROR', 'get_sources', '%s' % e, dolog=not testing)
			return sources

	def matchAlias(self, title, aliases):
		try:
			for alias in aliases:
				if cleantitle.get(title) == cleantitle.get(alias['title']):
					return True
		except:
			return False
			
def file_quality(title):
	#print "%s - %s" % (self.name, url)
	try:
		title = title.lower()
	
		if '1080p' in title:
			return '1080p'
		elif '720p' in title:
			return '720p'
		elif '480p' in title:
			return '480p'
		elif '360p' in title:
			return '360p'
		else:
			return '360p'
	except:
		return '360p'

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
