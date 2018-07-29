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


import re,urllib,urlparse,base64,time

from resources.lib.libraries import client, control, cleantitle, testparams
from resources.lib import resolvers, proxies

name = 'Ganool'
loggertxt = []

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'May. 21, 2018'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.base_link_alts = ['https://ganol.movie']
		self.base_link = self.base_link_alts[0]
		self.MainPageValidatingContent = 'Ganool : Download &amp; Watch Movies Online Free'
		self.type_filter = ['movie', 'show', 'anime']
		self.name = name
		self.disabled = False
		self.loggertxt = []
		self.ssl = False
		self.logo = 'https://i.imgur.com/gRy6qYD.png'
		self.search_link = '/?s=%s'
		self.headers = {'Connection' : 'keep-alive'}
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
			
			query_url = urlparse.urljoin(self.base_link, self.search_link) % (urllib.quote_plus(cleantitle.query(title)) + ('+' + str(year)) if year != None else '')
			
			log(type='INFO', method='get_movie', err='Searching - %s' % (query_url), dolog=False, logToControl=False, doPrint=True)
			
			result = proxies.request(query_url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			
			url_data = client.parseDOM(result, 'div', attrs = {'class': 'item'})
			
			links_data = []
			
			for data in url_data:
				#print data
				link = client.parseDOM(data, 'a', ret='href')[0]
				titlex = client.parseDOM(data, 'span', attrs = {'class': 'tt'})[0]
				title = titlex
				year2 = client.parseDOM(data, 'span', attrs = {'class': 'year'})[0]
				
				if str(year) == str(year2):
					xyear = ' (%s)' % year2
					if xyear in title:
						title = title.split(xyear)[0]
					quality, riptype = cleantitle.getQuality2(client.parseDOM(data, 'span', attrs = {'class': 'calidad2'})[0])
					
					#print link, title, year2, quality, riptype
					log(type='INFO', method='get_movie', err='Processing %s - %s' % (titlex, link), dolog=False, logToControl=False, doPrint=True)
					result = proxies.request(link, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
					
					try:
						poster = client.parseDOM(result, 'img', attrs = {'itemprop': 'image'}, ret='src')[0]
					except:
						poster = None
					
					elems = client.parseDOM(result, 'li', attrs = {'class': 'elemento'})
					for elem in elems:
						url = client.parseDOM(elem, 'a', ret='href')[0]
						type = client.parseDOM(elem, 'span', attrs = {'class': 'a'})[0]
						
						result = proxies.request(link, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
						
						elems = client.parseDOM(result, 'li', attrs = {'class': 'elemento'})
						for elem in elems:
							url = client.parseDOM(elem, 'a', ret='href')[0]
							type = client.parseDOM(elem, 'span', attrs = {'class': 'a'})[0]
							
							if 'play' in type:
								link_data = {'link':url, 'page':link, 'title':title, 'year':year2, 'qual':quality, 'rip':riptype, 'poster':poster}
								links_data.append(link_data)

						if testing == True:
							break

			return links_data
			
		except Exception as e: 
			log('ERROR', 'get_movie','%s: %s' % (title,e), dolog=self.init)
			return

	def get_show(self, imdb=None, tvdb=None, tvshowtitle=None, year=None, season=None, proxy_options=None, key=None, testing=False):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_show','Provider Disabled by User')
				return None
			
			query_url = urlparse.urljoin(self.base_link, self.search_link) % (urllib.quote_plus(cleantitle.query(tvshowtitle)) + ('+season+' + str(season)) if season != None else '')
			
			log(type='INFO', method='get_show', err='Searching - %s' % (query_url), dolog=False, logToControl=False, doPrint=True)
			result = proxies.request(query_url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			
			url_data = client.parseDOM(result, 'div', attrs = {'class': 'item'})
			
			try:
				poster = client.parseDOM(result, 'img', attrs = {'itemprop': 'image'}, ret='src')[0]
			except:
				poster = None
			
			links_data = []
			
			for data in url_data:
				#print data
				link = client.parseDOM(data, 'a', ret='href')[0]
				title = client.parseDOM(data, 'span', attrs = {'class': 'tt'})[0]
				year2 = client.parseDOM(data, 'span', attrs = {'class': 'year'})[0]
				
				if lose_match_year(year, year2, season):
					xyear = ' (%s)' % year2
					if xyear in title:
						title = title.split(xyear)[0]
					quality, riptype = cleantitle.getQuality2(client.parseDOM(data, 'span', attrs = {'class': 'calidad2'})[0])
					
					#print link, title, year2, quality, riptype
					
					link_data = {'page':link, 'title':title, 'year':year2, 'qual':quality, 'rip':riptype, 'poster':poster}
					links_data.append(link_data)
					if testing == True:
						break

			return links_data
			
		except Exception as e: 
			log('ERROR', 'get_show','%s: %s' % (tvshowtitle,e), dolog=self.init)
			return


	def get_episode(self, url=None, imdb=None, tvdb=None, title=None, year=None, season=None, episode=None, proxy_options=None, key=None, testing=False):
		try:
			if control.setting('Provider-%s' % name) == False:
				return None
			
			if url == None: return
			
			links_data = []
			for data in url:
				#print data
				log(type='INFO', method='get_episode', err='Processing %s - %s' % (data['title'], data['page']), dolog=False, logToControl=False, doPrint=True)
				result = proxies.request(data['page'], proxy_options=proxy_options, use_web_proxy=self.proxyrequired)	
				elems = client.parseDOM(result, 'li', attrs = {'class': 'elemento'})
				
				for elem in elems:
					ep = client.parseDOM(elem, 'span', attrs = {'class': 'c'})[0]
					
					if ep.lower().replace('episode','').strip() == str(episode):
						type = client.parseDOM(elem, 'span', attrs = {'class': 'a'})[0]
						
						if 'play' in type:
							url = client.parseDOM(elem, 'a', ret='href')[0]
							link_data = {'link':url, 'page':data['page'], 'title':data['title'], 'year':data['year'], 'qual':data['qual'], 'rip':data['rip'], 'poster':data['poster']}
							links_data.append(link_data)
				if testing == True:
					break

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

			links_m = []
			for data in url:
				try:
					links_m = resolvers.createMeta(data['link'], self.name, self.logo, data['qual'], links_m, key, poster=data['poster'], riptype=data['rip'], testing=testing)
					if testing == True and len(links_m) > 0:
						break
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

def lose_match_year(yr1, yr2, seasonNr):
	try:
		yr1 = str(yr1)
		yr2 = str(yr2)
		seasonNr = int(seasonNr)
		if yr1 == yr2 or int(yr1) - seasonNr == int(yr2) or int(yr2) - seasonNr == int(yr1):
			return True
		else:
			raise
	except:
		False
			
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
