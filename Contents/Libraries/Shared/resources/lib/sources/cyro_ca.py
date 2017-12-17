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

import re,urlparse,datetime,os,base64,urllib,time

from resources.lib.libraries import cleantitle
from resources.lib import resolvers
from resources.lib.libraries import client
from resources.lib.libraries import testparams
from resources.lib.libraries import control
from resources.lib import proxies

name = 'G2G'
loggertxt = []

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'Nov. 13, 2017'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.base_link_alts = ['http://xpau.se','http://xpau.se.prx2.unblocksites.co','http://xpau.se.prx.proxyunblocker.org']
		self.base_link = self.base_link_alts[0]
		self.MainPageValidatingContent = 'movies'
		self.type_filter = ['movie', 'show']
		self.urlhost = 'xpau.se'
		self.name = name
		self.loggertxt = []
		self.ssl = False
		self.disabled = False
		self.logo = 'http://i.imgur.com/coVgHWS.png'
		self.watch_link = '/watch/%s'
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
			return url
		except Exception as e: 
			log('ERROR', 'get_movie','%s: %s' % (title,e), dolog=self.init)
			return

	def get_show(self, imdb=None, tvdb=None, tvshowtitle=None, year=None, season=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_show','Provider Disabled by User')
				return None
			return
		except Exception as e: 
			log('ERROR', 'get_show','%s: %s' % (tvshowtitle,e), dolog=self.init)
			return

	def get_episode(self, url=None, imdb=None, tvdb=None, title=None, year=None, season=None, episode=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				return None
			url = {'imdb': imdb, 'tvdb': tvdb, 'title': title, 'season': season, 'episode': episode}
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
			
			url_arr=[]
			
			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			
			if 'episode' in data and 'season' in data:
				url0 = (data['title'].translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower() + "/s%s/e%s" % (data['season'],data['episode'])
				url_arr.append(url0)
			else:
				url1 = (data['title'].translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower()
				url2 = (data['title'].translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower() + "-%s" % (data['year'])
				url_arr.append(url1)
				url_arr.append(url2)
				try:
					title = data['title']
					title = title.split(':')
					title = title[0]
					url3 = (title.translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower()
					url_arr.append(url3)
				except:
					pass
				
			if 'episode' in data and 'season' in data:
				try:
					url1 = (data['title'].split(':')[0].translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower() + "/s%s/e%s" % (data['season'],data['episode'])
					url_arr.append(url1)
				except:
					pass
			else:
				try:
					url4 = (data['title'].split(':')[0].translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower()
					url5 = (data['title'].split(':')[0].translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower()+ "-%s" % (data['year'])
					url_arr.append(url4)
					url_arr.append(url5)
				except:
					pass
					
			url_arr = list(set(url_arr))
			links = []
			for url in url_arr:
				try:
					#print url
					
					url = urlparse.urljoin(self.base_link, self.watch_link % url)
					
					#print url

					r = proxies.request(url, output='geturl', proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
					
					#print r
				
					if r == None: raise Exception()

					r = result = proxies.request(url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
					#print "resp ===== %s" % r
					
					quality = '720p'

					r = re.sub(r'[^\x00-\x7F]+',' ', r)

					if 'episode' not in data or 'season' not in data:
						y = re.findall('Date\s*:\s*.+?>.+?(\d{4})', r)
						y = y[0] if len(y) > 0 else None
						#print y

						if ('year' in data and y != None and data['year'] != y): 
							#print 'year not found'
							raise Exception()

					q = client.parseDOM(r, 'title')
					q = q[0] if len(q) > 0 else None
					quality = '1080p' if ' 1080' in q else '720p'
					
					sub_url = None
					
					try:
						sub_url = urlparse.urljoin(self.base_link, re.findall('\/.*srt', result)[0])
					except:
						pass
					
					#print quality

					#r = client.parseDOM(r, 'div', attrs = {'id': '5throw'})[0]
					#r = client.parseDOM(r, 'a', ret='href', attrs = {'rel': 'nofollow'})
					
					try:
						r = client.parseDOM(r, 'div', attrs = {'id': '1strow'})[0]
						#print r
						r = client.parseDOM(r, 'a', ret='href', attrs = {'id': 'dm1'})[0]
						#print r
						links = resolvers.createMeta(r, self.name, self.logo, quality, links, key, vidtype='Movie', sub_url=sub_url, testing=testing)
					except Exception as e:
						log('FAIL', 'get_sources-1', e , dolog=False)	
						
					try:
						r = self.returnFinalLink(url)
						if r != None:
							links = resolvers.createMeta(r, self.name, self.logo, quality, links, key, vidtype='Movie', sub_url=sub_url, testing=testing)
					except Exception as e:
						log('FAIL', 'get_sources-2', e , dolog=False)	
				
					try:
						r = client.parseDOM(result, 'iframe', ret='src')
						r2 = [i for i in r if 'g2g' in i or 'ytid' in i]
						#print r2
						for r in r2:
							try:
								if 'http' not in r and self.urlhost in r:
									r = 'http:' + r
								elif 'http' not in r:
									r = self.base_link + r
								#print r
								r = proxies.request(r, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
								r = re.sub(r'[^\x00-\x7F]+',' ', r)
								r = client.parseDOM(r, 'iframe', ret='src')[0]
								
								part2=False
								if '.php' in r:
									r = self.base_link + r
									rx = r.replace('.php','2.php')
									
									r = proxies.request(r, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
									r = re.sub(r'[^\x00-\x7F]+',' ', r)
									r = client.parseDOM(r, 'iframe', ret='src')[0]
									
									try:
										rx = proxies.request(rx, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
										rx = re.sub(r'[^\x00-\x7F]+',' ', rx)
										rx = client.parseDOM(rx, 'iframe', ret='src')[0]
										if 'http' not in rx:
											rx = 'http:' + rx
										part2=True
									except:
										pass
								if 'http' not in r:
									r = 'http:' + r
								
								#print r
								
								if 'youtube' in r:
									vidtype = 'Trailer'
									qualityt = '720p'
									r = r.replace('?showinfo=0','')
								else:
									vidtype = 'Movie'
									qualityt = quality
									
								if part2:
									#print '2-part video'
									links = resolvers.createMeta(r, self.name, self.logo, qualityt, links, key, vidtype=vidtype, txt='Part-1', sub_url=sub_url, testing=testing)
									links = resolvers.createMeta(rx, self.name, self.logo, qualityt, links, key, vidtype=vidtype, txt='Part-2', sub_url=sub_url, testing=testing)
								else:
									links = resolvers.createMeta(r, self.name, self.logo, qualityt, links, key, vidtype=vidtype, sub_url=sub_url, testing=testing)
								
							except:
								pass
								
					except Exception as e:
						log('FAIL', 'get_sources-3', e , dolog=False)
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
		try:
			return url
		except:
			return
			
	def returnFinalLink(self, url):
		site = self.base_link
		headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*//**;q=0.8',
					'Accept-Language':'en-US,en;q=0.8',
					'Cache-Control':'max-age=0',
					'Connection':'keep-alive'}
		headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
		#headers['Cookie'] = ''
		#url = 'http://xpau.se/watch/war-for-the-planet-of-the-apes'
		
		for x in range(0,15):

			if 'wait' in url:
				url = client.request(url, output='geturl')
				
			resp = client.request(url, headers=headers)
			
			if x == 0:
				r = client.parseDOM(resp, 'a', ret='href', attrs = {'id': 'playthevid'})[0]
			elif 'adfoc' in url or 'wait' in url:
				r = client.parseDOM(resp, 'a', ret='href', attrs = {'id': 'skipper'})[0]
			else:
				try:
					r = client.parseDOM(resp, 'iframe', ret='src')[0]
				except:
					return None

			if 'google' in r:
				return r
			
			if 'http' not in r:
				url = site + r
			else:
				url = r

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
