# -*- coding: utf-8 -*-

#########################################################################################################
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

import re,urllib,urlparse,json,hashlib,base64,time

from resources.lib.libraries import client, cleantitle, testparams, control, jsunfuck, source_utils
from resources.lib import resolvers, proxies

CODE = '''def retA():
	class Infix:
		def __init__(self, function):
			self.function = function
		def __ror__(self, other):
			return Infix(lambda x, self=self, other=other: self.function(other, x))
		def __or__(self, other):
			return self.function(other)
		def __rlshift__(self, other):
			return Infix(lambda x, self=self, other=other: self.function(other, x))
		def __rshift__(self, other):
			return self.function(other)
		def __call__(self, value1, value2):
			return self.function(value1, value2)
	def my_add(x, y):
		try: return x + y
		except Exception: return str(x) + str(y)
	x = Infix(my_add)
	return %s
param = retA()'''

name = 'YesMovie'
loggertxt = []

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.1.2'
		self.update_date = 'Feb. 05, 2019'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.base_link_alts = ['https://yesmovies.gg']
		self.base_link = self.base_link_alts[0]
		self.MainPageValidatingContent = 'Yesmovies - Watch FREE Movies Online'
		self.ssl = False
		self.headers = {}
		self.cookie = None
		self.disabled = False
		self.name = name
		self.type_filter = ['movie', 'show', 'anime']
		self.loggertxt = []
		self.logo = 'https://i.imgur.com/jjJJgd6.png'
		self.info_link = '/ajax/movie_info/%s.html'
		self.info_link2 = 'https://api.yesmovies.gg/ajax/movie_load_info/%s/'
		self.episode_link = '/ajax/v4_movie_episodes/%s'
		self.playlist_link = '/ajax/v2_get_sources/%s.html?hash=%s'
		self.server_link = '/ajax/v4_movie_episodes/%s'
		self.embed_link = '/ajax/movie_embed/%s'
		self.token_link = '/ajax/movie_token?eid=%s&mid=%s'
		self.sourcelink = '/ajax/movie_sources/%s?x=%s&y=%s'
		self.api_search = 'https://api.ocloud.stream/movie/search/%s?link_web=%s' #'https://api.yesmovies.gg/movie/search/%s?link_web=%s'
		self.speedtest = 0
		if len(proxies.sourceProxies)==0:
			proxies.init()
		self.proxyrequired = False
		self.msg = ''
		self.siteonline = self.testSite()
		self.testparser = 'Unknown'
		self.testparser = self.testParser()
		self.firstRunDisabled = True
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
		
	def setNewCookies(self, site):
		try:
			ua = client.randomagent()
			self.headers['User-Agent'] = ua
			self.cookie = proxies.request(url=site, headers=self.headers, output='cookie', use_web_proxy=self.proxyrequired)
			if self.cookie == None:
				raise Exception('Retrieved cookie None')
			self.headers['Cookie'] = self.cookie
			log('SUCCESS', 'setNewCookies', 'CF Cookie : %s for %s' % (self.cookie,site))
		except Exception as e:
			log('ERROR','setNewCookies', '%s' % e)
		
	def testSite(self):
		for site in self.base_link_alts:
			try:
				sitex = client.getRedirectingUrl(site, headers=self.headers).strip("/")
				self.setNewCookies(sitex)
				if 'http' not in sitex:
					raise Exception('Error in geturl')
				else:
					site = sitex
			except:
				pass
			self.base_link = site
			bool = self.testSiteAlts()
			if bool == True:
				return bool
				
		self.base_link = self.base_link_alts[0]
		return False
		
	def testSiteAlts(self):
		try:
			x1 = time.time()
			http_res, content = proxies.request(url=self.base_link, headers=self.headers, output='response', use_web_proxy=False)
			print content
			self.speedtest = time.time() - x1
			if content != None and content.find(self.MainPageValidatingContent) >-1:
				log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,self.base_link))
				return True
			else:
				if ('%s' % http_res) == '520':
					log('FAIL', 'testSite', 'Website down ! HTTP Resp : %s for %s' % (http_res,self.base_link))
				else:
					log('FAIL', 'testSite', 'Validation content Not Found. HTTP Resp : %s for %s' % (http_res,self.base_link))
				x1 = time.time()
				http_res, content = proxies.request(url=self.base_link, headers=self.headers, output='response', use_web_proxy=True)
				self.speedtest = time.time() - x1
				if content != None and content.find(self.MainPageValidatingContent) >-1:
					self.proxyrequired = True
					log('SUCCESS', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,self.base_link))
					return True
				else:
					time.sleep(2.0)
					x1 = time.time()
					http_res, content = proxies.request(url=self.base_link, headers=self.headers, output='response', use_web_proxy=True)
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
				
			variations = [title, title.replace('&','and')]
			
			for title in variations:
				try:
					t = cleantitle.get(title)

					q = self.api_search % (urllib.quote_plus(cleantitle.query(title).replace(' ','-')), self.base_link)
					#q = urlparse.urljoin(self.base_link, q)
					#print q
					
					#r = client.request(q, headers=self.headers, IPv4=True)
					r = proxies.request(q, headers=self.headers, IPv4=True, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
					#if not r == None: break

					r = client.parseDOM(r, 'div', attrs = {'class': 'ml-item'})
					#print r
					
					r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title'), client.parseDOM(i, 'a', ret='data-url')) for i in r]
					#print r
					
					r = [(i[0][0], i[1][0], i[2][0]) for i in r if i[0] and i[1] and i[2]]
					#print r

					r = [(i[0],i[2]) for i in r if t == cleantitle.get(i[1])][:2]
					#print r
					#r = [(i, re.findall('(\d+)', i)[-1]) for i in r]

					for i in r:
						try:
							u = i[1]
							url = i[0]
							#print u
							if 'http' not in u:
								u = urlparse.urljoin(self.base_link, u)
							y, q, h = self.ymovies_info(u)
							if 'http' not in h:
								h = urlparse.urljoin(self.base_link, h)
							#print '%s == %s' % (y, year)

							if str(y).strip() != str(year).strip() or h == None:
								raise Exception()
							url = h
							return [url, None]
						except:
							return [url, None]
				except:
					pass
		except Exception as e: 
			log('ERROR', 'get_movie','%s: %s' % (title,e), dolog=self.init)
			return

	def get_show(self, imdb=None, tvdb=None, tvshowtitle=None, year=None, season=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_show','Provider Disabled by User')
				return None
			url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
			url = urllib.urlencode(url)
			return url
		except Exception as e: 
			log('ERROR', 'get_show','%s: %s' % (tvshowtitle,e), dolog=self.init)
			return

	def get_episode(self, url=None, imdb=None, tvdb=None, title=None, year=None, season=None, episode=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				return None
			if url != None:
				data = urlparse.parse_qs(url)
				data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
			else:
				data = {}
				data['tvshowtitle'] = title
			
			t1 = data['tvshowtitle']
			#t2 = cleantitle.get(data['tvshowtitle'])
			titles = [t1]
			if '\'s' in t1:
				t0 = t1.replace('\'s','')
				titles.append(t0)
				if ' ' in t0:
					t0 = t0.split(' ')
					t0 = t0[0]
					titles.append(t0)
			elif '\'' in t1:
				t0 = t1.replace('\'','')
				titles.append(t0)
				if ' ' in t0:
					t0 = t0.split(' ')
					t0 = t0[0]
					titles.append(t0)
			
			for title in titles:
				#print title
				try:
					season = '%01d' % int(season) ; episode = '%01d' % int(episode)
					#year = re.findall('(\d{4})', date)[0]
					years = [str(year), str(int(year)+1), str(int(year)-1), str(int(year)-int(season)), str(int(year)+int(season))]

					r = self.ymovies_info_season(title, season, proxy_options=proxy_options)
					if r == None or len(r) == 0: raise Exception()
					#print r
					
					r = [(i[0], re.findall('(.+?)\s+(?:-|)\s+season\s+(\d+)$', i[1].lower()), i[2]) for i in r]
					#print r
					
					#r = [(i[0], i[1][0][0], i[1][0][1], i[2]) for i in r if i[1]]
					#print r
					
					for i in r:
						try:
							u = i[2]
							if 'http' not in u:
								u = urlparse.urljoin(self.base_link, u)
							y, q, h = self.ymovies_info(u, proxy_options=proxy_options)
							if 'http' not in h:
								h = urlparse.urljoin(self.base_link, h)
							mychk = False
							years = [str(year),str(int(year) + 1),str(int(year) - 1)]
							for x in years:
								if str(y) == x: mychk = True
							if mychk == False: raise Exception()
							return [h + '?=%s' % episode, episode]
						except:
							pass
							
					# yr variation for shows
					try:
						year = int(year) - int(season)
						for i in r:
							try:
								u = i[2]
								if 'http' not in u:
									u = urlparse.urljoin(self.base_link, u)
								y, q, h = self.ymovies_info(u, proxy_options=proxy_options)
								if 'http' not in h:
									h = urlparse.urljoin(self.base_link, h)
								mychk = False
								years = [str(year),str(int(year) + 1),str(int(year) - 1)]
								for x in years:
									if str(y) == x: mychk = True
								if mychk == False: raise Exception()
								return [h + '?=%s' % episode, episode]
							except:
								pass
					except:
						pass
						
					# yr ignore for shows
					for i in r:
						h = i[0]
						if 'http' not in h:
							h = urlparse.urljoin(self.base_link, h)
						return [h + '?=%s' % episode, episode]
				except:
					pass		
			return
		except Exception as e: 
			log('ERROR', 'get_episode','%s: %s' % (title,e), dolog=self.init)
			return

	def ymovies_info_season(self, title, season, proxy_options=None):
		try:
			qs = []
			q = '%s Season %s' % (cleantitle.query(title), season)
			qs.append(q)
			q = cleantitle.query(title)
			qs.append(q)
			
			#print qs
			for qm in qs:
				try:
					#q = '/movie/search/%s' % (urllib.quote_plus(qm))
					q = self.api_search % (urllib.quote_plus(cleantitle.query(qm).replace(' ','-')), self.base_link)
					#q = urlparse.urljoin(self.base_link, q)
					#print q
					for i in range(3):
						#r = client.request(q, headers=self.headers, IPv4=True)
						r = proxies.request(q, headers=self.headers, IPv4=True, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
						if not r == None: break
					
					r = client.parseDOM(r, 'div', attrs = {'class': 'ml-item'})
					r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title'), client.parseDOM(i, 'a', ret='data-url')) for i in r]
					r = [(i[0][0], i[1][0], i[2][0]) for i in r if i[0] and i[1] and i[2]]
					if not r == None and len(r) > 0: break
				except:
					pass

			return r
		except:
			return

	def ymovies_info(self, url, proxy_options=None):
		try:
			if 'ajax' not in url:
				#r = client.request(url, headers=self.headers, IPv4=True)
				r = proxies.request(url, headers=self.headers, IPv4=True, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
				id = re.findall(r'var id = (.*);',r)[0]
				url = self.info_link2 % id

			#r = client.request('%s?link_web=%s' % (url, self.base_link), headers=self.headers, IPv4=True)
			r = proxies.request('%s?link_web=%s' % (url, self.base_link), headers=self.headers, IPv4=True, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			r = r.replace('\\','')
			#print r
			q = client.parseDOM(r, 'div', attrs = {'class': 'jtip-quality'})[0]
			q = cleantitle.getQuality(q)
			y = client.parseDOM(r, 'div', attrs = {'class': 'jt-info'})[0]
			h = client.parseDOM(r, 'div', attrs = {'class': 'jtip-bottom'})[0]
			h = client.parseDOM(h, 'a', ret='href')[0].replace(self.base_link,self.base_link+'/')
			return (y, q, h)
		except:
			return

	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):
		#try:
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
			trailers = []
			headers = self.headers
			headers = {'Referer': self.base_link}
			sub_url = None
			
			u = url[0]
			ep = url[1]
			#r = client.request(u, headers=headers IPv4=True)
			
			r = proxies.request(u, headers=self.headers, IPv4=True, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			
			if testing == False:
				try:				
					#regex = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
					#matches = re.finditer(regex, r, re.MULTILINE)
					matches = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+').findall(r)
					for match in matches:
						try:
							#print match
							if 'youtube.com' in match:
								match = match.replace('embed/','watch?v=')
								trailers.append(match)
						except:
							pass
				except Exception as e:
					pass
					
				for trailer in trailers:
					links_m = resolvers.createMeta(trailer, self.name, self.logo, '720p', links_m, key, vidtype='Trailer', testing=testing)
					
			u = '%s/watching.html?ep=0' % u
			r = proxies.request(u, headers=self.headers, IPv4=True, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			print u
			
			try:
				vidtype='Movie'

				if ep == None:
					r1 = client.parseDOM(r, 'div', attrs = {'class': 'pa-main anime_muti_link'})[0]
					srcs = client.parseDOM(r1, 'li', ret='data-video')
				else:
					srcs = client.parseDOM(r, 'a', ret='player-data', attrs = {'episode-data': str(ep)})
					vidtype='Show'
					
				try:
					elem = client.parseDOM(r, 'span', attrs = {'class': 'quality'})[0]
					qual = source_utils.check_sd_url(elem)
					riptype = source_utils.check_sd_url_rip(elem)
				except Exception as e:
					qual = '480p'
					riptype = 'BRRIP'
					
				try:
					poster = client.parseDOM(r, 'div', attrs = {'class': 'dm-thumb'})[0]
					poster = client.parseDOM(poster, 'img', ret='src')[0]
				except:
					poster = None
					
				#print srcs
					
				for s in srcs:
					try:
						if s.startswith('//'):
							s = 'https:%s' % s
						links_m = resolvers.createMeta(s, self.name, self.logo, qual, links_m, key, poster=poster, riptype=riptype, vidtype=vidtype, sub_url=sub_url, testing=testing)
						if testing == True and len(links_m) > 0:
							break
					except:
						pass
			except:
				pass
				
			sources += [l for l in links_m]
			
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
		return client.googlepass(url)


	def uncensored1(self, script):
		try:
			script = '(' + script.split("(_$$)) ('_');")[0].split("/* `$$` */")[-1].strip()
			script = script.replace('(__$)[$$$]', '\'"\'')
			script = script.replace('(__$)[_$]', '"\\\\"')
			script = script.replace('(o^_^o)', '3')
			script = script.replace('(c^_^o)', '0')
			script = script.replace('(_$$)', '1')
			script = script.replace('($$_)', '4')

			vGlobals = {"__builtins__": None, '__name__': __name__, 'str': str, 'Exception': Exception}
			vLocals = {'param': None}
			exec (CODE % script.replace('+', '|x|'), vGlobals, vLocals)
			#js_ret = js2py.eval_js(CODE % script.replace('+', '|x|'))
			
			data = vLocals['param'].decode('string_escape')
			x = re.search('''_x=['"]([^"']+)''', data).group(1)
			y = re.search('''_y=['"]([^"']+)''', data).group(1)
			return {'x': x, 'y': y}
		except Exception as e:
			log(type='ERROR', method='uncensored1', err='%s' % e)
			pass

	def uncensored2(self, script):
		try:
			js = jsunfuck.JSUnfuck(script).decode()
			x = re.search('''_x=['"]([^"']+)''', js).group(1)
			y = re.search('''_y=['"]([^"']+)''', js).group(1)
			return {'x': x, 'y': y}
		except Exception as e:
			log(type='ERROR', method='uncensored2', err='%s' % e)
			pass
			
	def uncensored3(self, script):
		try:
			js = script
			x = re.search('''_x=['"]([^"']+)''', js).group(1)
			y = re.search('''_y=['"]([^"']+)''', js).group(1)
			return {'x': x, 'y': y}
		except Exception as e:
			log(type='ERROR', method='uncensored3', err='%s' % e)
			pass

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
