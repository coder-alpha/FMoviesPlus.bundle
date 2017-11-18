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

USE_ALL_HOST_SEARCH = True
USE_MEGA_SPECIFIC_SEARCH = True
USE_OPENLOAD_SPECIFIC_SEARCH = True
USE_GDRIVE_SPECIFIC_SEARCH = False

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'Nov. 14, 2017'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.count = 2
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
		self.msg = ''
		self.error = ''
		self.testparser = 'Unknown'
		self.fetchedtoday = 0
		self.siteonline = self.testSite()
		self.testparser = self.testParser()
		self.init = True
		if control.setting('control_all_uc_api_key') == control.base64.b64decode(control.base64.b64decode(control.all_uc_api)):
			log(type='INFO', method='init', err='Using Plugin (Non-User) Set API Key - Count is set at 2')
			self.count = 2
		else:
			log(type='INFO', method='init', err='Using User Set API Key - Count is set at 10')
			self.count = 10
		log(type='INFO', method='init', err=' -- Initializing %s %s %s End --' % (name, self.ver, self.update_date))
		
	def info(self):
		msg = self.error
		if self.fetchedtoday > 0:
			msg = '%sFetched today: %s' % (msg, str(self.fetchedtoday))
		return {
			'url': self.base_link,
			'name': self.name,
			'msg' : msg,
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
				log('FAIL', 'testSite', 'Validation content Not Found. HTTP Resp : %s for %s' % (http_res,self.base_link))
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
					else:
						log('FAIL', 'testSite', 'Validation content Not Found. HTTP Resp : %s via proxy for %s' % (http_res,self.base_link))
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
					
			if self.error != '':
				log('ERROR', 'testParser', 'Parser NOT working. %s' % self.error)
			else:
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
			stream_url = []
			
			if control.setting('control_all_uc_api_key'):
				if control.setting('realdebrid_token') or control.setting('premiumize_user'):
					self.moviesearch_link = '/api/search/download?user=%s&password=%s&query=%s+%s&count=%s'
				else:
					self.moviesearch_link = '/api/search/stream/?apikey=%s&query=%s+%s&count=%s'
				
				url = self.moviesearch_link % (control.setting('control_all_uc_api_key'),cleantitle.geturl(title), year, str(self.count))
				r = urlparse.urljoin(self.base_link, url)
				xr = r + "+%23newlinks"
				
				if USE_ALL_HOST_SEARCH == True:
					rc, rr = proxies.request(xr, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True, output='response')
					r1 = json.loads(rr)
					self.fetchedtoday = r1['fetchedtoday']
					if r1['status'] != 'success' and str(rc) not in client.HTTP_GOOD_RESP_CODES:
						self.error = '%s ' % r1['message']
						raise Exception(self.error)
					
					for item in r1['result']:
						if len(item['hosterurls']) == 1:
							src = item['sourcename'].encode('utf-8')
							ext = item['extension'].encode('utf-8')
							lang = item['lang'].encode('utf-8')
							tmp = item['hosterurls'][0]['url']
							tmp = client.replaceHTMLCodes(tmp)
							tmp = tmp.encode('utf-8')
							if ext == '':
								tmp_e = tmp.split('.')
								ext = tmp_e[len(tmp_e)-1]
							xtitle = item['title'].encode('utf-8')
							stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': xtitle, 'lang':lang, 'src':src, 'ext':ext})
						
				if USE_GDRIVE_SPECIFIC_SEARCH == True and self.init == True and control.setting('Host-gvideo') != False:
					r = xr + "+host%3Adrive.google.com"
					rc, rr = proxies.request(r, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True, output='response')
					r1 = json.loads(rr)
					self.fetchedtoday = r1['fetchedtoday']
					if r1['status'] != 'success' and str(rc) not in client.HTTP_GOOD_RESP_CODES:
						self.error = '%s ' % r1['message']
						raise Exception(self.error)
					
					for item in r1['result']:
						if len(item['hosterurls']) == 1:
							src = item['sourcename'].encode('utf-8')
							ext = item['extension'].encode('utf-8')
							lang = item['lang'].encode('utf-8')
							tmp = item['hosterurls'][0]['url']
							tmp = client.replaceHTMLCodes(tmp)
							tmp = tmp.encode('utf-8')
							if ext == '':
								tmp_e = tmp.split('.')
								ext = tmp_e[len(tmp_e)-1]
							xtitle = item['title'].encode('utf-8')
							stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': xtitle, 'lang':lang, 'src':src, 'ext':ext})
									
				if USE_OPENLOAD_SPECIFIC_SEARCH == True and self.init == True and control.setting('Host-openload') != False:
					r = xr + "+host%3Aopenload.co"
					rc, rr = proxies.request(r, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True, output='response')
					r1 = json.loads(rr)
					self.fetchedtoday = r1['fetchedtoday']
					if r1['status'] != 'success' and str(rc) not in client.HTTP_GOOD_RESP_CODES:
						self.error = '%s ' % r1['message']
						raise Exception(self.error)

					for item in r1['result']:
						if len(item['hosterurls']) == 1:
							src = item['sourcename'].encode('utf-8')
							ext = item['extension'].encode('utf-8')
							lang = item['lang'].encode('utf-8')
							tmp = item['hosterurls'][0]['url']
							tmp = client.replaceHTMLCodes(tmp)
							tmp = tmp.encode('utf-8')
							if ext == '':
								tmp_e = tmp.split('.')
								ext = tmp_e[len(tmp_e)-1]
							xtitle = item['title'].encode('utf-8')
							stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': xtitle, 'lang':lang, 'src':src, 'ext':ext})
							
				if USE_MEGA_SPECIFIC_SEARCH == True and self.init == True and control.setting('Host-mega') != False:
					self.moviesearch_link = '/api/search/download?apikey=%s&query=%s+%s&count=%s'
					url = self.moviesearch_link % (control.setting('control_all_uc_api_key'),cleantitle.geturl(title), year, str(self.count))
					r = urlparse.urljoin(self.base_link, url)
					r = r + "+host%3Amega.nz"
					r = r + "+%23newlinks"
					rc, rr = proxies.request(r, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True, output='response')
					r1 = json.loads(rr)
					self.fetchedtoday = r1['fetchedtoday']
					if r1['status'] != 'success' and str(rc) not in client.HTTP_GOOD_RESP_CODES:
						self.error = '%s ' % r1['message']
						raise Exception(self.error)

					for item in r1['result']:
						if len(item['hosterurls']) == 1:
							src = item['sourcename'].encode('utf-8')
							ext = item['extension'].encode('utf-8')
							lang = item['lang'].encode('utf-8')
							tmp = item['hosterurls'][0]['url']
							tmp = client.replaceHTMLCodes(tmp)
							tmp = tmp.encode('utf-8')
							if ext == '':
								tmp_e = tmp.split('.')
								ext = tmp_e[len(tmp_e)-1]
							xtitle = item['title'].encode('utf-8')
							stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': xtitle, 'lang':lang, 'src':src, 'ext':ext})
						
			return stream_url
		except Exception as e: 
			log('ERROR', 'get_movie','%s: %s' % (title,e), dolog=self.init)
			return

	def get_show(self, imdb=None, tvdb=None, tvshowtitle=None, year=None, season=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_show','Provider Disabled by User')
				return None
			url = '%s (%s)' % (tvshowtitle, year)
			url = client.replaceHTMLCodes(url)
			url = url.encode('utf-8')
			return url
		except Exception as e: 
			log('ERROR', 'get_show','%s: %s' % (tvshowtitle,e), dolog=self.init)
			return


	def get_episode(self, url=None, imdb=None, tvdb=None, title=None, year=None, season=None, episode=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				return None
			stream_url = []
			if control.setting('control_all_uc_api_key'):
				if control.setting('realdebrid_token') or control.setting('premiumize_user'):
					self.moviesearch_link = '/api/search/download?user=%s&password=%s&query=%s&count=%s'
				else:
					self.moviesearch_link = '/api/search/stream/?apikey=%s&query=%s&count=%s'

			tvshowtitle, year = re.compile('(.+?) [(](\d{4})[)]$').findall(url)[0]
			season = str(season)
			episode = str(episode)
			season, episode = season.zfill(2), episode.zfill(2)
			query = '%s s%se%s' % (tvshowtitle, season, episode)
			query = self.moviesearch_link % (control.setting('control_all_uc_api_key'), urllib.quote_plus(query), str(self.count))
			r = urlparse.urljoin(self.base_link, query)
			xr = r + "+%23newlinks"
			#r = requests.get(r).json()
			
			if USE_ALL_HOST_SEARCH == True:
				rc, rr = proxies.request(xr, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True, output='response')
				rr = json.loads(rr)
				self.fetchedtoday = rr['fetchedtoday']
				if rr['status'] != 'success' and str(rc) not in client.HTTP_GOOD_RESP_CODES:
					self.error = '%s ' % rr['message']
					raise Exception(self.error)
				
				for item in rr['result']:   
					if len(item['hosterurls']) == 1:
						src = item['sourcename'].encode('utf-8')
						ext = item['extension'].encode('utf-8')
						lang = item['lang'].encode('utf-8')
						tmp = item['hosterurls'][0]['url']
						tmp = client.replaceHTMLCodes(tmp)
						tmp = tmp.encode('utf-8')
						if ext == '':
							tmp_e = tmp.split('.')
							ext = tmp_e[len(tmp_e)-1]
						xtitle = item['title'].encode('utf-8')
						stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': xtitle, 'lang':lang, 'src':src, 'ext':ext})
			
			if USE_GDRIVE_SPECIFIC_SEARCH == True and self.init == True and control.setting('Host-gvideo') != False:
				r = xr + "+host%3Adrive.google.com"
				rc, rr = proxies.request(r, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True, output='response')
				rr = json.loads(rr)
				self.fetchedtoday = rr['fetchedtoday']
				if rr['status'] != 'success' and str(rc) not in client.HTTP_GOOD_RESP_CODES:
					self.error = '%s ' % rr['message']
					raise Exception(self.error)

				for item in rr['result']:   
					if len(item['hosterurls']) == 1:
						src = item['sourcename'].encode('utf-8')
						ext = item['extension'].encode('utf-8')
						lang = item['lang'].encode('utf-8')
						tmp = item['hosterurls'][0]['url']
						tmp = client.replaceHTMLCodes(tmp)
						tmp = tmp.encode('utf-8')
						if ext == '':
							tmp_e = tmp.split('.')
							ext = tmp_e[len(tmp_e)-1]
						xtitle = item['title'].encode('utf-8')
						stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': xtitle, 'lang':lang, 'src':src, 'ext':ext})
					
			if USE_OPENLOAD_SPECIFIC_SEARCH == True and self.init == True and control.setting('Host-openload') != False:
				r = xr + "+host%3Aopenload.co"
				rc, rr = proxies.request(r, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True, output='response')
				rr = json.loads(rr)
				self.fetchedtoday = rr['fetchedtoday']
				if rr['status'] != 'success' and str(rc) not in client.HTTP_GOOD_RESP_CODES:
					self.error = '%s ' % rr['message']
					raise Exception(self.error)

				for item in rr['result']:   
					if len(item['hosterurls']) == 1:
						src = item['sourcename'].encode('utf-8')
						ext = item['extension'].encode('utf-8')
						lang = item['lang'].encode('utf-8')
						tmp = item['hosterurls'][0]['url']
						tmp = client.replaceHTMLCodes(tmp)
						tmp = tmp.encode('utf-8')
						if ext == '':
							tmp_e = tmp.split('.')
							ext = tmp_e[len(tmp_e)-1]
						xtitle = item['title'].encode('utf-8')
						stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': xtitle, 'lang':lang, 'src':src, 'ext':ext})
						
			if USE_MEGA_SPECIFIC_SEARCH == True and self.init == True and control.setting('Host-mega') != False:
				self.moviesearch_link = '/api/search/download?apikey=%s&query=%s&count=%s'
				query = '%s s%se%s' % (tvshowtitle, season, episode)
				query = self.moviesearch_link % (control.setting('control_all_uc_api_key'), urllib.quote_plus(query), str(self.count))
				r = urlparse.urljoin(self.base_link, query)
				xr = r + "+%23newlinks"
				r = xr + "+host%3Amega.nz"
				rc, rr = proxies.request(r, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True, output='response')
				rr = json.loads(rr)
				self.fetchedtoday = rr['fetchedtoday']
				if rr['status'] != 'success' and str(rc) not in client.HTTP_GOOD_RESP_CODES:
					self.error = '%s ' % rr['message']
					raise Exception(self.error)

				for item in rr['result']:
					if len(item['hosterurls']) == 1:
						src = item['sourcename'].encode('utf-8')
						ext = item['extension'].encode('utf-8')
						lang = item['lang'].encode('utf-8')
						tmp = item['hosterurls'][0]['url']
						tmp = client.replaceHTMLCodes(tmp)
						tmp = tmp.encode('utf-8')
						if ext == '':
							tmp_e = tmp.split('.')
							ext = tmp_e[len(tmp_e)-1]
						xtitle = item['title'].encode('utf-8')
						stream_url.append({'url': tmp, 'hoster': item['hostername'], 'title': xtitle, 'lang':lang, 'src':src, 'ext':ext})
					
			return stream_url
		except Exception as e: 
			log('ERROR', 'get_episode','%s: %s' % (title,e), dolog=self.init)
			return

	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):
		try:
			sources = []
			if url == None: 
				log('FAIL','get_sources','Could not find a matching title: %s' % cleantitle.title_from_key(key), dolog=not testing)
				return sources
			
			processed = []
			for link in url:
				if re.match('((?!\.part[0-9]).)*$', link['url'], flags=re.IGNORECASE) and '://' in link['url'] and link['url'] not in processed:
						host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(link['url'].strip().lower()).netloc)[0].split('.')[0]
						scheme = urlparse.urlparse(link['url']).scheme
						#if host in hostDict and scheme:	
						if scheme:
							if '1080' in link['title'] or '1080' in link['url']: 
								quality = '1080p'
							elif '720' in link['title'] or '720' in link['url']: 
								quality = 'HD'
							else:
								quality = 'SD'
								
							file_ext = '.mp4'
							if len(link['ext']) > 0 and len(link['ext']) < 4 and len(link['src']) > 0:
								txt = '%s (.%s)' % (link['src'],link['ext'])
								file_ext = '.%s' % link['ext']
							elif len(link['ext']) > 0 and len(link['ext']) < 4 and len(link['src']) == 0:
								txt = '%s (.%s)' % (link['src'],link['ext'])
								file_ext = '.%s' % link['ext']
							elif (len(link['ext']) == 0 or len(link['ext']) > 3) and len(link['src']) > 0:
								txt = '%s' % link['src']
							else:
								txt = ''
								
							if 'trailer' in link['title'].lower():
								sources = resolvers.createMeta(link['url'], self.name, self.logo, quality, sources, key, lang=link['lang'], txt=txt, file_ext=file_ext, vidtype='Trailer', testing=testing)
							else:
								sources = resolvers.createMeta(link['url'], self.name, self.logo, quality, sources, key, lang=link['lang'], txt=txt, file_ext=file_ext, testing=testing)
								
							processed.append(link['url'])

			if self.fetchedtoday > 0:
				self.msg = 'Fetched today: %s' % str(self.fetchedtoday)
				log('INFO', 'get_sources', self.msg, dolog=not testing)
				
			if len(sources) == 0:
				log('FAIL','get_sources','Could not find a matching title: %s' % cleantitle.title_from_key(key))
				return sources
			
			log('SUCCESS', 'get_sources','%s sources : %s' % (cleantitle.title_from_key(key), len(sources)), dolog=not testing)
			return sources
		except Exception as e:
			log('ERROR', 'get_sources', '%s' % e, dolog=not testing)
			return sources

	def resolve(self, url):
		control.log('>>>>>>>>>>>>>>>>>> Resolve ALLUC %s' % url)
		return resolvers.request(url)
		
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
