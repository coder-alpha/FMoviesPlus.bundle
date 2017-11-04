import time, sys, os, json, re

# try:
	# try:
		# PATH_R = os.path.dirname(os.path.abspath(__file__)).split('Code')[0]
	# except:
		# PATH_R = os.path.dirname(os.path.abspath('__file__')).split('Code')[0]
		
	# PATH = os.path.join(PATH_R, 'Libraries/Shared')
	# sys.path.insert(0,PATH)
# except:
	# pass

import omdb
from resources.lib.sources import sources
from resources.lib import resolvers
from resources.lib.libraries import client, control

initA = []
initBool = []

InterfaceThread = {}
InterfaceThreadLastQuery = {'LastQuery':''}

def init():

	del initA[:]
	del initBool[:]
	
	init = sources()
	initA.append(init)
	
	return "Interface Framework Initialized"
	
def isInitialized():
	if len(initA) > 0:
		return True
	else:
		return False
	
def wait_for_init(timeout=300):

	if len(initA) == 0 and len(initBool) == 0:
		initBool.append(True)
		init()

	c = 0
	while len(initA) == 0 and c < timeout:
		time.sleep(1)
		c += 1
		
	if len(initA) == 0:
		return False
	else:
		return True

def runGetSources(
	name = None,
	title = None,
	year = None,
	ver = None,
	imdb = None,
	tmdb = None,
	tvdb = None,
	tvrage = None,
	season = None,
	episode = None,
	tvshowtitle = None,
	alter = None,
	date = None,
	meta = None,
	proxy_options = None,
	provider_options = None,
	key = None,
	useCached = True,
	session = None):
	
	# fix stuff
	if episode != None:
		try:
			ep = int(episode)
			episode = str(ep)
		except:
			pass
			
	if season != None:
		try:
			sea = int(season)
			season = str(sea)
		except:
			pass
			
	if useCached == True:
		srcs = getSources(encode=False)
		filter_extSources = []
		filter_extSources += [i for i in srcs if i['key'] == key]
		if len(filter_extSources) > 0:
			if Prefs["use_debug"]:
				Log("name:%s title:%s tvshowtitle:%s year:%s season:%s episode:%s imdb:%s key:%s" % (name, title, tvshowtitle, year, season, episode, imdb, key))
				Log("Available in Cache Already. key: %s" % key)
			return

	if imdb == None:
		try:
			#res = omdb.request(t=title, y=int(year), c=Prefs['ca_api_key'], ver=ver, r='json', timeout=10)
			res = searchOMDB(title=title, year=year, doSearch=False, ver=ver)
			imdb_t = json.loads(res.content)['imdbID']
			imdb = imdb_t
		except:
			pass
			
	if Prefs["use_debug"]:
		Log("name:%s title:%s tvshowtitle:%s year:%s season:%s episode:%s imdb:%s key:%s" % (name, title, tvshowtitle, year, season, episode, imdb, key))

	if wait_for_init() == False:
		return
		
	initA[0].getSources(name, title, year, imdb, tmdb, tvdb, tvrage, season, episode, tvshowtitle, alter, date, proxy_options, provider_options, key, session)
	
	# while initA[0].checkProgress() != 100:
		# time.sleep(1)
		# if Prefs["use_debug"]:
			# Log('Threads progress: %s' % initA[0].checkProgress())
	
	# sources = initA[0].sourcesFilter()
	# if Prefs["use_debug"]:
		# Log("Length sources: %s" % len(sources))
		# for source in sources:
			# if True:# and source['provider'] == 'G2G':
				# Log('Provider---------: %s' % source['provider'])
				# Log('Source---------: %s' % source)
				# Log('Online----------: %s' % source['online'])
				# #Log('Type: %s --- Quality: %s' % (source['rip'],source['quality']))
				# #Log('%s URL---------: %s' % (source['source'], source['url']))
				# #Log('Key: %s' % source['key'])
				# #Log('urldata: %s' % json.loads(client.b64decode(source['urldata'])))
				# #Log('params: %s' % json.loads(client.b64decode(source['params'])))
				
def searchOMDB(title, year=None, doSearch=False, ver=None):
	try:
		c=0
		res = None
		if doSearch:
			if Prefs["use_debug"]:
				Log("OMDB Search: Title:%s Year:%s" % (title,year))
			while res == None and c < 3:
				try:
					if year == None:
						res = omdb.search(title, c=Prefs['ca_api_key'], ver=ver)
					else:
						res = omdb.search('%s %s' % (title, year), c=Prefs['ca_api_key'], ver=ver)
				except:
					c += 1
					time.sleep(1.0)
		else:
			if Prefs["use_debug"]:
				Log("OMDB Request: Title:%s Year:%s" % (title,year))
			while res == None and c < 3:
				try:
					if year == None:
						res = omdb.request(t=title, r='json', c=Prefs['ca_api_key'], ver=ver, timeout=10)
					else:
						res = omdb.request(t=title, y=int(year), c=Prefs['ca_api_key'], ver=ver, r='json', timeout=10)
				except:
					c += 1
					time.sleep(1.0)

		return res
	except Exception as e:
		Log("interface.py>searchOMDB() >> : >>> %s" % (e))
		return None
		
def requestOMDB(t, y, Season, i, ver=None):
	try:
		if Prefs["use_debug"]:
			Log("OMDB Request: Title:%s Year:%s Season:%s imdb:%s" % (t,y,Season,i))
		
		c = 0
		res = None
		while res == None and c < 3:
			try:
				res = omdb.request(t=t, y=int(y), Season=str(Season), i=i, c=Prefs['ca_api_key'], ver=ver, r='json', timeout=10)
			except Exception as e:
				c += 1
				time.sleep(1.0)
		
		return res
	except Exception as e:
		Log("interface.py>requestOMDB() >> : >>> %s" % (e))
		return None
		
def getOMDB(title, year, season, episode, imdbid, ver=None):
	try:
		if Prefs["use_debug"]:
			Log("OMDB Request: Title:%s Year:%s Season:%s Episode:%s imdb:%s" % (title, year, season, episode, imdbid))
			
		c = 0
		res = None
		while res == None and c < 3:
			try:
				res = omdb.get(title=title, year=int(year), season=str(season), episode=str(episode), imdbid=imdbid, c=Prefs['ca_api_key'], ver=ver, timeout=10)
			except Exception as e:
				c += 1
				time.sleep(1.0)
		
		return res
	except Exception as e:
		Log("interface.py>requestOMDB() >> : >>> %s" % (e))
		return None

def clearSources():
	if wait_for_init() == False:
		return
	initA[0].clearSources()
	
def purgeSources(key, maxcachetimeallowed=0):
	if wait_for_init() == False:
		return
	#initA[0].purgeSources(maxcachetimeallowed=maxcachetimeallowed)
	initA[0].purgeSourcesKey(key=key, maxcachetimeallowed=maxcachetimeallowed)
	if Prefs["use_debug"]:
		Log('Purging source based on time-stamp. key: %s > maxcachetimeallowed: %s' % (key,maxcachetimeallowed))
	
def checkProgress(key, useCached=True):
	if wait_for_init() == False:
		return

	# if useCached:
		# srcs = getSources(encode=False)
		# filter_extSources = []
		# filter_extSources += [i for i in srcs if i['key'] == key]
		# if len(filter_extSources) > 0:
			# return 100
		
	prog = initA[0].checkProgress(key=key)
	# if Prefs['use_debug']:
		# Log("Progress request: %s" % prog)
	return prog
	
def getCacheItemsNo():
	if wait_for_init() == False:
		return

	srcs = getSources(encode=False)
	if srcs != None:
		return len(srcs)
		
	return 0
	
def getCacheSize():
	if wait_for_init() == False:
		return

	srcs = getSources(encode=False)
	if srcs != None:
		return sys.getsizeof(srcs)
		
	return 0
	
def getSources(key=None, encode=True):
	if wait_for_init() == False:
		return

	if encode:
		return E(JSON.StringFromObject(initA[0].sourcesFilter(key=key)))
		
	return initA[0].sourcesFilter(key=key)
	
def getProxies():
	if wait_for_init() == False:
		return
	return E(JSON.StringFromObject(initA[0].getProxies()))
	
def getHosts(encode=True):
	if wait_for_init() == False:
		return
		
	if encode == False:
		return initA[0].getHosts()
		
	return E(JSON.StringFromObject(initA[0].getHosts()))
	
def getHostsPlaybackSupport(encode=True):
	if wait_for_init() == False:
		return
		
	if encode == False:
		return initA[0].getHostsPlaybackSupport()
		
	return E(JSON.StringFromObject(initA[0].getHostsPlaybackSupport()))
	
def getProviders(encode=True):
	if wait_for_init() == False:
		return
		
	if encode == False:
		return initA[0].getProviders()
		
	return E(JSON.StringFromObject(initA[0].getProviders()))
	
def getProvidersLoggerTxts(choice=None, dumpToLog=True):
	if wait_for_init() == False:
		return
	loggertxt = []
	if Prefs["use_debug"] or choice != None:
		#Log(" === LOGGER txt START === ")
		for provider in initA[0].providersCaller:
			try:
				if choice == None:
					if dumpToLog == True:
						Log(" === Provider: %s Start ===" % provider['name'])
					provider['call'].getLog()
					for txt in provider['call'].loggertxt:
						loggertxt.append(txt)
						if dumpToLog == True:
							Log(txt)
					if dumpToLog == True:
						Log(" === Provider: %s End ===" % provider['name'])
				elif choice == provider['name']:
					if dumpToLog == True:
						Log(" === Provider: %s Start ===" % provider['name'])
					provider['call'].getLog()
					for txt in provider['call'].loggertxt:
						loggertxt.append(txt)
						if dumpToLog == True:
							Log(txt)
					if dumpToLog == True:
						Log(" === Provider: %s End ===" % provider['name'])
			except Exception as e:
				Log(e)	
		#Log(" === LOGGER txt END === ")
	return list(reversed(loggertxt))

	
def getHostsLoggerTxts(choice=None, dumpToLog=True):
	if wait_for_init() == False:
		return
	loggertxt = []
	if Prefs["use_debug"] or choice != None:
		#Log(" === LOGGER txt START === ")
		for host in initA[0].hostsCaller():
			try:
				if choice == None:
					if dumpToLog == True:
						Log(" === Host: %s Start ===" % host['name'])
					host['call'].getLog()
					for txt in host['call'].loggertxt:
						loggertxt.append(txt)
						if dumpToLog == True:
							Log(txt)
					if dumpToLog == True:
						Log(" === Host: %s End ===" % host['name'])
				elif choice == host['name']:
					if dumpToLog == True:
						Log(" === Host: %s Start ===" % host['name'])
					host['call'].getLog()
					for txt in host['call'].loggertxt:
						loggertxt.append(txt)
						if dumpToLog == True:
							Log(txt)
					if dumpToLog == True:
						Log(" === Host: %s End ===" % host['name'])
			except Exception as e:
				Log(e)				
		#Log(" === LOGGER txt END === ")
	return list(reversed(loggertxt))
	
def getControlLoggerTxts():
	if wait_for_init() == False:
		return
	loggertxt = []
	if Prefs["use_debug"]:
		Log(" === CONTROL txt Start ===")
		for txt in control.loggertxt:
			loggertxt.append(txt)
			Log(txt)
		Log(" === CONTROL txt End ===")
	return loggertxt
	
def getExtSourcesThreadStatus(key=None):
	if key in InterfaceThread:
		if InterfaceThreadLastQuery['LastQuery'] == key:
			return True
		return InterfaceThread[key]
	return False
	
def checkKeyInThread(key=None):
	
	return initA[0].checkKeyInThread(key=key)
		
def getExtSources(movtitle=None, year=None, tvshowtitle=None, season=None, episode=None, proxy_options=None, provider_options=None, key=None, maxcachetime=0, ver=None, imdb_id=None, session=None):

	InterfaceThread[key] = True
	
	if wait_for_init() == False:
		return
		
	purgeSources(key=key, maxcachetimeallowed=maxcachetime)

	if movtitle != None:
		p = re.compile('(.())\(([^()]|())*\)')
		m = p.search(movtitle)
		if m:
			name = movtitle.replace(m.group(),'').strip()
		else:
			name = movtitle.strip()
	elif tvshowtitle !=None:
		name = tvshowtitle
		
	runGetSources(
	name = name,
	title = name,
	year = year,
	ver = ver,
	tvshowtitle = tvshowtitle,
	season = season,
	episode = episode,
	proxy_options = proxy_options,
	provider_options = provider_options,
	key = key,
	imdb=imdb_id,
	useCached = True,
	session=session)
	
	# if Prefs['use_debug']:
		# Log("Movie: %s" % movtitle)
	
	while initA[0].checkProgress(key) != 100:
		time.sleep(2)
		#os.system('cls')
		#print 'Threads progress: %s' % initA[0].checkProgress()
		#if Prefs["use_debug"]:
		#	Log('Threads key: %s progress: %s' % (key,initA[0].checkProgress(key)))
		
		
	InterfaceThreadLastQuery['LastQuery'] = key
	InterfaceThread[key] = False
	
	return E(JSON.StringFromObject(initA[0].sourcesFilter(key=key)))
	
def request(url, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout='30', httpsskip=False, use_web_proxy=False, XHR=False, IPv4=False, hideurl=False):

	if hideurl == True:
		Log.Debug("Requesting (via Interface) : %s" % client.getUrlHost(url))
	else:
		Log.Debug("Requesting (via Interface) : %s" % url)
	if Prefs["use_debug"]:
		Log("Headers: %s" % headers)

	return client.request(url=url, close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=timeout, httpsskip=httpsskip, use_web_proxy=use_web_proxy, XHR=XHR, IPv4=IPv4)
	
def request_via_proxy(url, proxy_name, proxy_url, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout='30', httpsskip=False, use_web_proxy=False, XHR=False, IPv4=False, hideurl=False):
	if wait_for_init() == False:
		return
		
	if hideurl == True:
		Log.Debug("Requesting (via Interface) : %s" % client.getUrlHost(url))
	else:
		Log.Debug("Requesting (via Interface) : %s" % url)
	if Prefs["use_debug"]:
		Log("Headers: %s" % headers)
		
	return initA[0].request_via_proxy(url=url, proxy_name=proxy_name, proxy_url=proxy_url, close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=timeout, httpsskip=httpsskip, use_web_proxy=use_web_proxy, XHR=XHR, IPv4=IPv4)
	
def request_via_proxy_as_backup(url, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout='30', httpsskip=False, XHR=False, IPv4=False, hideurl=False):
	if wait_for_init() == False:
		return
		
	if hideurl == True:
		Log.Debug("Requesting (via Interface) : %s" % client.getUrlHost(url))
	else:
		Log.Debug("Requesting (via Interface) : %s" % url)
		
	if Prefs["use_debug"]:
		Log("Headers: %s" % headers)
		
	use_web_proxy=False
	use_web_proxy_as_backup=True
	return initA[0].request_via_proxy(url=url, proxy_name=None, proxy_url=None, close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=timeout, httpsskip=httpsskip, XHR=XHR, use_web_proxy=use_web_proxy, use_web_proxy_as_backup=use_web_proxy_as_backup, IPv4=IPv4)

def test():
	print init()
	
#test()