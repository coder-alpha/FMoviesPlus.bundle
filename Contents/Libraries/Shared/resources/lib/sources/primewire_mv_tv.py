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

from resources.lib.libraries import client, cleantitle, source_utils, testparams, control, jsunpack
from resources.lib import resolvers, proxies
import js2py

name = 'Primewire'
loggertxt = []
AVOID_DOMAINS = ['9c40a04e9732e6a6.com','egresspath.com']

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.1.4'
		self.update_date = 'Feb. 10, 2019'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.base_link_alts = ['https://letmewatchthis.cx']
		self.base_link = self.base_link_alts[0]
		self.MainPageValidatingContent = ['PrimeWire | LetMeWatchThis | 1Channel']
		self.type_filter = ['movie', 'show', 'anime']
		self.name = name
		self.disabled = False
		self.loggertxt = []
		self.ssl = False
		self.headers = {}
		ua = client.randomagent()
		self.headers['User-Agent'] = ua
		self.logo = 'http://i.imgur.com/6zeDNpu.png'
		self.key_link = '/index.php?search'
		self.moviesearch_link = '/index.php?search_keywords=%s&key=%s&search_section=1'
		self.tvsearch_link = '/index.php?tv=&search_keywords=%s&key=%s&search_section=1'
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
			if content != None and source_utils.isArrayStringInTxt(content, self.MainPageValidatingContent):
				log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,site))
				return True
			else:
				log('FAIL', 'testSite', 'Validation content Not Found. HTTP Resp : %s for %s' % (http_res,site))
				x1 = time.time()
				http_res, content = proxies.request(url=site, output='response', use_web_proxy=True)
				self.speedtest = time.time() - x1
				if content != None and source_utils.isArrayStringInTxt(content, self.MainPageValidatingContent):
					self.proxyrequired = True
					log('SUCCESS', 'testSite', 'HTTP Resp : %s via proxy for %s' % (http_res,site))
					return True
				else:
					time.sleep(2.0)
					x1 = time.time()
					http_res, content = proxies.request(url=site, output='response', use_web_proxy=True)
					self.speedtest = time.time() - x1
					if content != None and source_utils.isArrayStringInTxt(content, self.MainPageValidatingContent):
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

	def lose_match_year(self, str, text):
		try:
			yr = '(%s)' % str(year)
			if yr in text:
				return True
			elif (str(yr) in text or str(int(yr)-1) in text or str(int(yr)+1) in text):
				return True
			return False
		except:
			False


	def get_movie(self, imdb, title, year, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_movie','Provider Disabled by User')
				return None
			if self.siteonline == False:
				log('INFO','get_movie','Provider is Offline')
				return None
				
			result = None
			query = urlparse.urljoin(self.base_link, self.key_link)

			log('INFO','get_movie-1', query, dolog=False)
			query = proxies.request(query, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			
			keyx = client.parseDOM(query, 'input', ret='value', attrs = {'name': 'search_keywords'})[0]
			#log('SUCCESS', 'get_movie-1b', query, doPrint=True)
			#print "key ------------ %s" % key

			query = self.moviesearch_link % (urllib.quote_plus(cleantitle.query(title)), keyx.replace('Search ',''))
			log('INFO','get_movie-2', query, dolog=False)
			
			query = urlparse.urljoin(self.base_link, query)
			log('INFO','get_movie-3', query, dolog=False)

			result = proxies.request(query, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			
			#if 'page=2' in result or 'page%3D2' in result: result += str(proxies.request(query + '&page=2', 'index_item', proxy_options=proxy_options, use_web_proxy=self.proxyrequired))
			if 'page=2' in result or 'page%3D2' in result:
				result += str(proxies.request(query + '&page=2', proxy_options=proxy_options, use_web_proxy=self.proxyrequired))
			
			result = client.parseDOM(result, 'div', attrs = {'class': 'index_item.+?'})
			
			title = 'watch' + cleantitle.get(title)
			years = ['(%s)' % str(year), '(%s)' % str(int(year)+1), '(%s)' % str(int(year)-1)]

			result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in result]
			result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
			result = [i for i in result if any(x in i[1] for x in years)]

			r = []
			for i in result:
				u = i[0]
				try: u = urlparse.parse_qs(urlparse.urlparse(u).query)['u'][0]
				except: pass
				try: u = urlparse.parse_qs(urlparse.urlparse(u).query)['q'][0]
				except: pass
				r += [(u, i[1])]

			match = [i[0] for i in r if title == cleantitle.get(i[1]) and self.lose_match_year(year, i[1])]
			
			log('INFO','get_movie-4', match, dolog=False)

			match2 = [i[0] for i in r]
			match2 = [x for y,x in enumerate(match2) if x not in match2[:y]]
			if match2 == []: return
			
			log('INFO','get_movie-5', match2, dolog=False)
			
			url = ''
			if len(match2) == 1:
				url = match2[0]
			else:
				for i in match2[:5]:
					try:
						if len(match) > 0: url = match[0] ; break
						#r = proxies.request(urlparse.urljoin(self.base_link, i), 'choose_tabs', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
						r = proxies.request(urlparse.urljoin(self.base_link, i), proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
						#log('SUCCESS', 'get_movie-4', 'r', dolog=testing, doPrint=False)
						if imdb != None and imdb in str(r): url = i ; break
						r = client.parseDOM(r, 'div', attrs={'class':'movie_info'})
						#print "tag -- %s" % r
						if year != None and year in str(r): url = i ; break
					except:
						pass

			url = re.findall('(?://.+?|)(/.+)', url)[0]
			url = client.replaceHTMLCodes(url)
			url = url.encode('utf-8')
			url = urlparse.urljoin(self.base_link, url)
			log('INFO','get_movie-6', url, dolog=False)
			
			return url
		except Exception as e: 
			log('ERROR', 'get_movie','%s: %s' % (title,e), dolog=self.init)
			return

	def get_show(self, imdb=None, tvdb=None, tvshowtitle=None, year=None, season=None, proxy_options=None, key=None):
		query = None
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_show','Provider Disabled by User')
				return None
			if self.siteonline == False:
				log('INFO','get_show','Provider is Offline')
				return None
				
			#print "PRIMEWIRE get_show %s" % tvshowtitle
			oyear = year
			query = urlparse.urljoin(self.base_link, self.key_link)

			log('INFO','get_show-1', query, dolog=False)
			query = proxies.request(query, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			query = cleantitle.asciiOnly(query)
			
			keyx = client.parseDOM(query, 'input', ret='value', attrs = {'name': 'search_keywords'})[0]
			#log('SUCCESS', 'get_movie-1b', query, doPrint=True)
			#print "key ------------ %s" % key

			query = self.tvsearch_link % (urllib.quote_plus(cleantitle.query(tvshowtitle).lower()), keyx.replace('Search ',''))
			log('INFO','get_show-2', query, dolog=False)
			
			query = urlparse.urljoin(self.base_link, query)
			log('INFO','get_show-3', query, dolog=False)

			result = proxies.request(query, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			result = cleantitle.asciiOnly(result)
			#print result
			
			if 'Sorry but I couldn\'t find anything like that' in result:
				query = self.tvsearch_link % urllib.quote_plus(cleantitle.query(tvshowtitle).lower().replace(str(season),''))
				query = urlparse.urljoin(self.base_link, query)

				#result = str(proxies.request(query, 'index_item', proxy_options=proxy_options, use_web_proxy=self.proxyrequired))
				result = proxies.request(query, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
				result = cleantitle.asciiOnly(result)
				#tvshowtitle = 'watch' + cleantitle.get(tvshowtitle).replace(str(season),'').strip()
			else:
				pass
				#tvshowtitle = 'watch' + cleantitle.get(tvshowtitle)
			
			#if 'page=2' in result or 'page%3D2' in result: result += str(proxies.request(query + '&page=2', 'index_item', proxy_options=proxy_options, use_web_proxy=self.proxyrequired))
			if 'page=2' in result or 'page%3D2' in result: 
				result = proxies.request(query + '&page=2', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
				result = cleantitle.asciiOnly(result)

			# .//div[@class='tv_container']/div[@data-id="2"]
			result = client.parseDOM(result, 'div', attrs = {'class': 'index_item index_item_ie'})
			#print result
			
			years = ['%s' % str(year)]
			for iy in range(0,int(season)):
				years.append('%s' % str(int(year)-int(iy)))
				years.append('%s' % str(int(year)+int(iy)))
			
			syear = int(year) - int(season)
			years.append('%s' % str(int(syear)))
			years.append('%s' % str(int(syear)-int(1)))
			years.append('%s' % str(int(syear)+int(1)))

			years = list(set(years))
			#print years
				
			result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in result]
			result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
			result = [i for i in result if any(x in i[1] for x in years)]
			
			r = []
			for i in result:
				u = i[0]
				try: u = urlparse.parse_qs(urlparse.urlparse(u).query)['u'][0]
				except: pass
				try: u = urlparse.parse_qs(urlparse.urlparse(u).query)['q'][0]
				except: pass
				r += [(u, i[1])]
			
			for year in years:
				match = [i[0] for i in r if tvshowtitle == cleantitle.get(i[1]) and '(%s)' % str(year) in i[1]]
				if len(match) > 0:
					break
				
				match = [i[0] for i in r if tvshowtitle.lower() == cleantitle.get(i[1]) and ('(%s)' % str(year) in i[1] or '(%s)' % str(syear) in i[1])]
				if len(match) > 0:
					break
			
			match2 = [i[0] for i in r]
			match2 = [x for y,x in enumerate(match2) if x not in match2[:y]]
			if match2 == []: return

			for i in match2[:5]:
				try:
					if len(match) > 0: url = match[0] ; break
					#r = proxies.request(urlparse.urljoin(self.base_link, i), 'tv_episode_item', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
					if imdb != None:
						r = proxies.request(i, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
						r = cleantitle.asciiOnly(r)
						if imdb in str(r): url = i ; break
					else:
						url = match2[0]
						break
				except:
					pass

			url = re.findall('(?://.+?|)(/.+)', url)[0]
			url = client.replaceHTMLCodes(url)
			url = url.encode('utf-8')
			return url
		except Exception as e: 
			log('ERROR', 'get_show','%s (%s): %s' % (tvshowtitle,query,e), dolog=self.init)
			return


	def get_episode(self, url=None, imdb=None, tvdb=None, title=None, year=None, season=None, episode=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				return None
			
			if url == None: return

			xurl = urlparse.urljoin(self.base_link, url)
			log('INFO', 'get_episode-1A',xurl, dolog=False)
			
			result = proxies.request(xurl, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			result = cleantitle.asciiOnly(result)
			
			loc = url.replace(self.base_link+'/','')
			url = testjs(result, self.base_link, loc)
			log('INFO', 'get_episode-1B',url, dolog=False)
			
			result = proxies.request(url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			result = cleantitle.asciiOnly(result)
			#print result
			
			if len(result) == 0:
				for site in self.base_link_alts:
					if site != self.base_link:
						turl = urlparse.urljoin(site, url)
						result = proxies.request(turl, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
						result = cleantitle.asciiOnly(result)
						if len(result) > 0:
							xurl = turl
							break
			
			if len(result) == 0:
				raise Exception('Empty page received: %s' % urlparse.urljoin(self.base_link, url))
			
			result = client.parseDOM(result, 'div', attrs = {'class': 'tv_episode_item'})
			#print result

			title = cleantitle.get(title)

			result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'span', attrs = {'class': 'tv_episode_name'}), re.compile('(\d{4}-\d{2}-\d{2})').findall(i)) for i in result]
			
			#print result
			
			result = [(i[0], i[1][0], i[2]) for i in result if len(i[1]) > 0] + [(i[0], None, i[2]) for i in result if len(i[1]) == 0]
			result = [(i[0], i[1], i[2][0]) for i in result if len(i[2]) > 0] + [(i[0], i[1], None) for i in result if len(i[2]) == 0]
			result = [(i[0][0], i[1], i[2]) for i in result if len(i[0]) > 0]
			
			#print result

			url = [i for i in result if title == cleantitle.get(i[1]) and year == i[2]][:1]
			if len(url) == 0: url = [i for i in result if year == i[2]]
			if len(url) == 0 or len(url) > 1: url = [i for i in result if 'season-%01d-episode-%01d' % (int(season), int(episode)) in i[0]]

			url = client.replaceHTMLCodes(url[0][0])
			try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
			except: pass
			try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['q'][0]
			except: pass
			
			#print url
			
			# url = re.findall('(?://.+?|)(/.+)', url)[0]
			# url = client.replaceHTMLCodes(url)
			# url = url.encode('utf-8')
			url = urlparse.urljoin(self.base_link, url)
			
			return url
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

			log('INFO', 'get_sources-1A',url, dolog=False)
			#result = proxies.request(url, 'choose_tabs', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			
			result = proxies.request(url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			result = cleantitle.asciiOnly(result)
			
			try:
				poster1 = client.parseDOM(result, 'div', attrs = {'class': 'movie_thumb'})[0]
				poster = client.parseDOM(poster1, 'img', ret='src')[0]
				if 'www' not in poster:
					poster = 'http:%s' % poster
			except:
				poster = None
			
			loc = url.replace(self.base_link+'/','')
			url = testjs(result, self.base_link, loc)
			vidtype = 'Movie'
			if 'season' in url:
				vidtype = 'Show'
				url = url.replace('=tv-','=watch-').replace('/season','&season')
				url = url.replace('season-','season=').replace('-episode-','&episode=')
			log('INFO', 'get_sources-1B',url, dolog=False)
			
			result = proxies.request(url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			result = cleantitle.asciiOnly(result)
			
			links_m = []
			trailers = []
			if testing == False:
				try:
					matches = re.findall(r'\"(//www.youtube.*?)\"',result)
					for match in matches:
						try:
							#print match
							if 'youtube.com' in match and '"' not in match:
								match = match.replace('embed/','watch?v=')
								if 'http' not in match:
									match = 'http:%s' % match
								trailers.append(match)
						except:
							pass
				except Exception as e:
					pass
					
				for trailer in trailers:
					try:
						l = resolvers.createMeta(trailer, self.name, self.logo, '720p', [], key, vidtype='Trailer', testing=testing)
						for ll in l:
							if ll != None and 'key' in ll.keys():
								links_m.append(ll)
					except:
						pass
			
			links = client.parseDOM(result, 'tbody')
			
			try:
				riptypex = client.parseDOM(result, 'div', attrs = {'class': 'warning_message'})[0]
			except:
				riptypex = 'BRRIP'
				
			c=0
			for i in links:
				try:
					url = client.parseDOM(i, 'a', ret='href')[0]
					url = urlparse.urljoin(self.base_link, url)
					#print url
					r = client.request(url)
					r = cleantitle.asciiOnly(r)
					links = client.parseDOM(r, 'script')
					p = False
					urls_p = []
					for l in links:
						if 'eval' in l:
							unpacked_code = jsunpack.unpack(l)
							unpacked_code = jsunpack.unpack(unpacked_code)
							#print unpacked_code
							host = re.findall(r"var host=\\'(.*?)\\'",unpacked_code)
							hosted = re.findall(r"var hosted=\\'(.*?)\\'",unpacked_code)[0]
							loc = re.findall(r"var loc=\\'(.*?)\\'",unpacked_code)[0]
							if loc != None and len(loc) > 4:
								for h in host:
									if hosted in h:
										url = h + loc
										#print url
										urls_p.append(url)
										#url = re.findall(r"'(http.*)'",unpacked_code)[0]
										p = True
										break
					if p == False:
						raise
					c=c+1
					
					for url in urls_p:
						log('INFO', 'get_sources-2A-%s' % c, url, dolog=False)
						
						if 'http' not in url:
							raise Exception()
						for u in AVOID_DOMAINS:
							if u in url:
								raise Exception()
						
						quality = client.parseDOM(i, 'span', ret='class')[0]
						
						if quality == 'quality_cam' or quality == 'quality_ts': # quality_ts
							quality = '480p'
							riptype = 'CAM'
						elif quality == 'quality_dvd': 
							quality = '720p'
							riptype = 'BRRIP'
						else:
							riptype = riptypex
							quality = '480p'
							
						try:
							l = resolvers.createMeta(url, self.name, self.logo, quality, [], key, vidtype=vidtype, poster=poster, riptype=riptype, testing=testing)
							for ll in l:
								if ll != None and 'key' in ll.keys():
									links_m.append(ll)
						except:
							pass
				except:
					pass
					
			for l in links_m:
				if l != None and 'key' in l.keys():
					sources.append(l)

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
			
def testjs(html, url, loc):
	jss = re.findall(r'eval\(.+\)', html)
	js = None
	for j in jss:
		if 'goml' in j:
			js = j
			break
	html_with_unpacked_js = jsunpack.unpack(js)
	ret = js2py.eval_js(html_with_unpacked_js + '; page+"PLACE_HOLDER"+code')
	ret = ret.replace('PLACE_HOLDER',loc)
	ret = '%s/%s' % (url, ret)
	ret = ret.replace('slug=/watch','slug=watch')
	return ret

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
