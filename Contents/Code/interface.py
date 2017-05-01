import time, sys, os, json, re
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
	useCached = True):
	
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
			
	if useCached:
		srcs = getSources(encode=False)
		filter_extSources = []
		filter_extSources += [i for i in srcs if i['key'] == key]
		if len(filter_extSources) > 0:
			if Prefs["use_debug"]:
				Log("name:%s title:%s tvshowtitle:%s year:%s season:%s episode:%s imdb:%s key:%s" % (name, title, tvshowtitle, year, season, episode, imdb, key))
				Log("Available in Cache Already. Key: %s" % key)
			return
	
	if imdb == None:
		try:
			res = omdb.request(t=title, y=int(year), r='json', timeout=10)
			imdb_t = json.loads(res.content)['imdbID']
			imdb = imdb_t
		except:
			pass
		
	if Prefs["use_debug"]:
		Log("name:%s title:%s tvshowtitle:%s year:%s season:%s episode:%s imdb:%s key:%s" % (name, title, tvshowtitle, year, season, episode, imdb, key))
	
	if wait_for_init() == False:
		return
		
	initA[0].getSources(name, title, year, imdb, tmdb, tvdb, tvrage, season, episode, tvshowtitle, alter, date, proxy_options, provider_options, key)
	
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
				
def searchOMDB(title, year=None, doSearch=False):
	try:
		if doSearch:
			print "OMDB Search"
			if year == None:
				res = omdb.search(title)
			else:
				res = omdb.search('%s %s' % (title, year))
		else:
			print "OMDB Request"
			if year == None:
				res = omdb.request(t=title, r='json', timeout=10)
			else:
				res = omdb.request(t=title, y=int(year), r='json', timeout=10)
		
		return res
	except:
		return None

def clearSources():
	if wait_for_init() == False:
		return
	initA[0].clearSources()
	
def purgeSources(maxcachetimeallowed=0):
	if wait_for_init() == False:
		return
	initA[0].purgeSources(maxcachetimeallowed=maxcachetimeallowed)
	
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
	
def getSources(encode=True):
	if wait_for_init() == False:
		return

	if encode:
		return E(JSON.StringFromObject(initA[0].sourcesFilter()))
		
	return initA[0].sourcesFilter()
	
def getProxies():
	if wait_for_init() == False:
		return
	return E(JSON.StringFromObject(initA[0].getProxies()))
	
def getHosts():
	if wait_for_init() == False:
		return
	return E(JSON.StringFromObject(initA[0].getHosts()))
	
def getProviders():
	if wait_for_init() == False:
		return
	return E(JSON.StringFromObject(initA[0].getProviders()))
	
def getProvidersLoggerTxts():
	if wait_for_init() == False:
		return
	loggertxt = []
	if Prefs["use_debug"]:
		Log(" === LOGGER txt START === ")
		for provider in initA[0].providersCaller:
			Log(" === Provider: %s Start ===" % provider['name'])
			for txt in provider['call'].loggertxt:
				loggertxt.append(txt)
				Log(txt)
			Log(" === Provider: %s Start End ===" % provider['name'])
			
			Log(" === CONTROL txt Start ===")
			for txt in control.loggertxt:
				loggertxt.append(txt)
				Log(txt)
			Log(" === CONTROL txt End ===")
		Log(" === LOGGER txt END === ")
	return loggertxt
	
def getExtSourcesThreadStatus(key=None):
	if key in InterfaceThread:
		if InterfaceThreadLastQuery['LastQuery'] == key:
			return True
		return InterfaceThread[key]
	return False
		
def getExtSources(movtitle=None, year=None, tvshowtitle=None, season=None, episode=None, proxy_options=None, provider_options=None, key=None, maxcachetime=0):

	InterfaceThread[key] = True
	
	if wait_for_init() == False:
		return
		
	purgeSources(maxcachetimeallowed=maxcachetime)

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
	tvshowtitle = tvshowtitle,
	season = season,
	episode = episode,
	proxy_options = proxy_options,
	provider_options = provider_options,
	key = key)
	
	# if Prefs['use_debug']:
		# Log("Movie: %s" % movtitle)
	
	while initA[0].checkProgress() != 100:
		time.sleep(0.5)
		#os.system('cls')
		print 'Threads progress: %s' % initA[0].checkProgress()
		# Log('Threads progress: %s' % initA[0].checkProgress())
		
		
	InterfaceThreadLastQuery['LastQuery'] = key
	InterfaceThread[key] = False
	
	return E(JSON.StringFromObject(initA[0].sourcesFilter()))
	
def request(url, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout='30', httpsskip=False, use_web_proxy=False, XHR=False):

	Log.Debug("Requesting (via Interface) : %s" % url)
	if Prefs["use_debug"]:
		Log("Headers: %s" % headers)

	return client.request(url=url, close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=timeout, httpsskip=httpsskip, use_web_proxy=use_web_proxy, XHR=XHR)
	
def request_via_proxy(url, proxy_name, proxy_url, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout='30', httpsskip=False, use_web_proxy=False, XHR=False):
	if wait_for_init() == False:
		return
		
	Log.Debug("Requesting (via Interface) : %s" % url)
	if Prefs["use_debug"]:
		Log("Headers: %s" % headers)
		
	return initA[0].request_via_proxy(url=url, proxy_name=proxy_name, proxy_url=proxy_url, close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=timeout, httpsskip=httpsskip, use_web_proxy=use_web_proxy, XHR=XHR)
	
def request_via_proxy_as_backup(url, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout='30', httpsskip=False, XHR=False):
	if wait_for_init() == False:
		return
		
	Log.Debug("Requesting (via Interface) : %s" % url)
	if Prefs["use_debug"]:
		Log("Headers: %s" % headers)
		
	use_web_proxy=False
	use_web_proxy_as_backup=True
	return initA[0].request_via_proxy(url=url, proxy_name=None, proxy_url=None, close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=timeout, httpsskip=httpsskip, XHR=XHR, use_web_proxy=use_web_proxy, use_web_proxy_as_backup=use_web_proxy_as_backup)

	