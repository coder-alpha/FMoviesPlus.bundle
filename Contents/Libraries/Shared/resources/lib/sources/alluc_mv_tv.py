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
import re,urllib,urlparse,json,time
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import testparams
from resources.lib.libraries import control
from resources.lib import resolvers
from resources.lib import proxies


class source:
	def __init__(self):
		print " -- Initializing AllUc Start --"
		self.domains = ['alluc.ee','alluc.com']
		self.base_link = 'https://www.alluc.ee'
		self.moviesearch_link = ''
		self.MainPageValidatingContent = 'Video Link Search Engine - Alluc'
		self.type_filter = ['movie', 'show','anime']
		self.ssl = False
		self.name = 'ALL-UC'
		self.loggertxt = []
		self.logo = 'https://www.alluc.ee/img/alluc_plus_logo.png'
		self.speedtest = 0
		if len(proxies.sourceProxies)==0:
			proxies.init()
		self.proxyrequired = False
		self.siteonline = self.testSite()
		self.testparser = 'Unknown'
		self.testparser = self.testParser()
		print " -- Initializing AllUc End --"
		
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


	def get_movie(self, imdb, title, year, proxy_options=None, key=None, testing=False):
		try:
			stream_url = []
			if control.setting('control_all_uc_api_key'):
				if control.setting('realdebrid_token') or control.setting('premiumize_user'):
					self.moviesearch_link = '/api/search/download?user=%s&password=%s&query=%s+%s'
				else:
					self.moviesearch_link = '/api/search/stream/?apikey=%s&query=%s+%s'
				
				url = self.moviesearch_link % (control.setting('control_all_uc_api_key'),cleantitle.geturl(title), year)
				r = urlparse.urljoin(self.base_link, url)
				r = r + "+%23newlinks"
				rr = proxies.request(r, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
				r1 = json.loads(rr)

				for item in r1['result']:
					if len(item['hosterurls']) == 1:
						lang = item['lang'].encode('utf-8')
						tmp = item['hosterurls'][0]['url']
						tmp = client.replaceHTMLCodes(tmp)
						tmp = tmp.encode('utf-8')
						title = item['title'].encode('utf-8')
						stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': title, 'lang':lang})
						
				r = r + "&host%3Agoogle.com"
				rr = proxies.request(r, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
				r1 = json.loads(rr)

				for item in r1['result']:
					if len(item['hosterurls']) == 1:
						lang = item['lang'].encode('utf-8')
						tmp = item['hosterurls'][0]['url']
						tmp = client.replaceHTMLCodes(tmp)
						tmp = tmp.encode('utf-8')
						title = item['title'].encode('utf-8')
						stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': title, 'lang':lang})
						
			return stream_url
		except Exception as e: 
			control.log(e)
			return

	def get_show(self, imdb, tvdb, tvshowtitle, year, season, proxy_options=None, key=None):
		try:
			url = '%s (%s)' % (tvshowtitle, year)
			url = client.replaceHTMLCodes(url)
			url = url.encode('utf-8')
			return url
		except:
			return


	def get_episode(self, url, imdb, tvdb, title, date, season, episode, proxy_options=None, key=None):
		try:
			stream_url = []
			if control.setting('control_all_uc_api_key'):
				if control.setting('realdebrid_token') or control.setting('premiumize_user'):
					self.moviesearch_link = '/api/search/download?user=%s&password=%s&query=%s'
				else:
					self.moviesearch_link = '/api/search/stream/?apikey=%s&query=%s'

			tvshowtitle, year = re.compile('(.+?) [(](\d{4})[)]$').findall(url)[0]
			season, episode = season.zfill(2), episode.zfill(2)
			query = '%s s%se%s' % (tvshowtitle, season, episode)
			query = self.moviesearch_link % (control.setting('control_all_uc_api_key'), urllib.quote_plus(query))
			r = urlparse.urljoin(self.base_link, query)
			r = r + "+%23newlinks"
			#r = requests.get(r).json()
			rr = proxies.request(r, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
			rr = json.loads(rr)

			for item in rr['result']:   
				if len(item['hosterurls']) == 1:
					lang = item['lang'].encode('utf-8')
					tmp = item['hosterurls'][0]['url']
					tmp = client.replaceHTMLCodes(tmp)
					tmp = tmp.encode('utf-8')
					title = item['title'].encode('utf-8')
					stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': title, 'lang':lang})
			
			r = r + "&host%3Agoogle.com"
			r = proxies.request(r, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
			r = json.loads(r)

			for item in r['result']:   
				if len(item['hosterurls']) == 1:
					lang = item['lang'].encode('utf-8')
					tmp = item['hosterurls'][0]['url']
					tmp = client.replaceHTMLCodes(tmp)
					tmp = tmp.encode('utf-8')
					title = item['title'].encode('utf-8')
					stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': title, 'lang':lang})
					
			return stream_url
		except Exception as e: 
			control.log('alluc error tv')
			control.log(e)
			return

	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):
		try:
			#sources = []
			links = []

			if url == None: return links
			
			for link in url:
				if re.match('((?!\.part[0-9]).)*$', link['url'], flags=re.IGNORECASE) and '://' in link['url']:
						host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(link['url'].strip().lower()).netloc)[0].split('.')[0]
						scheme = urlparse.urlparse(link['url']).scheme
						#if host in hostDict and scheme:	
						if scheme:
							if '1080' in link["url"] or '1080' in link['url']: 
								quality = "1080p"
							elif '720' in link['title'] or '720' in link['url']: 
								quality = 'HD'
							else:
								quality = 'SD'
							#sources.append({ 'source' : host, 'quality' : quality, 'provider': 'alluc', 'url': link['url'] })
							links = resolvers.createMeta(link['url'], self.name, self.logo, quality, links, key, lang=link['lang'])
							if testing and len(links) > 0:
								break
			#return sources
			return links
		except Exception as e:
			control.log('ERROR ALLUC %s' % e)
			return links

	def resolve(self, url):
		control.log('>>>>>>>>>>>>>>>>>> Resolve ALLUC %s' % url)
		return resolvers.request(url)
		
def logger(msg):
	control.log(msg)