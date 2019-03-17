# -*- coding: utf-8 -*-

# Coder Alpha
# https://github.com/coder-alpha
#

'''
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
#########################################################################################################

import re,urllib,urlparse,json,random,time,base64
from resources.lib.libraries import control
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import testparams
from resources.lib.libraries import workers
from resources.lib import resolvers
from resources.lib import proxies

name = 'GoWatchSeries'
loggertxt = []

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'Feb. 12, 2019'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.refreshCookies = False
		self.disabled = False
		self.base_link_alts = ['https://gowatchseries.co']
		self.base_link = self.base_link_alts[0]
		self.MainPageValidatingContent = ['Watchseries','Watch Series']
		self.type_filter = ['movie', 'show', 'anime']
		self.ssl = False
		self.name = name
		self.headers = {}
		self.cookie = None
		self.loggertxt = []
		self.logo = 'https://i.imgur.com/d0ubvug.png'
		self.speedtest = 0
		if len(proxies.sourceProxies)==0:
			proxies.init()
		self.proxyrequired = False
		self.msg = ''
		self.siteonline = self.testSite()
		self.testparser = 'Unknown'
		self.testparser = self.testParser()
		self.initAndSleepThread()
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
		
	def testSite(self):
		for site in self.base_link_alts:
			try:
				sitex = client.getRedirectingUrl(site).strip("/")
				if 'http' not in sitex:
					raise Exception('Error in geturl')
				else:
					site = sitex
			except:
				pass
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
		if self.refreshCookies == False:
			return
		thread_i = workers.Thread(self.InitSleepThread)
		thread_i.start()
		
	def InitSleepThread(self):
		while True:
			time.sleep(60*100)
			self.siteonline = self.testSite()
			self.testparser = self.testParser()
			self.initAndSleep()
			
	def initAndSleep(self):
		try:
			t_base_link = self.base_link
			self.headers = {'X-Requested-With': 'XMLHttpRequest'}
			self.headers['Referer'] = t_base_link
			ua = client.randomagent()
			self.headers['User-Agent'] = ua
			
			#get cf cookie
			cookie = proxies.request(url=t_base_link, headers=self.headers, output='cookie', use_web_proxy=self.proxyrequired, httpsskip=True)
			self.headers['Cookie'] = cookie
			log('SUCCESS', 'initAndSleep', 'Cookies : %s for %s' % (cookie,self.base_link))
		except Exception as e:
			log('ERROR','initAndSleep', '%s' % e)
		
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

	def get_movie(self, imdb, title, year, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_movie','Provider Disabled by User')
				return None
			if self.siteonline == False:
				log('INFO','get_movie','Provider is Offline')
				return None
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
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
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_sources','Provider Disabled by User')
				log('INFO', 'get_sources', 'Completed')
				return sources
			if url == None: 
				log('FAIL','get_sources','url == None. Could not find a matching title: %s' % cleantitle.title_from_key(key), dolog=not testing)
				log('INFO', 'get_sources', 'Completed')
				return sources
			
			year = None
			episode = None
			season = None
			
			log('INFO','get_sources-1', 'data-items: %s' % url, dolog=False)
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
			try: season = data['season']
			except: pass
			try: episode = data['episode']
			except: pass
					
			queries = []
			if season != None:
				queries = [{'keyword': '%s %s' % (title, season)}, {'keyword': title}]
			else:
				queries = [{'keyword': '%s %s' % (title, year)}, {'keyword': title}]
			
			rs = []
			for query in queries:
				search_url = urlparse.urljoin(self.base_link, '/search.html')
				search_url = search_url + '?' + urllib.urlencode(query)
				log('INFO','get_sources-2', 'search-url: %s' % search_url, dolog=False)
				
				result = proxies.request(search_url, headers=self.headers, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
				rs = client.parseDOM(result, 'ul', attrs = {'class': 'listing items'})
				if len(rs) > 0 and len(rs[0].strip()) > 4:
					break
					
			r = [(urlparse.urljoin(self.base_link,client.parseDOM(i, 'a', ret='href')[0]), client.parseDOM(i, 'div', attrs = {'class': 'name'})) for i in rs]
			ux = None
			for s in r:
				ux = s[0]
				result = proxies.request(ux, headers=self.headers, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
				rs = client.parseDOM(result, 'div', attrs = {'class': 'watch infonation'})[0]
				rs = client.parseDOM(rs, 'ul', attrs = {'class': 'three'})[0]
				if season != None:
					break
				if year!=None and year in rs:
					break
					
			log('INFO','get_sources-3', 'match-page-url: %s' % ux, dolog=False)
			links_m = []
			trailers = []
			poster = None
			vidtype = 'Movie'
			if season != None:
				vidtype = 'Show'
				
			riptype = 'BRRIP'
			quality = '720p'
			sub_url = None
			
			try:
				poster1 = client.parseDOM(result, 'div', attrs = {'class':'picture'})
				poster = client.parseDOM(poster1, 'img', ret='src')[0]
			except: pass
			
			links = client.parseDOM(result, 'li', attrs = {'class': 'child_episode'})
			
			try:
				if season == None:
					rip_qual = client.parseDOM(result, 'div', attrs = {'id': 'info_movies'})[0]
					rip_qual = client.parseDOM(rip_qual, 'div', attrs = {'class': 'right'})[0]
					rip_qual = client.parseDOM(rip_qual, 'a')[0].strip()
					rip_qual2 = ep_title = client.parseDOM(links[0], 'a', ret='title')[0]

					if 'HD' not in rip_qual and 'HD' not in rip_qual2:
						riptype = 'CAM'
					elif 'CAM' in rip_qual or 'CAM' in rip_qual2:
						riptype = 'CAM'
					if riptype == 'CAM':
						quality = '480p'
					if '720p' in rip_qual or '720p' in rip_qual2:
						quality = '720p'
					elif '1080p' in rip_qual or '1080p' in rip_qual2:
						quality = '1080p'
			except: pass
			mov_url = None
			
			for l in links:
				mov_urlx = urlparse.urljoin(self.base_link,client.parseDOM(l, 'a', ret='href')[0])
				ep_title = client.parseDOM(l, 'a', ret='title')[0]

				if season == None:
					mov_url = mov_urlx
				else:
					try:
						ep_nr = re.findall(r'Episode (.*?) ',ep_title)[0]
					except:
						try:
							ep_nr = re.findall(r'Episode (.*?)-',ep_title)[0]
						except:
							try:
								ep_nr = re.findall(r'Episode (.*?):',ep_title)[0]
							except: 
								ep_nr = re.findall(r'Episode (.*)',ep_title)[0]
					ep_nr = ep_nr.replace('-','').replace(':','').replace(' ','')
					if int(episode) == int(ep_nr):
						mov_url = mov_urlx
				
			if mov_url == None:
				raise Exception('No match found !')
				
			if season == None:
				log('INFO','get_sources-4', 'movie-page-url: %s' % mov_url, dolog=False)
			else:
				log('INFO','get_sources-4', 'show-episode-url: %s' % mov_url, dolog=False)
				
			page_url = mov_url
			result = proxies.request(mov_url, headers=self.headers, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, httpsskip=True)
			
			try:
				sub_url = re.findall(r'\"(.*vtt)\"', result)[0]
			except:
				pass
			
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
					links_m = resolvers.createMeta(trailer, self.name, self.logo, '720p', links_m, key, poster=poster, vidtype='Trailer', testing=testing)
			
			links = client.parseDOM(result, 'div', attrs = {'class': 'anime_muti_link'})
			links = client.parseDOM(links, 'li', ret='data-video')
			video_urls = []

			for l in links:
				if 'http' not in l:
					l = 'http:' + l
				video_urls.append(l)
				
			for video_url in video_urls:
				links_m = resolvers.createMeta(video_url, self.name, self.logo, quality, links_m, key, poster=poster, riptype=riptype, vidtype=vidtype, sub_url=sub_url, testing=testing, page_url=page_url)
			
			sources += [l for l in links_m]
			
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
