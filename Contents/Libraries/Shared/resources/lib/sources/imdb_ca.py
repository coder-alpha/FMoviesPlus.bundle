# -*- coding: utf-8 -*-

#########################################################################################################
#
# IMDb
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


import re,urllib,urlparse,json,time

from resources.lib.libraries import cleantitle
from resources.lib import resolvers
from resources.lib.libraries import client
from resources.lib.libraries import testparams
from resources.lib.libraries import control
from resources.lib import proxies

name = 'IMDb'
loggertxt = []

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.2'
		self.update_date = 'Dec. 19, 2017'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.priority = 1
		self.disabled = False
		self.language = ['en']
		self.type_filter = ['movie', 'show', 'anime']
		self.domains = ['imdb.com']
		self.base_link_alts = ['http://www.imdb.com']
		self.base_link = self.base_link_alts[0]
		self.page_link = 'http://www.imdb.com/title/%s/videogallery'
		self.MainPageValidatingContent = 'IMDb - Movies, TV and Celebrities - IMDb'
		self.name = name
		self.loggertxt = []
		self.ssl = False
		self.logo = 'https://i.imgur.com/LqO2Fn0.png'
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
				
			if imdb == None:
				raise
				
			return self.page_link % imdb
		except Exception as e: 
			log('ERROR', 'get_movie','%s: %s' % (title,e), dolog=self.init)
			return
		
	def get_show(self, tvshowtitle, season, imdb=None, tvdb=None, year=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_show','Provider Disabled by User')
				return None
				
			if imdb == None:
				raise
				
			return self.page_link % imdb
		except Exception as e:
			log('ERROR', 'get_show','%s: %s' % (tvshowtitle,e), dolog=self.init)
			return


	def get_episode(self, url, episode, imdb=None, tvdb=None, title=None, year=None, season=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				return None
				
			if url != None:
				return url
				
			if imdb == None:
				raise
				
			return self.page_link % imdb
			
		except Exception as e:
			log('ERROR', 'get_episode','%s: %s' % (title,e), dolog=self.init)
			return


	def get_sources(self, url, hosthdDict=None, hostDict=None, locDict=None, proxy_options=None, key=None, testing=False):
		try:
			sources = []
			if url == None: 
				log('FAIL','get_sources','Could not find a matching title: %s' % cleantitle.title_from_key(key), dolog=not testing)
				return sources

			# get IMDb item page
			result = proxies.request(url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
			r = client.parseDOM(result, 'div', attrs = {'class': 'aux-content-widget-3'})[1]
				
			# get types of videos available
			types = {'content_type-trailer':'Trailer', 'content_type-clip':'Clip', 'content_type-interview':'Interviews', 'content_type-other':'Misc.','content_type-featurette':'Featurette'}
			re_map_types = {'Featurette':'Featurette','Clip':'Trailer','Trailer':'Trailer','Interviews':'Interviews','Misc.':'Misc.'}
			
			r1 = client.parseDOM(r, 'a', ret='href')
			
			types_map = {}
			
			for r1_url in r1:
				type = 'Trailer'
				for t in types.keys():
					if t in r1_url:
						type = types[t]
						break
						
				if type not in types_map.keys():
					types_map[type] = []
						
				result_r1 = proxies.request(urlparse.urljoin(self.base_link, r1_url), proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
				
				r2 = client.parseDOM(result_r1, 'div', attrs = {'class': 'search-results'})[0]
				r2a = client.parseDOM(r2, 'a', ret='href')
				
				for r2a1 in r2a:
					if 'ref_' in r2a1:
						types_map[type].append(urlparse.urljoin(self.base_link, r2a1))
				
			links = []
			quality = u'720p'
			selection_map = {}
			
			for vidtype in types_map.keys():
				page_links = types_map[vidtype]
				for page_link in page_links:
					try:
						res = proxies.request(page_link, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
						vidurls = re.findall(r'encodings\":(.*?\])', res)[0]
						vidurls_json = json.loads(vidurls)
						txt = re.findall(r'<title>(.*?)</title>', res)[0]
						txt = txt.replace('&quot;','')

						for viddata in vidurls_json:
							try:
								vidurl = viddata['videoUrl']
								if '.mp4' in vidurl:
									if txt not in selection_map.keys():
										selection_map[txt] = {}
									quality = viddata['definition']
									vidtype = re_map_types[vidtype]
									try:
										l = resolvers.createMeta(vidurl, self.name, self.logo, quality, [], key, vidtype=vidtype, testing=testing, txt=txt)
										l = l[0]
										if testing == True:
											links.append(l)
											break
									except Exception as e:
										log('ERROR', 'get_sources-0', '%s' % e, dolog=not testing)	
									if l['quality'] in selection_map[txt].keys():
										selection_map[txt][l['quality']].append({'fs' : int(l['fs']), 'link': l})
									else:
										selection_map[txt][l['quality']] = [{'fs' : int(l['fs']), 'link': l}]
							except Exception as e:
								log('ERROR', 'get_sources-1', '%s' % e, dolog=not testing)
					except Exception as e:
						log('ERROR', 'get_sources-2', '%s' % e, dolog=not testing)
					if testing == True and len(links) > 0:
						break
				if testing == True and len(links) > 0:
					break
						
			#print selection_map
			for sel_titles in selection_map.keys():
				for sel in selection_map[sel_titles].keys():
					qls = selection_map[sel_titles][sel]
					files = sorted(qls, key=lambda k: k['fs'], reverse=True)
					file = files[0]
					links.append(file['link'])
					
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
