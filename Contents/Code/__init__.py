######################################################################################
#
#	FMovies.se by Coder Alpha
# 	https://github.com/coder-alpha/FMoviesPlus.bundle
#
######################################################################################

import re, urllib, urllib2, json, sys, time, random
import common, updater, fmovies, playback
from DumbTools import DumbKeyboard

SITE = "FMovies"
TITLE = common.TITLE
PREFIX = common.PREFIX
ART = "art-default.jpg"
ICON = "icon-fmovies.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_SEARCH_QUE = "icon-search-queue.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_FILTER = "icon-filter.png"
ICON_GENRE = "icon-genre.png"
ICON_LATEST = "icon-latest.png"
ICON_SIMILAR = "icon-similar.png"
ICON_OTHERSEASONS = "icon-otherseasons.png"
ICON_HOT = "icon-hot.png"
ICON_ENTER = "icon-enter.png"
ICON_QUEUE = "icon-bookmark.png"
ICON_UNAV = "MoviePosterUnavailable.jpg"
ICON_PREFS = "icon-prefs.png"
ICON_UPDATE = "icon-update.png"
ICON_UPDATE_NEW = "icon-update-new.png"
ICON_DEVICE_OPTIONS = "icon-device-options.png"
ICON_OPTIONS = "icon-options.png"
ICON_CLEAR = "icon-clear.png"
ICON_DK_ENABLE = "icon-dumbKeyboardE.png"
ICON_DK_DISABLE = "icon-dumbKeyboardD.png"
ICON_GL_ENABLE = "icon-gl-enable.png"
ICON_GL_DISABLE = "icon-gl-disable.png"
ICON_INFO = "icon-info.png"
ICON_STAR = "icon-star.png"
ICON_PEOPLE = "icon-people.png"
ICON_TAG = "icon-tag.png"
ICON_OTHERPROVIDERS = "icon-otherproviders.png"
ICON_OTHERHOSTS = "icon-otherhosts.png"
ICON_OTHERSOURCES = "icon-othersources.png"
ICON_SAVE = "icon-save.png"
ICON_QUALITIES = "icon-qualities.png"
ICON_RIPTYPE = "icon-riptype.png"
ICON_QUESTION = "icon-question.png"
ICON_PROXY = "icon-proxy.png"
ICON_PROXY_DEFAULT = "icon-proxy-default.png"
ICON_REFRESH = "icon-refresh.png"
ICON_ALERT = "icon-alert.png"
ICON_HELP = "icon-help.png"
ICON_OK = "icon-ok.png"
ICON_NOTOK = "icon-error.png"
ICON_SUMMARY = "icon-summary.png"
ICON_VIDTYPE = "icon-videotype.png"

MC = common.NewMessageContainer(common.PREFIX, common.TITLE)

######################################################################################
# Set global variables

CAT_WHATS_HOT = ['Sizzlers','Most Favourited','Recommended','Most Watched This Week','Most Watched This Month','Latest Movies','Latest TV-Series','Requested Movies']
CAT_REGULAR = ['Movies','TV-Series','Top-IMDb','Most Watched']
CAT_FILTERS = ['Release','Genre','Country','Filter Setup >>>']
CAT_GROUPS = ['What\'s Hot ?', 'Movies & TV-Series', 'Sort using...','Site News']

Filter = {}
Filter_Search = {}

SITE_NEWS_LOCS = []

VALID_PREFS_MSGS = []

CONVERT_BMS = []

CUSTOM_TIMEOUT_DICT = {}

CUSTOM_TIMEOUT_CLIENTS = {'Plex Web': 15}

######################################################################################

def Start():

	Thread.Create(SleepAndUpdateThread)
	Thread.Create(SleepPersistAndUpdateCookie)
	
	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	#DirectoryObject.thumb = R(ICON_LIST)
	DirectoryObject.art = R(ART)
	#VideoClipObject.thumb = R(ICON_UNAV)
	VideoClipObject.art = R(ART)
	
	common.CACHE.clear()
	common.CACHE_META.clear()
	HTTP.ClearCache()
	
	try:
		CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
	except:
		CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
		
	HTTP.CacheTime = CACHE_EXPIRY
	HTTP.Headers['User-Agent'] = common.client.randomagent()
	fmovies.BASE_URL = Prefs["base_url"]
	HTTP.Headers['Referer'] = fmovies.BASE_URL
	
	DumpPrefs()
	ValidateMyPrefs()
	
	# convert old style bookmarks to new
	if len(CONVERT_BMS) == 0:
		convertbookmarks()

######################################################################################
# Menu hierarchy
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
@route(PREFIX + "/MainMenu")
def MainMenu(**kwargs):

	fmovies.BASE_URL = Prefs["base_url"]
	HTTP.Headers['Referer'] = fmovies.BASE_URL
	
	session = common.getSession()
	ClientInfo(session=session)
	if len(VALID_PREFS_MSGS) > 0:
		return DisplayMsgs()
	
	oc = ObjectContainer(title2=TITLE, no_cache=isForceNoCache())
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[0], session=session), title = CAT_GROUPS[0], thumb = R(ICON_HOT)))
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[1], session=session), title = CAT_GROUPS[1], thumb = R(ICON_MOVIES)))
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[2], session=session), title = CAT_GROUPS[2], thumb = R(ICON_FILTER)))
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[3], session=session), title = CAT_GROUPS[3], thumb = R(ICON_INFO)))
	
	# ToDo: Not quite sure how to read back what was actually played from ServiceCode and not just show a viewed item
	oc.add(DirectoryObject(key = Callback(RecentWatchList, title="Recent WatchList", session=session), title = "Recent WatchList", thumb = R(ICON_LATEST)))
	oc.add(DirectoryObject(key = Callback(Bookmarks, title="Bookmarks"), title = "Bookmarks", thumb = R(ICON_QUEUE)))
	oc.add(DirectoryObject(key = Callback(SearchQueueMenu, title = 'Search Queue'), title = 'Search Queue', summary='Search using saved search terms', thumb = R(ICON_SEARCH_QUE)))
	
	if common.UsingOption(key=common.DEVICE_OPTIONS[0], session=session):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
	
	oc.add(DirectoryObject(key = Callback(Options, session=session), title = 'Options', thumb = R(ICON_OPTIONS), summary='Options that can be accessed from a Client, includes Enabling DumbKeyboard & Clearing Cache'))
	#oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
	
	oc.add(DirectoryObject(key = Callback(Help), title = "Help", summary = "Help and tutorial videos.", thumb = R(ICON_HELP)))
	
	try:
		if updater.update_available()[0]:
			oc.add(DirectoryObject(key = Callback(updater.menu, title='Update Plugin'), title = 'Update (New Available)', thumb = R(ICON_UPDATE_NEW)))
		else:
			oc.add(DirectoryObject(key = Callback(updater.menu, title='Update Plugin'), title = 'Update (Running Latest)', thumb = R(ICON_UPDATE)))
	except:
		pass
	
	return oc
	

######################################################################################
@route(PREFIX + "/SiteCookieRoutine")
def SiteCookieRoutine(session=None, reset=False, dump=False, quiet=False, **kwargs):

	# This will get/set cookie that might be required for search before listing stage
	fmovies.setTokenCookie(use_debug=Prefs["use_debug"], reset=reset, dump=dump, quiet=quiet)

######################################################################################
@route(PREFIX + "/SleepPersistAndUpdateCookie")
def SleepPersistAndUpdateCookie(**kwargs):

	while common.interface.isInitialized() == False:
		time.sleep(1)

	SLEEP_TIME = 5 * 60
	while True:
		SiteCookieRoutine(quiet=True)
		if Prefs["use_debug"]:
			Log("Thread SleepPersistAndUpdateCookie: Sleeping for %s mins." % int(SLEEP_TIME/60))
		time.sleep(SLEEP_TIME)
	
######################################################################################
@route(PREFIX + "/SleepAndUpdateThread")
def SleepAndUpdateThread(update=True, startthread=True, session=None, **kwargs):

	if update == True:
		x1 = time.time()
		ret = common.interface.init()
		x2 = time.time()

		Log("%s on %s !" % (ret, time.ctime(x2)))
		Log("Interface Initialization took %s sec. !" % (x2-x1))
			
	if session == None:
		session = common.getSession()
	
	try:
		LOAD_T = Dict['INTERNAL_SOURCES_QUALS']
		if LOAD_T != None:
			ARRAY_T = JSON.ObjectFromString(D(LOAD_T))
		if LOAD_T != None and len(ARRAY_T) > 0:
			del common.INTERNAL_SOURCES_QUALS[:]
			for q in ARRAY_T:
				common.INTERNAL_SOURCES_QUALS.append(q)
		else:
			del common.INTERNAL_SOURCES_QUALS[:]
			for q in common.INTERNAL_SOURCES_QUALS_CONST:
				common.INTERNAL_SOURCES_QUALS.append(q)
	except:
		pass
	#Log("common.INTERNAL_SOURCES_QUALS %s" % INTERNAL_SOURCES_QUALS)

	try:
		LOAD_T = Dict['INTERNAL_SOURCES_RIPTYPE']
		if LOAD_T != None:
			ARRAY_T = JSON.ObjectFromString(D(LOAD_T))
		if LOAD_T != None and len(ARRAY_T) > 0:
			del common.INTERNAL_SOURCES_RIPTYPE[:]
			for r in ARRAY_T:
				common.INTERNAL_SOURCES_RIPTYPE.append(r)
		else:
			del common.INTERNAL_SOURCES_RIPTYPE[:]
			for q in common.INTERNAL_SOURCES_RIPTYPE_CONST:
				common.INTERNAL_SOURCES_RIPTYPE.append(q)
	except:
		pass
	#Log("common.INTERNAL_SOURCES_RIPTYPE %s" % INTERNAL_SOURCES_RIPTYPE)
	
	try:
		LOAD_T = Dict['INTERNAL_SOURCES_FILETYPE']
		if LOAD_T != None:
			ARRAY_T = JSON.ObjectFromString(D(LOAD_T))
		if LOAD_T != None and len(ARRAY_T) > 0:
			del common.INTERNAL_SOURCES_FILETYPE[:]
			for r in ARRAY_T:
				common.INTERNAL_SOURCES_FILETYPE.append(r)
		else:
			del common.INTERNAL_SOURCES_FILETYPE[:]
			for q in common.INTERNAL_SOURCES_FILETYPE_CONST:
				common.INTERNAL_SOURCES_FILETYPE.append(q)
	except:
		pass
	#Log("common.INTERNAL_SOURCES_FILETYPE %s" % INTERNAL_SOURCES_FILETYPE)

	try:
		LOAD_T = Dict['OPTIONS_PROVIDERS']
		curr_provs = LOAD_T
		ExtProviders(curr_provs=curr_provs,session=session)
	except:
		ExtProviders()
		
	try:
		LOAD_T = Dict['OPTIONS_PROXY']
		curr_proxies = LOAD_T
		proxy = JSON.ObjectFromString(D(curr_proxies))
		#Log("loaded proxy %s" % proxy)
		proxy_n = E(JSON.StringFromObject(proxy[0]))
		ExtProxies(n=proxy_n,curr_proxies=curr_proxies,session=session)
	except:
		ExtProxies(session=session)
		
	try:
		LOAD_T = Dict['INTERNAL_SOURCES']
		curr_sources = LOAD_T
		sources = JSON.ObjectFromString(D(curr_sources))
		#Log("sources %s" % sources)
		sources_n = E(JSON.StringFromObject(sources[0]))
		ExtHosts(n=sources_n,curr_sources=curr_sources,session=session)
	except:
		ExtHosts(session=session)
		
	# time.sleep(120)
	# if startthread == True:
		# while True:
			# time.sleep(60*60)
			# ret = common.interface.init()
			# if Prefs["use_debug"]:
				# Log("%s at %s !" % (ret, time.ctime(time.time())))
		
	
######################################################################################
@route(PREFIX + "/GetCacheTimeString")
def GetCacheTimeString(**kwargs):

	time_str = 0
	
	if common.CACHE_EXPIRY == 0:
		time_str = int(time.time())

	return time_str

######################################################################################
@route(PREFIX + "/options")
def Options(session=None, **kwargs):

	oc = ObjectContainer(title2='Options', no_cache=isForceNoCache())
	
	if session == None:
		session = common.getSession()
	
	oc.add(DirectoryObject(key = Callback(DeviceOptions, session=session), title = 'Device Options', thumb = R(ICON_DEVICE_OPTIONS), summary='Device Specific Options includes Enabling DumbKeyboard, Redirector and List View mode'))
	
	msg = '%s' % (len(common.CACHE)+len(common.CACHE_META))
	smsg = msg
	extmemory = 0
	if common.interface.isInitialized():
		smsg = '%s' % (len(common.CACHE) + len(common.CACHE_META) + common.interface.getCacheItemsNo())
		msg = '%s Internal, %s External' % (len(common.CACHE), common.interface.getCacheItemsNo())
		extmemory = common.interface.getCacheSize()
	
	oc.add(DirectoryObject(key = Callback(ClearCache), title = "Clear Cache (%s items)" % smsg, summary='Forces clearing of the Cached cookies, sources and webpages. %s Cached Sources and %s WebPages/Links consuming %s KB memory.' % (msg,len(common.CACHE_META), round(((sys.getsizeof(common.CACHE)+sys.getsizeof(common.CACHE_META)+extmemory)/1024),2)), thumb = R(ICON_CLEAR)))
	
	oc.add(DirectoryObject(key = Callback(ResetCookies), title = "Reset Cookies", summary='Reset Session, CF, etc. cookies', thumb = R(ICON_CLEAR)))
	
	if common.interface.isInitialized():
		oc.add(DirectoryObject(key = Callback(InterfaceOptions, session=session), title = 'Interface Options', thumb = R(ICON_PREFS), summary='Interface for Proxies, Hosts, Providers and Playback Quality'))
		oc.add(DirectoryObject(key = Callback(ResetExtOptions), title = "Reset Interface Options", summary='Resets Interface Options', thumb = R(ICON_REFRESH)))
	else:
		oc.add(DirectoryObject(key = Callback(Options, session=session), title = 'Interface Initializing.. Please wait & retry', thumb = R(ICON_ALERT)))
		
	return oc
	
######################################################################################
@route(PREFIX + "/deviceoptions")
def DeviceOptions(session=None, **kwargs):

	oc = ObjectContainer(title2='Device Options', no_cache=isForceNoCache())
	
	if session == None:
		session = common.getSession()
	c = 1
	for key in common.DEVICE_OPTIONS:
		summary = common.DEVICE_OPTION[key]
		bool = False if (Dict['Toggle'+key+session] == None or Dict['Toggle'+key+session] == 'disabled') else True
		title_msg = "%02d). %s %s | %s" % (c, common.GetEmoji(type=bool, mode='simple', session=session), key, summary)
		oc.add(DirectoryObject(key=Callback(common.setDictVal, key=key, val=not bool, session=session), title = title_msg))
		c += 1
	
	return oc
	
######################################################################################
@route(PREFIX + "/interfaceoptions")
def InterfaceOptions(session=None, **kwargs):
	
	oc = ObjectContainer(title2='Interface Options', no_cache=isForceNoCache())
	
	if session == None:
		session = common.getSession()
	
	try:
		proxy_n = None
		curr_proxies = None
		LOAD_T = Dict['OPTIONS_PROXY']
		curr_proxies = LOAD_T
		proxy = JSON.ObjectFromString(D(curr_proxies))
		#Log("proxy %s" % proxy)
		proxy_n = E(JSON.StringFromObject(proxy[0]))
	except Exception as e:
		Log("Proxy Loading > %s" % e.args)
		pass
	oc.add(DirectoryObject(key = Callback(ExtProxies,n=proxy_n, curr_proxies=curr_proxies, session=session), title = "Proxies", summary='List all the Proxies that are installed.', thumb = R(ICON_PROXY)))
	
	try:
		sources_n = None
		curr_sources = None
		LOAD_T = Dict['INTERNAL_SOURCES']
		curr_sources = LOAD_T
		sources = JSON.ObjectFromString(D(curr_sources))
		#Log("sources %s" % sources)
		sources_n = E(JSON.StringFromObject(sources[0]))
	except:
		pass
	oc.add(DirectoryObject(key = Callback(ExtHosts,n=sources_n, curr_sources=curr_sources, session=session), title = "External Hosts", summary='List all the External Hosts that are installed.', thumb = R(ICON_OTHERHOSTS)))
		
	try:
		curr_provs = None
		LOAD_T = Dict['OPTIONS_PROVIDERS']
		curr_provs = LOAD_T
	except:
		pass
	oc.add(DirectoryObject(key = Callback(ExtProviders,curr_provs=curr_provs, session=session), title = "External Providers", summary='Enable/Disable External Host Providers.', thumb = R(ICON_OTHERPROVIDERS)))
	
	oc.add(DirectoryObject(key = Callback(ExtHostsQuals, session=session), title = "Qualities Allowed", summary='Enable/Disable External Host Qualities.', thumb = R(ICON_QUALITIES)))
	oc.add(DirectoryObject(key = Callback(ExtHostsRipType, session=session), title = "Rip Type Allowed", summary='Enable/Disable External Host Rip Type.', thumb = R(ICON_RIPTYPE)))
	oc.add(DirectoryObject(key = Callback(ExtHostsFileType, session=session), title = "Video Type Allowed", summary='Enable/Disable External Host Video Type.', thumb = R(ICON_VIDTYPE)))
	oc.add(DirectoryObject(key = Callback(Summarize, session=session), title = "Summarize Options", summary='Shows a quick glance of all options', thumb = R(ICON_SUMMARY)))
	
	return oc
	
######################################################################################
@route(PREFIX + "/Summarize")
def Summarize(session=None, **kwargs):

	oc = ObjectContainer(title2='Summary of Options')
	c = 0
	for proxy in common.OPTIONS_PROXY:
		c += 1
		title_msg = "Enabled: %s | Proxy: %s | Url: %s | Captcha: %s | SSL: %s | Working: %s | Speed: %s sec." % (common.GetEmoji(type=proxy['working'], mode='simple', session=session), proxy['name'], proxy['url'], common.GetEmoji(type=str(proxy['captcha']), mode='simple', session=session), common.GetEmoji(type=proxy['SSL'], mode='simple', session=session), common.GetEmoji(type=proxy['working'], mode='simple', session=session), proxy['speed'])
		oc.add(DirectoryObject(title = title_msg, key = Callback(MC.message_container, header="Summary Screen", message="Does Nothing")))

	c = 0
	for host in common.INTERNAL_SOURCES:
		c += 1
		title_msg = "Enabled: %s | Host: %s | Quality: %s | Captcha: %s | Working: %s | Speed: %s sec." % (common.GetEmoji(type=host['working'], mode='simple', session=session), host['name'], host['quality'], common.GetEmoji(type=str(host['captcha']), mode='simple', session=session), common.GetEmoji(type=host['working'], mode='simple', session=session), host['speed'])
		oc.add(DirectoryObject(title = title_msg, key = Callback(MC.message_container, header="Summary Screen", message="Does Nothing")))

	c = 0
	for provider in common.OPTIONS_PROVIDERS:
		c += 1
		label = provider['name']
		bool = provider['enabled']
		website = provider['url']
		title_msg = "Enabled: %s | Provider: %s | Url: %s | Online: %s | Proxy Req.: %s | Parser: %s | Speed: %s sec." % (common.GetEmoji(type=bool, mode='simple', session=session), label, website, common.GetEmoji(type=str(provider['online']), mode='simple', session=session),common.GetEmoji(type=str(provider['online_via_proxy']), mode='simple', session=session), common.GetEmoji(type=str(provider['parser']), mode='simple', session=session), provider['speed'])
		oc.add(DirectoryObject(title = title_msg, key = Callback(MC.message_container, header="Summary Screen", message="Does Nothing")))
		
	
	for qual in common.INTERNAL_SOURCES_QUALS:
		label = qual['label']
		bool = qual['enabled']
		title_msg = "Enabled: %s | Quality: %s" % (common.GetEmoji(type=bool, mode='simple', session=session), label)
		oc.add(DirectoryObject(title = title_msg, key = Callback(MC.message_container, header="Summary Screen", message="Does Nothing")))
	

	for qual in common.INTERNAL_SOURCES_RIPTYPE:
		label = qual['label']
		bool = qual['enabled']
		title_msg = "Enabled: %s | Rip-Type: %s" % (common.GetEmoji(type=bool, mode='simple', session=session), label)
		oc.add(DirectoryObject(title = title_msg, key = Callback(MC.message_container, header="Summary Screen", message="Does Nothing")))
		
	for qual in common.INTERNAL_SOURCES_FILETYPE:
		label = qual['label']
		bool = qual['enabled']
		title_msg = "Enabled: %s | File-Type: %s" % (common.GetEmoji(type=bool, mode='simple', session=session), label)
		oc.add(DirectoryObject(title = title_msg, key = Callback(MC.message_container, header="Summary Screen", message="Does Nothing")))
		
	common.interface.getProvidersLoggerTxts()
		
	return oc
	

	
######################################################################################
@route(PREFIX + "/ExtHostsRipType")
def ExtHostsRipType(item=None, setbool='True', session=None, **kwargs):

	oc = ObjectContainer(title2='External Hosts RipType')
	
	if session == None:
		session = common.getSession()
	
	for qual in common.INTERNAL_SOURCES_RIPTYPE:
	
		label = qual['label']
		bool = qual['enabled']
		if bool == 'True':
			bool = True
		else:
			bool = False
		
		if label == item:
			bool = not bool
		
		title_msg = "Enabled: %s | Rip-Type: %s" % (common.GetEmoji(type=bool, mode='simple', session=session), label)
		oc.add(DirectoryObject(key = Callback(ExtHostsRipType, item=label, setbool=not bool), title = title_msg, thumb = Resource.ContentsOfURLWithFallback(url=None, fallback=None)))
		
	oc.add(DirectoryObject(
			key = Callback(MainMenu, update = MakeSelectionExtHostsRipType(item=item, setbool=setbool)),
			title = '<< Save Selection >>',
			summary = 'Save the Selection which is used when listing External Sources.',
			thumb = R(ICON_SAVE)
		))

	return oc
	
######################################################################################
@route(PREFIX + "/MakeSelectionExtHostsRipType")
def MakeSelectionExtHostsRipType(item=None, setbool='True', **kwargs):

	if item != None:
		ARRAY_T = []
		ARRAY_T += [q for q in common.INTERNAL_SOURCES_RIPTYPE]
		del common.INTERNAL_SOURCES_RIPTYPE[:]
		
		for qual in ARRAY_T:
			bool = qual['enabled']
			if item == qual['label']:
				bool = setbool
				
			qual['enabled'] = bool
			common.INTERNAL_SOURCES_RIPTYPE.append(qual)
		
	#Log(common.INTERNAL_SOURCES_RIPTYPE)
	Dict['INTERNAL_SOURCES_RIPTYPE'] = E(JSON.StringFromObject(common.INTERNAL_SOURCES_RIPTYPE))
	Dict.Save()
	
######################################################################################
@route(PREFIX + "/ExtHostsFileType")
def ExtHostsFileType(item=None, setbool='True', session=None, **kwargs):

	if item!=None and item in 'Movie/Show' and setbool == 'False':
		return MC.message_container('Info', 'Movie/Show selection cannot be disabled !')

	oc = ObjectContainer(title2='External Hosts Video Type')
	
	if session == None:
		session = common.getSession()
	
	for qual in common.INTERNAL_SOURCES_FILETYPE:
	
		label = qual['label']
		bool = qual['enabled']
		if bool == 'True':
			bool = True
		else:
			bool = False
		
		if label == item:
			bool = not bool
		
		title_msg = "Enabled: %s | Video-Type: %s" % (common.GetEmoji(type=bool, mode='simple', session=session), label)
		oc.add(DirectoryObject(key = Callback(ExtHostsFileType, item=label, setbool=not bool), title = title_msg, thumb = Resource.ContentsOfURLWithFallback(url=None, fallback=None)))
		
	oc.add(DirectoryObject(
			key = Callback(MainMenu, update = MakeSelectionExtHostsFileType(item=item, setbool=setbool)),
			title = '<< Save Selection >>',
			summary = 'Save the Selection which is used when listing External Sources.',
			thumb = R(ICON_SAVE)
		))

	return oc

######################################################################################
@route(PREFIX + "/MakeSelectionExtHostsFileType")
def MakeSelectionExtHostsFileType(item=None, setbool='True', **kwargs):

	if item != None:
		ARRAY_T = []
		ARRAY_T += [q for q in common.INTERNAL_SOURCES_FILETYPE]
		del common.INTERNAL_SOURCES_FILETYPE[:]
		
		for qual in ARRAY_T:
			bool = qual['enabled']
			if item == qual['label']:
				bool = setbool
				
			qual['enabled'] = bool
			common.INTERNAL_SOURCES_FILETYPE.append(qual)
		
	#Log(common.INTERNAL_SOURCES_FILETYPE)
	Dict['INTERNAL_SOURCES_FILETYPE'] = E(JSON.StringFromObject(common.INTERNAL_SOURCES_FILETYPE))
	Dict.Save()
	
######################################################################################
@route(PREFIX + "/ExtHostsQuals")
def ExtHostsQuals(item=None, setbool='True', session=None, **kwargs):

	oc = ObjectContainer(title2='External Hosts Qualities')
	
	if session == None:
		session = common.getSession()
	
	for qual in common.INTERNAL_SOURCES_QUALS:
	
		label = qual['label']
		bool = qual['enabled']
		if bool == 'True':
			bool = True
		else:
			bool = False
		
		if label == item:
			bool = not bool
		
		title_msg = "Enabled: %s | Quality: %s" % (common.GetEmoji(type=bool, mode='simple', session=session), label)
		oc.add(DirectoryObject(key = Callback(ExtHostsQuals, item=label, setbool=not bool), title = title_msg, thumb = Resource.ContentsOfURLWithFallback(url=None, fallback=None)))
		
	oc.add(DirectoryObject(
			key = Callback(MainMenu, update = MakeSelectionExtHostsQuals(item=item, setbool=setbool)),
			title = '<< Save Selection >>',
			summary = 'Save the Selection which is used when listing External Sources.',
			thumb = R(ICON_SAVE)
		))

	return oc

######################################################################################
@route(PREFIX + "/MakeSelectionExtHostsQuals")
def MakeSelectionExtHostsQuals(item=None, setbool='True', **kwargs):

	if item != None:
		ARRAY_T = []
		ARRAY_T += [q for q in common.INTERNAL_SOURCES_QUALS]
		del common.INTERNAL_SOURCES_QUALS[:]
		
		for qual in ARRAY_T:
			bool = qual['enabled']
			if item == qual['label']:
				bool = setbool
			
			qual['enabled']=bool
			common.INTERNAL_SOURCES_QUALS.append(qual)
		
	#Log(common.INTERNAL_SOURCES_QUALS)
	Dict['INTERNAL_SOURCES_QUALS'] = E(JSON.StringFromObject(common.INTERNAL_SOURCES_QUALS))
	Dict.Save()

######################################################################################
@route(PREFIX + "/ExtProviders")
def ExtProviders(curr_provs=None, refresh=False, item=None, setbool='True', session=None, **kwargs):

	oc = ObjectContainer(title2='External Providers')
	
	if refresh == True:
		common.interface.init()
	
	scanned_extProviders = JSON.ObjectFromString(D(common.interface.getProviders()))
	
	if session == None:
		session = common.getSession()
	
	ARRAY_T = []
	for prov in scanned_extProviders:
		prov['enabled'] = 'True'
		ARRAY_T.append(prov)

	if curr_provs == None:
		curr_provs = []
		curr_provs += [q for q in common.OPTIONS_PROVIDERS]
	else:
		curr_provs = JSON.ObjectFromString(D(curr_provs))
			
	del common.OPTIONS_PROVIDERS[:]
	
	if curr_provs != None and len(curr_provs) > 0:
		p_urls = []
		p_urls += [i['url'] for i in curr_provs]
	
		for s_prov in ARRAY_T:
			if s_prov['url'] in p_urls:
				for provider in curr_provs:
					if s_prov['url'] == provider['url']:
						if str(s_prov['enabled']) == 'True' and str(provider['enabled']) == 'True':
							s_prov['enabled'] = True
						else:
							s_prov['enabled'] = False
						common.OPTIONS_PROVIDERS.append(s_prov)
						break
			else:
				common.OPTIONS_PROVIDERS.append(s_prov)
	else:
		for provider in ARRAY_T:
			common.OPTIONS_PROVIDERS.append(provider)
	
	c = 0
	for provider in common.OPTIONS_PROVIDERS:
		c += 1
		label = provider['name']
		bool = str(provider['enabled'])
		website = provider['url']
		
		if item == label:
			bool = setbool

		if bool == 'True':
			bool = True
		else:
			bool = False

		title_msg = "%02d | Enabled: %s | Provider: %s | Url: %s | Online: %s | Proxy Req.: %s | Parser: %s | Speed: %s sec." % (c, common.GetEmoji(type=bool, mode='simple', session=session), label, website, common.GetEmoji(type=str(provider['online']), mode='simple', session=session),common.GetEmoji(type=str(provider['online_via_proxy']), mode='simple', session=session), common.GetEmoji(type=str(provider['parser']), mode='simple', session=session), provider['speed'])
		oc.add(DirectoryObject(key = Callback(ExtProviders, curr_provs=None, item=label, setbool=not bool), title = title_msg, thumb = Resource.ContentsOfURLWithFallback(url = provider['logo'], fallback=ICON_QUESTION)))
		
	#oc.add(DirectoryObject(key = Callback(ExtProviders, refresh=True), title = "Refresh External Providers", summary='Reload newly installed External Host Providers.', thumb = R(ICON_REFRESH)))
		
	oc.add(DirectoryObject(
			key = Callback(MainMenu, update = MakeSelectionProviders(item=item, setbool=setbool)),
			title = '<< Save Selection >>',
			summary = 'Save the Selection which is used when listing External Sources.',
			thumb = R(ICON_SAVE)
		))
		
	return oc
	
######################################################################################
@route(PREFIX + "/MakeSelectionProviders")
def MakeSelectionProviders(item=None, setbool='True', **kwargs):

	if item != None:
		ARRAY_T = []
		ARRAY_T += [q for q in common.OPTIONS_PROVIDERS]
		del common.OPTIONS_PROVIDERS[:]
		
		for qual in ARRAY_T:
			bool = qual['enabled']
			if item == qual['name']:
				bool = setbool
				
			qual['enabled'] = bool
			common.OPTIONS_PROVIDERS.append(qual)
		
	#Log(common.OPTIONS_PROVIDERS)
	Dict['OPTIONS_PROVIDERS'] = E(JSON.StringFromObject(common.OPTIONS_PROVIDERS))
	Dict.Save()

######################################################################################
@route(PREFIX + "/ExtHosts")
def ExtHosts(refresh=False, n=None, curr_sources=None, session=None, **kwargs):

	oc = ObjectContainer(title2='External Hosts')
	
	if refresh == True:
		common.interface.init()
		
	exHosts = JSON.ObjectFromString(D(common.interface.getHosts()))
	
	if session == None:
		session = common.getSession()
	
	if n != None:
		n = JSON.ObjectFromString(D(n))
		order = JSON.ObjectFromString(D(curr_sources))
		if len(order) == len(exHosts):
			order.remove(n)
			order.insert(0,n)
			
			new_order=[]
			others = []
			for o in order:
				bool = True
				lh = None
				for host in exHosts:
					lh = host
					if host['name'] == o['name']:
						new_order.append(o)
						bool = False
						break
				if bool == True:
					others.append(lh)
					
			for ot in others:
				new_order.append(ot)
			
			filter = []
			for o in new_order: filter += [i for i in exHosts if i['name'].lower() == o['name'].lower()]
			exHosts = filter

	del common.INTERNAL_SOURCES[:]
	
	c = 0
	for host in exHosts:
		if c == 0:
			n = host
		c += 1
		title_msg = "%02d | Enabled: %s | Host: %s | Quality: %s | Captcha: %s | Working: %s | Speed: %s sec." % (c, common.GetEmoji(type=host['working'], mode='simple', session=session), host['name'], host['quality'], common.GetEmoji(type=str(host['captcha']), mode='simple', session=session), common.GetEmoji(type=host['working'], mode='simple', session=session), host['speed'])
		
		summary = "%s%s" % ('' if host['msg'] == '' else '%s%s%s' % ('**', host['msg'], '** | '), title_msg)
		try:
			common.INTERNAL_SOURCES.append(host)
			oc.add(DirectoryObject(key = Callback(ExtHosts, n=E(JSON.StringFromObject(host)), curr_sources=E(JSON.StringFromObject(exHosts))), title = title_msg, summary = summary, thumb = Resource.ContentsOfURLWithFallback(url = host['logo'], fallback=ICON_QUESTION)))
		except:
			pass
				
	oc.add(DirectoryObject(
		key = Callback(MainMenu, update = MakeSelectionHosts()),
		title = '<< Save Selection >>',
		summary = 'Save the Selection which is used when listing External Sources.',
		thumb = R(ICON_SAVE)
		)
	)

	return oc
	
######################################################################################
@route(PREFIX + "/MakeSelectionHosts")
def MakeSelectionHosts(**kwargs):

	#Log("INTERNAL_SOURCES %s" % common.INTERNAL_SOURCES)
	Dict['INTERNAL_SOURCES'] = E(JSON.StringFromObject(common.INTERNAL_SOURCES))
	Dict.Save()
	
######################################################################################
@route(PREFIX + "/ExtProxies")
def ExtProxies(refresh=False, n=None, curr_proxies=None, session=None, **kwargs):

	oc = ObjectContainer(title2='Proxies')
	
	if refresh == True:
		common.interface.init()
		
	proxies = JSON.ObjectFromString(D(common.interface.getProxies()))
	
	if session == None:
		session = common.getSession()

	if n != None:
		n = JSON.ObjectFromString(D(n))
		order = JSON.ObjectFromString(D(curr_proxies))
		if len(order) == len(proxies):
			#Log("order %s" % order)
			order.remove(n)
			order.insert(0,n)
			
			new_order=[]
			others = []
			for o in order:
				bool = True
				lh = None
				for host in proxies:
					lh = host
					if host['name'] == o['name']:
						new_order.append(o)
						bool = False
						break
				if bool == True:
					others.append(lh)
					
			for ot in others:
				new_order.append(ot)
			
			filter = []
			for o in new_order: filter += [i for i in proxies if i['name'].lower() == o['name'].lower()]
			proxies = filter
	
	del common.OPTIONS_PROXY[:]
	
	c = 0
	for proxy in proxies:
		if c == 0:
			n = proxy
		c += 1
		title_msg = "%02d | Enabled: %s | Proxy: %s | Url: %s | Captcha: %s | SSL: %s | Working: %s | Speed: %s sec." % (c, common.GetEmoji(type=proxy['working'], mode='simple', session=session), proxy['name'], proxy['url'], common.GetEmoji(type=str(proxy['captcha']), mode='simple', session=session), common.GetEmoji(type=proxy['SSL'], mode='simple', session=session), common.GetEmoji(type=proxy['working'], mode='simple', session=session), proxy['speed'])
		
		try:
			common.OPTIONS_PROXY.append(proxy)
			oc.add(DirectoryObject(key = Callback(ExtProxies, n=E(JSON.StringFromObject(proxy)), curr_proxies=E(JSON.StringFromObject(proxies))), title = title_msg, summary = title_msg, thumb = R(ICON_PROXY_DEFAULT)))
		except:
			pass
				
	oc.add(DirectoryObject(
		key = Callback(MainMenu, update = MakeSelectionProxies()),
		title = '<< Save Selection >>',
		summary = 'Save the Selection which is used when listing External Sources.',
		thumb = R(ICON_SAVE)
		)
	)
	
	return oc
	
######################################################################################
@route(PREFIX + "/MakeSelectionProxies")
def MakeSelectionProxies(**kwargs):

	#Log("OPTIONS_PROXY %s" % common.OPTIONS_PROXY)
	Dict['OPTIONS_PROXY'] = E(JSON.StringFromObject(common.OPTIONS_PROXY))
	Dict.Save()

######################################################################################
@route(PREFIX + "/clearcache")
def ClearCache(**kwargs):
	
	common.CACHE.clear()
	common.CACHE_META.clear()
	HTTP.ClearCache()

	msg = 'Internal'
	try:
		if common.interface.isInitialized():
			msg = 'Internal & External'
			common.interface.clearSources()
	except:
		pass

	return MC.message_container('Clear Cache', '%s Cache has been cleared !' % msg)
	
######################################################################################
@route(PREFIX + "/resetcookies")
def ResetCookies(**kwargs):

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")
	
	if Prefs["webhook_url"] == String.Base64Decode(common.WBH):
		c = Dict[common.WBH]
		if c != None and int(c) >= 10:
			return MC.message_container('Webhook', 'Please fork your own WebHook ! Refer forum thread.')
	
	del common.CACHE_COOKIE[:]
	
	Thread.Create(SiteCookieRoutine,{},None,True,True)
	
	time.sleep(10.0)
	
	return MC.message_container('Reset Cookies', 'Cookies have been reset and token text dumped to log (if required) !')
	
######################################################################################
@route(PREFIX + "/ResetExtOptions")
def ResetExtOptions(**kwargs):
	
	del common.OPTIONS_PROVIDERS[:]
	del common.OPTIONS_PROXY[:]
	del common.INTERNAL_SOURCES[:]
	Dict['OPTIONS_PROXY'] = None
	Dict['OPTIONS_PROVIDERS'] = None
	Dict['INTERNAL_SOURCES'] = None
	Dict['INTERNAL_SOURCES_QUALS'] = None
	Dict['INTERNAL_SOURCES_RIPTYPE'] = None
	Dict['INTERNAL_SOURCES_FILETYPE'] = None
	Dict.Save()
	
	Thread.Create(SleepAndUpdateThread,{},True,False)
	
	return MC.message_container('Reset Options', 'Interface Options have been Reset !')
	
######################################################################################
@route(PREFIX + "/testSite")
def testSite(url, **kwargs):
	try:
		resp = '0'
		cookies = None
		if len(common.CACHE_COOKIE) > 0:
			cookies = common.CACHE_COOKIE[0]['cookie']
		req = common.GetHttpRequest(url=url, cookies=cookies)
		if req != None:
			response = urllib2.urlopen(req, timeout=common.client.GLOBAL_TIMEOUT_FOR_HTTP_REQUEST)
			resp = str(response.getcode())
		
		if resp in common.client.HTTP_GOOD_RESP_CODES:
			page_data = HTML.ElementFromString(response.read())
			return (True, None, page_data)
		else:
			msg = ("HTTP Code %s for %s. Enable SSL option in Channel Prefs." % (resp, url))
			Log("HTTP Error: %s", msg)
			return (False, MC.message_container("HTTP Error", msg), None)
	except urllib2.HTTPError, err:
		msg = ("%s for %s" % (err.code, url))
		Log(msg)
		return (False, MC.message_container("HTTP Error %s" % (err.code), "Error: Try Enabling SSL option in Channel Prefs."), None)
	except urllib2.URLError, err:
		msg = ("%s for %s" % (err.args, url))
		Log(msg)
		return (False, MC.message_container("HTTP Error %s" % (err.args), "Error: Try Enabling SSL option in Channel Prefs."), None)

######################################################################################
@route(PREFIX + "/showMenu")
def ShowMenu(title, session=None, **kwargs):

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")
	
	oc = ObjectContainer(title2 = title, no_cache=isForceNoCache())
	
	if title == CAT_GROUPS[0]:
		elems = CAT_WHATS_HOT
	elif title == CAT_GROUPS[1]:
		elems = CAT_REGULAR
	elif title == CAT_GROUPS[2]:
		elems = CAT_FILTERS
		
	if title == CAT_GROUPS[1]:
		for title in elems:
			oc.add(DirectoryObject(
				key = Callback(ShowCategory, title = title),
				title = title
				)
			)
	elif title == CAT_GROUPS[3]:
		
		page_data = common.GetPageElements(url=fmovies.BASE_URL)
		if page_data == None:
			bool, noc, page_data = testSite(url=fmovies.BASE_URL)
			if bool == False:
				return noc

		notices_all = []
		try:
			# Main page news
			try:
				notices_m = page_data.xpath(".//*[@id='body-wrapper']/div/div[@class='alert alert-primary notice']/text()")
				notice_txt = ""
				for notice in notices_m:
					notice_txt += notice
				if notice_txt != "":
					notices_all.append(notice_txt.strip())
			except:
				pass
			if len(SITE_NEWS_LOCS) == 0:
				try:
					elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row movie-list']//div[@class='item']")
					for elem in elems:
						loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
						SITE_NEWS_LOCS.append(loc)
				except:
					pass
			
			if len(SITE_NEWS_LOCS) > 0:
				LOC = random.choice(SITE_NEWS_LOCS)
				try:
					page_data = common.GetPageElements(url=LOC)
					SITE_NEWS_LOCS.remove(LOC)
					notices = page_data.xpath(".//*[@id='movie']//div[@class='alert alert-warning']//b//text()")
					if notices[0] == '':
						notices = ['No site news Available.']
				except:
					notices = ['No site news Available.']
			else:
				notices = ['No site news Available.']
		except:
			notices = ['Could not connect to site.']
			
		for notice in notices:
			notices_all.append(notice)
			
		for notice in notices_all:
			notice = unicode(notice)
			oc.add(DirectoryObject(
				title = notice,
				key = Callback(MC.message_container, 'Site News', 'No site news Available.'),
				summary = notice,
				thumb = R(ICON_INFO)
				)
			)
	else:
		for title in elems:
			if title == CAT_FILTERS[3]:
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title),
					title = title
					)
				)
			else:
				oc.add(DirectoryObject(
					key = Callback(SortMenu, title = title),
					title = title
					)
				)
			
	if common.UsingOption(key=common.DEVICE_OPTIONS[0]):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
	return oc

######################################################################################
@route(PREFIX + "/sortMenu")
def SortMenu(title, session=None, **kwargs):

	url = fmovies.BASE_URL
	oc = ObjectContainer(title2 = title, no_cache=isForceNoCache())
	
	# Test for the site url initially to report a logical error
	page_data = common.GetPageElements(url = url)
	if page_data == None:
		bool, noc, page_data = testSite(url=url)
		if bool == False:
			return noc

	if title in CAT_FILTERS:
		if title == CAT_FILTERS[0]:
			elems = page_data.xpath(".//*[@id='menu']//li[@class='has-children'][3]//li//a")
		elif title == CAT_FILTERS[1]:
			elems = page_data.xpath(".//*[@id='menu']//li[@class='has-children'][1]//li//a")
		elif title == CAT_FILTERS[2]:
			elems = page_data.xpath(".//*[@id='menu']//li[@class='has-children'][2]//li//a")

		for elem in elems:
			key = elem.xpath(".//text()")[0]
			urlpath = elem.xpath(".//@href")[0]
			if 'http' not in urlpath:
				urlpath = fmovies.BASE_URL + urlpath
			skey=key
			key=key.replace(' ','-')
				
			oc.add(DirectoryObject(
				key = Callback(ShowCategory, title = title, urlpath = urlpath, key = key),
				title = skey
				)
			)
	elif title in CAT_WHATS_HOT:
		if title == CAT_WHATS_HOT[0]:
			elems = page_data.xpath(".//*[@id='header-wrapper']//div[@class='swiper-wrapper']//div[contains(@class, 'item swiper-slide')]")
			for elem in elems:
				name = elem.xpath(".//a[@class='name']//text()")[0]
				loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
				
				thumbstr = elem.xpath(".//@style")[0]
				matches = re.findall(ur"url=([^\"]*)\)", thumbstr)
				thumb = matches[0]
				quality = elem.xpath(".//div[@class='meta']//span[@class='quality']//text()")[0]
				summary = elem.xpath(".//p[@class='desc']//text()")[0]
				try:
					more_info_link = elem.xpath(".//@data-tip")[0]
				except:
					more_info_link = None

				oc.add(DirectoryObject(
					key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
					title = name + " (" + quality + ")",
					summary = GetMovieInfo(summary=summary, urlPath=more_info_link, referer=url),
					thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
					)
				)
		else:
			if title == CAT_WHATS_HOT[1]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@data-name='most-favorited']//div[@class='item']")
			elif title == CAT_WHATS_HOT[2]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@data-name='recommend']//div[@class='item']")
			elif title == CAT_WHATS_HOT[3]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@data-name='views-week']//div[@class='item']")
			elif title == CAT_WHATS_HOT[4]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@data-name='views-month']//div[@class='item']")
			elif title == CAT_WHATS_HOT[5]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='widget latest-movies']//div[@data-name='all']//div[@class='item']")
			elif title == CAT_WHATS_HOT[6]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='widget latest-series']//div[@class='item']")
			elif title == CAT_WHATS_HOT[7]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='widget requested']//div[@class='item']")
			
			for elem in elems:
				name = elem.xpath(".//a[@class='name']//text()")[0]
				loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
				thumb = elem.xpath(".//a[@class='poster']//@src")[0].split('url=')[1]
				summary = 'Plot Summary on Item Page.'
				
				eps_nos = ''
				title_eps_no = ''
				try:
					eps_nos = elem.xpath(".//div[@class='status']//span//text()")[0]
					eps_no_i = str(int(eps_nos.strip()))
					title_eps_no = ' (Eps:'+eps_no_i+')'
					eps_nos = ' Episodes: ' + eps_no_i
				except:
					pass
				
				try:
					more_info_link = elem.xpath(".//@data-tip")[0]
				except:
					more_info_link = None

				oc.add(DirectoryObject(
					key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
					title = name + title_eps_no,
					summary = GetMovieInfo(summary=summary, urlPath=more_info_link, referer=url) + eps_nos,
					thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
					)
				)
	
	if common.UsingOption(key=common.DEVICE_OPTIONS[0]):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
	if len(oc) == 1:
		return MC.message_container(title, 'No Videos Available')
	return oc
	
######################################################################################
@route(PREFIX + "/showcategory")
def ShowCategory(title, key=' ', urlpath=None, page_count='1', session=None, **kwargs):
	
	if urlpath != None:
		newurl = urlpath + '?page=%s' % page_count
	else:
		if title == CAT_FILTERS[0]:
			newurl = (fmovies.BASE_URL + '/release-' + key.lower() + '?page=%s' % page_count)
		elif title == CAT_FILTERS[1]:
			newurl = (fmovies.BASE_URL + '/genre/' + key.lower() + '?page=%s' % page_count)
		elif title == CAT_FILTERS[2]:
			newurl = (fmovies.BASE_URL + '/country/' + key.lower() + '?page=%s' % page_count)
		elif title == CAT_REGULAR[0]:
			newurl = (fmovies.BASE_URL + '/movies' + '?page=%s' % page_count)
		elif title == CAT_REGULAR[1]:
			newurl = (fmovies.BASE_URL + '/tv-series' + '?page=%s' % page_count)
		elif title == CAT_REGULAR[2]:
			newurl = (fmovies.BASE_URL + '/top-imdb' + '?page=%s' % page_count)
		elif title == CAT_REGULAR[3]:
			newurl = (fmovies.BASE_URL + '/most-watched' + '?page=%s' % page_count)
		
	page_data = common.GetPageElements(url=newurl)
	
	elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row movie-list']//div[@class='item']")
	last_page_no = int(page_count)
	try:
		last_page_no = int(page_data.xpath(".//*[@id='body-wrapper']//ul[@class='pagination'][1]//li[last()-1]//text()")[0])
	except:
		pass
		
	if key != ' ':
		oc = ObjectContainer(title2 = title + '|' + key.title() + '|Page ' + str(page_count) + ' of ' + str(last_page_no), no_cache=isForceNoCache())
	else:
		oc = ObjectContainer(title2 = title + '|Page ' + str(page_count) + ' of ' + str(last_page_no), no_cache=isForceNoCache())
		
	for elem in elems:
		name = elem.xpath(".//a[@class='name']//text()")[0]
		loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
		thumb = elem.xpath(".//a[@class='poster']//@src")[0].split('url=')[1]
		summary = 'Plot Summary on Item Page.'
		
		eps_nos = ''
		title_eps_no = ''
		try:
			eps_nos = elem.xpath(".//div[@class='status']//span//text()")[0]
			eps_no_i = str(int(eps_nos.strip()))
			title_eps_no = ' (Eps:'+eps_no_i+')'
			eps_nos = ' Episodes: ' + eps_no_i
		except:
			pass
		try:
			more_info_link = elem.xpath(".//@data-tip")[0]
		except:
			more_info_link = None

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
			title = name + title_eps_no,
			summary = GetMovieInfo(summary=summary, urlPath=more_info_link, referer=newurl) + eps_nos,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
			)
		)
		
	if int(page_count) < last_page_no:
		oc.add(NextPageObject(
			key = Callback(ShowCategory, title = title, key = key, urlpath = urlpath, page_count = str(int(page_count) + 1)),
			title = "Next Page (" + str(int(page_count) + 1) +'/'+ str(last_page_no) + ") >>",
			thumb = R(ICON_NEXT)
			)
		)
		
	if common.UsingOption(key=common.DEVICE_OPTIONS[0]):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))

	if len(oc) == 1:
		return MC.message_container(title, 'No More Videos Available')
		
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu',
		thumb = R(ICON)
		)
	)
	
	return oc

######################################################################################
@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url, thumb, session=None, **kwargs):

	page_data = common.GetPageElements(url=url)
	if page_data == None:
		return MC.message_container("Unknown Error", "Error: The page was not received.")
		
	session = common.getSession()
	client_id = '%s-%s' % (Client.Product, session)
	if client_id not in CUSTOM_TIMEOUT_DICT:
		CUSTOM_TIMEOUT_DICT[client_id] = {}
		
	try:
		title = unicode(page_data.xpath(".//*[@id='info']//h1[@class='name']//text()")[0])
	except:
		title = unicode(title)
		
	try:
		item_unav = ''
		errs = page_data.xpath(".//*[@id='movie']//div[@class='alert alert-primary notice'][2]//text()")
		for err in errs:
			if 'There is no server for this movie right now, please try again later.' in err:
				item_unav = ' ' + common.GetEmoji(type='neg', session=session)
				break
	except:
		pass
		
	try:
		if thumb == None:
			thumb = page_data.xpath(".//*[@id='info']//div//img")[0].split('url=')[1]
	except:
		thumb = R(ICON_UNAV)
		
	try:
		serverts = page_data.xpath(".//body[@class='watching']//@data-ts")[0]
	except:
		serverts = 0
	
	try:
		art = page_data.xpath(".//meta[@property='og:image'][1]//@content")[0]
	except:
		art = 'https://cdn.rawgit.com/coder-alpha/FMoviesPlus.bundle/master/Contents/Resources/art-default.jpg'
	oc = ObjectContainer(title2 = title + item_unav, art = art, no_cache=isForceNoCache())
	
	try:
		summary = page_data.xpath(".//*[@id='info']//div[@class='info col-md-19']//div[@class='desc']//text()")[0]
		#summary = re.sub(r'[^0-9a-zA-Z \-/.,\':+&!()]', '', summary)
	except:
		summary = 'Summary Not Available.'
	
	try:
		trailer = page_data.xpath(".//*[@id='control']//div['item mbtb watch-trailer hidden-xs']//@data-url")[0]
	except:
		trailer = None
	
	try:
		year = str(page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][2]//dd[2]//text()")[0][0:4])
	except:
		year = 'Not Available'
		
	try:
		rating = str(page_data.xpath(".//*[@id='info']//div[@class='info col-md-19']//span[1]//b//text()")[0])
	except:
		rating = 'Not Available'
		
	try:
		duration = int(page_data.xpath(".//*[@id='info']//div[@class='info col-md-19']//span[2]//b//text()")[0].strip('/episode').strip(' min'))
	except:
		duration = 'Not Available'

	try:
		genre0 = page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][1]//dd[1]//a//text()")
		genre = (','.join(str(x) for x in genre0))
		if genre == '':
			genre = 'Not Available'
	except:
		genre = 'Not Available'
	
	try:
		directors0 = page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][1]//dd[3]//text()")
		directors = (','.join(str(x) for x in directors0))
		if directors.strip() == '...':
			directors = 'Not Available'
	except:
		directors = 'Not Available'
	
	try:
		roles0 = page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][1]//dd[2]//a//text()")
		roles = (','.join(str(x) for x in roles0))
		if roles == '':
			roles = 'Not Available'
	except:
		roles = 'Not Available'
	
	try:
		servers = page_data.xpath(".//*[@id='servers']//div[@class='server row']")
	except:
		servers = []
	
	summary += '\n '
	summary += 'Actors: ' + roles + '\n '
	summary += 'Directors: ' + directors + '\n '
	
	if str(duration) == 'Not Available':
		summary += 'Runtime: ' + str(duration) + '\n '
	else:
		summary += 'Runtime: ' + str(duration) + ' min.' + '\n '
	
	summary += 'Year: ' + year + '\n '
	summary += 'Genre: ' + genre + '\n '
	summary += 'IMDB rating: ' + rating + '\n '
	
	summary = unicode(summary)
	
	try:
		similar_reccos = []
		similar_reccos_elems = page_data.xpath(".//*[@id='movie']//div[@class='row movie-list']//div[@class='item']")

		for elem in similar_reccos_elems:
			similar_reccos_name = elem.xpath(".//a[@class='name']//text()")[0]
			similar_reccos_loc = elem.xpath(".//a[@class='name']//@href")[0]
			similar_reccos_thumb = elem.xpath(".//a[@class='poster']//@src")[0].split('url=')[1]
			try:
				eps_nos = elem.xpath(".//div[@class='status']//span//text()")[0]
				eps_nos = ' Episodes: ' + str(int(eps_nos.strip()))
			except:
				eps_nos = ''
			try:
				similar_reccos_more_info_link = elem.xpath(".//@data-tip")[0]
			except:
				similar_reccos_more_info_link = None
			similar_reccos.append({'name':similar_reccos_name, 'loc':similar_reccos_loc, 'thumb':similar_reccos_thumb, 'more_info_link':similar_reccos_more_info_link, 'eps_nos':eps_nos})
	except:
		similar_reccos = []
		
	try:
		tags0 = page_data.xpath(".//*[@id='tags']//a//text()")
		tags = (','.join(str(x) for x in tags0))
		if tags == '':
			tags = 'Not Available'
	except:
		tags = 'Not Available'
	
	episodes = []
	try:
		episodes = page_data.xpath(".//*[@id='movie']//div[@class='widget boxed episode-summary']//div[@class='item']")
	except:
		pass
		
	servers_list = {}
	episodes_list = []
	server_lab = []
	isTvSeries = False
	isMovieWithMultiPart = False
	
	try:
		item_type = page_data.xpath(".//div[@id='movie']/@data-type")[0]
		if item_type == 'series':
			isTvSeries = True
	except:
		pass
		
	for server in servers:
		label = server.xpath(".//label[@class='name col-md-4 col-sm-5']//text()[2]")[0].strip()
		if 'Server F' in label:
			label = label.replace('Server F','Google ')
		
		server_lab.append(label)
		items = server.xpath(".//ul//li")
		if len(items) > 1:
			isMovieWithMultiPart = True
			
		servers_list[label] = []
		c=0
		for item in items:
			servers_list[label].append([])
			servers_list[label][c]={}
			label_qual = item.xpath(".//a//text()")[0].strip()
			label_val = item.xpath(".//a//@data-id")[0]
			servers_list[label][c]['quality'] = label_qual
			servers_list[label][c]['loc'] = label_val
			c += 1

	# label array of servers available - sort them so that presentation order is consistent
	server_lab = sorted(server_lab)
	
	# remap server list - this way its easier to iterate for tv-show episodes
	servers_list_new = []
	c=0
	
	if len(servers_list) > 0:
		for k in servers_list:
			break
		for no in servers_list[k]:
			servers_list_new.append([])
			servers_list_new[c] = {}
			for label in servers_list:
				servers_list_new[c][label] = {}
				try:
					servers_list_new[c][label] = {'quality':servers_list[label][c]['quality'], 'loc':servers_list[label][c]['loc']}
				except:
					if c > 99:
						servers_list_new[c][label] = {'quality':"%03d" % (c+1), 'loc':''}
					else:
						servers_list_new[c][label] = {'quality':"%02d" % (c+1), 'loc':''}
			c += 1
		
	# trailer
	try:
		if trailer != None:
			url_serv = URLService.ServiceIdentifierForURL(trailer)
			if url_serv!= None:
				oc.add(VideoClipObject(
					url = trailer,
					title = title + ' (Trailer)',
					thumb = GetThumb(thumb),
					art = art,
					summary = summary)
				)
	except:
		pass
		
	if len(episodes) > 0 and isTvSeries:
		# case for presenting tv-series with synopsis
		if Prefs["use_debug"]:
			Log("case for presenting tv-series with synopsis")
		det_Season = common.cleantitle.removeParanthesis(title).split(' ')
		SeasonN = 1
		try:
			SeasonN = int(det_Season[len(det_Season)-1])
			oc.title2 = title.replace(str(SeasonN), '(Season ' + str(SeasonN) + ')')
		except:
			oc.title2 = title
			
		c_not_missing = 1
		for episode in episodes:
			ep_no = None
			try:
				noS = episode.xpath(".//div[@class='ep']//i//text()")[0].strip()
				no = noS
				ep_no = int(no)
			except:
				no = '0'
				
			if no != '0' and ep_no == c_not_missing:
				try:
					name = episode.xpath(".//span[@class='name']//text()")[0]
				except:
					name = 'Episode Name Not Available.'
				try:
					air_date = episode.xpath(".//div[@class='date']//text()")[0]
				except:
					air_date = ''
				try:
					desc = episode.xpath(".//div[@class='desc']//text()")[0]
				except:
					desc = 'Episode Summary Not Available.'

				episodes_list.append({"name":name,"air_date":air_date,"desc":desc})
			else:
				# episode does not have a number - could be a Special - its listed alphabetically but might fall in a different airing sequence
				c=0
				successIns = False
				for eps in servers_list_new:
					
					if noS in eps[server_lab[0]]['quality']:
						try:
							name = episode.xpath(".//span[@class='name']//text()")[0]
						except:
							name = 'Episode Name Not Available.'
						try:
							air_date = episode.xpath(".//div[@class='date']//text()")[0]
						except:
							air_date = ''
						try:
							desc = episode.xpath(".//div[@class='desc']//text()")[0]
						except:
							desc = 'Episode Summary Not Available.'
						episodes_list.insert(c, {"name":name,"air_date":air_date,"desc":desc})
						successIns = True
						break
					c += 1
				if not successIns:
					episodes_list.append({"name":'',"air_date":'',"desc":''})
			c_not_missing += 1
		
		eps_i = 1
		c_not_missing=-1
		c=0
		for eps in servers_list_new:
		
			if '-' in eps[server_lab[0]]['quality'] and verify2partcond(eps[server_lab[0]]['quality']): # 2 part episode condition
				qual_i = (int(eps[server_lab[0]]['quality'].split('-')[0])-eps_i)
				eps_i += 1
			else:
				try:
					qual_i = (int(eps[server_lab[0]]['quality'])-eps_i)
				except:
					qual_i = c_not_missing+1
					eps_i = eps_i-1
			
			try:
				if '-' in eps[server_lab[0]]['quality'] and episodes_list[qual_i]['name'] in eps[server_lab[0]]['quality'] and not verify2partcond(eps[server_lab[0]]['quality']):
					title_s = 'Ep:' + eps[server_lab[0]]['quality']
					episode = eps[server_lab[0]]['quality']
				else:
					title_s = 'Ep:' + eps[server_lab[0]]['quality'] + ' - ' + episodes_list[qual_i]['name']
					episode = eps[server_lab[0]]['quality']
			except:
				title_s = 'Ep:' + eps[server_lab[0]]['quality']
				episode = eps[server_lab[0]]['quality']
			try:
				desc = episodes_list[qual_i]['air_date'] + " : " + episodes_list[qual_i]['desc']
			except:
				desc = 'Episode Summary Not Available.'
				
			try:
				oc.add(DirectoryObject(
					key = Callback(TvShowDetail, tvshow=title, title=title_s, url=url, servers_list_new=servers_list_new[c], server_lab=(','.join(str(x) for x in server_lab)), summary=desc+'\n '+summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, serverts=serverts, season=SeasonN, episode=episode),
					title = title_s,
					summary = desc+ '\n ' +summary,
					art = art,
					thumb = Resource.ContentsOfURLWithFallback(url = GetThumb(thumb), fallback = GetThumb(ICON_UNAV))
					)
				)
				c_not_missing = qual_i
				c += 1
			except Exception as e:
				Log('ERROR init.py>EpisodeDetail>Tv1 %s, %s' % (e.args, title_s))
				pass
			
		if SeasonN > 0 or True: # enable for all - even if this might be a single season
			oc.add(DirectoryObject(
			key = Callback(Search, query = common.cleantitle.removeParanthesisAndSeason(title, SeasonN), mode='other seasons', thumb=thumb, summary=summary),
			title = "Other Seasons",
			summary = 'Other Seasons of ' + common.cleantitle.removeParanthesis(title),
			art = art,
			thumb = R(ICON_OTHERSEASONS)
			))

	elif isTvSeries:
		# case for presenting tv-series without synopsis
		if Prefs["use_debug"]:
			Log("case for presenting tv-series without synopsis")
		det_Season = common.cleantitle.removeParanthesis(title).split(' ')
		SeasonN = 1
		try:
			SeasonN = int(det_Season[len(det_Season)-1])
			oc.title2 = title.replace(str(SeasonN), '(Season ' + str(SeasonN) + ')')
		except:
			oc.title2 = title
			
		c=0
		for eps in servers_list_new:
			try:
				episode = eps[server_lab[0]]['quality']
				title_s = 'Ep:' + episode
				oc.add(DirectoryObject(
					key = Callback(TvShowDetail, tvshow=title, title=title_s, url=url, servers_list_new=servers_list_new[c], server_lab=(','.join(str(x) for x in server_lab)), summary='Episode Summary Not Available.\n ' + summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, serverts=serverts, season=SeasonN, episode=episode),
					title = title_s,
					summary = 'Episode Summary Not Available.\n ' + summary,
					thumb = Resource.ContentsOfURLWithFallback(url = GetThumb(thumb), fallback = GetThumb(ICON_UNAV))
					)
				)
				c += 1
			except Exception as e:
				Log('ERROR init.py>EpisodeDetail>Tv2 %s, %s' % (e.args, title_s))
				pass
		if SeasonN > 0 or True: # enable for all - even if this might be a single season
			oc.add(DirectoryObject(
			key = Callback(Search, query = common.cleantitle.removeParanthesisAndSeason(title, SeasonN), mode='other seasons', thumb=thumb, summary=summary),
			title = "Other Seasons",
			summary = 'Other Seasons of ' + common.cleantitle.removeParanthesisAndSeason(title, SeasonN),
			art = art,
			thumb = R(ICON_OTHERSEASONS)
			))
	elif isTvSeries == False and isMovieWithMultiPart == True:
		# case for presenting tv-series without synopsis
		if Prefs["use_debug"]:
			Log("case for presenting movie with multi-selection (possibly audio)")
			
		if Prefs['disable_extsources'] == False:
			#common.interface.clearSources()
			#Thread.Create(ExtSources, {}, movtitle=title, year=year, title=title, url=url, summary=summary, thumb=thumb, art=art, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles)
			key = generatemoviekey(movtitle=title, year=year, tvshowtitle=None, season=None, episode=None)
			try:
				CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
			except:
				CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
			Thread.Create(common.interface.getExtSources, {}, movtitle=title, year=year, tvshowtitle=None, season=None, episode=None, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY)
		
		SeasonN = 0
		oc.title2 = title
			
		c=0
		for eps in servers_list_new:
			try:
				episode = eps[server_lab[0]]['quality']
				title_s = episode
				oc.add(VideoClipObject(
					key = Callback(TvShowDetail, tvshow=title, title=title_s, url=url, servers_list_new=servers_list_new[c], server_lab=(','.join(str(x) for x in server_lab)), summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, serverts=serverts, season=SeasonN, episode=episode, treatasmovie=True),
					title = title_s,
					summary = summary,
					thumb = Resource.ContentsOfURLWithFallback(url = GetThumb(thumb), fallback = GetThumb(ICON_UNAV))
					)
				)
				c += 1
			except Exception as e:
				Log('ERROR init.py>EpisodeDetail>Movie1 %s, %s' % (e.args, title_s))
				pass
				
		if Prefs['disable_extsources'] == False and common.interface.isInitialized():
			oc.add(DirectoryObject(
				key = Callback(ExtSources, movtitle=title, year=year, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles), 
				title = 'External Sources',
				summary = 'List sources of this movie by External Providers.',
				thumb = R(ICON_OTHERSOURCES)
				)
			)
	else:
		# case for presenting movies
		if Prefs["use_debug"]:
			Log("case for presenting movies")
		
		if Prefs['disable_extsources'] == False:
			#Thread.Create(ExtSources, {}, movtitle=title, year=year, title=title, url=url, summary=summary, thumb=thumb, art=art, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles)
			key = generatemoviekey(movtitle=title, year=year, tvshowtitle=None, season=None, episode=None)
			if common.interface.getExtSourcesThreadStatus(key=key) == False:
				#common.interface.clearSources()
				try:
					CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
				except:
					CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
				Thread.Create(common.interface.getExtSources, {}, movtitle=title, year=year, tvshowtitle=None, season=None, episode=None, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY)
		
		# create timeout thread
		Thread.Create(ThreadTimeoutTimer, {}, Client.Product, E(url), client_id)
	
		pair_required = False
		for label in server_lab:
			for label_i in servers_list[label]:
				url_s = label_i['loc']
				if common.UsingOption(common.DEVICE_OPTIONS[5]):
					try:
						title_s = ''
						if Prefs["use_debug"]:
							Log("%s - %s" % (url, url_s))
						server_info, isOpenLoad, error = fmovies.GetApiUrl(url=url, key=url_s, serverts=serverts)
						
						if server_info != None:
							qual = common.getHighestQualityLabel(server_info, label_i['quality'])
							title_s = label + ' - ' + qual
						
							pair_required = False
							pair = ''
							status = ''
							isVideoOnline = 'unknown'
							if Prefs["use_linkchecker"]:
								data = server_info
								if isOpenLoad == True:
									pass
								else:
									data = E(JSON.StringFromObject({"server":server_info}))
								isVideoOnline = common.isItemVidAvailable(isOpenLoad=isOpenLoad, data=data)
								
							if isOpenLoad == True:
								pair_required = common.host_openload.isPairingRequired(url=server_info)
								if pair_required == True:
									pair = ' *Pairing required* '
								if Prefs["use_debug"]:
									Log("%s --- %s : %s" % (server_info, pair, pair_required))
								
							if isVideoOnline != str(False):
								status = common.GetEmoji(type=isVideoOnline, session=session) + ' ' + pair
							else:
								status = common.GetEmoji(type=isVideoOnline, session=session)
								
							try:
								redirector_stat = ''
								redirector_enabled = 'false'
								if common.UsingOption(key=common.DEVICE_OPTIONS[2]) and isOpenLoad == False:
									redirector_stat = ' (via Redirector)'
									redirector_enabled = 'true'
									
								durl = "fmovies://" + E(JSON.StringFromObject({"url":url, "server":common.ResolveFinalUrl(isOpenLoad, data=server_info, pair_required=pair_required), "title":title, "summary":summary, "thumb":thumb, "art":art, "year":year, "rating":rating, "duration":str(duration), "genre":genre, "roles":roles, "directors":directors, "roles":roles, "isOpenLoad":str(isOpenLoad), "useSSL":str(Prefs["use_https_alt"]), "isVideoOnline":str(isVideoOnline), "useRedirector": redirector_enabled, 'urldata':'','quality':qual, 'pairrequired':pair_required}))
									
								oc.add(VideoClipObject(
									url = durl,
									title = status + title + ' - ' + title_s + redirector_stat,
									thumb = GetThumb(thumb),
									duration = int(duration) * 60 * 1000,
									year = int(year),
									art = art,
									summary = summary,
									key = AddRecentWatchList(title=title, url=url, summary=summary, thumb=thumb)
									)
								)
							except Exception as e:
								Log('ERROR init.py>EpisodeDetail>Movie2a %s' % (e.args))
								Log("ERROR: %s with key:%s returned %s" % (url,url_s,server_info))
								Log('ERROR init.py>EpisodeDetail>Movie2a %s' % (title + ' - ' + title_s))
						else:
							pass
							if Prefs["use_debug"]:
								Log("Video will not be displayed as playback option !")
								Log("ERROR: %s" % error)
								Log("ERROR: %s with key:%s returned %s" % (url,url_s,server_info))
					except Exception as e:
						Log("ERROR init.py>EpisodeDetail>Movie2b %s %s" % (url,url_s))
						Log("ERROR init.py>EpisodeDetail>Movie2b %s" % (server_info))
						Log('ERROR init.py>EpisodeDetail>Movie2b %s, %s' % (e.args, (title + ' - ' + title_s)))
						pass
				else:
					if common.UsingOption(common.DEVICE_OPTIONS[6]):
						oc.add(MovieObject(
							key = Callback(VideoDetail, title=title, url=url, url_s=url_s, label=label, label_i_qual=label_i['quality'], serverts=serverts, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles),
							title = label,
							duration = int(duration) * 60 * 1000,
							year = int(year),
							rating_key = url+url_s,
							summary = summary,
							thumb = GetThumb(thumb)
							)
						)
					else:
						oc.add(DirectoryObject(
							key = Callback(VideoDetail, title=title, url=url, url_s=url_s, label=label, label_i_qual=label_i['quality'], serverts=serverts, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles),
							title = label,
							summary = summary,
							thumb = GetThumb(thumb)
							)
						)
				
			if label != server_lab[len(server_lab)-1] and isTimeoutApproaching(clientProd = Client.Product, item = E(url), client_id=client_id, session=session):
				Log("isTimeoutApproaching action")
				break
				#return MC.message_container('Timeout', 'Timeout: Please try again !')

		if Prefs['disable_extsources'] == False and common.interface.isInitialized():
			oc.add(DirectoryObject(
				key = Callback(ExtSources, movtitle=title, year=year, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles), 
				title = 'External Sources',
				summary = 'List sources of this movie by External Providers.',
				thumb = GetThumb(R(ICON_OTHERSOURCES))
				)
			)
						
	itemtype = ('show' if isTvSeries else 'movie')
						
	if len(similar_reccos) > 0:
		oc.add(DirectoryObject(
			key = Callback(SimilarRecommendations, title = title, similar_reccos = E(JSON.StringFromObject(similar_reccos)), referer=url),
			title = "Similar Recommendations",
			summary = 'Discover other %s similar to %s' % (itemtype, title),
			art = art,
			thumb = GetThumb(R(ICON_SIMILAR))
		)
	)
	
	if roles != 'Not Available':
		oc.add(DirectoryObject(
			key = Callback(MoviesWithPeople, stars = roles),
			title = "People Search",
			summary = 'Search for movies/shows based on a person from the current %s' % (itemtype),
			art = art,
			thumb = GetThumb(R(ICON_PEOPLE))
		)
	)
	
	if tags != 'Not Available':
		oc.add(DirectoryObject(
			key = Callback(MoviesWithTag, tags = tags),
			title = "Tag Search",
			summary = 'Search for movies/shows based on a Tag from the current %s' % (itemtype),
			art = art,
			thumb = GetThumb(R(ICON_TAG))
		)
	)
		
	if Check(title=title,url=url):
		oc.add(DirectoryObject(
			key = Callback(RemoveBookmark, title = title, url = url),
			title = "Remove Bookmark",
			summary = 'Removes the current %s from the Boomark que' % (itemtype),
			art = art,
			thumb = GetThumb(R(ICON_QUEUE))
		)
	)
	else:
		oc.add(DirectoryObject(
			key = Callback(AddBookmark, title = title, url = url, summary=summary, thumb=thumb),
			title = "Add Bookmark",
			summary = 'Adds the current %s to the Boomark que' % (itemtype),
			art = art,
			thumb = GetThumb(R(ICON_QUEUE))
		)
	)
	
	return oc
	
	
####################################################################################################
@route(PREFIX + "/TvShowDetail")
def TvShowDetail(tvshow, title, url, servers_list_new, server_lab, summary, thumb, art, year, rating, duration, genre, directors, roles, serverts, season=None, episode=None, treatasmovie=False, session=None, **kwargs):

	oc = ObjectContainer(title2 = title, art = art, no_cache=isForceNoCache())

	servers_list_new = servers_list_new.replace("'", "\"")
	servers_list_new = json.loads(servers_list_new)
	
	server_lab = server_lab.split(',')
	
	session = common.getSession()
	client_id = '%s-%s' % (Client.Product, session)

	watch_title = tvshow
	if treatasmovie==False:
		tvshowcleaned = tvshow.replace(' ' + str(season),'')
		#watch_title = "%s - S%sE%s" % (tvshowtitle.replace(str(season),'').replace('(Special)','').strip(),season,episode)
		watch_title = common.cleantitle.tvWatchTitle(tvshowcleaned,season,episode,title)
		
	if treatasmovie==False and Prefs['disable_extsources'] == False:
		#Thread.Create(ExtSources, {}, tvshowtitle=tvshow, season=season, episode=episode, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles)
		tvshowcleaned = tvshow.replace(' ' + str(season),'')
		
		key = generatemoviekey(movtitle=None, year=year, tvshowtitle=tvshowcleaned, season=season, episode=episode)
		if common.interface.getExtSourcesThreadStatus(key=key) == False:
			#common.interface.clearSources()
			try:
				CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
			except:
				CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
			Thread.Create(common.interface.getExtSources, {}, movtitle=None, year=year, tvshowtitle=tvshowcleaned, season=season, episode=episode, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY)
	
	# create timeout thread
	Thread.Create(ThreadTimeoutTimer, {}, Client.Product, E(url), client_id)
	
	pair_required = False
	for label in server_lab:
		url_s = servers_list_new[label]['loc']
		
		if common.UsingOption(common.DEVICE_OPTIONS[5]):	
			server_info,isOpenLoad, error = fmovies.GetApiUrl(url=url, key=url_s, serverts=serverts)
			if server_info != None:
			
				pair = ''
				pair_required = False
				status = ''
				isVideoOnline = 'unknown'
				if Prefs["use_linkchecker"]:
					data = server_info
					if isOpenLoad == True:
						pass
					else:
						data = E(JSON.StringFromObject({"server":server_info}))
					isVideoOnline = common.isItemVidAvailable(isOpenLoad=isOpenLoad, data=data)
					
				if isOpenLoad == True:
					pair_required = common.host_openload.isPairingRequired(url=server_info)
					if pair_required == True:
						pair = ' *Pairing required* '
					if Prefs["use_debug"]:
						Log("%s --- %s : %s" % (server_info, pair, pair_required))
					
				if isVideoOnline != str(False):
					status = common.GetEmoji(type=isVideoOnline, session=session) + ' ' + pair
				else:
					status = common.GetEmoji(type=isVideoOnline, session=session)
					
				redirector_stat = ''
				redirector_enabled = 'false'
				if common.UsingOption(key=common.DEVICE_OPTIONS[2]) and isOpenLoad == False:
					redirector_stat = ' (via Redirector)'
					redirector_enabled = 'true'
				
				durl = "fmovies://" + E(JSON.StringFromObject({"url":url, "server":common.ResolveFinalUrl(isOpenLoad, data=server_info, pair_required=pair_required), "title":title, "summary":summary, "thumb":thumb, "art":art, "year":year, "rating":rating, "duration":str(duration), "genre":genre, "directors":directors, "roles":roles, "isOpenLoad":str(isOpenLoad), "useSSL":str(Prefs["use_https_alt"]), "isVideoOnline":str(isVideoOnline), "useRedirector": redirector_enabled, 'urldata':'', 'pairrequired':pair_required}))
				
				try:
					oc.add(VideoClipObject(
						url = durl,
						title = status + title + ' (' + label + ')' + redirector_stat,
						thumb = GetThumb(thumb),
						duration = int(duration) * 60 * 1000,
						year = int(year),
						art = art,
						summary = summary,
						key = AddRecentWatchList(title = watch_title, url=url, summary=summary, thumb=thumb)
						)
					)
				except:
					Log('ERROR init.py>TvShowDetail %s, %s' % (e.args, (title + ' - ' + title_s)))
					Log("ERROR: %s with key:%s returned %s" % (url,url_s,server_info))
			else:
				pass
				if Prefs["use_debug"]:
					Log("Video will not be displayed as playback option !")
					Log("ERROR: %s" % error)
					Log("ERROR: %s with key:%s returned %s" % (url,url_s,server_info))
		else:
			if common.UsingOption(common.DEVICE_OPTIONS[6]):
				oc.add(MovieObject(
					key = Callback(VideoDetail, title=title, url=url, url_s=url_s, label=label, label_i_qual=None, serverts=serverts, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles),
					duration = int(duration) * 60 * 1000,
					year = int(year),
					title = label,
					rating_key = url+url_s,
					summary = summary,
					thumb = GetThumb(thumb)
					)
				)
			else:
				oc.add(DirectoryObject(
					key = Callback(VideoDetail, title=title, url=url, url_s=url_s, label=label, label_i_qual=None, serverts=serverts, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles),
					title = label,
					summary = summary,
					thumb = GetThumb(thumb)
					)
				)
			
		if label != server_lab[len(server_lab)-1] and isTimeoutApproaching(clientProd = Client.Product, item = E(url), client_id=client_id, session=session):
			Log("isTimeoutApproaching action")
			break
			#return MC.message_container('Timeout', 'Timeout: Please try again !')
		
	if treatasmovie==False and Prefs['disable_extsources'] == False and common.interface.isInitialized():
		oc.add(DirectoryObject(
			key = Callback(ExtSources, tvshowtitle=tvshow, season=season, episode=episode, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles),
			title = 'External Sources',
			summary = 'List sources of this episode by External Providers.',
			thumb = GetThumb(R(ICON_OTHERSOURCES))
			)
		)
	
	return oc
	
######################################################################################
@route(PREFIX + "/Videodetail")
def VideoDetail(title, url, url_s, label_i_qual, label, serverts, thumb, summary, art, year, rating, duration, genre, directors, roles, session=None, **kwargs):
	
	oc = ObjectContainer(title2=title)
	try:
		# url_s = label_i['loc']
		# label_i_qual = label_i['quality']
		server_info = None
		title_s = ''
		if Prefs["use_debug"]:
			Log("%s - %s" % (url, url_s))
		server_info, isOpenLoad, error = fmovies.GetApiUrl(url=url, key=url_s, serverts=serverts)
		
		if server_info != None:
			if label_i_qual != None:
				qual = common.getHighestQualityLabel(server_info, label_i_qual)
				title_s = label + ' - ' + qual
			else:
				title_s = label
				qual = None
			
			pair_required = False
			pair = ''
			status = ''
			isVideoOnline = 'unknown'
			if Prefs["use_linkchecker"]:
				data = server_info
				if isOpenLoad == True:
					pass
				else:
					data = E(JSON.StringFromObject({"server":server_info}))
				isVideoOnline = common.isItemVidAvailable(isOpenLoad=isOpenLoad, data=data)
				
			if isOpenLoad == True:
				pair_required = common.host_openload.isPairingRequired(url=server_info)
				if pair_required == True:
					pair = ' *Pairing required* '
				if Prefs["use_debug"]:
					Log("%s --- %s : %s" % (server_info, pair, pair_required))
				
			if isVideoOnline != str(False):
				status = common.GetEmoji(type=isVideoOnline, session=session) + ' ' + pair
			else:
				status = common.GetEmoji(type=isVideoOnline, session=session)
				
			try:
				redirector_stat = ''
				redirector_enabled = 'false'
				if common.UsingOption(key=common.DEVICE_OPTIONS[2]) and isOpenLoad == False:
					redirector_stat = ' (via Redirector)'
					redirector_enabled = 'true'
					
				durl = "fmovies://" + E(JSON.StringFromObject({"url":url, "server":common.ResolveFinalUrl(isOpenLoad, data=server_info, pair_required=pair_required), "title":title, "summary":summary, "thumb":thumb, "art":art, "year":year, "rating":rating, "duration":str(duration), "genre":genre, "roles":roles, "directors":directors, "roles":roles, "isOpenLoad":str(isOpenLoad), "useSSL":str(Prefs["use_https_alt"]), "isVideoOnline":str(isVideoOnline), "useRedirector": redirector_enabled, 'urldata':'','quality':qual, 'pairrequired':pair_required}))
					
				oc.add(VideoClipObject(
					url = durl,
					title = status + title + ' - ' + title_s + redirector_stat,
					thumb = GetThumb(thumb),
					duration = int(duration) * 60 * 1000,
					year = int(year),
					art = art,
					summary = summary,
					key = AddRecentWatchList(title=title, url=url, summary=summary, thumb=thumb)
					)
				)
			except Exception as e:
				Log('ERROR init.py>VideoDetail>Movie1 %s' % (e.args))
				Log("ERROR: %s with key:%s returned %s" % (url,url_s,server_info))
				Log('ERROR init.py>VideoDetail>Movie2 %s' % (title + ' - ' + title_s))
		else:
			pass
			if Prefs["use_debug"]:
				Log("Video will not be displayed as playback option !")
				Log("ERROR: %s" % error)
				Log("ERROR: %s with key:%s returned %s" % (url,url_s,server_info))
			return MC.message_container('Video Unavailable', 'Video Unavailable. Error: %s' % error)
	except Exception as e:
		Log("ERROR init.py>VideoDetail>Movie3 %s %s" % (url,url_s))
		Log("ERROR init.py>VideoDetail>Movie3 %s" % (server_info))
		Log('ERROR init.py>VideoDetail>Movie3 %s, %s' % (e.args, (title + ' - ' + title_s)))
		
		return MC.message_container('Video Unavailable', 'Video Unavailable. Error in Code.')

	return oc
	
######################################################################################
@route(PREFIX + "/ExtSources")
def ExtSources(title, url, summary, thumb, art, rating, duration, genre, directors, roles, movtitle=None, year=None, tvshowtitle=None, season=None, episode=None, session=None, use_prog_conc=False, **kwargs):
	
	tvshowcleaned = tvshowtitle
	if tvshowtitle != None:
		tvshowcleaned = tvshowtitle.replace(' ' + str(season),'')
	key = generatemoviekey(movtitle=movtitle, year=year, tvshowtitle=tvshowcleaned, season=season, episode=episode)
	
	prog = common.interface.checkProgress(key)
	if prog == 0:
		if common.interface.getExtSourcesThreadStatus(key=key) == False or common.interface.checkKeyInThread(key=key) == False:
			#common.interface.clearSources()
			try:
				CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
			except:
				CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
			Thread.Create(common.interface.getExtSources, {}, movtitle=movtitle, year=year, tvshowtitle=tvshowtitle, season=season, episode=episode, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY)
		time.sleep(7)
		prog = common.interface.checkProgress(key)
	if prog < 100:
		# if prog == 0:
			# common.interface.getExtSources(movtitle=movtitle, year=year, tvshowtitle=tvshowtitle, season=str(season), episode=str(episode), proxy_options=common.OPTIONS_PROXY)
			# return
		# time.sleep(1)
		# prog = common.interface.checkProgress()
		# if prog < 100:
		if use_prog_conc:
			oc = ObjectContainer(title2='External Sources - Progress %s%s' % (prog, '%'), no_history=True, no_cache=True)
			oc.add(DirectoryObject(
				key = Callback(ExtSources, movtitle=movtitle, tvshowtitle=tvshowtitle, season=season, episode=episode, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, session=session),
				title = 'Refresh - %s%s Done' % (prog,'%'),
				summary = 'List sources by External Providers.',
				thumb = GetThumb(R(ICON_OTHERSOURCES))
				)
			)
			return oc
		return MC.message_container('External Sources', 'Sources are being fetched ! Progress %s%s' % (prog,'%'))
	
	oc = ObjectContainer(title2='External Sources')
	
	watch_title = movtitle
	if season != None and episode != None:
		#watch_title = "%s - S%sE%s" % (tvshowtitle.replace(str(season),'').replace('(Special)','').strip(),season,episode)
		watch_title = common.cleantitle.tvWatchTitle(tvshowtitle,season,episode,title)
		
	#Log("Title: %s" % watch_title)
	#Log("External Sources Progress: %s" % prog)
	
	#extSour = JSON.ObjectFromString(D(common.interface.getSources()))
	extSour = common.interface.getSources(encode=False)
	
	if len(extSour) == 0:
		return MC.message_container('External Sources', 'No External Sources Available.')
	
	# match key
	filter_extSources = []
	filter_extSources += [i for i in extSour if i['key'] == key]
	
	extSourKey = []
	extSourKey += [i for i in filter_extSources]
	
	if len(extSourKey) == 0:
		return MC.message_container('External Sources', 'No External Sources Available for this video.')
		
	internal_extSources = extSourKey
	
	if Prefs["use_debug"] and common.DEV_DEBUG == True:
		Log("---------=== DEV DEBUG START ===------------")
		Log("Length sources: %s" % len(internal_extSources))
		for source in internal_extSources:
			if True:
				Log('Provider---------: %s' % source['provider'])
				Log('Source---------: %s' % source)
				Log('Online----------: %s' % source['online'])
				Log('Type: %s --- Quality: %s' % (source['rip'],source['quality']))
				Log('%s URL---------: %s' % (source['source'], source['url']))
				Log('Key: %s' % source['key'])
				Log('urldata: %s' % json.loads(common.client.b64decode(source['urldata'])))
				Log('params: %s' % json.loads(common.client.b64decode(source['params'])))
		Log("---------=== DEV DEBUG END ===------------")
		
	# filter sources based on enabled quality in common.INTERNAL_SOURCES_QUALS
	#Log(common.INTERNAL_SOURCES_QUALS)
	filter_extSources = []
	for qual in common.INTERNAL_SOURCES_QUALS: filter_extSources += [i for i in internal_extSources if i['quality'].lower() == qual['label'].lower() and str(qual['enabled'])=='True']
	internal_extSources = filter_extSources
	
	# filter sources based on enabled rip-type in common.INTERNAL_SOURCES_RIPTYPE
	#Log(common.INTERNAL_SOURCES_RIPTYPE)
	filter_extSources = []
	for riptype in common.INTERNAL_SOURCES_RIPTYPE: filter_extSources += [i for i in internal_extSources if i['rip'].lower() == riptype['label'].lower() and str(riptype['enabled'])=='True']
	internal_extSources = filter_extSources
	
	# filter sources based on enabled rip-type in common.INTERNAL_SOURCES_FILETYPE
	#Log(common.INTERNAL_SOURCES_FILETYPE)
	filter_extSources = []
	for vidtype in common.INTERNAL_SOURCES_FILETYPE: filter_extSources += [i for i in internal_extSources if i['vidtype'].lower() in vidtype['label'].lower() and str(vidtype['enabled'])=='True']
	internal_extSources = filter_extSources
	
	# filter sources based on enabled provider in common.OPTIONS_PROVIDERS
	#Log(common.OPTIONS_PROVIDERS)
	filter_extSources = []
	for provider in common.OPTIONS_PROVIDERS: filter_extSources += [i for i in internal_extSources if i['provider'].lower() == provider['name'].lower() and str(provider['enabled'])=='True']
	internal_extSources = filter_extSources
	
	# order sources based on sequence of common.INTERNAL_SOURCES / quality
	#Log(common.INTERNAL_SOURCES)
	filter_extSources = []
	for host in common.INTERNAL_SOURCES: filter_extSources += [i for i in internal_extSources if i['quality'] == '4K' and i['source'].lower() == host['name']]
	for host in common.INTERNAL_SOURCES: filter_extSources += [i for i in internal_extSources if i['quality'] == '1080p' and i['source'].lower() == host['name']]
	for host in common.INTERNAL_SOURCES: filter_extSources += [i for i in internal_extSources if i['quality'] == '720p' and i['source'].lower() == host['name']]
	for host in common.INTERNAL_SOURCES: filter_extSources += [i for i in internal_extSources if i['quality'] == '480p' and i['source'].lower() == host['name']]
	for host in common.INTERNAL_SOURCES: filter_extSources += [i for i in internal_extSources if i['quality'] == '360p' and i['source'].lower() == host['name']]
	internal_extSources = filter_extSources
	
	# order sources based on sequence of common.INTERNAL_SOURCES_FILETYPE / video type
	#Log(common.INTERNAL_SOURCES_FILETYPE)
	filter_extSources = []
	filter_extSources += [i for i in internal_extSources if 'Trailer'.lower() == i['vidtype'].lower()]
	filter_extSources += [i for i in internal_extSources if 'Movie'.lower() in i['vidtype'].lower() or 'Show'.lower() in i['vidtype'].lower()]
	filter_extSources += [i for i in internal_extSources if 'Behind the scenes'.lower() == i['vidtype'].lower()]
	filter_extSources += [i for i in internal_extSources if 'Music Video'.lower() == i['vidtype'].lower()]
	filter_extSources += [i for i in internal_extSources if 'Misc.'.lower() == i['vidtype'].lower()]
	internal_extSources = filter_extSources
	
	filter_extSources = []
	for i in internal_extSources:
		if i not in filter_extSources:
			filter_extSources.append(i)
	internal_extSources = filter_extSources
	
	for source in internal_extSources:
		status = common.GetEmoji(type=source['online'], session=session)
		vidUrl = source['url']
		
		isOpenLoad = True if source['source'] == 'openload' else False
		isVideoOnline = source['online']
		
		redirector_stat = ''
		redirector_enabled = 'false'
		if common.UsingOption(key=common.DEVICE_OPTIONS[2]) and isOpenLoad == False:
			redirector_stat = '| (via Redirector)'
			redirector_enabled = 'true'
			
		pair_required = True if source['maininfo'] == ' *Pairing required* ' else False
		
		if source['vidtype'] in 'Movie/Show':
			title_msg = "%s %s| %s | %s | %s | %s" % (status, source['maininfo'], source['rip'], source['quality'], source['source'], source['provider'])
		else:
			title_msg = "%s %s| %s | %s | %s | %s | %s" % (status, source['maininfo'], source['vidtype'], source['rip'], source['quality'], source['source'], source['provider'])
		# if Prefs["use_debug"]:
			# Log("%s --- %s" % (title_msg, vidUrl))
			# Log('Playback: %s' % common.interface.getHostsPlaybackSupport(encode=False)[source['source']])
		
		if vidUrl != None and source['enabled'] and common.interface.getHostsPlaybackSupport(encode=False)[source['source']]:
			urldata = common.client.b64decode(source['urldata'])
			urldata = json.loads(urldata)
			
			if urldata != '':
				#Log(urldata)
				urldata = E(JSON.StringFromObject(urldata))
				
			params = common.client.b64decode(source['params'])
			params = json.loads(params)
			if params != '':
				#Log(params)
				params = E(JSON.StringFromObject(params))
				
			
			durl = "fmovies://" + E(JSON.StringFromObject({"url":url, "server":vidUrl, "title":title, "summary":summary, "thumb":thumb, "art":art, "year":year, "rating":rating, "duration":str(duration), "genre":genre, "directors":directors, "roles":roles, "isOpenLoad":str(isOpenLoad), "useSSL":str(Prefs["use_https_alt"]), "isVideoOnline":str(isVideoOnline), "useRedirector": redirector_enabled, 'quality':source['quality'], 'urldata':urldata, 'params':params, 'pairrequired':pair_required}))
			try:
				oc.add(VideoClipObject(
					url = durl,
					title = title_msg + source['titleinfo'] + redirector_stat,
					thumb = GetThumb(thumb),
					art = art,
					summary = summary,
					key = AddRecentWatchList(title = watch_title, url=url, summary=summary, thumb=thumb)
					)
				)
			except:
				pass

		elif vidUrl != None and source['enabled'] == False and common.ALT_PLAYBACK:
			# ToDo
			oc.add(playback.CreateVideoObject(title, summary, thumb, params, duration, genre, vidUrl, source['quality']))
		
		elif vidUrl != None:
			try:
				url_serv = URLService.ServiceIdentifierForURL(vidUrl)
				if url_serv != None:
					oc.add(VideoClipObject(
						url = vidUrl,
						title = title_msg + ' | (via Plex Service %s)' % url_serv,
						thumb = GetThumb(thumb),
						art = art,
						summary = summary,
						key = AddRecentWatchList(title = watch_title, url=url, summary=summary, thumb=thumb)
						)
					)
			except:
				pass
	
	if Prefs['use_ext_urlservices']:
		external_extSources = extSourKey
		
		# filter sources based on enabled quality in common.INTERNAL_SOURCES_QUALS
		filter_extSources = []
		for qual in common.INTERNAL_SOURCES_QUALS: filter_extSources += [i for i in external_extSources if i['quality'].lower() == qual['label'].lower() and str(qual['enabled'])=='True']
		external_extSources = filter_extSources
		
		# filter sources based on enabled rip-type in common.INTERNAL_SOURCES_RIPTYPE
		filter_extSources = []
		for riptype in common.INTERNAL_SOURCES_RIPTYPE: filter_extSources += [i for i in external_extSources if i['rip'].lower() == riptype['label'].lower() and str(riptype['enabled'])=='True']
		external_extSources = filter_extSources
		
		# filter sources based on enabled vid-type in common.INTERNAL_SOURCES_FILETYPE
		filter_extSources = []
		for vidtype in common.INTERNAL_SOURCES_FILETYPE: filter_extSources += [i for i in internal_extSources if i['vidtype'].lower() in vidtype['label'].lower() and str(vidtype['enabled'])=='True']
		internal_extSources = filter_extSources
		
		# filter sources based on enabled provider in common.OPTIONS_PROVIDERS
		filter_extSources = []
		for provider in common.OPTIONS_PROVIDERS: filter_extSources += [i for i in external_extSources if i['provider'].lower() == provider['name'].lower() and str(provider['enabled'])=='True']
		external_extSources = filter_extSources
		
		# order sources based on quality
		filter_extSources = []
		filter_extSources += [i for i in external_extSources if i['quality'] == '4K']
		filter_extSources += [i for i in external_extSources if i['quality'] == '1080p']
		filter_extSources += [i for i in external_extSources if i['quality'] == '720p']
		filter_extSources += [i for i in external_extSources if i['quality'] == '480p']
		filter_extSources += [i for i in external_extSources if i['quality'] == '360p']
		external_extSources = filter_extSources
		
		# order sources based on sequence of common.INTERNAL_SOURCES_FILETYPE / video type
		#Log(common.INTERNAL_SOURCES_FILETYPE)
		filter_extSources = []
		filter_extSources = []
		filter_extSources += [i for i in external_extSources if 'Trailer'.lower() == i['vidtype'].lower()]
		filter_extSources += [i for i in external_extSources if 'Movie'.lower() in i['vidtype'].lower() or 'Show'.lower() in i['vidtype'].lower()]
		filter_extSources += [i for i in external_extSources if 'Behind the scenes'.lower() == i['vidtype'].lower()]
		filter_extSources += [i for i in external_extSources if 'Music Video'.lower() == i['vidtype'].lower()]
		filter_extSources += [i for i in external_extSources if 'Misc.'.lower() == i['vidtype'].lower()]
		external_extSources = filter_extSources
		
		filter_extSources = []
		for i in external_extSources:
			if i not in filter_extSources:
				filter_extSources.append(i)
		external_extSources = filter_extSources
		
		extSources_urlservice = []
		for source in external_extSources:
			ls = source
			bool = True
			for i in common.INTERNAL_SOURCES:
				if i['name'] == source['source']:
					bool = False
					break
			if bool == True:
				extSources_urlservice.append(source)
		
		for source in extSources_urlservice:
			vidUrl = source['url']
			if vidUrl != None:
				status = common.GetEmoji(type=source['online'], session=session)
				isOpenLoad = False
				isVideoOnline = source['online']
				if source['vidtype'] in 'Movie/Show':
					title_msg = "%s %s| %s | %s | %s | %s" % (status, source['maininfo'], source['rip'], source['quality'], source['source'], source['provider'])
				else:
					title_msg = "%s %s| %s | %s | %s | %s | %s" % (status, source['maininfo'], source['vidtype'], source['rip'], source['quality'], source['source'], source['provider'])
				
				try:
					url_serv = URLService.ServiceIdentifierForURL(vidUrl)
					if url_serv != None:
						oc.add(VideoClipObject(
							url = vidUrl,
							title = title_msg + source['titleinfo'] + ' | (via Plex Service %s)' % url_serv,
							thumb = GetThumb(thumb),
							art = art,
							summary = summary,
							key = AddRecentWatchList(title = watch_title, url=url, summary=summary, thumb=thumb)
							)
						)
				except:
					pass
					
	if len(oc) == 0:
		return MC.message_container('External Sources', 'No videos based on Filter Selection')
	
	return oc
	
def generatemoviekey(movtitle=None, year=None, tvshowtitle=None, season=None, episode=None):

	enc = {'movtitle':movtitle, 'year':year, 'tvshowtitle':tvshowtitle, 'season':season, 'episode':episode}
	enc = common.client.urllib.urlencode(enc)
	return common.client.b64encode(enc)

####################################################################################################
@route(PREFIX + "/ThreadTimeoutTimer")	
def ThreadTimeoutTimer(clientProd, item, client_id, **kwargs):

	if clientProd in CUSTOM_TIMEOUT_CLIENTS:
		c=0
		while c < int(CUSTOM_TIMEOUT_CLIENTS[clientProd]) + 1:
			CUSTOM_TIMEOUT_DICT[client_id][item] = c
			time.sleep(1.0)
			c += 1
			
		del CUSTOM_TIMEOUT_DICT[client_id][item]
	
####################################################################################################
@route(PREFIX + "/isTimeoutApproaching")	
def isTimeoutApproaching(clientProd, item, client_id, session=None, **kwargs):
	
	# define custom timeouts for each client along with session & item to make it unique for multiple instances
	
	if common.USE_CUSTOM_TIMEOUT == True and common.UsingOption(common.DEVICE_OPTIONS[5], session=session) and Client.Product in CUSTOM_TIMEOUT_CLIENTS:
		if client_id in CUSTOM_TIMEOUT_DICT and item in CUSTOM_TIMEOUT_DICT[client_id]:
			t_sec = int(CUSTOM_TIMEOUT_DICT[client_id][item])
			if t_sec < int(CUSTOM_TIMEOUT_CLIENTS[clientProd]):
				if Prefs["use_debug"]:
					Log("Custom Timout Timer: %s on %s: %s sec." % (D(item), client_id, t_sec))
				return False
	else:
		# return False for clients not defined in custom timeout checker
		return False
	
	# remove entry before returning True
	if Prefs["use_debug"]:
		Log("Custom Timout was reached for %s on %s" % (D(item), client_id))
		
	if client_id in CUSTOM_TIMEOUT_DICT and item in CUSTOM_TIMEOUT_DICT[client_id]:
		del CUSTOM_TIMEOUT_DICT[client_id][item]
	return True
	
####################################################################################################
@route(PREFIX + "/GetThumb")	
def GetThumb(thumb, **kwargs):
	if common.UsingOption(key=common.DEVICE_OPTIONS[1]):
		return None
	
	if thumb != None and thumb == 'N/A':
		thumb = R(ICON_UNAV)
	return thumb

####################################################################################################
@route(PREFIX + "/SimilarRecommendations")	
def SimilarRecommendations(title, similar_reccos, referer=None, **kwargs):

	oc = ObjectContainer(title2 = 'Similar to ' + title, no_cache=isForceNoCache())
	
	similar_reccos = JSON.ObjectFromString(D(similar_reccos))
	
	for elem in similar_reccos:
		name = elem['name']
		loc = fmovies.BASE_URL + elem['loc']
		thumb = elem['thumb']
		eps_nos = elem['eps_nos']
		summary = 'Plot Summary on Item Page.'
		more_info_link = elem['more_info_link']

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
			title = name,
			summary = GetMovieInfo(summary=summary, urlPath=more_info_link, referer=referer) + eps_nos,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
			)
		)
	
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu',
		thumb = R(ICON)
		)
	)
	
	return oc
	
####################################################################################################
@route(PREFIX + "/MoviesWithPeople")
def MoviesWithPeople(stars, **kwargs):

	oc = ObjectContainer(title2 = 'People Search', no_cache=isForceNoCache())
	
	roles_s = stars.split(',')
	if len(roles_s) > 0:
		roles_s = sorted(roles_s)
	for role in roles_s:
		role = common.removeAccents(role)
		oc.add(DirectoryObject(
			key = Callback(Search, query = role, surl= fmovies.BASE_URL + fmovies.STAR_PATH + role.lower().replace(' ', '-'), mode = 'people'),
			title = role + ' >>>',
			summary = 'Other movie/show starring ' + role,
			thumb = R(ICON_STAR)
			)
		)
	
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu',
		thumb = R(ICON)
		)
	)
	
	return oc
	
####################################################################################################
@route(PREFIX + "/MoviesWithTag")	
def MoviesWithTag(tags, **kwargs):

	oc = ObjectContainer(title2 = 'Tag Search', no_cache=isForceNoCache())
	
	tags_s = tags.split(',')
	if len(tags_s) > 0:
		tags_s = sorted(tags_s)
	for tag in tags_s:
		tag = re.sub(r'[^0-9a-zA-Z ]', '', tag)
		oc.add(DirectoryObject(
			key = Callback(Search, query = tag, surl= fmovies.BASE_URL + fmovies.KEYWORD_PATH + tag.lower().replace(' ', '-'), mode = 'tag'),
			title = tag + ' >>>',
			summary = 'Other movie/show with keyword ' + tag,
			thumb = R(ICON_TAG)
			)
		)
	
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu',
		thumb = R(ICON)
		)
	)
	
	return oc
	
####################################################################################################
@route(PREFIX + "/getmovieinfo")
def GetMovieInfo(summary, urlPath, referer=None, **kwargs):

	if common.NoMovieInfo == True or urlPath == None and (summary == None or summary == '') or Prefs['use_web_proxy']:
		return 'Plot Summary on Item Page'
	elif summary != None and Prefs["dont_fetch_more_info"]:
		return summary
	elif urlPath == None:
		return summary
	elif Prefs["dont_fetch_more_info"]:
		return 'Plot Summary on Item Page'
		
	try:
		url = fmovies.BASE_URL + '/' + urlPath
		page_data = common.GetPageElements(url=url, referer=referer)
		
		summary = ''
		
		try:
			summary_n = page_data.xpath(".//div[@class='inner']//p[@class='desc']//text()")[0]
			summary = summary_n + ' |\n '
		except:
			pass
		
		try:
			quality = page_data.xpath(".//div[@class='inner']//span[@class='quality']//text()")[0]
			year = page_data.xpath(".//div[@class='inner']//div[@class='title']//span//text()")[0]
			rating = (page_data.xpath(".//div[@class='inner']//span[@class='imdb']//text()"))[1].strip()
			summary += 'IMDb: ' + rating + ' | ' + 'Year: ' + year + ' | ' + 'Quality: ' + quality + ' |\n '
		except:
			pass
		
		try:
			country = page_data.xpath(".//div[@class='inner']//div[@class='meta'][1]//a//text()")[0]
			genre = page_data.xpath(".//div[@class='inner']//div[@class='meta'][2]//a//text()")[0]
			summary += 'Country: ' + country + ' | ' + 'Genre: ' + genre + ' |\n '
		except:
			pass
		
		try:
			actors = (page_data.xpath(".//div[@class='inner']//div[@class='meta'][3]//text()"))[2].strip()
			summary += 'Actors: ' + actors + '\n '
		except:
			pass
			
		if summary == '':
			summary = 'Plot Summary on Item Page'

	except:
		summary = 'Plot Summary on Item Page'
		
	return summary
	
######################################################################################
# Adds a movie to the RecentWatchList list using the (title + 'R4S') as a key for the url
@route(PREFIX + "/addRecentWatchList")
def AddRecentWatchList(title, url, summary, thumb, **kwargs):

	if url == None:
		return
	#append the time string to title so we can sort old to new items
	try:
		timestr = str(int(time.time()))
		Dict[timestr+'RR44SS'+title+'RR44SS'] = title + 'RR44SS' + url +'RR44SS'+ summary + 'RR44SS' + thumb + 'RR44SS' + timestr 
		Dict.Save()
	except:
		pass
		
	return None

######################################################################################
# Loads RecentWatchList shows from Dict.  Titles are used as keys to store the show urls.
@route(PREFIX + "/RecentWatchList")
def RecentWatchList(title, session=None, **kwargs):

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")

	oc = ObjectContainer(title1=title, no_cache=isForceNoCache())
	NO_OF_ITEMS_IN_RECENT_LIST = 50
	
	urls_list = []
	items_to_del = []
	items_in_recent = []
	
	for each in Dict:
		longstring = str(Dict[each])
		
		if 'https:' in longstring and 'RR44SS' in longstring:
			longstringsplit = longstring.split('RR44SS')
			urls_list.append({'key': each, 'time': longstringsplit[4], 'val': longstring})
				
	if len(urls_list) == 0:
		return MC.message_container(title, 'No Items Available')
		
	newlist = sorted(urls_list, key=lambda k: k['time'], reverse=True)

	fmovies_base = fmovies.BASE_URL.replace('https://www.','')
	fmovies_base = fmovies_base.replace('https://','')
	
	c=0
	for each in newlist:
	
		longstring = each['val']
		longstringsplit = longstring.split('RR44SS')
		stitle = unicode(longstringsplit[0])
		url = longstringsplit[1]
		summary = unicode(longstringsplit[2])
		thumb = longstringsplit[3]
		timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(longstringsplit[4])))
		
		#Log("%s %s" % (stitle, url))
		url = url.replace('www.','')
		
		if url.replace('fmovies.to',fmovies_base) in items_in_recent or c > NO_OF_ITEMS_IN_RECENT_LIST:
			items_to_del.append(each['key'])
		elif url.replace('fmovies.se',fmovies_base) in items_in_recent or c > NO_OF_ITEMS_IN_RECENT_LIST:
			items_to_del.append(each['key'])
		elif url.replace('fmovies.is',fmovies_base) in items_in_recent or c > NO_OF_ITEMS_IN_RECENT_LIST:
			items_to_del.append(each['key'])
		else:
			items_in_recent.append(url)
				
			oc.add(DirectoryObject(
				key=Callback(EpisodeDetail, title=stitle, url=url, thumb=thumb),
				title=stitle,
				thumb=thumb,
				tagline = timestr,
				summary=summary
				)
			)
			c += 1

	if c >= NO_OF_ITEMS_IN_RECENT_LIST or len(items_to_del) > 0:
		for each in items_to_del:
			del Dict[each]
		Dict.Save()

	#oc.objects.sort(key=lambda obj: obj.tagline, reverse=True)
	
	#add a way to clear RecentWatchList list
	oc.add(DirectoryObject(
		key = Callback(ClearRecentWatchList),
		title = "Clear Recent WatchList",
		thumb = R(ICON_QUEUE),
		summary = "CAUTION! This will clear your entire Recent WatchList !"
		)
	)
	
	return oc
	
######################################################################################
# Clears the Dict that stores the bookmarks list
@route(PREFIX + "/clearRecentWatchList")
def ClearRecentWatchList(**kwargs):

	remove_list = []
	for each in Dict:
		try:
			longstring = Dict[each]
			if longstring.find(SITE.lower()) != -1 and 'http' in longstring and 'RR44SS' in longstring:
				remove_list.append(each)
		except:
			continue

	for watchlist in remove_list:
		try:
			del Dict[watchlist]
		except Exception as e:
			Log.Error('Error Clearing Recent WatchList: %s' %str(e))
			continue

	Dict.Save()
	return MC.message_container("My Recent WatchList", 'Your Recent WatchList list will be cleared soon.')
	
######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.
@route(PREFIX + "/bookmarks")
def Bookmarks(title, **kwargs):

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")
	
	oc = ObjectContainer(title1=title, no_cache=isForceNoCache())
	
	fmovies_base = fmovies.BASE_URL.replace('https://www.','')
	fmovies_base = fmovies_base.replace('https://','')
	
	items_in_bm = []
	items_to_del = []
	
	for each in Dict:
		longstring = str(Dict[each])
		
		if 'https:' in longstring and 'Key5Split' in longstring:	
			stitle = unicode(longstring.split('Key5Split')[0])
			url = longstring.split('Key5Split')[1]
			summary = unicode(longstring.split('Key5Split')[2])
			thumb = longstring.split('Key5Split')[3]
			
			url = url.replace('www.','')
			
			if 'fmovies.to' in url:
				url = url.replace('fmovies.to',fmovies_base)
			elif 'fmovies.se' in url:
				url = url.replace('fmovies.se',fmovies_base)
			elif 'fmovies.is' in url:
				url = url.replace('fmovies.is',fmovies_base)
				
			#Log("BM : %s" % url)
				
			if url not in items_in_bm:
				
				items_in_bm.append(url)
				
				if fmovies.FILTER_PATH in url:
					oc.add(DirectoryObject(
						key=Callback(Search, query=stitle.replace(' (All Seasons)',''), mode='other seasons', thumb=thumb, summary=summary),
						title=stitle,
						thumb=thumb,
						summary=summary
						)
					)
				else:
					oc.add(DirectoryObject(
						key=Callback(EpisodeDetail, title=stitle, url=url, thumb=thumb),
						title=stitle,
						thumb=thumb,
						summary=summary
						)
					)
			else:
				items_to_del.append(each)
					
	if len(items_to_del) > 0:
		for each in items_to_del:
			del Dict[each]
		Dict.Save()
				
	if len(oc) == 0:
		return MC.message_container(title, 'No Bookmarked Videos Available')
		
	oc.objects.sort(key=lambda obj: obj.title, reverse=False)
	
	#add a way to clear bookmarks list
	oc.add(DirectoryObject(
		key = Callback(ClearBookmarks),
		title = "Clear Bookmarks",
		thumb = R(ICON_QUEUE),
		summary = "CAUTION! This will clear your entire bookmark list!"
		)
	)
		
	return oc
	
######################################################################################
# Converts old style bookmarks
@route(PREFIX + "/convertbookmarks")
def convertbookmarks(**kwargs):

	try:
		Covert_List = {}
		Delete_List = []
		for each in Dict:
			longstring = str(Dict[each])
			
			if 'https:' in longstring and 'Key4Split' in longstring:	
				title = unicode(longstring.split('Key4Split')[0])
				url = longstring.split('Key4Split')[1]
				summary = unicode(longstring.split('Key4Split')[2])
				thumb = longstring.split('Key4Split')[3]
				
				Covert_List[title+'-'+E(url)] = (title + 'Key5Split' + url +'Key5Split'+ summary + 'Key5Split' + thumb)
				Delete_List.append(title)
			elif 'https:' in longstring and 'Key5Split' in longstring:
				title = unicode(longstring.split('Key5Split')[0])
				url = longstring.split('Key5Split')[1]
				summary = unicode(longstring.split('Key5Split')[2])
				thumb = longstring.split('Key5Split')[3]
				
				Delete_List.append(title+'-'+E(url))
				url = url.replace('www.','')
				Covert_List[title+'-'+E(url)] = (title + 'Key5Split' + url +'Key5Split'+ summary + 'Key5Split' + thumb)
			
		if len(Delete_List) > 0:
			for item in Delete_List:
				del Dict[item]

		if len(Covert_List) > 0:
			for item in Covert_List:
				Dict[item] = Covert_List[item]
				
		CONVERT_BMS.append('Done')
		Dict.Save()
	except:
		pass

######################################################################################
# Checks a show to the bookmarks list using the title as a key for the url
@route(PREFIX + "/checkbookmark")
def Check(title, url, **kwargs):
	
	longstring = Dict[title+'-'+E(url)]
	fmovies_urlhost = common.client.geturlhost(url)
	#Log("%s --- %s --- %s" % (longstring, url, fmovies_urlhost))
	if longstring != None and (longstring.lower()).find(SITE.lower()) != -1 and url in longstring:
		return True

	surl = url.replace(fmovies_urlhost,'fmovies.to')
	longstring = Dict[title+'-'+E(surl)]
	if longstring != None and (longstring.lower()).find(SITE.lower()) != -1 and surl in longstring:
		return True
	
	surl = url.replace(fmovies_urlhost,'fmovies.se')
	longstring = Dict[title+'-'+E(surl)]
	if longstring != None and (longstring.lower()).find(SITE.lower()) != -1 and surl in longstring:
		return True
		
	surl = url.replace(fmovies_urlhost,'fmovies.is')
	longstring = Dict[title+'-'+E(surl)]
	if longstring != None and (longstring.lower()).find(SITE.lower()) != -1 and surl in longstring:
		return True

	return False

######################################################################################
# Adds a movie to the bookmarks list using the title as a key for the url
@route(PREFIX + "/addbookmark")
def AddBookmark(title, url, summary, thumb, **kwargs):

	if Check(title=title, url=url):
		return MC.message_container(title, 'This item has already been added to your bookmarks.')
		
	Dict[title+'-'+E(url)] = (title + 'Key5Split' + url +'Key5Split'+ summary + 'Key5Split' + thumb)
	Dict.Save()
	return MC.message_container(title, 'This item has been added to your bookmarks.')

######################################################################################
# Removes a movie to the bookmarks list using the title as a key for the url
@route(PREFIX + "/removebookmark")
def RemoveBookmark(title, url, **kwargs):

	try:
		del Dict[title+'-'+E(url)]
	except:
		pass

	fmovies_urlhost = common.client.geturlhost(url)
	
	try:
		del Dict[title+'-'+E(url.replace(fmovies_urlhost,'fmovies.to'))]
	except:
		pass
	try:
		del Dict[title+'-'+E(url.replace(fmovies_urlhost,'fmovies.se'))]
	except:
		pass
	try:
		del Dict[title+'-'+E(url.replace(fmovies_urlhost,'fmovies.is'))]
	except:
		pass		
		
	Dict.Save()
	return MC.message_container(title, 'This item has been removed from your bookmarks.')

######################################################################################
# Clears the Dict that stores the bookmarks list
@route(PREFIX + "/clearbookmarks")
def ClearBookmarks(**kwargs):

	remove_list = []
	for each in Dict:
		try:
			url = Dict[each]
			if url.find(SITE.lower()) != -1 and 'http' in url and 'RR44SS' not in url:
				remove_list.append(each)
		except:
			continue

	for bookmark in remove_list:
		try:
			del Dict[bookmark]
		except Exception as e:
			Log.Error('Error Clearing Bookmarks: %s' %str(e))
			continue

	Dict.Save()
	return MC.message_container("Bookmarks", 'Your bookmark list will be cleared soon.')

######################################################################################
# Clears the Dict that stores the search list
@route(PREFIX + "/clearsearches")
def ClearSearches(**kwargs):

	remove_list = []
	for each in Dict:
		try:
			if each.find(SITE.lower()) != -1 and 'MyCustomSearch' in each:
				remove_list.append(each)
		except:
			continue

	for search_term in remove_list:
		try:
			del Dict[search_term]
		except Exception as e:
			Log.Error('Error Clearing Searches: %s' %str(e))
			continue

	Dict.Save()
	return MC.message_container("Search Queue", "Your Search Queue list will be cleared soon.")

####################################################################################################
@route(PREFIX + "/search")
def Search(query=None, surl=None, page_count='1', mode='default', thumb=None, summary=None, **kwargs):

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")

	last_page_no = page_count
	query2 = None
	
	if surl != None:
		if mode == 'people' or mode == 'tag':
			url = surl + '?page=%s' % (str(page_count))
		else:
			url = surl + '&page=%s' % (str(page_count))
	else:
		if mode == 'default':
			timestr = str(int(time.time()))
			Dict[SITE.lower() +'MyCustomSearch'+query] = query + 'MyCustomSearch' + timestr
			Dict.Save()
			url = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
		elif mode == 'other seasons':
			url = fmovies.BASE_URL + fmovies.FILTER_PATH + '?type=series&page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
		else:
			url = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))

	page_data = common.GetPageElements(url=url)
	if page_data == None and mode == 'other seasons':
		url = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
		page_data = common.GetPageElements(url=url)
		
	elems = []
	error = False
	try:
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row movie-list']//div[@class='item']")
		last_page_no = int(page_count)
		last_page_no = int(page_data.xpath(".//*[@id='body-wrapper']//ul[@class='pagination'][1]//li[last()-1]//text()")[0])
	except:
		error = True
		pass
	no_elems = len(elems)
	
	if error==True and no_elems == 0 and mode == 'other seasons':
		xurl = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
		page_data = common.GetPageElements(url=xurl)
		try:
			elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row movie-list']//div[@class='item']")
			last_page_no = int(page_count)
			last_page_no = int(page_data.xpath(".//*[@id='body-wrapper']//ul[@class='pagination'][1]//li[last()-1]//text()")[0])
		except:
			error = True
			pass
		no_elems = len(elems)
		
	try:
		oc = ObjectContainer(title2 = 'Search Results for %s' % query, no_cache=isForceNoCache())

		if mode == 'default':
			oc = ObjectContainer(title2 = 'Search Results|Page ' + str(page_count) + ' of ' + str(last_page_no), no_cache=isForceNoCache())
		elif mode == 'tag':
			oc = ObjectContainer(title2 = 'Tag: ' + query, no_cache=isForceNoCache())
		elif mode == 'people':
			oc = ObjectContainer(title2 = 'People: ' + query, no_cache=isForceNoCache())
		else:
			oc = ObjectContainer(title2 = 'Other Seasons for ' + query, no_cache=isForceNoCache())
			
		for elem in elems:
			name = elem.xpath(".//a[@class='name']//text()")[0]
			loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
			thumb = elem.xpath(".//a[@class='poster']//@src")[0].split('url=')[1]
			summary = 'Plot Summary on Item Page.'
			if query2 == None:
				try:
					query2 = common.cleantitle.onlytitle(name)
					query2 = common.cleantitle.get(query2)
				except:
					query2 = None
			
			eps_nos = ''
			title_eps_no = ''
			try:
				eps_nos = elem.xpath(".//div[@class='status']//span//text()")[0]
				eps_no_i = str(int(eps_nos.strip()))
				title_eps_no = ' (Eps:'+eps_no_i+')'
				eps_nos = ' Episodes: ' + eps_no_i
			except:
				pass
			try:
				more_info_link = elem.xpath(".//@data-tip")[0]
			except:
				more_info_link = None
			
			do = DirectoryObject(
				key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
				title = name + title_eps_no,
				summary = GetMovieInfo(summary=summary, urlPath=more_info_link, referer=url) + eps_nos,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
				)
			if mode == 'default' or mode == 'people' or mode == 'tag':
				oc.add(do)
			elif mode == 'other seasons' and query.lower() in name.lower() and len(common.cleantitle.removeParanthesis(name).lower().replace(query.lower(), '').strip()) < 3:
				fixname_SN = name.lower().replace(query.lower(),'').replace(' ','').strip()
				# when we clean name we expect the season no. only to be present - if not then maybe its not a related season i.e. skip item
				try:
					if len(fixname_SN) > 0:
						fixname_SN_i = int(fixname_SN)
						newname = query + " " + ("%02d" % fixname_SN_i)
					else:
						newname = query
					do.title = newname + title_eps_no
				except:
					pass
				oc.add(do)
				
		if mode == 'other seasons' or mode == 'tag':
			oc.objects.sort(key=lambda obj: obj.title, reverse=False)
	except Exception as e:
		Log('__init.py__ > Search Error: %s URL: %s' % (e, url))
		pass
			
	if Prefs['disable_extsources'] == False and common.interface.isInitialized() and page_count=='1' and mode == 'default':
		if True:
			oc_ext = SearchExt(query=query, query2=query2, append=True)
			for o in oc_ext:
				oc.add(o)
		else:
			oc.add(DirectoryObject(
					key = Callback(SearchExt, query=query),
					title = 'Search in External Sources',
					summary = 'Search for a possible match in External Sources',
					thumb = R(ICON_SEARCH)
					)
				)
	
	if len(oc) == 0:
		if mode == 'other seasons':
			return MC.message_container('Other Seasons', 'No Other Seasons Available currently')
		else:
			if page_count=='1':
				return MC.message_container('Search Results', 'No Videos Available - please refine your query !')
			else:
				return MC.message_container('Search Results', 'No More Videos Available')
				
	if mode == 'default' or mode == 'people' or mode == 'tag' or (mode == 'other seasons' and no_elems == len(oc)):
		if int(page_count) < last_page_no:
			oc.add(NextPageObject(
				key = Callback(Search, query = query, surl = surl, page_count = str(int(page_count) + 1), mode=mode),
				title = "Next Page (" + str(int(page_count) + 1) +'/'+ str(last_page_no) + ") >>",
				thumb = R(ICON_NEXT)
				)
			)
			
	if mode == 'other seasons' and page_count=='1':
		if Check(title=query + ' (All Seasons)',url=url):
			oc.add(DirectoryObject(
				key = Callback(RemoveBookmark, title = query + ' (All Seasons)', url = url),
				title = "Remove Bookmark",
				summary = 'Removes the current show season from the Boomark que',
				thumb = R(ICON_QUEUE)
				)
			)
		else:
			oc.add(DirectoryObject(
				key = Callback(AddBookmark, title = query + ' (All Seasons)', url = url, summary=summary, thumb=thumb),
				title = "Add Bookmark",
				summary = 'Adds the current show season to the Boomark que',
				thumb = R(ICON_QUEUE)
				)
			)
		
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu',
		thumb = R(ICON)
		)
	)

	return oc
	
####################################################################################################
@route(PREFIX + "/SearchExt")
def SearchExt(query=None, query2=None, session=None, append=False, **kwargs):

	if append == False:
		oc = ObjectContainer(title2='Search In External Sources', no_cache=isForceNoCache())
	else:
		oc = []
	
	extSearches = []
	if query != None:
		extSearches = [(query, None)]
		title, year = common.cleantitle.getTitleAndYear(query)
		if query2 != None:
			extSearches.append((query2, None))
		extSearches.append((title, year))
		extSearches.append((title, None))
	
	imdbArray = []
	showitems = []
	
	for extS in extSearches:
		title, year = extS
		res = common.interface.searchOMDB(title, year)
		try:
			item = json.loads(res.content)
		except:
			item = None
		
		try:
			if item != None and item['imdbID'] not in imdbArray:
				item['doSearch'] = False
				imdbArray.append(item['imdbID'])
				showitems.append(item)
		except:
			pass
			
	for extS in extSearches:
		title, year = extS
		items = common.interface.searchOMDB(title, year, doSearch=True)
		try:
			if items != None:
				for item in items:
					if item.imdb_id not in imdbArray:
						new_item = {}
						new_item['doSearch'] = True
						imdbArray.append(item.imdb_id)
						
						new_item['imdbID'] = item.imdb_id
						new_item['Title'] = item.title
						new_item['Year'] = item.year
						new_item['Poster'] = item.poster
						new_item['Type'] = item.type
						
						new_item['Plot'] = 'Plot Summary Not Available'
						new_item['Runtime'] = 'Not Available'
						new_item['imdbRating'] = 'Not Available'
						new_item['Actors'] = 'Not Available'
						new_item['Director'] = 'Not Available'
						new_item['Genre'] = 'Not Available'
						
						showitems.append(new_item)
		except:
			pass

	try:
		CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
	except:
		CACHE_EXPIRY = common.CACHE_EXPIRY_TIME

	for item in showitems:
	
		imdbid = unicode(item['imdbID'])
		title = unicode(item['Title'])
		year = unicode(item['Year'])
		thumb = unicode(item['Poster'])
		summary = unicode(item['Plot'])
		duration = unicode(item['Runtime']).replace('min','').strip()
		rating = unicode(item['imdbRating'])
		roles = unicode(item['Actors'])
		directors = unicode(item['Director'])
		genre = unicode(item['Genre'])
		type = unicode(item['Type'])
		
		if str(directors) == 'N/A':
			directors = 'Not Available'
		if str(roles) == 'N/A':
			roles = 'Not Available'
		
		if type == 'movie':
			mtitle = title
			tvtitle = None
			season = None
			episode = None
		else:
			mtitle = None
			tvtitle = title
			episode = None
			season = None
		
		watch_title = '%s (%s)' % (title,year)
				
		summary += '\n '
		summary += 'Actors: ' + roles + '\n '
		summary += 'Directors: ' + directors + '\n '
		
		if str(duration) == 'Not Available':
			summary += 'Runtime: ' + str(duration) + '\n '
		else:
			summary += 'Runtime: ' + str(duration) + ' min.' + '\n '
		
		summary += 'Year: ' + year + '\n '
		summary += 'Genre: ' + genre + '\n '
		summary += 'IMDB rating: ' + rating + '\n '
		
		summary = unicode(summary.replace('–','-'))
		
		if '–' in year:
			y = year.split('–')
			year = str(y[0]).strip()
		
		if type == 'movie':
			key = generatemoviekey(movtitle=mtitle, year=year, tvshowtitle=tvtitle, season=season, episode=episode)
			if common.interface.getExtSourcesThreadStatus(key=key) == False:
				Thread.Create(common.interface.getExtSources, {}, movtitle=mtitle, year=year, tvshowtitle=tvtitle, season=season, episode=episode, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY)
		
		thumb = GetThumb(thumb)
		dobj = DirectoryObject(
			key = Callback(DoIMDBExtSources, title=title, year=year, type=type, imdbid=imdbid, summary=summary, thumb=thumb, session=session), 
			title = '*'+watch_title,
			summary = summary,
			thumb = thumb)
			
		if append == True:
			oc.append(dobj)
		else:
			oc.add(dobj)
	
	if len(oc) == 0 and append == False:
		return MC.message_container('Search Results', 'No Videos Available in External Sources - Please refine your Search term')
	
	return oc
	
####################################################################################################
@route(PREFIX + "/DoIMDBExtSources")
def DoIMDBExtSources(title, year, type, imdbid, season=None, episode=None, episodeNr='1', summary=None, simpleSummary=False, thumb=None, item=None, session=None, **kwargs):

	if type == 'movie':
		res = common.interface.searchOMDB(title, year)
		try:
			item = json.loads(res.content)
		except:
			item = None
		
		title = item['Title']
		year = item['Year']
		thumb = item['Poster']
		summary = item['Plot']
		duration = item['Runtime'].replace('min','').strip()
		rating = item['imdbRating']
		roles = item['Actors']
		directors = item['Director']
		genre = item['Genre']
		
		if str(directors) == 'N/A':
			directors = 'Not Available'
		if str(roles) == 'N/A':
			roles = 'Not Available'
	
		mtitle = title
		tvtitle = None
		season = None
		episode = None
		
		summary += '\n '
		summary += 'Actors: ' + roles + '\n '
		summary += 'Directors: ' + directors + '\n '
		
		if str(duration) == 'Not Available':
			summary += 'Runtime: ' + str(duration) + '\n '
		else:
			summary += 'Runtime: ' + str(duration) + ' min.' + '\n '
		
		summary += 'Year: ' + year + '\n '
		summary += 'Genre: ' + genre + '\n '
		summary += 'IMDB rating: ' + rating + '\n '
		
		summary = unicode(summary)

		return ExtSources(movtitle=title, year=year, title=title, url=None, summary=summary, thumb=thumb, art=None, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, season=season, episode=episode, session=session)
	else:
	
		if season != None:
			season = str(int(season))
		if episode != None:
			episode = str(int(episode))
	
		if season == None:
			oc = ObjectContainer(title2='%s (%s)' % (title, year), no_cache=isForceNoCache())
			try:
				res = common.interface.omdb.request(t=title, y=year, Season=str(1), i=imdbid)
				SeasonNR = int(json.loads(res.content)['totalSeasons'])
				for i in range(1,SeasonNR+1):
					oc.add(DirectoryObject(key = Callback(DoIMDBExtSources, title=title, year=year, type=type, imdbid=imdbid, thumb=thumb, summary=summary, season=str(i), episode=None, session=session), 
						title = '*%s (Season %s)' % (title, str(i)),
						thumb = thumb))
				DumbKeyboard(PREFIX, oc, DoIMDBExtSourcesSeason, dktitle = 'Input Season No.', dkthumb=R(ICON_DK_ENABLE), dkNumOnly=True, dkHistory=False, title=title, year=year, type=type, imdbid=imdbid, thumb=thumb, summary=summary, session=session)
			except:
				DumbKeyboard(PREFIX, oc, DoIMDBExtSourcesSeason, dktitle = 'Input Season No.', dkthumb=R(ICON_DK_ENABLE), dkNumOnly=True, dkHistory=False, title=title, year=year, type=type, imdbid=imdbid, thumb=thumb, summary=summary, session=session)
	
		elif episode == None:
			oc = ObjectContainer(title2='%s (Season %s)' % (title, season), no_cache=isForceNoCache())
			
			try:
				CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
			except:
				CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
			
			x_title=title
			x_year=year
			x_season=season
			x_imdbid=imdbid
			x_thumb=thumb
			
			DumbKeyboard(PREFIX, oc, DoIMDBExtSourcesEpisode, dktitle = 'Input Episode No.', dkthumb=R(ICON_DK_ENABLE), dkNumOnly=True, dkHistory=False, title=title, year=year, type=type, imdbid=imdbid, thumb=thumb, season=season, summary=summary, session=session)
			
			for e in range(int(episodeNr),1000):
				item = common.interface.omdb.get(title=x_title, year=x_year, season=x_season, episode=str(e), imdbid=x_imdbid)
				if len(item) == 0:
					break
					
				title = item['title']
				year = item['year']
				thumb = item['poster']
				summary = item['plot']
				duration = item['runtime'].replace('min','').strip()
				rating = item['imdb_rating']
				roles = item['actors']
				directors = item['director']
				genre = item['genre']
				released = item['released']
				
				if str(summary) == 'N/A':
					summary = 'Plot Summary Not Available'
				if str(directors) == 'N/A':
					directors = 'Not Available'
				if str(roles) == 'N/A':
					roles = 'Not Available'
				
				summary += '\n '
				summary += 'Actors: ' + roles + '\n '
				summary += 'Directors: ' + directors + '\n '
				
				if str(duration) == 'Not Available':
					summary += 'Runtime: ' + str(duration) + '\n '
				else:
					summary += 'Runtime: ' + str(duration) + ' min.' + '\n '
				
				summary += 'Year: ' + year + '\n '
				summary += 'Genre: ' + genre + '\n '
				summary += 'IMDB rating: ' + rating + '\n '
				
				if '–' in year:
					y = year.split('–')
					year = str(y[0]).strip()
					
				watch_title = 'S%02dE%02d - %s' % (int(season), e, title)
				if int(season) > 99 and e > 99:
					watch_title = 'S%03dE%03d - %s' % (int(season), e, title)
				elif e > 99:
					watch_title = 'S%02dE%03d - %s' % (int(season), e, title)
					
				summary = watch_title + ' : ' + summary
				watch_title = unicode(watch_title)
				
				if str(released) != 'N/A' and str(released) != 'Not Available':
					summary = released + ' : ' + summary
				
				summary = unicode(summary.replace('–','-'))
					
				oc.add(DirectoryObject(
				key = Callback(DoIMDBExtSources, title=x_title, year=x_year, type=type, imdbid=imdbid, item=E(JSON.StringFromObject(item)), season=season, episode=str(e), session=session), 
				title = '*'+watch_title,
				summary = summary,
				thumb = thumb))
				
				key = generatemoviekey(movtitle=None, year=x_year, tvshowtitle=x_title, season=season, episode=str(e))
				if common.interface.getExtSourcesThreadStatus(key=key) == False:
					Thread.Create(common.interface.getExtSources, {}, movtitle=None, year=x_year, tvshowtitle=x_title, season=season, episode=str(e), proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY)
				
				time.sleep(0.1)
				
				if int(episodeNr) + 4 == e:
					oc.add(DirectoryObject(
					key = Callback(DoIMDBExtSources, title=x_title, year=x_year, type=type, imdbid=x_imdbid, thumb=x_thumb, season=season, episodeNr=str(e+1), session=session), 
					title = 'Next Page >>',
					thumb = R(ICON_NEXT)))
					break
				
		else:
			item = JSON.ObjectFromString(D(item))
		
			#title = item['title']
			#year = item['year']
			
			thumb = item['poster']
			summary = item['plot']
			duration = item['runtime'].replace('min','').strip()
			rating = item['imdb_rating']
			roles = item['actors']
			directors = item['director']
			genre = item['genre']
			released = item['released']
			
			if simpleSummary == False:
				if str(summary) == 'N/A':
					summary = 'Plot Summary Not Available'
				if str(directors) == 'N/A':
					directors = 'Not Available'
				if str(roles) == 'N/A':
					roles = 'Not Available'
			
				summary += '\n '
				summary += 'Actors: ' + roles + '\n '
				summary += 'Directors: ' + directors + '\n '
				
				if str(duration) == 'Not Available':
					summary += 'Runtime: ' + str(duration) + '\n '
				else:
					summary += 'Runtime: ' + str(duration) + ' min.' + '\n '
				
				summary += 'Year: ' + year + '\n '
				summary += 'Genre: ' + genre + '\n '
				summary += 'IMDB rating: ' + rating + '\n '
				
				if str(released) != 'N/A' and str(released) != 'Not Available':
					summary = released + ' : ' + summary
			
			summary = unicode(summary.replace('–','-'))
			

			return ExtSources(tvshowtitle=title, year=year, title=title, url=None, summary=summary, thumb=thumb, art=None, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, season=season, episode=episode, session=session)
			
		return oc
			
####################################################################################################
@route(PREFIX + "/DoIMDBExtSourcesSeason")
def DoIMDBExtSourcesSeason(query, title, year, type, imdbid, summary, thumb, session, **kwargs):

	try:
		season = str(int(query))
	except:
		season = '1'

	return DoIMDBExtSources(title=title, year=year, type=type, imdbid=imdbid, season=season, summary=summary, thumb=thumb, session=session)
	
####################################################################################################
@route(PREFIX + "/DoIMDBExtSourcesEpisode")
def DoIMDBExtSourcesEpisode(query, title, year, type, imdbid, season, summary, thumb, session, **kwargs):

	try:
		episode = str(int(query))
	except:
		episode = '1'
		
	watch_title = 'S%02dE%02d' % (int(season), int(episode))
	if int(season) > 99 and int(episode) > 99:
		watch_title = 'S%03dE%03d' % (int(season), int(episode))
	elif int(episode) > 99:
		watch_title = 'S%02dE%03d' % (int(season), int(episode))
		
	watch_title = unicode(watch_title)
	
	try:
		CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
	except:
		CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
	
	key = generatemoviekey(movtitle=None, year=year, tvshowtitle=title, season=season, episode=episode)
	if common.interface.getExtSourcesThreadStatus(key=key) == False:
		Thread.Create(common.interface.getExtSources, {}, movtitle=None, year=year, tvshowtitle=title, season=season, episode=episode, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY)
		
	item = {}
	item['poster'] = thumb
	item['plot'] = summary
	item['runtime'] = 'Not Available'
	item['imdb_rating'] = 'Not Available'
	item['actors'] = 'Not Available'
	item['director'] = 'Not Available'
	item['genre'] = 'Not Available'
	item['released'] = 'Not Available'
	
	oc = ObjectContainer(title2='%s (%s)' % (title, watch_title), no_cache=isForceNoCache())
	oc.add(DirectoryObject(
		key = Callback(DoIMDBExtSources, title=title, year=year, type=type, imdbid=imdbid, item=E(JSON.StringFromObject(item)), simpleSummary=True, season=season, episode=episode, session=session), 
		title = '*'+watch_title,
		summary = watch_title + ' : ' + summary,
		thumb = thumb))
		
	return oc
	
####################################################################################################
@route(PREFIX + "/searchQueueMenu")
def SearchQueueMenu(title, **kwargs):

	oc = ObjectContainer(title2='Search Using Term', no_cache=isForceNoCache())
	
	urls_list = []
	
	for each in Dict:
		query = Dict[each]
		try:
			if each.find(SITE.lower()) != -1 and 'MyCustomSearch' in each and query != 'removed':
				timestr = '1483228800'
				if 'MyCustomSearch' in query:
					split_query = query.split('MyCustomSearch')
					query = split_query[0]
					timestr = split_query[1]
					
				urls_list.append({'key': query, 'time': timestr})
				
		except:
			pass
			
	if len(urls_list) == 0:
		return MC.message_container(title, 'No Items Available')
		
	newlist = sorted(urls_list, key=lambda k: k['time'], reverse=True)
		
	oc.add(DirectoryObject(
		key = Callback(ClearSearches),
		title = "Clear Search Queue",
		thumb = R(ICON_SEARCH),
		summary = "CAUTION! This will clear your entire search queue list!"
		)
	)
	
	for item in newlist:
		timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(item['time'])))
		query = item['key']
		oc.add(DirectoryObject(key = Callback(Search, query = query, page_count='1'), title = query, tagline = timestr, thumb = R(ICON_SEARCH)))

	return oc
	
######################################################################################
@route(PREFIX + "/Help")
def Help():

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")

	oc = ObjectContainer(title2 = 'Help', no_cache=isForceNoCache())
	help_page_links = common.GetPageAsString(url=common.Help_Videos)
	help_page_items = help_page_links.split('||')
	for item in help_page_items:
		if '|' in item:
			meta = item.split('|')
			if len(meta) >=4:
				try:
					oc.add(VideoClipObject(
						title = meta[0],
						url = meta[1],
						thumb = meta[2],
						summary = meta[3])
					)
				except:
					pass
	return oc
	
######################################################################################
@route(PREFIX + "/filtersetup")
def FilterSetup(title, key1 = None, key2val = None, mode='add', update=True, session=None, **kwargs):

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")

	oc = ObjectContainer(title2 = title, no_cache=isForceNoCache())
	
	if len(Filter) == 0:
		# Initialize Filter Data
		FilterSetupData()
		
	if len(Filter) == 0:
		return MC.message_container("Filter Setup Error", "Sorry but the Filter could not be created !")
	#Log(Filter)
	
	if session == None:
		session = common.getSession()
		
	if len(Filter_Search) == 0:
		# Set defaults for 'Sort' & 'Order'
		Filter_Search['sort'] = 'post_date'
		Filter_Search['order'] = 'desc'
	
	if key1 == None:
		for f_key in sorted(Filter):
			oc.add(DirectoryObject(
				key = Callback(FilterSetup, title = title, key1 = f_key),
				title = f_key.title()
				)
			)
	else:
		oc = ObjectContainer(title2 = title + ' (' + key1.title() + ')', no_cache=isForceNoCache())
		
		for f2_key in sorted(Filter[key1]):

			selected = ''
			# This indicates selected item
	
			if (key2val != None and key2val == Filter[key1][f2_key]):
				if (mode == 'add' or key1 == 'sort' or key1 == 'order'):
					selected = ' ' + common.GetEmoji(type='pos', mode='simple', session=session)
			
			elif (key1 != 'sort' and key1 != 'order' and key1 in Filter_Search and Filter[key1][f2_key] in Filter_Search[key1]):
				selected = ' ' + common.GetEmoji(type='pos', mode='simple', session=session)
			
			elif (key2val == None and key1 in Filter_Search and Filter[key1][f2_key] in Filter_Search[key1]):
				selected = ' ' + common.GetEmoji(type='pos', mode='simple', session=session)
				
				
			key_title = f2_key.title() + selected
			if key1 == 'quality' or 'mode: and' in f2_key.lower(): # dont Camelcase quality values and Mode in Genre
				key_title = f2_key + selected
			
			if mode == 'rem' and selected != '':
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title, key1 = key1, key2val = Filter[key1][f2_key], update = MakeSelections(key1=key1, key2val=key2val, mode='rem', k2v= Filter[key1][f2_key]), mode='rem'),
					title = key_title
					)
				)
			elif selected != '':
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title, key1 = key1, key2val = Filter[key1][f2_key], update = MakeSelections(key1=key1, key2val=key2val, mode='rem', k2v= Filter[key1][f2_key]), mode='rem'),
					title = key_title
					)
				)
			else:
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title, key1 = key1, key2val = Filter[key1][f2_key], update = MakeSelections(key1=key1, key2val=key2val, mode=mode, k2v=Filter[key1][f2_key])),
					title = key_title
					)
				)
		
		oc.add(DirectoryObject(
			key = Callback(FilterSetup, title = title, key1 = None, key2val = None, update = MakeSelections(key1=key1, key2val=key2val, mode=mode, k2v=key2val)),
			title = 'Continue Filter Setup >>'
			)
		)
		
	# Build search string
	searchString = ''
	searchStringDesc = 'Sorting using ' + common.GetKeyFromVal(Filter['sort'],Filter_Search['sort']) + ' in ' + common.GetKeyFromVal(Filter['order'],Filter_Search['order']) + ' order.'
	
	for k1 in Filter_Search:
		if k1 != 'sort' and k1 != 'order':
			searchStringDesc += ' Filter ' + k1.title() + ' has '
			c=0
			for k2v in Filter_Search[k1]:
				searchString += k1 + '[]=' + k2v + '&'
				if c == len(Filter_Search[k1])-1:
					searchStringDesc += common.GetKeyFromVal(Filter[k1],k2v) + '.'
				else:
					searchStringDesc += common.GetKeyFromVal(Filter[k1],k2v) + ', '
				c += 1

	searchString += Filter_Search['sort'] + ':' + Filter_Search['order']
	searchString = searchString.replace(' ','+')

	
	# Build Filter-Search Url
	#https://fmovies.se/filter?sort=post_date%3Adesc&genre%5B%5D=25&genre_mode=and&country%5B%5D=2&type%5B%5D=movie&quality%5B%5D=HD+1080p&release%5B%5D=2017
	searchUrl = fmovies.BASE_URL + fmovies.FILTER_PATH + '?' + urllib2.quote(searchString, safe='_+=&')
	
	oc.add(DirectoryObject(
		key = Callback(Search, surl=searchUrl),
		title = '<<< Submit Search >>>',
		summary = searchStringDesc
		)
	)
	
	oc.add(DirectoryObject(
		key = Callback(ClearFilter),
		title = 'Reset Search Filter'
		)
	)
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu'
		)
	)
	
	return oc
	
######################################################################################
@route(PREFIX + "/makeselections")
def MakeSelections(key1, key2val, mode, k2v, **kwargs):
	
	if k2v != key2val or key1 == None or key2val == None:
		return False
	
	# Update Filter_Search based on previous selection
	# ToDo: This will deselect
	if (key1 != 'sort' and key1 != 'order' and key1 != None and key2val != None and key1 in Filter_Search and key2val in Filter_Search[key1] and mode == 'rem'):
		Filter_Search[key1].remove(key2val)
		if len(Filter_Search[key1]) == 0:
			del Filter_Search[key1]
	
	# This indicates selected item
	elif (key1 != None and key2val != None and (key1 not in Filter_Search or key2val not in Filter_Search[key1]) and mode == 'add'):
		if key1 != None and key2val != None:
			if key1 == 'sort' or key1 == 'order':
				Filter_Search[key1] = key2val
			else:
				if key1 not in Filter_Search:
					Filter_Search[key1] = []
				if key2val not in Filter_Search[key1]:
					Filter_Search[key1].append(key2val)
		
	return True

######################################################################################
@route(PREFIX + "/clearfilter")
def ClearFilter(**kwargs):
	Filter_Search.clear()
	
	oc = ObjectContainer(title2 = "Filter Reset", no_cache=isForceNoCache())
	oc.add(DirectoryObject(
		key = Callback(FilterSetup, title=CAT_FILTERS[3]),
		title = CAT_FILTERS[3]
		)
	)
	return oc

######################################################################################
@route(PREFIX + "/filtersetupdata-%s" % time.time())
def FilterSetupData(**kwargs):

	try:
		url = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?keyword=fmovies+%s' % time.time()
		page_data = common.GetPageElements(url=url)
		
		Filter['sort']={}
		Filter['order']={'Ascending':'asc', 'Descending':'desc'}
		Filter['genre']={}
		Filter['country']={}
		Filter['type']={}
		Filter['quality']={}
		Filter['release']={}
		
		# Get Sort by info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter']//li")
		for elem in elems:
			key = elem.xpath(".//text()")[0].strip()
			val = elem.xpath(".//@data-value")[0].split(':')[0].strip()
			Filter['sort'][key] = val
			
		# Get Genre info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter genre']//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			if key == 'Mode: AND':
				key = 'Mode: AND (unchecked is OR)'
			Filter['genre'][key] = val
			
		# Get Country info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter country']//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			Filter['country'][key] = val
			
		# Get Type info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter type']//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			Filter['type'][key] = val
		
		# Get Quality info - page has wrong div classification using div[6] instead
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row']//div[6]//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			Filter['quality'][key] = val
			
		# Get Release info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter quality']//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			Filter['release'][key] = val
	
	except:
		# Empty partial Filter if failed - error will be reported when using Filter
		Filter.clear()

######################################################################################
@route(PREFIX + "/isForceNoCache")
def isForceNoCache(**kwargs):
	# no_cache=isForceNoCache()
	
	if common.CACHE_EXPIRY == 0:
		return True
		
	return False

######################################################################################
@route(PREFIX + "/verify2partcond")
def verify2partcond(ep_title, **kwargs):
# verify 2 part episode condition (eg. "01-02" type of titles)
# single parts can also have "-" in episode titles and this condition will verify (eg "00 - Special - The Journey So Far")

	try:
		splitem = ep_title.split("-")
		for item in splitem:
			i = int(item.strip()) # if success for both splits then it must be a 2 part vid
		return True
	except:
		pass
	return False

######################################################################################
#
# Supposed to run when Prefs are changed but doesnt seem to work on Plex as expected
# https://forums.plex.tv/discussion/182523/validateprefs-not-working
# Update - does not support producing a dialog - show dialog somewhere else/later
#
@route(PREFIX + "/ValidatePrefs")
def ValidatePrefs(changed=True, **kwargs):

	if changed == True:
		Log("Your Channel Preferences have changed !")
	
	if fmovies.BASE_URL != Prefs["base_url"]:
		del common.CACHE_COOKIE[:]
		fmovies.BASE_URL = Prefs["base_url"]
		HTTP.Headers['Referer'] = fmovies.BASE_URL
	
	try:
		common.CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
	except:
		common.CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
	
	if changed == True:
		DumpPrefs(changed=changed)
		
	common.CACHE.clear()
	common.CACHE_META.clear()
	HTTP.ClearCache()
	
	ValidateMyPrefs()
	
	return
	
######################################################################################
@route(PREFIX + "/DumpPrefs")
def DumpPrefs(changed=False, **kwargs):
	Log("=================FMoviesPlus Prefs=================")
	Log("Channel Preferences:")
	Log("Base site url: %s" % (fmovies.BASE_URL))
	Log("Cache Expiry Time (in mins.): %s" % (Prefs["cache_expiry_time"]))
	Log("No Extra Info. for Nav. Pages (Speeds Up Navigation): %s" % (Prefs["dont_fetch_more_info"]))
	Log("Use SSL Web-Proxy: %s" % (Prefs["use_web_proxy"]))
	Log("Use Alternate SSL/TLS: %s" % (Prefs["use_https_alt"]))
	Log("Use Other Installed URL Services: %s" % (Prefs["use_ext_urlservices"]))
	Log("Use LinkChecker for Videos: %s" % (Prefs["use_linkchecker"]))
	Log("Enable Debug Mode: %s" % (Prefs["use_debug"]))
	Log("=============================================")
	
	if changed == False:
		ValidatePrefs(changed=False)

######################################################################################
@route(PREFIX + "/ClientInfo")
def ClientInfo(session=None, **kwargs):
	Log("=================FMoviesPlus Client Info=================")
	Log(common.TITLE + ' v. %s %s' % (common.VERSION, common.TAG))
	Log("OS: " + sys.platform)
	Log("Client.Product: %s" % Client.Product)
	Log("Client.Platform: %s" % Client.Platform)
	Log("Client.Version: %s" % Client.Version)
	Log("=============================================")
	
	DumpDeviceOptions(session=session)
	
######################################################################################
@route(PREFIX + "/DumpDeviceOptions")
def DumpDeviceOptions(session=None, **kwargs):

	Log("=================FMoviesPlus Device Options=================")
	Log("Device Options:")
	if session == None:
		session = common.getSession()
	for devOpt in common.DEVICE_OPTION.keys():
		key = 'Toggle' + devOpt + session
		Log("%s : %s | %s" % (devOpt, 'Disabled' if (Dict[key]==None or Dict[key]=='disabled') else 'Enabled', common.DEVICE_OPTION[devOpt]))
	
	Log("=============================================")

######################################################################################
@route(PREFIX + "/ValidateMyPrefs")
def ValidateMyPrefs(**kwargs):

	try:
		test_cache_time = int(Prefs["cache_expiry_time"])
	except:
		ret = ['Error Cache Time', 'Cache Time field needs only numbers.']
		Log("%s : %s" % (ret[0], ret[1]))
		VALID_PREFS_MSGS.append(ret)
	
######################################################################################
@route(PREFIX + "/DisplayMsgs")
def DisplayMsgs(**kwargs):

	if len(VALID_PREFS_MSGS) > 0:
		ret = VALID_PREFS_MSGS[0]
		VALID_PREFS_MSGS.remove(ret)
		Log("Removed - %s : %s" % (ret[0], ret[1]))
		return MC.message_container(ret[0], ret[1])

