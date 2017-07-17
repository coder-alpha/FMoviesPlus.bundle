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


class source:
	def __init__(self):
		self.priority = 1
		self.language = ['en']
		self.type_filter = ['anime']
		self.domains = ['gogoanimemobile.com', 'gogoanimemobile.net', 'gogoanime.io']
		self.base_link = 'https://www.gogoanime.io'
		self.search_link = '/search.html?keyword=%s'
		self.episode_link = '/%s-episode-%s'
		self.MainPageValidatingContent = 'anime'
		self.urlhost = 'gogoanime.io'
		self.name = 'GoGoAnime'
		self.loggertxt = []
		self.ssl = False
		self.logo = 'http://i.imgur.com/XC3vwqj.png'
		self.headers = {}
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
			'speed': round(self.speedtest,3),
			'name': self.name,
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
			if self.siteonline == False:
				self.log('ERROR', 'testParser', 'testSite returned False', dolog=True)
				return False
		
			for show in testparams.test_shows:
				geturl = self.get_show(tvshowtitle=show['title'], season=show['season'], year=show['year'])
				geturl = self.get_episode(geturl, episode=show['episode'])
				links = self.get_sources(url=geturl, testing=True)
				
				if links != None and len(links) > 0:
					self.log('SUCCESS', 'testParser', 'links : %s' % len(links), dolog=True)
					return True
				else:
					self.log('ERROR', 'testParser', 'geturl : %s' % geturl, dolog=True)
					self.log('ERROR', 'testParser', 'links : %s' % links, dolog=True)
			return False
		except Exception as e:
			self.log('ERROR', 'testParser', '%s' % e, dolog=True)
			return False
		
	def get_show(self, tvshowtitle, season, imdb=None, tvdb=None, year=None, proxy_options=None, key=None):
		try:
			
			t = cleantitle.get(tvshowtitle)

			q = urlparse.urljoin(self.base_link, self.search_link)
			q = q % urllib.quote_plus(tvshowtitle)
			
			#r = client.request(q)
			r = proxies.request(q, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)

			r = client.parseDOM(r, 'ul', attrs={'class': 'items'})
			r = client.parseDOM(r, 'li')
			r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title'), re.findall('\d{4}', i)) for i in r]
			
			r = [(i[0][0], i[1][0], i[2][-1]) for i in r if i[0] and i[1] and i[2]]
			r = [i for i in r if t == cleantitle.get(i[1]) and year == i[2]]
			r = r[0][0]

			url = re.findall('(?://.+?|)(/.+)', r)[0]
			url = client.replaceHTMLCodes(url)
			url = url.encode('utf-8')
			
			return url
		except Exception as e:
			print e
			return


	def get_episode(self, url, episode, imdb=None, tvdb=None, title=None, year=None, season=None, proxy_options=None, key=None):
		try:
			if url == None: return

			url = [i for i in url.strip('/').split('/')][-1]
			url = self.episode_link % (url, episode)
			
			return url
		except Exception as e:
			print e
			return


	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):
		try:
			sources = []

			if url == None: return sources

			url = urlparse.urljoin(self.base_link, url)
			
			#r = client.request(url)
			r = proxies.request(url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)

			r = client.parseDOM(r, 'iframe', ret='src')
			
			links = []

			for u in r:
				try:
					if not u.startswith('http') and not 'vidstreaming' in u: raise Exception()

					#url = client.request(u)
					url = proxies.request(u, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
					
					url = client.parseDOM(url, 'source', ret='src')

					for i in url:
						#try: sources.append({'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'language': 'en', 'url': i, 'direct': True, 'debridonly': False})
						#except: pass
						
						try:
							qualityt = client.googletag(i)[0]['quality']
						except:
							qualityt = u'720p'
						try:
							links = resolvers.createMeta(i, self.name, self.logo, qualityt, links, key, vidtype='Show')
						except:
							pass
						if testing and len(links) > 0:
							break
				except:
					pass
					
			for i in links: sources.append(i)

			return sources
		except Exception as e:
			control.log('ERROR %s get_sources > %s' % (self.name, e))
			return sources

	def resolve(self, url):
		return url
		
def logger(msg):
	control.log(msg)
	


