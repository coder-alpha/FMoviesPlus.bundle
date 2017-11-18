# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 Exodus

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


import re,urllib,urlparse,json,time

from resources.lib.libraries import cleantitle
from resources.lib import resolvers
from resources.lib.libraries import client
from resources.lib.libraries import testparams
from resources.lib.libraries import control
from resources.lib import proxies

name = 'GoGoAnime'
loggertxt = []

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'Nov. 13, 2017'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.priority = 1
		self.disabled = False
		self.language = ['en']
		self.type_filter = ['anime']
		self.domains = ['gogoanimemobile.com', 'gogoanimemobile.net', 'gogoanime.io']
		self.base_link_alts = ['https://ww3.gogoanime.io','https://gogoanime.io','http://gogoanimemobile.com', 'http://gogoanimemobile.net']
		self.base_link = self.base_link_alts[0]
		self.search_link = '/search.html?keyword=%s'
		self.episode_link = '/%s-episode-%s'
		self.MainPageValidatingContent = 'anime'
		self.urlhost = 'gogoanime.io'
		self.name = name
		self.loggertxt = []
		self.ssl = False
		self.logo = 'http://i.imgur.com/XC3vwqj.png'
		self.headers = {}
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
			'speed': round(self.speedtest,3),
			'name': self.name,
			'msg' : self.msg,
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
			if self.disabled == True:
				log('INFO','testParser', 'Plugin Disabled - cannot test parser')
				return False
			if self.siteonline == False:
				log('INFO', 'testParser', '%s is offline - cannot test parser' % self.base_link)
				return False
		
			for show in testparams.test_shows:
				geturl = self.get_show(tvshowtitle=show['title'], season=show['season'], year=show['year'])
				geturl = self.get_episode(geturl, episode=show['episode'])
				links = self.get_sources(url=geturl, testing=True)
				
				if links != None and len(links) > 0:
					log('SUCCESS', 'testParser', 'Parser is working')
					return True

			log('FAIL', 'testParser', 'Parser NOT working')
			return False
		except Exception as e:
			log('ERROR', 'testParser', '%s' % e)
			return False
			
	def get_movie(self,imdb, title, year, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_movie','Provider Disabled by User')
				return None
				
			return None
		except Exception as e: 
			log('ERROR', 'get_movie','%s: %s' % (title,e), dolog=self.init)
			return
		
	def get_show(self, tvshowtitle, season, imdb=None, tvdb=None, year=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_show','Provider Disabled by User')
				return None
				
			t = cleantitle.get(tvshowtitle)
			year = '%s' % year
			q = urlparse.urljoin(self.base_link, self.search_link)
			q = q % urllib.quote_plus(tvshowtitle)
			
			#r = client.request(q)
			r = proxies.request(q, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)

			r = client.parseDOM(r, 'ul', attrs={'class': 'items'})
			r = client.parseDOM(r, 'li')
			
			if len(r) == 0:
				raise Exception('Could not find a matching show title: %s' % tvshowtitle)
			
			r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title'), re.findall('\d{4}', i)) for i in r]
			
			r = [(i[0][0], i[1][0], i[2][-1]) for i in r if i[0] and i[1] and i[2]]
			r = [i for i in r if t == cleantitle.get(i[1]) and year == i[2]]
			r = r[0][0]

			url = re.findall('(?://.+?|)(/.+)', r)[0]
			url = client.replaceHTMLCodes(url)
			url = url.encode('utf-8')
			
			return url
		except Exception as e:
			log('ERROR', 'get_show','%s: %s' % (tvshowtitle,e), dolog=self.init)
			return


	def get_episode(self, url, episode, imdb=None, tvdb=None, title=None, year=None, season=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				return None
				
			if url == None: return

			url = [i for i in url.strip('/').split('/')][-1]
			url = self.episode_link % (url, episode)
			
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

			url = urlparse.urljoin(self.base_link, url)
			
			#r = client.request(url)
			req = proxies.request(url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)

			r = client.parseDOM(req, 'iframe', ret='src')
			try:
				r2 = re.findall('data-video=\"(.*?)\"', req)
				for r2_i in r2:
					r.append(r2_i)
			except:
				pass
				
			links = []

			for u in r:
				try:
					if 'http' not in u:
						u = 'http:' + u

					if u.startswith('http') == True:
						if 'vidstreaming' in u:
							#url = client.request(u)
							url = proxies.request(u, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
							
							url = client.parseDOM(url, 'source', ret='src')
						else:
							url = [u]

						for i in url:
							#try: sources.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
							#except: pass
							
							try:
								qualityt = client.googletag(i)[0]['quality']
							except:
								qualityt = u'720p'
							try:
								links = resolvers.createMeta(i, self.name, self.logo, qualityt, links, key, vidtype='Show', testing=testing)
							except:
								pass
				except:
					pass
					
			for i in links: sources.append(i)
			
			if len(sources) == 0:
				log('FAIL','get_sources','Could not find a matching title: %s' % cleantitle.title_from_key(key))
				return sources
			
			log('SUCCESS', 'get_sources','%s sources : %s' % (cleantitle.title_from_key(key), len(sources)), dolog=not testing)
			return sources
		except Exception as e:
			log('ERROR', 'get_sources', '%s' % e, dolog=not testing)
			return sources

	def resolve(self, url):
		return url
		
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
