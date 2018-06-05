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

from resources.lib.libraries import client, control, cleantitle, testparams
from resources.lib import resolvers, proxies

name = 'DocumentaryArea'
loggertxt = []

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'June 01, 2018'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.base_link_alts = ['http://www.documentaryarea.net']
		self.base_link = self.base_link_alts[0]
		self.MainPageValidatingContent = 'Documentary Area - Simply the best Documentaries'
		self.type_filter = ['movie', 'show', 'anime']
		self.name = name
		self.disabled = False
		self.loggertxt = []
		self.ssl = False
		self.logo = 'https://i.imgur.com/lRlaUzo.png'
		self.search_link = '/results.php?pageNum_Recordset1=%s&search=%s&genre='
		self.user_agent = client.agent()
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
			headers = {'Referer': self.base_link, 'User-Agent': self.user_agent}
			x1 = time.time()
			http_res, content = proxies.request(url=site, output='response', use_web_proxy=False, headers=headers)
			self.speedtest = time.time() - x1
			if content != None and content.find(self.MainPageValidatingContent) >-1:
				log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,site))
				return True
			else:
				log('FAIL', 'testSite', 'Validation content Not Found. HTTP Resp : %s for %s' % (http_res,site))
				x1 = time.time()
				http_res, content = proxies.request(url=site, output='response', use_web_proxy=True, headers=headers)
				self.speedtest = time.time() - x1
				if content != None and content.find(self.MainPageValidatingContent) >-1:
					self.proxyrequired = True
					log('SUCCESS', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,site))
					return True
				else:
					time.sleep(2.0)
					x1 = time.time()
					http_res, content = proxies.request(url=site, output='response', use_web_proxy=True, headers=headers)
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
		
			for movie in testparams.test_documentaries:
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
			
			headers = {'Referer': self.base_link, 'User-Agent': self.user_agent}
			max = None
			title = title.replace('3D','').strip()
			
			for pg in range(100):
				query_url = urlparse.urljoin(self.base_link, self.search_link) % (pg, urllib.quote_plus(cleantitle.query(title)))
				
				if max != None and int(pg) > int(max):
					raise
					
				log(type='INFO', method='get_movie', err='Searching - %s' % (query_url), dolog=False, logToControl=False, doPrint=True)
					
				result = proxies.request(query_url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, headers=headers, timeout=60)
				
				if max == None:
					try:
						max1 = client.parseDOM(result, 'a', attrs = {'class': 'page gradient'})
						max = int(max1[len(max1)-1])-1
					except:
						pass
					
				url_data = client.parseDOM(result, 'div', attrs = {'class': 'ajuste4'})
				#print url_data
				
				if len(url_data) == 0:
					raise
				
				links_data = []
				
				for data in url_data:
					data = client.parseDOM(data, 'div', attrs = {'class': 'view'})[0]
					url = urlparse.urljoin(self.base_link, client.parseDOM(data, 'a', ret='href')[0])
					titlex = client.parseDOM(data, 'img', ret='alt')[0]
					try:
						poster = urlparse.urljoin(self.base_link, client.parseDOM(data, 'img', ret='src')[0])
					except:
						poster = None
					
					if title in titlex or titlex in title:
						url = url.replace(' ','%20')
						log(type='INFO', method='get_movie', err='Verifying - %s' % url, dolog=False, logToControl=False, doPrint=True)
						result = proxies.request(url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, headers=headers, timeout=60)
						
						ex_title = client.parseDOM(result, 'div', attrs = {'class': 'rating'})[0]
						
						if year in ex_title:
							#print result
							all_links = re.findall(r'{.*file:.*}', result)
							try:
								srt = re.findall(r'\"(.*srt.*)\"', result)[0]
								srt = urlparse.urljoin(self.base_link,srt)
							except:
								srt = None
							for datax in all_links:
								datax = datax.replace('file','"file"').replace('label','"label"')
								data_j = json.loads(datax)
								file = data_j['file']
								label = data_j['label']
									
								link_data = {'file':file, 'title':titlex, 'label':label, 'page':url, 'srt':srt, 'poster':poster}
								links_data.append(link_data)

							return links_data
						
			return
			
		except Exception as e: 
			log('ERROR', 'get_movie','%s: %s' % (title,e), dolog=self.init)
		return

	def get_show(self, imdb=None, tvdb=None, tvshowtitle=None, year=None, season=None, proxy_options=None, key=None, testing=False):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_show','Provider Disabled by User')
				return None
			
			max = None
			for pg in range(100):
				query_url = urlparse.urljoin(self.base_link, self.search_link) % (pg, urllib.quote_plus(cleantitle.query(title)))
				
				if max != None and pg > int(max):
					raise
					
				log(type='INFO', method='get_show', err='Searching - %s' % (query_url), dolog=False, logToControl=False, doPrint=True)
					
				result = proxies.request(query_url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
				
				if max == None:
					max1 = client.parseDOM(result, 'a', attrs = {'class': 'page gradient'})
					max = max1[len(max1)-1]
					
				url_data = client.parseDOM(result, 'div', attrs = {'class': 'ajuste4'})
				
				links_data = []
				
				for data in url_data:
					#print data
					url = urlparse.urljoin(self.base_link, client.parseDOM(data, 'a', ret='href')[0])
					titlex = client.parseDOM(data, 'img', ret='alt')[0]
					try:
						poster = urlparse.urljoin(self.base_link, client.parseDOM(data, 'img', ret='src')[0])
					except:
						poster = None
						
					if titlex in title:
						link_data = {'page':url, 'title':titlex, 'poster':poster}
						links_data.append(link_data)

						if testing == True:
							break

						return links_data
						
			return
			
		except Exception as e: 
			log('ERROR', 'get_show','%s: %s' % (tvshowtitle,e), dolog=self.init)
			return


	def get_episode(self, url=None, imdb=None, tvdb=None, title=None, year=None, season=None, episode=None, proxy_options=None, key=None, testing=False):
		try:
			if control.setting('Provider-%s' % name) == False:
				return None
			
			if url == None: return
			
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
			TYPES_QUAL = {'SD':'480p', '3D SD':'480p', '3D FullHD':'1080p'}
			TYPES_RIP = {'SD':'BRRIP', '3D SD':'3D-BRRIP', '3D FullHD':'3D-BRRIP'}
			
			for data_j in url:
				try:
					file = data_j['file']
					page = data_j['page']
					poster = data_j['poster']
					label = data_j['label']
					sub_url = data_j['srt']
					qual = '480p'
					riptype = 'BRRIP'
					if label in TYPES_QUAL.keys():
						qual = TYPES_QUAL[label]
						riptype = TYPES_RIP[label]
				
					headers = {'Referer': page, 'User-Agent': self.user_agent}
					links_m = resolvers.createMeta(file, self.name, self.logo, qual, links_m, key, riptype, testing=testing, sub_url=sub_url, headers=headers, poster=poster)
					
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
