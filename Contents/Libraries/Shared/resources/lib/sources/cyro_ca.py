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

class source:
	def __init__(self):
		self.base_link = 'http://xpau.se'
		self.MainPageValidatingContent = 'movies'
		self.type_filter = ['movie', 'show']
		self.urlhost = 'xpau.se'
		self.name = 'G2G'
		self.loggertxt = []
		self.ssl = False
		self.logo = 'http://i.imgur.com/coVgHWS.png'
		self.watch_link = '/watch/%s'
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

	def get_movie(self,imdb, title, year, proxy_options=None, key=None, testing=False):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def get_show(self, imdb, tvdb, tvshowtitle, year, season, proxy_options=None, key=None):
			return


	def get_episode(self, url, imdb, tvdb, title, year, season, episode, proxy_options=None, key=None):
		try:
			url = {'imdb': imdb, 'tvdb': tvdb, 'title': title, 'season': season, 'episode': episode}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):
		try:
			sources = []
			
			#print '%s ---------- %s' % (self.name,url)

			if url == None: return sources
			
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
					
					#print quality

					#r = client.parseDOM(r, 'div', attrs = {'id': '5throw'})[0]
					#r = client.parseDOM(r, 'a', ret='href', attrs = {'rel': 'nofollow'})
				
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
									links = resolvers.createMeta(r, self.name, self.logo, qualityt, links, key, vidtype=vidtype, txt='Part-1')
									links = resolvers.createMeta(rx, self.name, self.logo, qualityt, links, key, vidtype=vidtype, txt='Part-2')
								else:
									links = resolvers.createMeta(r, self.name, self.logo, qualityt, links, key, vidtype=vidtype)
								
							except:
								pass
								
					except Exception as e:
						control.log('ERROR %s get_sources3 > %s' % (self.name, e.args))
				except:
					pass

			for i in links: sources.append(i)

			#print sources
			
			return sources
		except Exception as e:
			control.log('ERROR %s get_sources > %s' % (self.name, e))
			return sources


	def resolve(self, url):
		try:
			return url
		except:
			return

def logger(msg):
	control.log(msg)

