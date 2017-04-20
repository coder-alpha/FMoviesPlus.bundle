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

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import testparams
from resources.lib.libraries import control
from resources.lib import resolvers
from resources.lib import proxies

class source:
	def __init__(self):
		self.base_link = 'http://www.primewire.ag'
		self.MainPageValidatingContent = '1Channel | PrimeWire.ag - Watch Movies Online'
		self.name = 'Primewire'
		self.loggertxt = []
		self.ssl = False
		self.logo = 'http://i.imgur.com/6zeDNpu.png'
		self.key_link = '/index.php?search'
		self.link_1 = 'http://www.primewire.ag'
		self.link_2 = 'http://www.primewire.org'
		self.link_3 = 'http://www.primewire.is'
		self.moviesearch_link = '/index.php?search_keywords=%s&key=%s&search_section=1'
		self.tvsearch_link = '/index.php?search_keywords=%s&key=%s&search_section=2'
		self.headers = {'Connection' : 'keep-alive'}
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
			getmovieurl = self.get_movie(title=testparams.movie, year=testparams.movieYear, imdb=testparams.movieIMDb, testing=True)
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


	def get_movie(self, imdb, title, year, proxy_options=None, key=None, testing=False):
		try:
			#print "PRIMEWIRE get_movie %s" % title
			result = None
			query = urlparse.urljoin(self.base_link, self.key_link)
			#print "key ------------ %s" % key
			
			#key = proxies.request(key, 'searchform', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			query = proxies.request(query, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			self.log('SUCCESS', 'get_movie-1', 'query', dolog=testing, disp=False)
			
			query = client.parseDOM(query, 'input', ret='value', attrs = {'name': 'key'})[0]
			self.log('SUCCESS', 'get_movie-1b', 'query', dolog=testing, disp=False)
			#print "key ------------ %s" % key

			query = self.moviesearch_link % (urllib.quote_plus(cleantitle.query(title)), query)
			self.log('SUCCESS', 'get_movie-1c', 'query', dolog=testing, disp=False)
			
			query = urlparse.urljoin(self.base_link, query)
			self.log('SUCCESS', 'get_movie-1d', 'query', dolog=testing, disp=False)

			#result = str(proxies.request(query, 'index_item', proxy_options=proxy_options, use_web_proxy=self.proxyrequired))
			result = proxies.request(query, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			self.log('SUCCESS', 'get_movie-2', 'result', dolog=testing, disp=False)
			
			#if 'page=2' in result or 'page%3D2' in result: result += str(proxies.request(query + '&page=2', 'index_item', proxy_options=proxy_options, use_web_proxy=self.proxyrequired))
			if 'page=2' in result or 'page%3D2' in result:
				result += str(proxies.request(query + '&page=2', proxy_options=proxy_options, use_web_proxy=self.proxyrequired))
				self.log('SUCCESS', 'get_movie-3', '', dolog=testing, disp=False)
			
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

			#print result
			match = [i[0] for i in r if title == cleantitle.get(i[1]) and self.lose_match_year(year, i[1])]
			
			#print "match %s" % match

			match2 = [i[0] for i in r]
			match2 = [x for y,x in enumerate(match2) if x not in match2[:y]]
			if match2 == []: return
			
			#print "match2 %s" % match2
			
			url = ''
			if len(match2) == 1:
				url = self.base_link + match2[0]
			else:
				for i in match2[:5]:
					try:
						if len(match) > 0: url = match[0] ; break
						#r = proxies.request(urlparse.urljoin(self.base_link, i), 'choose_tabs', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
						r = proxies.request(urlparse.urljoin(self.base_link, i), proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
						self.log('SUCCESS', 'get_movie-4', 'r', dolog=testing, disp=False)
						if imdb != None and imdb in str(r): url = i ; break
						r = client.parseDOM(r, 'div', attrs={'class':'movie_info'})
						#print "tag -- %s" % r
						if year != None and year in str(r): url = i ; break
					except:
						pass

			url = re.findall('(?://.+?|)(/.+)', url)[0]
			url = client.replaceHTMLCodes(url)
			url = url.encode('utf-8')
			if url != None and'http://' not in url:
				url = 'http:' + url
			#print "PRIMEWIRE get_movie %s" % url
			
			self.log('SUCCESS', 'get_movie','%s' % url, dolog=testing)
			return url
		except Exception as e:
			self.log('ERROR', 'get_movie','%s' % e, dolog=testing)		
			self.log('ERROR', 'get_movie','%s' % '-- query --', dolog=testing)
			self.log('ERROR', 'get_movie','%s' % query, dolog=testing)
			self.log('ERROR', 'get_movie','%s' % '-- result --', dolog=testing)
			self.log('ERROR', 'get_movie','%s' % result, dolog=testing)
			return

	def get_show(self, imdb, tvdb, tvshowtitle, year, proxy_options=None, key=None):
		try:
			#print "PRIMEWIRE get_show %s" % tvshowtitle
			
			key = urlparse.urljoin(self.base_link, self.key_link)
			#key = proxies.request(key, 'searchform', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			key = proxies.request(key, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			key = client.parseDOM(key, 'input', ret='value', attrs = {'name': 'key'})[0]

			query = self.tvsearch_link % (urllib.quote_plus(cleantitle.query(tvshowtitle)), key)
			query = urlparse.urljoin(self.base_link, query)

			#result = str(proxies.request(query, 'index_item', proxy_options=proxy_options, use_web_proxy=self.proxyrequired))
			result = str(proxies.request(query, proxy_options=proxy_options, use_web_proxy=self.proxyrequired))
			#if 'page=2' in result or 'page%3D2' in result: result += str(proxies.request(query + '&page=2', 'index_item', proxy_options=proxy_options, use_web_proxy=self.proxyrequired))
			if 'page=2' in result or 'page%3D2' in result: result += str(proxies.request(query + '&page=2', proxy_options=proxy_options, use_web_proxy=self.proxyrequired))

			result = client.parseDOM(result, 'div', attrs = {'class': 'index_item.+?'})

			tvshowtitle = 'watch' + cleantitle.get(tvshowtitle)
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

			match = [i[0] for i in r if tvshowtitle == cleantitle.get(i[1]) and '(%s)' % str(year) in i[1]]

			match2 = [i[0] for i in r]
			match2 = [x for y,x in enumerate(match2) if x not in match2[:y]]
			if match2 == []: return

			for i in match2[:5]:
				try:
					if len(match) > 0: url = match[0] ; break
					#r = proxies.request(urlparse.urljoin(self.base_link, i), 'tv_episode_item', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
					r = proxies.request(urlparse.urljoin(self.base_link, i), proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
					if imdb in str(r): url = i ; break
				except:
					pass

			url = re.findall('(?://.+?|)(/.+)', url)[0]
			url = client.replaceHTMLCodes(url)
			url = url.encode('utf-8')
			return url
		except:
			return


	def get_episode(self, url, imdb, tvdb, title, year, season, episode, proxy_options=None, key=None):
		try:
			#print "PRIMEWIRE get_episode %s" % url
			
			if url == None: return

			url = urlparse.urljoin(self.base_link, url)

			#result = proxies.request(url, 'tv_episode_item', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			result = proxies.request(url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			result = client.parseDOM(result, 'div', attrs = {'class': 'tv_episode_item'})

			title = cleantitle.get(title)

			result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'span', attrs = {'class': 'tv_episode_name'}), re.compile('(\d{4}-\d{2}-\d{2})').findall(i)) for i in result]
			result = [(i[0], i[1][0], i[2]) for i in result if len(i[1]) > 0] + [(i[0], None, i[2]) for i in result if len(i[1]) == 0]
			result = [(i[0], i[1], i[2][0]) for i in result if len(i[2]) > 0] + [(i[0], i[1], None) for i in result if len(i[2]) == 0]
			result = [(i[0][0], i[1], i[2]) for i in result if len(i[0]) > 0]

			url = [i for i in result if title == cleantitle.get(i[1]) and year == i[2]][:1]
			if len(url) == 0: url = [i for i in result if year == i[2]]
			if len(url) == 0 or len(url) > 1: url = [i for i in result if 'season-%01d-episode-%01d' % (int(season), int(episode)) in i[0]]

			url = client.replaceHTMLCodes(url[0][0])
			try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
			except: pass
			try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['q'][0]
			except: pass
			url = re.findall('(?://.+?|)(/.+)', url)[0]
			url = client.replaceHTMLCodes(url)
			url = url.encode('utf-8')
			return url
		except:
			return

	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):
		try:
			sources = []
			
			#print "PRIMEWIRE get_sources %s" % url
			if self.testparser == False:
				return sources

			if url == None: return sources

			url = urlparse.urljoin(self.base_link, url)

			#result = proxies.request(url, 'choose_tabs', proxy_options=proxy_options, use_web_proxy=self.proxyrequired)
			result = proxies.request(url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired)

			links = client.parseDOM(result, 'tbody')

			for i in links:
				try:
					url = client.parseDOM(i, 'a', ret='href')[0]
					try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['u'][0]
					except: pass
					try: url = urlparse.parse_qs(urlparse.urlparse(url).query)['q'][0]
					except: pass
					url = urlparse.parse_qs(urlparse.urlparse(url).query)['url'][0]

					url = base64.b64decode(url)
					url = client.replaceHTMLCodes(url)
					url = url.encode('utf-8')
					
					if 'http' not in url:
						raise Exception()
					
					quality = client.parseDOM(i, 'span', ret='class')[0]
					
					if quality == 'quality_cam' or quality == 'quality_ts': quality = 'CAM'
					elif quality == 'quality_dvd': quality = 'SD'
					else:  raise Exception()
					
					links_m = []
					print "%s --- %s" % (self.name,url)
					links_m = resolvers.createMeta(url, self.name, self.logo, quality, links_m, key)

					sources += [l for l in links_m]
					if testing and len(sources) > 0:
						break
				except:
					pass

			self.log('SUCCESS', 'get_sources','links : %s' % len(sources), dolog=testing)
			return sources
		except Exception as e:
			self.log('ERROR', 'get_sources','%s' % e, dolog=testing)
			return sources


	def resolve(self, url):
		try:
			url = resolvers.request(url)
			return url
		except:
			return

def logger(msg):
	control.log(msg)

