﻿# -*- coding: utf-8 -*-

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
		self.isInitialized = False
		log(type='INFO', method='init', err=' -- Initializing Start --', name='sources')
		self.threads = {}
		self.threadSlots = {}
		self.providers = []
		self.providerInProcess = []
		self.providersInit1 = []
		self.providersInit2 = []
		self.providersCaller = []
		self.providersTimer = {}
		self.getSourcesAlive = False
		self.isProvThreadRunning = True
		self.sources = []

	def doInit(self):
		resolvers.init()
		proxies.init()
		self.sourcesDictionary()
		workers.Thread(self.initProviders())
		
	def getHosts(self):
		hosts = resolvers.info()
		return hosts
		
	def hostsCaller(self):
		return resolvers.sourceHostsCall
		
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

	def getProvidersInitStatus(self):
		del self.providersInit2[:]
		for package, name, is_pkg in pkgutil.walk_packages(__path__):
			self.providersInit2.append(name)
		return round((float(len(self.providersInit1))/float(len(self.providersInit2)))*100)
		
	def getCurrentProviderInProcess(self):
		if len(self.providerInProcess) > 0:
			return self.providerInProcess[0]
		else:
			return 'None'
		
	def initProviders(self):
		try:
			del self.providers[:]
			del self.providersCaller[:]
			del self.providerInProcess[:]
			
			for package, name, is_pkg in pkgutil.walk_packages(__path__):
				try:
					self.providerInProcess.append('%s.py' % name)
					c = __import__(name, globals(), locals(), [], -1).source()
					log("Adding Provider %s : %s to Interface" % (c.info()['name'], c.info()['url']),name='providers')
					self.providersCaller.append({'name':c.info()['name'], 'url':c.info()['url'], 'call':c})
					self.providers.append(c.info())
					self.providersTimer[c.info()['name']] = {}
					control.control_json[c.info()['name']] = {}
					self.providersInit1.append(c.info()['name'])
				except Exception as e:
					log(type='CRITICAL', err='Could not import %s > %s (Retrying)' % (name,e))
					try:
						c = __import__(name, globals(), locals(), [], -1).source()
						log("Adding Provider %s : %s to Interface" % (c.info()['name'], c.info()['url']),name='providers')
						self.providersCaller.append({'name':c.info()['name'], 'url':c.info()['url'], 'call':c})
						self.providers.append(c.info())
						self.providersTimer[c.info()['name']] = {}
						control.control_json[c.info()['name']] = {}
					except Exception as e:
						log(type='CRITICAL', err='Could not import %s > %s (Retrying-Failed)' % (name,e))
						error_info = {
							'url': 'Unknown',
							'name': "%s.py" % name,
							'msg': "Loading Error: %s" % e,
							'speed': 0.0,
							'logo': 'Unknown',
							'ssl': 'Unknown',
							'frd': True,
							'online': 'Unknown',
							'online_via_proxy' : 'Unknown',
							'parser': 'Unknown'
						}
						self.providers.append(error_info)
						self.providersTimer[name] = {}
						control.control_json[name] = {}
						self.providersInit1.append(name)
				del self.providerInProcess[:]
		except:
			pass
		self.isProvThreadRunning = False
		ret = control.loadPermStore()
		del self.providerInProcess[:]
		
		if ret != None:
			for k in ret.keys():
				control.control_json[k] = ret[k]
				self.providersTimer[k] = ret[k]

		log(type='INFO', method='init', err=' -- Initializing End --', name='sources')
		self.isInitialized = True

	def getSources(self, name, title, year, imdb, tmdb, tvdb, tvrage, season, episode, tvshowtitle, alter, date, proxy_options, provider_options, key, session):
		#try:
		sourceDict = []
		self.getSourcesAlive = True
		
		if provider_options !=None:
			myProviders = []
			for prov in provider_options: myProviders += [i for i in self.providersCaller if i['url'].lower() == prov['url'].lower() and str(prov['enabled'])=='True']
		else:
			myProviders = self.providersCaller
		
		content = 'movie' if tvshowtitle == None else 'show'
		
		self.threads[key] = []
		self.threadSlots[key] = []
		pos = 0
		if content == 'movie':
			log(err='Initializzing Search for Movie: %s' % title)
			title = cleantitle.normalize(title)
			for source in myProviders:
				try:
					source_name = 'Unknow source (import error)'
					source_name = source['name']
					log(err='Queing Search for Movie: %s (%s) in Provider %s' % (title,year,source_name))
					thread_i = workers.Thread(self.getMovieSource, title, year, imdb, proxy_options, key, re.sub('_mv_tv$|_mv$|_tv$', '', source['name']), source['call'])
					self.threads[key].append(thread_i)
					self.threadSlots[key].append({'thread':thread_i, 'status':'idle', 'pos':pos, 'source':source_name})
					pos += 1
					#thread_i.start()
				except Exception as e:
					log(type='ERROR', err='getSources %s - %s' % (source_name,e))
		else:
			log(err='Initializzing Search for Show: %s' % tvshowtitle)
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
					source_name = 'Unknow source (import error)'
					source_name = source['name']
					log(err='Queing Search for Show: %s S%sE%s in Provider %s' % (tvshowtitle,season,episode,source_name))
					thread_i = workers.Thread(self.getEpisodeSource, title, year, imdb, tvdb, season, episode, tvshowtitle, date, proxy_options, key, re.sub('_mv_tv$|_mv$|_tv$', '', source_name), source['call'])
					self.threads[key].append(thread_i)
					self.threadSlots[key].append({'thread':thread_i, 'status':'idle', 'pos':pos, 'source':source_name})
					pos += 1
					#thread_i.start()
				except Exception as e:
					log(type='ERROR', err='getSources %s - %s' % (source_name,e))

		thread_ex = workers.Thread(self.executeThreads, key)
		thread_ex.start()
					
		#sourceLabel = [re.sub('_mv_tv$|_mv$|_tv$', '', i) for i in sourceDict]
		#sourceLabel = [re.sub('v\d+$', '', i).upper() for i in sourceLabel]

		#time.sleep(0.5)
		self.getSourcesAlive = False
		return self.sources
		#except Exception as e:
		#	self.purgeSourcesKey(key=key)
		#	return self.sources
		
	def executeThreads(self, key):
		
		try:
			title = cleantitle.title_from_key(key)
			log(type='INFO', err='Starting threads : %s' % title)
			while key in self.threadSlots:
				for s in self.threadSlots[key]:
					active = 0
					done = 0
					idle = 0
					for s1 in self.threadSlots[key]:
						if s1['status'] == 'active':
							active += 1
						if s1['status'] == 'done':
							done += 1
						if s1['status'] == 'idle':
							idle += 1
							
					if done == len(self.threadSlots[key]):
						log(type='INFO', err='Threads completed ! : %s' % title)
						control.savePermStore()
						return
							
					if s['status'] == 'idle' and active < int(control.setting('control_concurrent_src_threads')):
						s['thread'].start()
						s['status'] = 'active'
						s['s_time'] = time.time()
						log(type='INFO', err='Starting thread : %s > %s' % (title, s['source']))
					
					time.sleep(0.1)
				time.sleep(1.0)
		except Exception as e:
			log(type='ERROR', err='Thread Title %s - %s' % (title,e))
		control.savePermStore()

	def checkProgress(self, key=None):
	
		if key in self.threads.keys():
			c = 0
			for x in self.threads[key]:
				if not x.isAlive(): 
					for s in self.threadSlots[key]:
						if x == s['thread'] and s['status'] == 'done':
							c += 1
					
			if len(self.threads[key]) == 0:
				return 100
						
			return float(int(float((float(c)/float(len(self.threads[key])))*100.0))*100)/100.0
		else:
			filtered = [i for i in self.sources if i['key'] == key]
			if len(filtered) > 0:
				return 100
			return 0
			
	def getDescProgress(self, key=None):

		str = []
		if key in self.threads.keys():
			for s in self.threadSlots[key]:
				if s['status'] == 'done':
					str.append('%s (%ss. %s)' % (s['source'], round(s['e_time']-s['s_time'], 2), u'\u2713'))
				elif s['status'] == 'idle':
					str.append('%s (%ss. %s)' % (s['source'], '0.00', u'\u21AD'))
				elif s['status'] == 'active' and 's_time' not in s.keys():
					str.append('%s (%ss. %s)' % (s['source'], round(0.01, 2), u'\u21AF'))
				elif s['status'] == 'active' and 's_time' in s.keys():
					str.append('%s (%ss. %s)' % (s['source'], round(time.time()-s['s_time'], 2), u'\u21AF'))
					
		ret_str = (' ,'.join(x for x in str))
		return ret_str
		
	def getETAProgress(self, key=None, type='movie'):

		c = 0
		if key in self.threads.keys():
			for s in self.threadSlots[key]:
				try:
					if s['status'] == 'idle':
						c += self.providersTimer[s['source']][type]
					elif s['status'] == 'active':
						c += max(self.providersTimer[s['source']][type] - (time.time()-s['s_time']), 0)
				except:
					return None
		return round(c,2)
			
	def checkKeyInThread(self, key=None):
	
		if key in self.threads.keys():
			return True
		else:
			return False

	def getMovieSource(self, title, year, imdb, proxy_options, key, source, call):
		
		try:
			url = call.get_movie(imdb=imdb, title=title, year=year, proxy_options=proxy_options, key=key)
			if url == None: raise Exception()
		except:
			pass

		try:
			sources = []
			sources = call.get_sources(url=url, hostDict=self.hosthdfullDict, hosthdDict=self.hostsdfullDict, locDict=self.hostlocDict, proxy_options=proxy_options, key=key)
			if sources == None: sources = []
			self.sources.extend(sources)
		except:
			pass
			
		for s in self.threadSlots[key]:
			if s['source'] == source:
				s['status'] = 'done'
				s['e_time'] = time.time()
				if 'movie' in self.providersTimer[source].keys():
					self.providersTimer[source]['movie'] += s['e_time'] - s['s_time']
					self.providersTimer[source]['movie'] = self.providersTimer[source]['movie']/2
				else:
					self.providersTimer[source]['movie'] = s['e_time'] - s['s_time']
				control.control_json[source]['movie'] = self.providersTimer[source]['movie']
				break


	def getEpisodeSource(self, title, year, imdb, tvdb, season, episode, tvshowtitle, date, proxy_options, key, source, call):
		
		try:
			url = call.get_show(imdb=imdb, tvdb=tvdb, tvshowtitle=tvshowtitle, year=year, season=season, proxy_options=proxy_options, key=key)
			if url == None: raise Exception()
		except:
			pass

		ep_url = None
		
		try:
			if episode == None: raise Exception()
			if ep_url == None: ep_url = call.get_episode(url=url, imdb=imdb, tvdb=tvdb, title=tvshowtitle, year=year, season=season, episode=episode, proxy_options=proxy_options, key=key)
			if ep_url == None: raise Exception()
		except:
			pass

		try:
			sources = []
			sources = call.get_sources(url=ep_url, hostDict=self.hosthdfullDict, hosthdDict=self.hostsdfullDict, locDict=self.hostlocDict, proxy_options=proxy_options, key=key)
			if sources == None: sources = []
			self.sources.extend(sources)
		except:
			pass
			
		for s in self.threadSlots[key]:
			if s['source'] == source:
				s['status'] = 'done'
				s['e_time'] = time.time()
				if 'tv' in self.providersTimer[source].keys():
					self.providersTimer[source]['tv'] += s['e_time'] - s['s_time']
					self.providersTimer[source]['tv'] = self.providersTimer[source]['tv']/2
				else:
					self.providersTimer[source]['tv'] = s['e_time'] - s['s_time']
				control.control_json[source]['tv'] = self.providersTimer[source]['tv']
				break

	def clearSources(self, key=None):
		try:
			del self.sources[:]
			self.sources = []
			self.threads.clear()
			self.threadSlots.clear()
			self.threads = {}
			self.threadSlots = {}	
		except Exception as e:
			log(type='ERROR', err='clearSources : %s' % e)
			
	def purgeSources(self, maxcachetimeallowed=0, override=False):
		try:
			filtered = []
			maxcachetimeallowed = float(maxcachetimeallowed)
			curr_time = time.time()
			if override == True:
				pass
			else:
				# if cache time < 2min; then get the sources from last 2min. otherwise it will always return 0 sources
				if maxcachetimeallowed < 2*60:
					maxcachetimeallowed = 2*60
				for i in self.sources:
					if (i['ts'] + float(maxcachetimeallowed)) >= curr_time:
						filtered.append(i)
				for k in self.threads:
					if self.checkKeyInThread(k) == True and self.checkProgress(k) == 100:
						del self.threads[k]
						del self.threadSlots[k]

			del self.sources[:]
			for i in filtered:
				self.sources.append(i)
		except Exception as e:
			log(type='ERROR', err='clearSources : %s' % e)
			
	def purgeSourcesKey(self, key=None, maxcachetimeallowed=0):
		try:
			filtered = []
			curr_time = time.time()
			if key == None:
				return False
			else:
				# if cache time < 2min; then get the sources from last 2min. otherwise it will always return 0 sources
				bool = False
				if maxcachetimeallowed < 2*60:
					maxcachetimeallowed = 2*60
				for i in self.sources:
					if (i['ts'] + float(maxcachetimeallowed)) >= curr_time:
						pass
					else:
						self.sources.remove(i)
						bool = True
				
				if self.checkKeyInThread(key) == True and self.checkProgress(key) == 100:
					del self.threads[key]
					del self.threadSlots[key]
					bool = True

		except Exception as e:
			log(type='ERROR', err='purgeSourcesKey : %s' % e)
			bool = False
			
		return bool

	def sourcesFilter(self, key=None):
		try:
			filter_extSources = []
			dups = []
			for i in self.sources:
				if i['url'] not in dups:
					if key == None:
						filter_extSources.append(i)
						dups.append(i['url'])
					elif i['key'] == key:
						filter_extSources.append(i)
						dups.append(i['url'])
					
			return filter_extSources
		except Exception as e:
			log(type='ERROR', err='sourcesFilter : %s' % e)
	

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

def log(err='', type='INFO', logToControl=True, doPrint=True, name='control', method=''):
	try:
		msg = '%s: %s > %s > %s : %s' % (time.ctime(time.time()), type, name, method, err)
		if logToControl == True:
			control.log(msg)
		if control.doPrint == True and doPrint == True:
			print msg
	except Exception as e:
		control.log('Error in Logging: %s >>> %s' % (msg,e))
