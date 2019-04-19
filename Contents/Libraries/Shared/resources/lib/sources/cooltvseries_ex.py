# -*- coding: utf-8 -*-

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

import re,urllib,urlparse,json,random,time,base64
from resources.lib.libraries import control
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import testparams
from resources.lib.libraries import workers
from resources.lib import resolvers
from resources.lib import proxies

name = 'CoolTvSeries'
loggertxt = []

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'Apr. 16, 2019'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.refreshCookies = False
		self.disabled = False
		self.base_link_alts = ['https://cooltvseries.com']
		self.base_link = self.base_link_alts[0]
		self.MainPageValidatingContent = ['TV Series Download - TV Shows Download | CooLTVSeries']
		self.type_filter = ['show']
		self.search_link = '/%s/season-%s/'
		self.ssl = False
		self.name = name
		self.headers = {}
		self.cookie = None
		self.loggertxt = []
		self.logo = 'https://i.imgur.com/dSyDD94.png'
		self.speedtest = 0
		if len(proxies.sourceProxies)==0:
			proxies.init()
		self.proxyrequired = False
		self.msg = ''
		self.siteonline = self.testSite()
		self.testparser = 'Unknown'
		self.testparser = self.testParser()
		self.initAndSleepThread()
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
			try:
				sitex = client.getRedirectingUrl(site).strip("/")
				if 'http' not in sitex:
					raise Exception('Error in geturl')
				else:
					site = sitex
			except:
				pass
			bool = self.testSiteAlts(site)
			if bool == True:
				return bool
				
		self.base_link = self.base_link_alts[0]
		return False
		
	def testSiteAlts(self, site):
		try:
			self.base_link = site
			if self.disabled:
				log('INFO','testSite', 'Plugin Disabled')
				return False
			self.initAndSleep()
			x1 = time.time()
			http_res, content = proxies.request(url=site, headers=self.headers, output='response', use_web_proxy=False, httpsskip=True)
			self.speedtest = time.time() - x1
			for valcon in self.MainPageValidatingContent:
				if content != None and content.find(valcon) >-1:
					log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,site))
					return True
			log('FAIL', 'testSite', 'Validation content Not Found. HTTP Resp : %s for %s' % (http_res,site))
			return False
		except Exception as e:
			log('ERROR','testSite', '%s' % e)
			return False
			
	def initAndSleepThread(self):
		if self.refreshCookies == False:
			return
		thread_i = workers.Thread(self.InitSleepThread)
		thread_i.start()
		
	def InitSleepThread(self):
		try:
			while self.init == True:
				tuid = control.id_generator(16)
				control.AddThread('%s-InitSleepThread' % self.name, 'Persists & Monitors Provider Requirements (Every 60 mins.)', time.time(), '4', True, tuid)
				time.sleep(60*60)
				self.siteonline = self.testSite()
				self.testparser = self.testParser()
				self.initAndSleep()
				control.RemoveThread(tuid)
		except Exception as e:
			log('ERROR','InitSleepThread', '%s' % e)
		control.RemoveThread(tuid)
			
	def initAndSleep(self):
		try:
			t_base_link = self.base_link
			self.headers = {'X-Requested-With': 'XMLHttpRequest'}
			self.headers['Referer'] = t_base_link
			ua = client.randomagent()
			self.headers['User-Agent'] = ua
			
			#get cf cookie
			cookie = proxies.request(url=t_base_link, headers=self.headers, output='cookie', use_web_proxy=self.proxyrequired, httpsskip=True)
			self.headers['Cookie'] = cookie
			log('SUCCESS', 'initAndSleep', 'Cookies : %s for %s' % (cookie,self.base_link))
		except Exception as e:
			log('ERROR','initAndSleep', '%s' % e)
		
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
			
			for show in testparams.test_shows:
				geturl = self.get_show(tvshowtitle=show['title'], season=show['season'], year=show['year'])
				geturl = self.get_episode(geturl, episode=show['episode'])
				links = self.get_sources(url=geturl, testing=True)
				
				if links != None and len(links) > 0:
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
			if self.siteonline == False:
				log('INFO','get_movie','Provider is Offline')
				return None
			url = {'imdb': imdb, 'title': title, 'year': year}
			url = urllib.urlencode(url)
			return url
		except Exception as e: 
			log('ERROR', 'get_movie','%s: %s' % (title,e), dolog=self.init)
			return

	def get_show(self, imdb=None, tvdb=None, tvshowtitle=None, year=None, season=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				log('INFO','get_show','Provider Disabled by User')
				return None
			if self.siteonline == False:
				log('INFO','get_show','Provider is Offline')
				return None
				
			try:
				url = cleantitle.geturl(tvshowtitle)
				return url
			except:
				return
	
		except Exception as e: 
			log('ERROR', 'get_show','%s: %s' % (tvshowtitle,e), dolog=self.init)
			return

	def get_episode(self, url=None, imdb=None, tvdb=None, title=None, year=None, season=None, episode=None, proxy_options=None, key=None):
		try:
			if control.setting('Provider-%s' % name) == False:
				return None
			if url == None: return
			
			try:
				if not url: return
				http = self.base_link + self.search_link % (url,season)
				season = '%02d' % int(season)
				episode = '%02d' % int(episode)
				r = client.request(http)
				match = re.compile('<a href="(.+?)-S'+season+'E'+episode+'-(.+?)">').findall(r)
				for url1,url2 in match:
					url = '%s-S%sE%s-%s' % (url1,season,episode,url2)
					return url
			except:
				return

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
			page_url = url
			r = client.request(url)
			try:
				match = re.compile('<li><a href="(.+?)" rel="nofollow">(.+?)<').findall(r)
				for url, check in match:
					quality = '720p'
					poster = None
					riptype = 'BRRIP'
					vidtype = 'Show'
					sub_url = None
					l = resolvers.createMeta(url, self.name, self.logo, quality, [], key, poster=poster, riptype=riptype, vidtype=vidtype, sub_url=sub_url, testing=testing, page_url=page_url)
					for ll in l:
						if ll != None and 'key' in ll.keys():
							links_m.append(ll)
			except:
				return
			
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

	def resolve(self, url):
		try:
			return url
		except:
			return
			
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
