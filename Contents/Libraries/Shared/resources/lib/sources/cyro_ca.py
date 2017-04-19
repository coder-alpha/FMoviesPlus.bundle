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
		self.base_link = 'http://cyro.se'
		self.urlhost = 'cyro.se'
		self.name = 'G2G'
		self.ssl = False
		self.logo = 'http://i.imgur.com/3VRoX2c.png'
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
		
	def testSite(self):
		try:
			x1 = time.time()
			http_res = proxies.request(url=self.base_link, output='responsecode', httpsskip=self.ssl, use_web_proxy=False)
			self.speedtest = time.time() - x1
			if http_res==None or http_res not in client.HTTP_GOOD_RESP_CODES:
				log('ERROR', self.name, 'HTTP Resp : %s for %s' % (http_res,self.base_link))
				x1 = time.time()
				http_res = proxies.request(url=self.base_link, output='responsecode', httpsskip=self.ssl, use_web_proxy=True)
				self.speedtest = time.time() - x1
				if http_res==None or http_res not in client.HTTP_GOOD_RESP_CODES:
					log('ERROR via proxy', self.name, 'HTTP Resp : %s for %s' % (http_res,self.base_link))
					return False
				else:
					self.proxyrequired = True
			return True
		except Exception as e:
			log('ERROR', self.name, '%s : %s' % (self.base_link, e))
			return False
		
	def testParser(self):
		print " -- testParser start --"
		try:
			getmovieurl = self.get_movie(title=testparams.movie, year=testparams.movieYear, imdb=testparams.movieIMDb)
			movielinks = self.get_sources(url=getmovieurl, testing=True)
			print movielinks
			print " -- testParser end --"
		
			if movielinks != None and len(movielinks) > 0:
				return True
			else:
				return False
		except Exception as e:
			print " -- testParser end with error --"
			print ('ERROR', self.name, '%s : %s' % (self.base_link, e))
			return False

	def get_movie(self,imdb, title, year, proxy_options=None, key=None):
		try:
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except:
			return


	def get_show(self, imdb, tvdb, tvshowtitle, year, proxy_options=None, key=None):
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
			
			if self.testparser == False:
				return sources

			if url == None: return sources
			
			data = urlparse.parse_qs(url)
			data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			
			if 'episode' in data and 'season' in data:
				url = (data['title'].translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower() + "/s%s/e%s" % (data['season'],data['episode'])
			else:
				url = (data['title'].translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower()
				
			#print url
			
			url = urlparse.urljoin(self.base_link, self.watch_link % url)
			
			#print url

			r = proxies.request(url, output='geturl', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			
			#print r
			
			if r == None:
				if 'episode' in data and 'season' in data:
					url = (data['title'].split(':')[0].translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower() + "/s%s/e%s" % (data['season'],data['episode'])
				else:
					url = (data['title'].split(':')[0].translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower()
					
				#print url
				
				url = urlparse.urljoin(self.base_link, self.watch_link % url)
				
				#print url

				r = proxies.request(url, output='geturl', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
				
				#print r
			
			if r == None: raise Exception()

			r = result = proxies.request(url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			#print "resp ===== %s" % r
			
			if r == None or '404 Not Found' in r and ':' in data['title'] and 'episode' not in data and 'season' not in data:
				#print "Trying cyro.se --- 2nd attempt"
				title = data['title']
				title = title.split(':')
				title = title[0]
				url = (title.translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower()
				
				url = urlparse.urljoin(self.base_link, self.watch_link % url)

				r = proxies.request(url, output='geturl', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
				
				r = result = proxies.request(url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			
			quality = '720p'

			try:
				r = re.sub(r'[^\x00-\x7F]+',' ', r)

				if 'episode' not in data or 'season' not in data:
					y = re.findall('Date\s*:\s*.+?>.+?(\d{4})', r)
					y = y[0] if len(y) > 0 else None

					if not (data['imdb'] in r or 'year' in data and data['year'] == y): raise Exception()

				q = client.parseDOM(r, 'title')
				q = q[0] if len(q) > 0 else None

				quality = '1080p' if ' 1080' in q else '720p'

				r = client.parseDOM(r, 'div', attrs = {'id': '5throw'})[0]
				r = client.parseDOM(r, 'a', ret='href', attrs = {'rel': 'nofollow'})
			except Exception as e:
				control.log('ERROR %s get_sources1 > %s' % (self.name, e.args))
				r = []

			links = []

			# for url in r:
				# try:
					# url = resolvers.request(url)
					# if url == None: raise Exception()
					# print url
					# links = resolvers.createMeta(url, self.name, self.logo, quality, links, key)
				# except Exception as e:
					# control.log('ERROR %s get_sources2 > %s' % (self.name, e.args))

			try:
				r = client.parseDOM(result, 'iframe', ret='src')
				r = [i for i in r if 'g2g' in i][0]
				#print r
				for i in range(0, 4):
					try:
						if 'http' not in r and self.urlhost in r:
							r = 'http:' + r
						elif 'http' not in r:
							r = self.base_link + r
						#print r
						r = proxies.request(r, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
						r = re.sub(r'[^\x00-\x7F]+',' ', r)
						r = client.parseDOM(r, 'iframe', ret='src')[0]
						
						if 'google' in r: break
					except:
						break

				if not 'google' in r: raise Exception()

				#print r
				links = resolvers.createMeta(r, self.name, self.logo, quality, links, key)
			except Exception as e:
				control.log('ERROR %s get_sources3 > %s' % (self.name, e.args))

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

def log(type, name, msg):
	control.log('%s: %s %s' % (type, name, msg))

