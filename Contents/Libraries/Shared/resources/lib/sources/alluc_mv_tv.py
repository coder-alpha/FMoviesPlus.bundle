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

name = 'ALL-UC'
loggertxt = []

USE_GDRIVE_SPECIFIC_SEARCH = False
USE_OPENLOAD_SPECIFIC_SEARCH = True

class source:
	def __init__(self):
		del loggertxt[:]
		log(type='INFO', method='init', err=' -- Initializing %s Start --' % name)
		self.domains = ['alluc.ee','alluc.com']
		self.base_link = 'https://www.alluc.ee'
		self.moviesearch_link = ''
		self.MainPageValidatingContent = 'Video Link Search Engine - Alluc'
		self.type_filter = ['movie', 'show','anime']
		self.ssl = False
		self.disabled = False
		self.name = name
		self.loggertxt = []
		self.logo = 'https://www.alluc.ee/img/alluc_plus_logo.png'
		self.speedtest = 0
		if len(proxies.sourceProxies)==0:
			proxies.init()
		self.proxyrequired = False
		self.siteonline = self.testSite()
		self.testparser = 'Unknown'
		self.testparser = self.testParser()
		self.msg = ''
		log(type='INFO', method='init', err=' -- Initializing %s End --' % name)
		
	def info(self):
		return {
			'url': self.base_link,
			'name': self.name,
			'msg' : self.msg,
			'speed': round(self.speedtest,3),
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
		try:
			x1 = time.time()
			http_res, content = proxies.request(url=self.base_link, output='response', use_web_proxy=False)
			self.speedtest = time.time() - x1
			if content != None and content.find(self.MainPageValidatingContent) >-1:
				log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,self.base_link))
				return True
			else:
				log('ERROR', 'testSite', 'HTTP Resp : %s for %s' % (http_res,self.base_link))
				x1 = time.time()
				http_res, content = proxies.request(url=self.base_link, output='response', use_web_proxy=True)
				self.speedtest = time.time() - x1
				if content != None and content.find(self.MainPageValidatingContent) >-1:
					self.proxyrequired = True
					log('SUCCESS', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,self.base_link))
					return True
				else:
					time.sleep(2.0)
					x1 = time.time()
					http_res, content = proxies.request(url=self.base_link, output='response', use_web_proxy=True)
					self.speedtest = time.time() - x1
					if content != None and content.find(self.MainPageValidatingContent) >-1:
						self.proxyrequired = True
						log('SUCCESS', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,self.base_link))
						return True

			log('ERROR', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,self.base_link))
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
					log('SUCCESS', 'testParser', 'links : %s' % len(movielinks))
					return True
				
			log('ERROR', 'testParser', 'movielinks : %s' % len(movielinks))
			return False
		except Exception as e:
			log('ERROR', 'testParser', '%s' % e)
			return False


	def get_movie(self, imdb, title, year, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('Provider Disabled by User')
				return None
			stream_url = []
			
			if control.setting('control_all_uc_api_key'):
				if control.setting('realdebrid_token') or control.setting('premiumize_user'):
					self.moviesearch_link = '/api/search/download?user=%s&password=%s&query=%s+%s'
				else:
					self.moviesearch_link = '/api/search/stream/?apikey=%s&query=%s+%s'
				
				url = self.moviesearch_link % (control.setting('control_all_uc_api_key'),cleantitle.geturl(title), year)
				r = urlparse.urljoin(self.base_link, url)
				xr = r + "+%23newlinks"
				rr = proxies.request(xr, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
				r1 = json.loads(rr)
				#print r1
				
				for item in r1['result']:
					if len(item['hosterurls']) == 1:
						lang = item['lang'].encode('utf-8')
						tmp = item['hosterurls'][0]['url']
						tmp = client.replaceHTMLCodes(tmp)
						tmp = tmp.encode('utf-8')
						title = item['title'].encode('utf-8')
						stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': title, 'lang':lang})
						
				if USE_GDRIVE_SPECIFIC_SEARCH == True:
					r = xr + "&host%3Adrive.google.com"
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
						
				if USE_OPENLOAD_SPECIFIC_SEARCH == True:
					r = xr + "&host%3Aopenload.co"
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
			log('ERROR', 'get_movie','%s: %s' % (title,e))
			return

	def get_show(self, imdb, tvdb, tvshowtitle, year, season, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('Provider Disabled by User')
				return None
			url = '%s (%s)' % (tvshowtitle, year)
			url = client.replaceHTMLCodes(url)
			url = url.encode('utf-8')
			return url
		except Exception as e: 
			log('ERROR', 'get_show','%s: %s' % (tvshowtitle,e))
			return


	def get_episode(self, url, imdb, tvdb, title, date, season, episode, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				return None
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
			xr = r + "+%23newlinks"
			#r = requests.get(r).json()
			rr = proxies.request(xr, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
			rr = json.loads(rr)

			for item in rr['result']:   
				if len(item['hosterurls']) == 1:
					lang = item['lang'].encode('utf-8')
					tmp = item['hosterurls'][0]['url']
					tmp = client.replaceHTMLCodes(tmp)
					tmp = tmp.encode('utf-8')
					title = item['title'].encode('utf-8')
					stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': title, 'lang':lang})
			
			if USE_GDRIVE_SPECIFIC_SEARCH == True:
				r = xr + "&host%3Adrive.google.com"
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
					
			if USE_OPENLOAD_SPECIFIC_SEARCH == True:
				r = xr + "&host%3Aopenload.co"
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
			log('ERROR', 'get_episode','%s: %s' % (title,e))
			return

	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):
		try:
			sources = []
			if url == None: return sources
			
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
							sources = resolvers.createMeta(link['url'], self.name, self.logo, quality, sources, key, lang=link['lang'], testing=testing)

			log('SUCCESS', 'get_sources','links : %s' % len(sources), dolog=False)
			return sources
		except Exception as e:
			log('ERROR', 'get_sources','%s' % e, dolog=False)
			return sources

	def resolve(self, url):
		control.log('>>>>>>>>>>>>>>>>>> Resolve ALLUC %s' % url)
		return resolvers.request(url)
		
def log(type='INFO', method='undefined', err='', dolog=True, logToControl=False, doPrint=True):
		msg = '%s: %s > %s > %s : %s' % (time.ctime(time.time()), type, name, method, err)
		if dolog == True:
			loggertxt.append(msg)
		if logToControl == True:
			control.log(msg)
		if doPrint == True:
			print msg