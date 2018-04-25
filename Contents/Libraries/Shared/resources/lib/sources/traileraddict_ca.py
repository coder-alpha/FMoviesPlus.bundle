# -*- coding: utf-8 -*-

#########################################################################################################
#
# TrailerAddict (courtesy : Pip Longrun)
# https://github.com/piplongrun/TrailerAddict.bundle
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
from resources.lib.libraries import unwise2
from resources.lib import proxies

name = 'TrailerAddict'
loggertxt = []

class source:
	def __init__(self):
		del loggertxt[:]
		self.ver = '0.0.1'
		self.update_date = 'Dec. 24, 2017'
		log(type='INFO', method='init', err=' -- Initializing %s %s %s Start --' % (name, self.ver, self.update_date))
		self.init = False
		self.priority = 1
		self.disabled = False
		self.language = ['en']
		self.type_filter = ['movie', 'show', 'anime']
		self.domains = ['traileraddict.com']
		self.base_link_alts = ['https://www.traileraddict.com']
		self.base_link = self.base_link_alts[0]
		self.page_link = 'https://api.tadata.me/imdb2ta/v2/?imdb_id=%s'
		self.MainPageValidatingContent = 'Trailer Addict - Movie Trailers'
		self.name = name
		self.loggertxt = []
		self.ssl = False
		self.logo = 'https://i.imgur.com/tVEryKQ.png'
		self.headers = {}
		self.speedtest = 0
		if len(proxies.sourceProxies)==0:
			proxies.init()
		self.force_use_proxyrequired = True
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
		if control.setting('Provider-%s' % name) == False:
			log('INFO','testSite', 'Plugin Disabled by User - cannot test site')
			return False
			
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
			if content != None and content.find(self.MainPageValidatingContent) >-1 and self.force_use_proxyrequired == False:
				log('SUCCESS', 'testSite', 'HTTP Resp : %s for %s' % (http_res,site))
				return True
			else:
				if self.force_use_proxyrequired == False:
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

			UA = client.agent()
				
			# get TA JSON data from tadata api
			result = proxies.request(url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
			resultx = json.loads(str(result))
			ta_url = resultx['url']
			poster = resultx['image'] if 'image' in resultx else None
			
			#print ta_url
			result = proxies.request(ta_url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
			
			# get types of videos available
			types = {'trailer':'Trailer', 'feature_trailer':'Trailer', 'theatrical_trailer':'Trailer', 'behind_the_scenes':'Behind the scenes', 'deleted_scene':'Deleted Scenes', 'featurette':'Featurette', 'featured_box':'Featurette', 'music_video':'Music Video', 'misc_scene':'Misc.'}
			quality_maps = {'4k':'4K','2k':'2K','1080p':'1080p', 'HD':'720p', 'M':'480p', 'S':'360p'}
			
			extras = []
			
			items = client.parseDOM(result, 'div', attrs = {'id':'featured_c'})[0]
			m_title = client.parseDOM(items, 'div', attrs = {'class':'movie_info'})
			#print m_title
			
			fail_bool = False
			for video in m_title:
				try:
					time.sleep(0.1)
					video = video.replace('rttttttttttt','')
					video = video.replace('rtttttttttt','')
					video = video.replace('\r','')
					video = video.replace('\t','')
					video = video.replace('\n','')

					title = client.parseDOM(video, 'a', attrs = {'class':'m_title'})[0]
					
					ta_tage_url = client.parseDOM(video, 'a', ret = 'href')[0]
					if 'http' not in ta_tage_url:
						ta_tage_url = urlparse.urljoin(self.base_link, ta_tage_url)
					
					try:
						vid_date = client.parseDOM(video, 'span', attrs = {'class':'m_date'})[0]
						vid_date = vid_date.replace(',','')
					except:
						vid_date = ''
					
					# Trailers
					if title.lower() == 'trailer':
						extra_type = 'trailer'
					elif title.lower() == 'feature trailer':
						extra_type = 'feature_trailer'
					elif title.lower() == 'theatrical trailer':
						extra_type = 'theatrical_trailer'

					# Behind the scenes
					elif 'behind the scenes' in title.lower():
						extra_type = 'behind_the_scenes'

					# Featurette
					elif 'featurette' in title.lower():
						extra_type = 'featurette'
						
					# Music Video
					elif 'music video' in title.lower():
						extra_type = 'music_video'

					# Interview
					elif 'interview' in title.lower():
						extra_type = 'interview'

						if title.lower().startswith('interview') or title.lower().startswith('generic interview'):
							title = title.split('nterview - ')[-1].split('nterview- ')[-1]

					# Deleted scene
					elif 'deleted scene' in title.lower():
						extra_type = 'deleted_scene'
						
					# Trailers
					elif 'trailer' in title.lower():
						extra_type = 'trailer'
						
					else:
						extra_type = 'misc_scene'

					# process ta_tage_url
					#print ta_tage_url
					result = proxies.request(ta_tage_url, proxy_options=proxy_options, use_web_proxy=self.proxyrequired, IPv4=True)
					
					data = None
					
					js = re.findall(r'eval\(function\(w,i,s,e\).*;', result)
					
					if len(js) > 0:
						data = js[0]
					else:
						try:
							jsd = re.findall(r'src="/util/client.js?c=(.*?)"><', result)[0].strip()
						except:
							try:
								jsd = re.findall(r'</style>rttr<!-- (.*?) -->rrttrtt<div id=\"embed_box\">', result)[0].strip()
							except:
								jsd = re.findall(r'</style>.*<!-- (.*?) -->.*<div id=\"embed_box\">', result, flags=re.DOTALL)[0].strip()
								
						jsd_url = tau % (urllib.quote_plus(jsd), client.b64encode(str(int(time.time()))), client.b64encode(ta_tage_url), client.b64encode(UA), control.setting('ver'), client.b64encode(control.setting('ca')))
						
						data = proxies.request(jsd_url)
						if data == None:
							log('ERROR', 'get_sources-1', '%s' % jsd_url, dolog=True)
					
					if data != None:
						if str(data) == '423':
							fail_bool = True
							raise Exception("Helper site is currently unavailable !")
						try:
							data = unwise2.unwise_process(data)
						except:
							raise Exception("unwise2 could not process data")
					else:
						raise Exception("URL Post Data Unavailable")
						
					files = re.findall(r'source src="([^"]+)"', data)
					quals = re.findall(r'res=\"(.*?)\"', data)
					processed = []
					
					for i in range(0, len(files)):
						v_file = files[i]
						if quals[i] in quality_maps.keys():
							quality = quality_maps[quals[i]]
						else:
							quality = '720p'
						#print extra_type
						if quality not in processed:
							#print v_file
							processed.append(quality)
							extras.append(
								{'etype': extra_type,
								'date': vid_date,
								'type': types[extra_type],
								'url' : v_file,
								'quality': quality,
								'title': title,
								'thumb': poster}
							)
					
					if testing == True and len(extras) > 0:
						break
				except Exception as e:
					log('ERROR', 'get_sources-2', '%s' % e, dolog=True)
					if fail_bool == True:
						raise Exception("%s" % e)

			links = []
			
			#print extras
			for extra in extras:
				links = resolvers.createMeta(extra['url'], self.name, self.logo, extra['quality'], links, key, vidtype=extra['type'], testing=testing, txt=extra['title'], poster=extra['thumb'])
				if testing == True and len(links) > 0:
					break

			for i in links:
				sources.append(i)
				
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

tau = client.b64ddecode('YUhSMGNITTZMeTlqYjJSbGNtRnNjR2hoTGpBd01IZGxZbWh2YzNSaGNIQXVZMjl0TDNKbGNYVmxjM1J6TDNKbGNUSXVjR2h3UDFGVlJWSlpYMU5VVWtsT1J6RTlKWE1tVVZWRlVsbGZVMVJTU1U1SE1qMGxjeVpSVlVWU1dWOVRWRkpKVGtjelBTVnpKbEZWUlZKWlgxTlVVa2xPUnpROUpYTW1kbVZ5UFNWekptTnZaR1Z5WVd4d2FHRTlKWE09')