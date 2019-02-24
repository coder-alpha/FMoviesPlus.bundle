#!/usr/bin/python
# -*- coding: utf-8 -*-

#########################################################################################################
#
# Flixanity
#
# Coder Alpha
# https://github.com/coder-alpha
#

'''
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
#########################################################################################################

import time, sys, os, json, re, base64,urlparse,urllib,urllib2,string,random,hashlib

from resources.lib.libraries import cleantitle, dom_parser2, client, testparams, control
from resources.lib import resolvers, proxies

BASE_URL = 'https://flixanity.site'
API_BASE_URL = 'https://api.flixanity.site'
SOURCES_URL = '/ajax/gonlflhyad.php'
EMBED_URL = '/ajax/jne.php'
SEARCH_URL = '/api/v1/cautare/upd'
KEY = 'MEE2cnUzNXl5aTV5bjRUSFlwSnF5MFg4MnRFOTVidA=='

name = 'FliXanity'
loggertxt = []

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.2'
		self.update_date = 'Fab. 07, 2019'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.priority = 1
		self.disabled = False
		self.language = ['en']
		self.type_filter = ['movie', 'show', 'anime']
		self.domains = ['flixanity.site']
		self.base_link_alts = [BASE_URL]
		self.base_link = self.base_link_alts[0]
		self.MainPageValidatingContent = 'FliXanity - Watch Movies & TV Shows Online'
		self.name = name
		self.loggertxt = []
		self.ssl = False
		self.logo = 'https://i.imgur.com/nLeucTN.png'
		self.headers = {}
		self.speedtest = 0
		if len(proxies.sourceProxies)==0:
			proxies.init()
		self.proxyrequired = False
		self.msg = ''
		self.flix = Flixanity()
		if self.flix.core_initialized == True:
			self.siteonline = self.testSite()
			self.testparser = 'Unknown'
			self.testparser = self.testParser()
		else:
			self.siteonline = False
			self.testparser = False
		self.firstRunDisabled = True
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
			
			res = self.flix.search(video_type='MOVIE', title=title, year=year)
			if len(res) > 0:
				return res[0]['url']
			else:
				log('FAIL', 'get_movie','%s: %s' % (title, 'No results found !'), dolog=self.init)
				
		except Exception as e: 
			log('ERROR', 'get_movie','%s: %s' % (title,e), dolog=self.init)
			return
		
	def get_show(self, tvshowtitle, season, imdb=None, tvdb=None, year=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_show','Provider Disabled by User')
				return None
				
			res = self.flix.search(video_type='TV SHOW', title=tvshowtitle, year=year, season=season)
			if len(res) > 0:
				return res[0]['url']
			else:
				log('FAIL', 'get_show','%s: %s' % (tvshowtitle, 'No results found !'), dolog=self.init)

		except Exception as e:
			log('ERROR', 'get_show','%s: %s' % (tvshowtitle,e), dolog=self.init)
			return


	def get_episode(self, url, episode, imdb=None, tvdb=None, title=None, year=None, season=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				return None
				
			if url == None:
				return None
				
			return url + str(episode)
			
		except Exception as e:
			log('ERROR', 'get_episode','%s: %s' % (title,e), dolog=self.init)
			return


	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):
		try:
			sources = []
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_sources','Provider Disabled by User')
				log('INFO', 'get_sources', 'Completed')
				return sources
			if url == None: 
				log('FAIL','get_sources','url == None. Could not find a matching title: %s' % cleantitle.title_from_key(key), dolog=not testing)
				log('INFO', 'get_sources', 'Completed')
				return sources

			links_m = []
			data = self.flix.get_sources(url)
			for d in data:
				vidurl = d['url']
				quality = d['quality']
				poster = d['poster']
				headers = {'Referer':url}
				try:
					links_m = resolvers.createMeta(vidurl, self.name, self.logo, quality, links_m, key, poster=poster, testing=testing, headers=headers)
					
					if testing == True:
						break
				except Exception as e:
					log('ERROR', 'get_sources-0', '%s' % e, dolog=not testing)	
					
			for i in links_m: sources.append(i)
			
			if len(sources) == 0:
				log('FAIL','get_sources','Could not find a matching title: %s' % cleantitle.title_from_key(key))
			else:
				log('SUCCESS', 'get_sources','%s sources : %s' % (cleantitle.title_from_key(key), len(sources)))
				
			log('INFO', 'get_sources', 'Completed')
			
			return sources
		except Exception as e:
			log('ERROR', 'get_sources', '%s' % e)
			log('INFO', 'get_sources', 'Completed')
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

class Flixanity():
	base_url = BASE_URL
	__token = None
	__t = None

	def __init__(self, timeout=10):
		self.timeout = timeout
		self.base_url = BASE_URL
		self.search_url = None
		self.s = None
		self.u = None
		self.username = None
		self.password = None
		self.modes = ['trial','full']
		self.mode = self.modes[0]
		self.results = 0
		self.max_results = 3
		self.cookie = None
		self.core_initialized = False
		html = client.request(self.base_url)
		if html == None:
			log(type='ERROR', method='init', err='- FliXanity Core NOT Initialized -')
		else:
			self.core_initialized = True
			log(type='INFO', method='init', err='- FliXanity Core Initialized -')
		flix_up = control.setting('control_flixanity_user_pass')
		if flix_up != None:
			try:
				self.username = flix_up.split(':')[0]
				self.password = flix_up.split(':')[1]
			except:
				log(type='ERROR', method='Login', err='FliXanity User:Pass not set or not in correct format of User:Pass')

	def get_sources(self, page_url):
	
		try:
			sources = []
			
			html = client.request(page_url)
			
			action = 'getEpisodeEmb' if '/episode/' in page_url else 'getMovieEmb'
			
			match = re.search('elid\s*=\s*"([^"]+)', html)
			if self.__token is None:
				self.__get_token()
				
			if match and self.__token is not None:
				elid = urllib.quote(base64.encodestring(str(int(time.time()))).strip())
				data = {'action': action, 'idEl': match.group(1), 'token': self.__token, 'elid': elid, 'nopop':''}
				ajax_url = urlparse.urljoin(self.base_url, SOURCES_URL)
				headers = {'authorization': 'Bearer %s' % (self.__get_bearer()), 'Referer': page_url, 'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
				#headers.update(XHR)
				
				try:
					poster = client.parseDOM(html, 'div', attrs = {'class': 'poster'})[0]
					poster = client.parseDOM(poster, 'img', ret='data-src')[0]
				except:
					poster = None

				data = client.encodePostData(data)
				html = client.request(ajax_url, post=data, cookie=self.cookie, headers=headers)
				html = html.replace('\\"', '"').replace('\\/', '/')
				rep_txt = re.findall(r'<iframe(.*?)</iframe>', html, re.IGNORECASE)
				for rep in rep_txt:
					html = html.replace(rep, rep.replace('"','\''))
					
				if html == None or len(html) == 0:
					raise Exception('HTML data not found on %s' % ajax_url)

				json_html = json.loads(html)
				
				for k in json_html.keys():
					html = json_html[k]['embed']
					quality, t = cleantitle.getQuality2(json_html[k]['type'].replace('fbcdn','').replace('-','').strip())
					pattern = '<iframe\s+src=\'([^\']+)'
					for match in re.finditer(pattern, html, re.DOTALL | re.I):
						url = match.group(1)
						host = client.geturlhost(url)
						
						direct = True
						
						if host == 'gvideo':
							direct = True
							quality = client.googletag(url)
						else:
							if 'vk.com' in url and url.endswith('oid='): continue  # skip bad vk.com links
							direct = False
							host = urlparse.urlparse(url).hostname
							
						source = {'multi-part': False, 'url': url, 'host': host, 'quality': quality, 'views': None, 'rating': None, 'direct': direct, 'poster':poster}
						sources.append(source)
		except:
			pass

		return sources

	def search(self, video_type, title, year, season='', episode=''):  # @UnusedVariable
		results = []
		
		#print 'Searching %s > %s' % (video_type, title)
		
		if self.mode == self.modes[0] and self.results >= self.max_results:
			log(type='INFO', method='Search', err='Trial limit reached. Please register with Flixanity and use your User:Pass in Channel settings.')
			return results
		
		self.__get_token()
		
		#print 'Token : %s' % self.__token
		
		if self.__token is None: return results
		
		title = title.lower()
		
		if self.search_url == None:
			search_url, u = self.__get_search_url()
			search_url = urlparse.urljoin(API_BASE_URL, search_url)
			s = self.__get_s()
			
			self.search_url = search_url
			self.u = u
			self.s = s
		else:
			search_url = self.search_url
			s = self.s
			u = self.u
			
		#print 'Search URL: %s' % search_url
			
		timestamp = int(time.time() * 1000)
		
		query = {'q': title, 'limit': '100', 'timestamp': timestamp, 'verifiedCheck': self.__token, 'set': s, 'rt': self.__get_rt(self.__token + s), 'sl': self.__get_sl(u)}

		headers = {'Referer': self.base_url}
		html = self._http_get(search_url, data=query, headers=headers, cache_limit=1)
		if video_type == 'TV SHOW':
			media_type = 'TV SHOW'
		else:
			media_type = 'MOVIE'
			
		json_item = json.loads(html)
		
		for item in json_item:
			if not item['meta'].upper().startswith(media_type): continue
			if not title.replace(':','').replace('  ',' ').lower() in item['title'].replace(':','').replace('  ',' ').lower(): continue
			match_year = str(item['year']) if 'year' in item and item['year'] else ''
			if not year or not match_year or year == match_year or (media_type == 'TV SHOW' and (not year or not match_year) and int(year) == int(match_year)+int(season)):
				furl = None
				if media_type == 'TV SHOW':
					furl = '%s/season/%s/episode/%s' % (urlparse.urljoin(self.base_url,item['permalink'].replace('/show/', '/tv-show/')), season, episode)
				else:
					furl = urlparse.urljoin(self.base_url, item['permalink'])
					
				result = {'title': item['title'], 'url': furl, 'year': match_year, 'id':item['_id'], 'type':item['type']}
				
				if furl != None:
					results.append(result)
					
		self.results += 1
		return results

	def _get_episode_url(self, show_url, season, episode):
		episode_pattern = 'href="([^"]+/season/%s/episode/%s/?)"' % (season, episode)
		title_pattern = 'href="(?P<url>[^"]+)"[^>]+title="(?:S\d+\s*E\d+:\s*)?(?P<title>[^"]+)'
		headers = {'Referer': urlparse.urljoin(self.base_url, show_url)}
		season_url = urlparse.urljoin(show_url, '/season/%s' % (season))
		season_url = urlparse.urljoin(self.base_url, season_url)
		html = self._http_get(season_url, headers=headers, cache_limit=2)
		fragment = dom_parser2.parse_dom(html, 'div', {'id': 'episodes'})
		
		return self._default_get_episode_url(fragment, video, episode_pattern, title_pattern)

	def _http_get(self, url, data=None, headers=None, XHR=False, method=None, cache_limit=8):
		
		if data != None:
			data = client.encodePostData(data)
			
		html = client.request(url, post=data, headers=headers, XHR=XHR)
		
		if html == None:
			return

		if '<span>Log In</span>' not in html:
			log(type='INFO', method='Login', err='Logging in for url (%s)' % (url))
			self.__login()
			html = client.request(url, post=data, headers=headers, XHR=XHR)

		self.__get_token(html)
		return html

	def __login(self):
		flix_up = control.setting('control_flixanity_user_pass')
		if flix_up != None:
			try:
				self.username = flix_up.split(':')[0]
				self.password = flix_up.split(':')[1]
			except:
				log(type='ERROR', method='Login', err='FliXanity User:Pass not set or not in correct format of User:Pass')
		
		# return all uncached blank pages if no user or pass
		if not self.username or not self.password:
			log(type='FAIL', method='Login', err='FliXanity Login Failed - No User:Pass set')
			return ''

		if (self.username+':'+self.password) == base64.b64decode(base64.b64decode(control.flix_up)):
			self.mode = self.modes[0]
		else:
			self.mode = self.modes[1]
		
		url = urlparse.urljoin(self.base_url, '/ajax/login.php')
		self.__get_token()
		if self.__token == None:
			log(type='FAIL', method='Login', err='FliXanity Login Failed - Could not get token')
			raise Exception('FliXanity Login Failed')
			
		data = {'username': self.username, 'password': self.password, 'action': 'login', 'token': self.__token, 't': ''}
		data = client.encodePostData(data)
		html = client.request(url, post=data, XHR=True)
		if html != '0':
			log(type='FAIL', method='Login', err='FliXanity Login Failed')
			raise Exception('FliXanity Login Failed')
		log(type='INFO', method='Login', err='FliXanity Login Done for User: %s' % self.username)
		r = client.request(self.base_url, post=data, XHR=True, output='extended')
		self.cookie = r[3] ; headers = r[1] ; html = r[0]

	def __get_bearer(self):
		if self.cookie == None:
			return
		cj = self.cookie
		cj = self.cookie.split(';')
		for cookie in cj:
			if '__utmx' in cookie:
				b = cookie.split('=')[1]
				return b
		return
	
	def __get_search_url(self):
		search_url = SEARCH_URL
		u = search_url[-10:]
		html = self._http_get(self.base_url, cache_limit=24)
		for attrs, _content in dom_parser2.parse_dom(html, 'script', {'type': 'text/javascript'}, req='src'):
			script = attrs['src']
			if 'flixanity' not in script: continue
			html = self._http_get(script, cache_limit=24)
			if 'autocomplete' not in html: continue
			
			r = re.search('r\s*=\s*"([^"]+)', html)
			n = re.search('n\s*=\s*"([^"]+)', html)
			u = re.search('u\s*=\s*"([^"]+)', html)
			if r and n and u:
				u = u.group(1)
				search_url = r.group(1) + n.group(1)[8:16] + u
				break
		return search_url, u
		
	def __get_token(self, html=''):
		flix_up = control.setting('control_flixanity_user_pass')
		if flix_up != None:
			try:
				self.username = flix_up.split(':')[0]
				self.password = flix_up.split(':')[1]
			except:
				log(type='ERROR', method='Login', err='FliXanity User:Pass not set or not in correct format of User:Pass')
		if self.username and self.password and self.__token is None:
			if not html:
				html = self._http_get(self.base_url, cache_limit=8)
				
			match = re.search("var\s+tok\s*=\s*'([^']+)", html)
			if match:
				self.__token = match.group(1)
			else:
				log(type='FAIL', method='Login', err='Unable to locate FliXanity token')
	
	def __get_s(self):
		return ''.join([random.choice(string.ascii_letters) for _ in xrange(25)])
	
	def __get_rt(self, s, shift=13):
		s2 = ''
		for c in s:
			limit = 122 if c in string.ascii_lowercase else 90
			new_code = ord(c) + shift
			if new_code > limit:
				new_code -= 26
			s2 += chr(new_code)
		return s2

	def __get_sl(self, url):
		u = url.split('/')[-1]
		return hashlib.md5(KEY + u).hexdigest()
		
def test():
	flix = Flixanity()
	results = []
	res = flix.search(video_type='MOVIE', title='Deadpool 2', year='2018')
	results.append(res)
	res = flix.search(video_type='TV SHOW', title='Young Sheldon', year='2017', season='1', episode='1')
	results.append(res)
	
	for rx in results:
		for r in rx:
			print 'Accessing: %s' % r['url']
			data = flix.get_sources(r['url'])
			for d in data:
				print 'Data: %s' % d
