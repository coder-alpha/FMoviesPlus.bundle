# -*- coding: utf-8 -*-

#
# Coder Alpha
# https://github.com/coder-alpha
#
# Adapted from lambda's Kodi plugin
# https://github.com/lambda81
# and modified for use with Plex Media Server
#
#########################################################################
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
#########################################################################

import sys,pkgutil,re,json,urllib,urlparse,datetime,time


try:
	# ToDo
	import urlresolver9 as urlresolver
except: pass

from resources.lib.libraries import control
from resources.lib.libraries import alterepisode
from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import workers

from resources.lib import resolvers
from resources.lib import proxies


class sources:
	def __init__(self):
		resolvers.init()
		proxies.init()
		self.sources = []
		self.sourcesDictionary()
		self.threads = {}
		self.providers = []
		self.providersCaller = []
		self.getSourcesAlive = False
		self.isProvThreadRunning = True
		workers.Thread(self.initProviders())
		
	def getHosts(self):
		hosts = resolvers.info()
		return hosts
		
	def getHostsPlaybackSupport(self):
		hostsplaybacksupport = resolvers.hostsplaybacksupport()
		return hostsplaybacksupport
		
	def getProxies(self):
		proxy = proxies.info()
		return proxy
		
	def request_via_proxy(self, url, proxy_name, proxy_url, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout='30', httpsskip=False, use_web_proxy=False, use_web_proxy_as_backup=False, XHR=False, IPv4=False):
		return proxies.request(url=url, proxy_name=proxy_name, proxy_url=proxy_url, close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=timeout, httpsskip=httpsskip, use_web_proxy=use_web_proxy, use_web_proxy_as_backup=use_web_proxy_as_backup, XHR=XHR, IPv4=IPv4)
		
	def getProviders(self):
		while self.isProvThreadRunning == True:
			time.sleep(1)
		return self.providers
		
	def initProviders(self):
		try:
			del self.providers[:]
			del self.providersCaller[:]
			
			for package, name, is_pkg in pkgutil.walk_packages(__path__):
				try:
					c = __import__(name, globals(), locals(), [], -1).source()
					print "Adding Provider %s : %s to Interface" % (c.info()['name'], c.info()['url'])
					self.providersCaller.append({'name':c.info()['name'], 'url':c.info()['url'], 'call':c})
					self.providers.append(c.info())
				except:
					control.log('Error: Loading File %s' % name)
					error_info = {
						'url': 'Unknown',
						'name': "%s.py - Loading Error" % name,
						'speed': 0.0,
						'logo': 'Unknown',
						'ssl': 'Unknown',
						'online': 'Unknown',
						'online_via_proxy' : 'Unknown',
						'parser': 'Unknown'
					}
					self.providers.append(error_info)
		except:
			pass
		self.isProvThreadRunning = False

	def getSources(self, name, title, year, imdb, tmdb, tvdb, tvrage, season, episode, tvshowtitle, alter, date, proxy_options, provider_options, key):
		#try:
		sourceDict = []
		self.getSourcesAlive = True
		
		if provider_options !=None:
			myProviders = []
			for prov in provider_options: myProviders += [i for i in self.providersCaller if i['url'].lower() == prov['url'].lower() and str(prov['enabled'])=='True']
		else:
			myProviders = self.providersCaller
		
		content = 'movie' if tvshowtitle == None else 'episode'
		
		self.threads[key] = []
		if content == 'movie':
			print 'Searching Movie'
			title = cleantitle.normalize(title)
			for source in myProviders:
				try:
					thread_i = workers.Thread(self.getMovieSource, title, year, imdb, proxy_options, key, re.sub('_mv_tv$|_mv$|_tv$', '', source['name']), source['call'])
					self.threads[key].append(thread_i)
					thread_i.start()
				except Exception as e:
					print ('Source getSources %s ERROR %s' % (source,e))
					control.log('Source getSources %s ERROR %s' % (source,e))
					pass
		else:
			print 'Searching Episode'
			try:
				tvshowtitle = cleantitle.normalize(tvshowtitle)
			except:
				pass
			try:
				season, episode = alterepisode.alterepisode().get(imdb, tmdb, tvdb, tvrage, season, episode, alter, title, date)
			except:
				pass
			for source in myProviders:
				try:
					thread_i = workers.Thread(self.getEpisodeSource, title, year, imdb, tvdb, season, episode, tvshowtitle, date, proxy_options, key, re.sub('_mv_tv$|_mv$|_tv$', '', source['name']), source['call'])
					self.threads[key].append(thread_i)
					thread_i.start()
				except Exception as e:
					print ('Source getSources %s ERROR %s' % (source, e))
					control.log('Source getSources %s ERROR %s' % (source, e))
					pass


		#sourceLabel = [re.sub('_mv_tv$|_mv$|_tv$', '', i) for i in sourceDict]
		#sourceLabel = [re.sub('v\d+$', '', i).upper() for i in sourceLabel]

		#time.sleep(0.5)
		self.getSourcesAlive = False
		return self.sources
		#except Exception as e:
		#	self.purgeSourcesKey(key=key)
		#	return self.sources

	def checkProgress(self, key=None):
	
		if key in self.threads.keys():
			c = 0
			for x in self.threads[key]:
				if not x.isAlive():
					c += 1
					
			if len(self.threads[key]) == 0:
				return 0
						
			return float(int(float((float(c)/float(len(self.threads[key])))*100.0))*100)/100.0
		else:
			return 0
			
	def checkKeyInThread(self, key=None):
	
		if key in self.threads.keys():
			return True
		else:
			return False


	def getMovieSource(self, title, year, imdb, proxy_options, key, source, call):
		
		try:
			url = call.get_movie(imdb, title, year, proxy_options, key)
			if url == None: raise Exception()
		except:
			pass

		try:
			sources = []
			sources = call.get_sources(url, self.hosthdfullDict, self.hostsdfullDict, self.hostlocDict, proxy_options, key)
			if sources == None: sources = []
			self.sources.extend(sources)
		except:
			pass


	def getEpisodeSource(self, title, year, imdb, tvdb, season, episode, tvshowtitle, date, proxy_options, key, source, call):
		
		try:
			url = call.get_show(imdb, tvdb, tvshowtitle, year, season, proxy_options, key)
			if url == None: raise Exception()
		except:
			pass

		ep_url = None
		
		try:
			if episode == None: raise Exception()
			if ep_url == None: ep_url = call.get_episode(url, imdb, tvdb, title, year, season, episode, proxy_options, key)
			if ep_url == None: raise Exception()
		except:
			pass

		try:
			sources = []
			sources = call.get_sources(ep_url, self.hosthdfullDict, self.hostsdfullDict, self.hostlocDict, proxy_options, key)
			if sources == None: sources = []
			self.sources.extend(sources)
		except:
			pass

	def clearSources(self, key=None):
		try:
			del self.sources[:]
			self.sources = []
			self.threads.clear()
			self.threads = {}
		except:
			pass
			
	def purgeSources(self, maxcachetimeallowed=0):
		filtered = []
		curr_time = time.time()
		filtered += [i for i in self.sources if (i['ts'] + maxcachetimeallowed) >= curr_time]
		del self.sources[:]
		for i in filtered:
			self.sources.append(i)
			
	def purgeSourcesKey(self, key=None):
		filtered = []
		filtered += [i for i in self.sources if i['key'] != key]
		del self.sources[:]
		for i in filtered:
			self.sources.append(i)

	def sourcesFilter(self):
	
		return self.sources
	

	def sourcesReset(self):
		
		return


	def sourcesResolve(self, url, provider):

		return


	def sourcesDialog(self):
		
		return


	def sourcesDirect(self):
		
		return
		
	def sourcesDictionary(self):
		hosts = resolvers.info()
		hosts = [i for i in hosts if 'host' in i]

		self.rdDict = []
		self.pzDict = []
		#self.rdDict = realdebrid.getHosts()
		#self.pzDict = premiumize.getHosts()

		self.hostlocDict = [i['netloc'] for i in hosts if i['quality'] == 'High' and i['captcha'] == False]
		try: self.hostlocDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hostlocDict)]
		except: pass
		self.hostlocDict = [x for y,x in enumerate(self.hostlocDict) if x not in self.hostlocDict[:y]]

		self.hostdirhdDict = [i['netloc'] for i in resolvers.info() if 'quality' in i and i['quality'] == 'High' and 'captcha' in i and i['captcha'] == False and 'a/c' in i and i['a/c'] == False]
		try: self.hostdirhdDict = [i.lower().rsplit('.', 1)[0] for i in reduce(lambda x, y: x+y, self.hostdirhdDict)]
		except: pass
		self.hostdirhdDict = [x for y,x in enumerate(self.hostdirhdDict) if x not in self.hostdirhdDict[:y]]

		self.hostprDict = [i['host'] for i in hosts if i['a/c'] == True]
		try: self.hostprDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hostprDict)]
		except: pass
		self.hostprDict = [x for y,x in enumerate(self.hostprDict) if x not in self.hostprDict[:y]]

		self.hostcapDict = [i['host'] for i in hosts if i['captcha'] == True]
		try: self.hostcapDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hostcapDict)]
		except: pass
		self.hostcapDict = [i for i in self.hostcapDict if not i in self.rdDict + self.pzDict]

		self.hosthdDict = [i['host'] for i in hosts if i['quality'] == 'High' and i['a/c'] == False and i['captcha'] == False]
		self.hosthdDict += [i['host'] for i in hosts if i['quality'] == 'High' and i['a/c'] == False and i['captcha'] == True]
		try: self.hosthdDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hosthdDict)]
		except: pass

		self.hosthqDict = [i['host'] for i in hosts if i['quality'] == 'High' and i['a/c'] == False and i['captcha'] == False]
		try: self.hosthqDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hosthqDict)]
		except: pass

		self.hostmqDict = [i['host'] for i in hosts if i['quality'] == 'Medium' and i['a/c'] == False and i['captcha'] == False]
		try: self.hostmqDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hostmqDict)]
		except: pass

		self.hostlqDict = [i['host'] for i in hosts if i['quality'] == 'Low' and i['a/c'] == False and i['captcha'] == False]
		try: self.hostlqDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hostlqDict)]
		except: pass

		try:
			self.hostDict = urlresolver.relevant_resolvers(order_matters=True)
			self.hostDict = [i.domains for i in self.hostDict if not '*' in i.domains]
			self.hostDict = [i.lower() for i in reduce(lambda x, y: x+y, self.hostDict)]
			self.hostDict = [x for y,x in enumerate(self.hostDict) if x not in self.hostDict[:y]]

		except:
			self.hostDict = []

		#for i in self.hostDict:
		#	control.log('##### SOURCES DICTY: %s' % i )

		self.hostsdfullDict = self.hostprDict + self.hosthqDict + self.hostmqDict + self.hostlqDict + self.hostDict
		#for i in self.hostsdfullDict:
		#	control.log('##### SOURCES DICTY2: %s' % i )
		#self.hostsdfullDict = self.hostDict

		self.hosthdfullDict = self.hostprDict + self.hosthdDict
