######################################################################################
#
#	FMovies.se by Coder Alpha
# 	https://github.com/coder-alpha/FMoviesPlus.bundle
#
######################################################################################

import re, urllib, urllib2, json, sys, time, random
import common, updater, fmovies, tools, download
from DumbTools import DumbKeyboard
import AuthTools
from __builtin__ import eval

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
ICON_UPARROW = "icon-uparrow.png"
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
ICON_OTHERSOURCESDOWNLOAD = "icon-othersourcesdownload.png"
ICON_SAVE = "icon-save.png"
ICON_QUALITIES = "icon-qualities.png"
ICON_FILESIZES = "icon-filesizes.png"
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
ICON_PLEX = "icon-plex.png"
ICON_DOWNLOADS = "icon-downloads.png"
ICON_REQUESTS = "icon-requests.png"
ICON_TOOLS = "icon-tools.png"
ICON_WARNING = "icon-warning.png"

MC = common.NewMessageContainer(common.PREFIX, common.TITLE)

CHECK_AUTH = 'CheckAuth'
######################################################################################
# Set global variables

CAT_WHATS_HOT = []
CAT_WHATS_HOT_REGULAR = ['Sizzlers','Most Favourited','Recommended','Most Watched This Week','Most Watched This Month','Latest Movies','Latest TV-Series','Requested Movies']
CAT_WHATS_HOT_ANIME = ['Recently Updated (Anime)','Recently Updated Sub (Anime)','Recently Updated Dub (Anime)', 'Trending (Anime)', 'Recently Added (Anime)', 'Ongoing (Anime)', 'Requested (Anime)']
CAT_REGULAR = ['Anime','Movies','TV-Series','Top-IMDb','Most Watched','Sitemap Listing']
CAT_FILTERS = ['Release','Genre','Country','Filter Setup >>>']
CAT_GROUPS = ['What\'s Hot ?', 'Movies & TV-Series', 'Sort using...','Site News']

Filter = {}
Filter_Search = {}

FilterExt = {}
FilterExt_Search = {}

SITE_NEWS_LOCS = []

VALID_PREFS_MSGS = []

CONVERT_BMS = []

CUSTOM_TIMEOUT_DICT = {}

CUSTOM_TIMEOUT_CLIENTS = {'Plex Web': 15}

######################################################################################

def Start():

	Thread.Create(SleepAndUpdateThread, {}, session='Generic')
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
	
	for x in CAT_WHATS_HOT_REGULAR:
		CAT_WHATS_HOT.append(x)
	for x in CAT_WHATS_HOT_ANIME:
		CAT_WHATS_HOT.append(x)
	
	try:
		CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
	except:
		CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
		
	HTTP.CacheTime = CACHE_EXPIRY
	Log.Debug("HTTP Cache Time set to %s min." % int(CACHE_EXPIRY/60))
	
	HTTP.Headers['User-Agent'] = common.client.randomagent()
	fmovies.BASE_URL = Prefs["new_base_url"]
	if common.CHECK_BASE_URL_REDIRECTION == True:
		RED_URL = common.client.request(fmovies.BASE_URL, output='geturl', timeout=7)
		if RED_URL != None and fmovies.BASE_URL not in RED_URL:
			Log("***Base URL has been overridden and set based on redirection: %s ***" % RED_URL[:-1])
			fmovies.BASE_URL = RED_URL[:-1]
	HTTP.Headers['Referer'] = fmovies.BASE_URL
	common.BASE_URL = fmovies.BASE_URL
	
	DumpPrefs()
	ValidateMyPrefs()
	
	# convert old style bookmarks to new
	if common.DEV_BM_CONVERSION and len(CONVERT_BMS) == 0:
		convertbookmarks()

######################################################################################
# Menu hierarchy
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
@route(PREFIX + "/MainMenu")
def MainMenu(**kwargs):

	fmovies.BASE_URL = Prefs["new_base_url"]
	if common.CHECK_BASE_URL_REDIRECTION == True:
		RED_URL = common.client.request(fmovies.BASE_URL, output='geturl', timeout=7)
		if RED_URL != None and fmovies.BASE_URL not in RED_URL:
			Log("*** Base URL has been overridden and set based on redirection: %s ***" % RED_URL[:-1])
			fmovies.BASE_URL = RED_URL[:-1]
	HTTP.Headers['Referer'] = fmovies.BASE_URL
	common.BASE_URL = fmovies.BASE_URL
	
	session = common.getSession()
	common.set_control_settings(session=session)
	ClientInfo(session=session)
	if len(VALID_PREFS_MSGS) > 0:
		return DisplayMsgs()
	
	oc = ObjectContainer(title2=TITLE, no_cache=common.isForceNoCache())
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[0], session=session), title = CAT_GROUPS[0], thumb = R(ICON_HOT)))
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[1], session=session), title = CAT_GROUPS[1], thumb = R(ICON_MOVIES)))
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[2], session=session), title = CAT_GROUPS[2], thumb = R(ICON_FILTER)))
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[3], session=session), title = CAT_GROUPS[3], thumb = R(ICON_INFO)))
	
	oc.add(DirectoryObject(key = Callback(FilterExtSetup, title = 'External Listing', session=session), title = 'External Listing', thumb = R(ICON_OTHERSOURCES)))
	
	# ToDo: Not quite sure how to read back what was actually played from ServiceCode and not just show a viewed item
	oc.add(DirectoryObject(key = Callback(RecentWatchList, title="Recent WatchList", session=session), title = "Recent WatchList", thumb = R(ICON_LATEST)))
	oc.add(DirectoryObject(key = Callback(Bookmarks, title="Bookmarks", session = session), title = "Bookmarks", thumb = R(ICON_QUEUE)))
	oc.add(DirectoryObject(key = Callback(Downloads, title="Downloads", session = session), title = "Downloads", thumb = R(ICON_DOWNLOADS)))
	oc.add(DirectoryObject(key = Callback(SearchQueueMenu, title = 'Search Queue', session = session), title = 'Search Queue', summary='Search using saved search terms', thumb = R(ICON_SEARCH_QUE)))
	
	if common.UsingOption(key=common.DEVICE_OPTIONS[0], session=session):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search, session = session), thumb = R(ICON_SEARCH), title='Search', summary='Search', prompt='Search for...'))
	
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
@route(PREFIX + "/PreCacheStuff")
def PreCacheStuff():

	PRE_CACHE_URLS = [fmovies.BASE_URL, fmovies.BASE_URL + '/home', fmovies.BASE_URL + fmovies.SITE_MAP, common.ANIME_URL]

	for url in PRE_CACHE_URLS:
		try:
			Thread.Create(common.GetPageAsString, {}, url)
			#HTTP.PreCache(newurl)
			if Prefs["use_debug"]:
				Log("Pre-Caching : %s" % url)
		except Exception as e:
			Log(e)

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
		Thread.Create(download.trigger_que_run)
	
######################################################################################
@route(PREFIX + "/SleepAndUpdateThread")
def SleepAndUpdateThread(update=True, startthread=True, session=None, **kwargs):

	doSave = False
	
	try:
		DOWNLOAD_OPTIONS_SAVED = JSON.ObjectFromString(D(Dict['DOWNLOAD_OPTIONS']))
		#Log("DOWNLOAD_OPTIONS %s" % DOWNLOAD_OPTIONS_SAVED)
		common.DOWNLOAD_OPTIONS = DOWNLOAD_OPTIONS_SAVED
	except Exception as e:
		Log(e)
		DownloadOptions(session=session)
		doSave = True
		
	####################################
		
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
			doSave = True
	except:
		pass
	#Log("common.INTERNAL_SOURCES_QUALS %s" % common.INTERNAL_SOURCES_QUALS)
	
	try:
		LOAD_T = Dict['INTERNAL_SOURCES_SIZES']
		if LOAD_T != None:
			ARRAY_T = JSON.ObjectFromString(D(LOAD_T))
		if LOAD_T != None and len(ARRAY_T) > 0:
			del common.INTERNAL_SOURCES_SIZES[:]
			for q in ARRAY_T:
				common.INTERNAL_SOURCES_SIZES.append(q)
		else:
			del common.INTERNAL_SOURCES_SIZES[:]
			for q in common.INTERNAL_SOURCES_SIZES_CONST:
				common.INTERNAL_SOURCES_SIZES.append(q)
			doSave = True
	except:
		pass
	#Log("common.INTERNAL_SOURCES_SIZES %s" % common.INTERNAL_SOURCES_SIZES)

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
			doSave = True
	except:
		pass
	#Log("common.INTERNAL_SOURCES_RIPTYPE %s" % common.INTERNAL_SOURCES_RIPTYPE)
	
	try:
		LOAD_T = Dict['INTERNAL_SOURCES_FILETYPE']
		if LOAD_T != None:
			ARRAY_T = JSON.ObjectFromString(D(LOAD_T))
		if LOAD_T != None and len(ARRAY_T) > 0:
			del common.INTERNAL_SOURCES_FILETYPE[:]
			for r in ARRAY_T:
				common.INTERNAL_SOURCES_FILETYPE.append(r)
				
			for r in common.INTERNAL_SOURCES_FILETYPE:
				ok_bool = False
				for r2 in common.INTERNAL_SOURCES_FILETYPE_CONST:
					if r['label'] == r2['label']:
						ok_bool = True
						break
				if ok_bool == False:
					common.INTERNAL_SOURCES_FILETYPE.remove(r)
			for r in common.INTERNAL_SOURCES_FILETYPE_CONST:
				ok_bool = False
				for r2 in common.INTERNAL_SOURCES_FILETYPE:
					if r['label'] == r2['label']:
						ok_bool = True
						break
				if ok_bool == False:
					common.INTERNAL_SOURCES_FILETYPE.append(r)
		else:
			del common.INTERNAL_SOURCES_FILETYPE[:]
			for q in common.INTERNAL_SOURCES_FILETYPE_CONST:
				common.INTERNAL_SOURCES_FILETYPE.append(q)
			doSave = True
	except:
		pass
	#Log("common.INTERNAL_SOURCES_FILETYPE %s" % common.INTERNAL_SOURCES_FILETYPE)

	try:
		LOAD_T = Dict['OPTIONS_PROVIDERS']
		curr_provs = LOAD_T
		ExtProviders(curr_provs=curr_provs,session=session)
	except:
		ExtProviders(session=session)
		doSave = True
		
	try:
		LOAD_T = Dict['OPTIONS_PROXY']
		curr_proxies = LOAD_T
		proxy = JSON.ObjectFromString(D(curr_proxies))
		#Log("loaded proxy %s" % proxy)
		proxy_n = E(JSON.StringFromObject(proxy[0]))
		ExtProxies(n=proxy_n,curr_proxies=curr_proxies,session=session)
	except:
		ExtProxies(session=session)
		doSave = True
		
	try:
		LOAD_T = Dict['INTERNAL_SOURCES']
		curr_sources = LOAD_T
		sources = JSON.ObjectFromString(D(curr_sources))
		#Log("sources %s" % sources)
		sources_n = E(JSON.StringFromObject(sources[0]))
		ExtHosts(n=sources_n,curr_sources=curr_sources,session=session)
	except:
		ExtHosts(session=session)
		doSave = True
		
	if doSave == True:
		Dict.Save()
		
	if update == True:
		PreCacheStuff()
		
	Thread.Create(download.DownloadInit)
		
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
def Options(session, **kwargs):

	oc = ObjectContainer(title2='Options', no_cache=common.isForceNoCache())
	
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
	
	oc.add(DirectoryObject(key = Callback(tools.DevToolsC), title = "Tools", summary='Tools - Save/Load Bookmarks', thumb = R(ICON_TOOLS)))
	
	oc.add(DirectoryObject(key = Callback(DownloadOptions, title="Download Options", session = session), title = "Download Options", thumb = R(ICON_DOWNLOADS)))
	
	if common.interface.isInitialized():
		oc.add(DirectoryObject(key = Callback(InterfaceOptions, session=session), title = 'Interface Options', thumb = R(ICON_PREFS), summary='Interface for Proxies, Hosts, Providers and Playback Quality'))
		oc.add(DirectoryObject(key = Callback(ResetExtOptions, session=session), title = "Reset Interface Options", summary='Resets Interface Options', thumb = R(ICON_REFRESH)))
	else:
		oc.add(DirectoryObject(key = Callback(Options, session=session), title = 'Interface Initializing.. Please wait & retry', thumb = R(ICON_ALERT)))
			
	oc.add(DirectoryObject(key = Callback(ResetAllOptions, session=session), title = "Factory Reset", summary='Factory Reset. Sets everything as a clean new installation. Channel Pref/Setting options are not affected !', thumb = R(ICON_REFRESH)))
	
	oc.add(DirectoryObject(key = Callback(MainMenu),title = '<< Main Menu',thumb = R(ICON)))
		
	return oc
	
######################################################################################
@route(PREFIX + "/deviceoptions")
def DeviceOptions(session, **kwargs):

	oc = ObjectContainer(title2='Device Options', no_cache=common.isForceNoCache())
	
	c = 1
	
	user = common.control.setting('%s-%s' % (session, 'user'))
	if user != None:
		summary = 'UserName: %s' % user
		title_msg = "00). %s" % summary
		oc.add(DirectoryObject(key=Callback(MyMessage, 'Info', summary), title = title_msg))
	
	for key in sorted(common.DEVICE_OPTIONS):
		summary = common.DEVICE_OPTION[key]
		bool = False if (Dict['Toggle'+key+session] == None or Dict['Toggle'+key+session] == 'disabled') else True
		title_msg = "%02d). %s %s | %s" % (c, common.GetEmoji(type=bool, mode='simple', session=session), key, summary)
		oc.add(DirectoryObject(key=Callback(common.setDictVal, key=key, val=not bool, session=session), title = title_msg))
		c += 1
	
	return oc
	
######################################################################################
@route(PREFIX + "/interfaceoptions")
def InterfaceOptions(session, **kwargs):
	
	if AuthTools.CheckAdmin() == False:
		return MC.message_container('Admin Access Only', 'Only the Admin can perform this action !')

	oc = ObjectContainer(title2='Interface Options', no_cache=common.isForceNoCache())
	
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
	oc.add(DirectoryObject(key = Callback(ExtHostsSizes, session=session), title = "Sizes Allowed", summary='Enable/Disable External Host File Sizes.', thumb = R(ICON_FILESIZES)))
	oc.add(DirectoryObject(key = Callback(Summarize, session=session), title = "Summarize Options", summary='Shows a quick glance of all options', thumb = R(ICON_SUMMARY)))
	
	oc.add(DirectoryObject(key = Callback(MainMenu),title = '<< Main Menu',thumb = R(ICON)))
	
	return oc
	
######################################################################################
@route(common.PREFIX + "/downloadoptions")
def DownloadOptions(session, refresh=0, **kwargs):
	
	if AuthTools.CheckAdmin() == False:
		return MC.message_container('Admin Access Only', 'Only the Admin can perform this action !')

	oc = ObjectContainer(title2='Download Options', no_cache=common.isForceNoCache())
	#Log(common.DOWNLOAD_OPTIONS)
	
	LIB_SECTIONS_TYPES = ['show', 'movie']
	for type in LIB_SECTIONS_TYPES:
		movie_show_sections = download.section_info(type)
		#Log(movie_show_sections)
		if len(movie_show_sections) > 0:
			set_default = False
			if len(common.DOWNLOAD_OPTIONS[type]) == 0:
				set_default = True
			else:
				set_default = True
				for section in movie_show_sections:
					for section_saved in common.DOWNLOAD_OPTIONS[type]:
						if section[3] == section_saved['path'] and section[2] == section_saved['title']:
							set_default = False
							break

			for section in movie_show_sections:
				bool = False
				item = {}
				item['key'] = section[0]
				item['title'] = section[2]
				item['path'] = section[3]
				if len(common.DOWNLOAD_OPTIONS[type]) == 0 or set_default == True:
					bool = True
					set_default = False
					
					item['enabled'] = bool
					common.DOWNLOAD_OPTIONS[type].append(item)
				else:
					skip = False
					for i in common.DOWNLOAD_OPTIONS[type]:
						if i['path'] == section[3] and i['title'] == section[2]:
							bool = i['enabled']
							skip = True
							break
					if skip == False:
						item['enabled'] = bool
						common.DOWNLOAD_OPTIONS[type].append(item)
		
				title_msg = 'Library:%s | Type:%s | Path:%s | Enabled:%s' % (section[2], type.title(), section[3], common.GetEmoji(type=bool, mode='simple', session=session))
				oc.add(DirectoryObject(title = title_msg, key = Callback(SetDownloadChoice, session=session, key=section[0], title=section[2], type=type, path=section[3], bool=bool)))
				
	if len(oc) == 0:
		return MC.message_container('No Library found', 'No library was found ! Please define a Movie and TV-Show library first !')

	oc.add(DirectoryObject(
		key = Callback(DownloadOptions, session=session, refresh=int(refresh)+1),
		title = 'Refresh',
		summary = 'Refresh to load any changes made to the library paths.',
		thumb = R(ICON_REFRESH)
	))
	
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Save Selection >>',
		summary = 'Save the Selection for Download Options',
		thumb = R(ICON_SAVE)
	))
		
	Dict['DOWNLOAD_OPTIONS'] = E(JSON.StringFromObject(common.DOWNLOAD_OPTIONS))
	Dict.Save()
	
	#Log(common.DOWNLOAD_OPTIONS)
			
	return oc
	
@route(common.PREFIX + "/setdownloadchoice")
def SetDownloadChoice(session, title, type, path, key, bool, **kwargs):
	
	item = {}
	item['key'] = key
	item['title'] = title
	item['path'] = path
	item['enabled'] = True if bool == 'True' else False
	try:
		
		for i in common.DOWNLOAD_OPTIONS[type]:
			if i['key'] == item['key'] and i['title'] == item['title'] and i['path'] == item['path']:
				common.DOWNLOAD_OPTIONS[type].remove(i)
	except:
		pass
		
	#Log(item)
	item['enabled'] = False if bool == 'True' else True
	#Log(item)
		
	#if item['enabled'] == True:
	common.DOWNLOAD_OPTIONS[type].append(item)
		
	#Log(common.DOWNLOAD_OPTIONS)
	
	Dict['DOWNLOAD_OPTIONS'] = E(JSON.StringFromObject(common.DOWNLOAD_OPTIONS))
	Dict.Save()
	
	return DownloadOptions(session)
	
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
		title_msg = "Enabled: %s | Host: %s | Quality: %s | Captcha: %s | Working: %s | Speed: %s sec." % (common.GetEmoji(type=host['enabled'], mode='simple', session=session), host['name'], host['quality'], common.GetEmoji(type=str(host['captcha']), mode='simple', session=session), common.GetEmoji(type=host['working'], mode='simple', session=session), host['speed'])
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
		
	for sz in common.INTERNAL_SOURCES_SIZES:
		label = sz['label']
		bool = sz['enabled']
		title_msg = "Enabled: %s | File Sizes: %s" % (common.GetEmoji(type=bool, mode='simple', session=session), label)
		oc.add(DirectoryObject(title = title_msg, key = Callback(MC.message_container, header="Summary Screen", message="Does Nothing")))
	

	for rt in common.INTERNAL_SOURCES_RIPTYPE:
		label = rt['label']
		bool = rt['enabled']
		title_msg = "Enabled: %s | Rip-Type: %s" % (common.GetEmoji(type=bool, mode='simple', session=session), label)
		oc.add(DirectoryObject(title = title_msg, key = Callback(MC.message_container, header="Summary Screen", message="Does Nothing")))
		
	for ft in common.INTERNAL_SOURCES_FILETYPE:
		label = ft['label']
		bool = ft['enabled']
		title_msg = "Enabled: %s | File-Type: %s" % (common.GetEmoji(type=bool, mode='simple', session=session), label)
		oc.add(DirectoryObject(title = title_msg, key = Callback(MC.message_container, header="Summary Screen", message="Does Nothing")))
		
	Log(" === INTERFACE LOGGER txt START === ")
		
	common.interface.getHostsLoggerTxts()
	
	common.interface.getProvidersLoggerTxts()
	
	common.interface.getControlLoggerTxts()
	
	Log(" === INTERFACE LOGGER txt END === ")
		
	return oc
	
######################################################################################
@route(PREFIX + "/ExtHostsRipType")
def ExtHostsRipType(session, item=None, setbool='True', **kwargs):

	oc = ObjectContainer(title2='External Hosts RipType')
	
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
		oc.add(DirectoryObject(key = Callback(ExtHostsRipType, session=session, item=label, setbool=not bool), title = title_msg, thumb = Resource.ContentsOfURLWithFallback(url=None, fallback=None)))
		
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
def ExtHostsFileType(session, item=None, setbool='True', **kwargs):

	if item!=None and item in 'Movie/Show' and setbool == 'False':
		return MC.message_container('Info', 'Movie/Show selection cannot be disabled !')

	oc = ObjectContainer(title2='External Hosts Video Type')
	
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
		oc.add(DirectoryObject(key = Callback(ExtHostsFileType, session=session, item=label, setbool=not bool), title = title_msg, thumb = Resource.ContentsOfURLWithFallback(url=None, fallback=None)))
		
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
def ExtHostsQuals(session, item=None, setbool='True', **kwargs):

	oc = ObjectContainer(title2='External Hosts Qualities')
	
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
		oc.add(DirectoryObject(key = Callback(ExtHostsQuals, session=session, item=label, setbool=not bool), title = title_msg, thumb = Resource.ContentsOfURLWithFallback(url=None, fallback=None)))
		
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
@route(PREFIX + "/ExtHostsSizes")
def ExtHostsSizes(session, item=None, setbool='True', **kwargs):

	oc = ObjectContainer(title2='External Hosts File Sizes')
	
	for sz in common.INTERNAL_SOURCES_SIZES:
	
		label = sz['label']
		bool = sz['enabled']
		if bool == 'True':
			bool = True
		else:
			bool = False
		
		if label == item:
			bool = not bool
		
		title_msg = "Enabled: %s | File Sizes: %s" % (common.GetEmoji(type=bool, mode='simple', session=session), label)
		oc.add(DirectoryObject(key = Callback(ExtHostsSizes, session=session, item=label, setbool=not bool), title = title_msg, thumb = Resource.ContentsOfURLWithFallback(url=None, fallback=None)))
		
	oc.add(DirectoryObject(
			key = Callback(MainMenu, update = MakeSelectionExtHostsSizes(item=item, setbool=setbool)),
			title = '<< Save Selection >>',
			summary = 'Save the Selection which is used when listing External Sources.',
			thumb = R(ICON_SAVE)
		))

	return oc

######################################################################################
@route(PREFIX + "/MakeSelectionExtHostsSizes")
def MakeSelectionExtHostsSizes(item=None, setbool='True', **kwargs):

	if item != None:
		ARRAY_T = []
		ARRAY_T += [q for q in common.INTERNAL_SOURCES_SIZES]
		del common.INTERNAL_SOURCES_SIZES[:]
		
		for sz in ARRAY_T:
			bool = sz['enabled']
			if item == sz['label']:
				bool = setbool
			
			sz['enabled']=bool
			common.INTERNAL_SOURCES_SIZES.append(sz)
		
	#Log(common.INTERNAL_SOURCES_SIZES)
	Dict['INTERNAL_SOURCES_SIZES'] = E(JSON.StringFromObject(common.INTERNAL_SOURCES_SIZES))
	Dict.Save()

######################################################################################
@route(PREFIX + "/ExtProviders")
def ExtProviders(session, curr_provs=None, refresh=False, item=None, setbool='True', **kwargs):

	oc = ObjectContainer(title2='External Providers')
	
	if refresh == True:
		common.interface.init()
	
	scanned_extProviders = JSON.ObjectFromString(D(common.interface.getProviders()))
	
	ARRAY_T = []
	for prov in scanned_extProviders:
		prov['enabled'] = True
		ARRAY_T.append(prov)

	if curr_provs == None:
		curr_provs = []
		curr_provs += [q for q in common.OPTIONS_PROVIDERS]
	else:
		curr_provs = JSON.ObjectFromString(D(curr_provs))
			
	del common.OPTIONS_PROVIDERS[:]
	common.OPTIONS_PROVIDERS = []
	
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
		
		if 'enabled' in provider.keys():
			if provider['online'] == False:
				provider['enabled'] = False
			pass
		else:
			provider['enabled'] = True
			
		set_bool = common.control.setting(common.INTERFACE_OPTIONS_LABELS['Provider']+'-'+provider['name'])
		if set_bool != provider['enabled']:
			common.set_settings_to_control(common.INTERFACE_OPTIONS_LABELS['Provider']+'-'+provider['name'], provider['enabled'])

		title_msg = "%02d | Enabled: %s | Provider: %s | Url: %s | Online: %s | Proxy Req.: %s | Parser: %s | Speed: %s sec." % (c, common.GetEmoji(type=provider['enabled'], mode='simple', session=session), provider['name'], provider['url'], common.GetEmoji(type=str(provider['online']), mode='simple', session=session),common.GetEmoji(type=str(provider['online_via_proxy']), mode='simple', session=session), common.GetEmoji(type=str(provider['parser']), mode='simple', session=session), provider['speed'])
		
		oc.add(DirectoryObject(key = Callback(SetProviderOptions, session=session, n=E(JSON.StringFromObject(provider)), curr_prov=E(JSON.StringFromObject(common.OPTIONS_PROVIDERS))), title = title_msg, summary = title_msg if provider['msg']=='' else provider['msg'], thumb = Resource.ContentsOfURLWithFallback(url = provider['logo'], fallback=ICON_QUESTION)))
		
	#oc.add(DirectoryObject(key = Callback(ExtProviders, refresh=True), title = "Refresh External Providers", summary='Reload newly installed External Host Providers.', thumb = R(ICON_REFRESH)))
		
	oc.add(DirectoryObject(
			key = Callback(MainMenu, update = MakeSelectionProviders()),
			title = '<< Save Selection >>',
			summary = 'Save the Selection which is used when listing External Sources.',
			thumb = R(ICON_SAVE)
		))
		
	return oc
	
######################################################################################
@route(PREFIX + "/SetProviderOptions")
def SetProviderOptions(session, refresh=False, n=None, curr_prov=None, option='0', **kwargs):
	
	provider = JSON.ObjectFromString(D(n))
	order = JSON.ObjectFromString(D(curr_prov))
	
	oc = ObjectContainer(title2='Set External Provider Options')
	
	c = 0
	for h in common.OPTIONS_PROVIDERS:
		if h['name'] == provider['name']:
			common.OPTIONS_PROVIDERS.remove(h)
			break
		c += 1
	
	reorder = False
	if option == '1':
		provider['enabled'] = False
	elif option == '2':
		provider['enabled'] = True
	elif option == '3':
		reorder = True
	
	if reorder == True:
		common.OPTIONS_PROVIDERS.insert(0,provider)
	else:
		common.OPTIONS_PROVIDERS.insert(c,provider)
	curr_prov = E(JSON.StringFromObject(common.OPTIONS_PROVIDERS))
	
	title_msg = "%02d | Enabled: %s | Provider: %s | Url: %s | Online: %s | Proxy Req.: %s | Parser: %s | Speed: %s sec." % (c, common.GetEmoji(type=provider['enabled'], mode='simple', session=session), provider['name'], provider['url'], common.GetEmoji(type=str(provider['online']), mode='simple', session=session),common.GetEmoji(type=str(provider['online_via_proxy']), mode='simple', session=session), common.GetEmoji(type=str(provider['parser']), mode='simple', session=session), provider['speed'])
	
	if provider['enabled'] == True:
		oc.add(DirectoryObject(key = Callback(SetProviderOptions, session=session, n=E(JSON.StringFromObject(provider)), curr_prov=curr_prov, option='1'), title = 'Disable Provider', summary = title_msg, thumb = R(ICON_OK)))
	else:
		oc.add(DirectoryObject(key = Callback(SetProviderOptions, session=session, n=E(JSON.StringFromObject(provider)), curr_prov=curr_prov, option='2'), title = 'Enable Provider', summary = title_msg, thumb = R(ICON_NOTOK)))
		
	oc.add(DirectoryObject(key = Callback(ExtProviders, session=session, n=E(JSON.StringFromObject(provider)), curr_prov=curr_prov), title = 'Move to Top in Provider List', summary = title_msg if provider['msg'] == '' else '%s - %s' % (provider['msg'],title_msg), thumb = R(ICON_UPARROW)))
	
	oc.add(DirectoryObject(title = "Tools", summary='Tools for providers', key = Callback(IntProviderTools, choice=None, provider=provider['name']), thumb = R(ICON_TOOLS)))
	
	oc.add(DirectoryObject(
		key = Callback(MainMenu, update = MakeSelectionProviders()),
		title = '<< Save Selection >>',
		summary = 'Save the Selection which is used when listing External Providers.',
		thumb = R(ICON_SAVE)
		)
	)
	
	return oc
	
######################################################################################
@route(PREFIX + "/MakeSelectionProviders")
def MakeSelectionProviders(**kwargs):
	
	#Log(common.OPTIONS_PROVIDERS)
	Dict['OPTIONS_PROVIDERS'] = E(JSON.StringFromObject(common.OPTIONS_PROVIDERS))
	Dict.Save()

######################################################################################
@route(PREFIX + "/ExtHosts")
def ExtHosts(session, refresh=False, n=None, curr_sources=None, **kwargs):

	oc = ObjectContainer(title2='External Hosts')
	
	if refresh == True:
		common.interface.init()
		
	exHosts = JSON.ObjectFromString(D(common.interface.getHosts()))
	
	if n != None:
		n = JSON.ObjectFromString(D(n))
		order = JSON.ObjectFromString(D(curr_sources))
		if len(order) == len(exHosts):
			for h in order:
				if h['name'] == n['name']:
					order.remove(h)
			order.insert(0,n)
			
			order_2=[]
			for o1 in order:
				for o2 in exHosts:
					if o1['name'] == o2['name']:
						o2['enabled'] = o1['enabled']
						order_2.append(o2)
			order = order_2
			
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
		c += 1
		
		if 'enabled' in host.keys():
			if host['working'] == False:
				host['enabled'] = False
			pass
		else:
			host['enabled'] = True
			
		set_bool = common.control.setting(common.INTERFACE_OPTIONS_LABELS['Host']+'-'+host['name'])
		if set_bool != host['enabled']:
			common.set_settings_to_control(common.INTERFACE_OPTIONS_LABELS['Host']+'-'+host['name'], host['enabled'])
		
		title_msg = "%02d | Enabled: %s | Host: %s | Working: %s | Streaming:%s | Downloading:%s | Speed: %s s. | Captcha: %s" % (c, common.GetEmoji(type=host['enabled'], mode='simple', session=session), host['name'], common.GetEmoji(type=host['working'], mode='simple', session=session), common.GetEmoji(type=str(host['streaming']), mode='simple', session=session), common.GetEmoji(type=str(host['downloading']), mode='simple', session=session), host['speed'], common.GetEmoji(type=str(host['captcha']), mode='simple', session=session))
		
		summary = "%s%s" % ('' if host['msg'] == '' else '%s%s%s' % ('**', host['msg'], '** | '), title_msg)
		try:
			common.INTERNAL_SOURCES.append(host)
			oc.add(DirectoryObject(key = Callback(SetHostOptions, session=session, n=E(JSON.StringFromObject(host)), curr_sources=E(JSON.StringFromObject(exHosts))), title = title_msg, summary = summary, thumb = Resource.ContentsOfURLWithFallback(url = host['logo'], fallback=ICON_QUESTION)))
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
@route(PREFIX + "/SetHostOptions")
def SetHostOptions(session, refresh=False, n=None, curr_sources=None, option='0', **kwargs):
	
	host = JSON.ObjectFromString(D(n))
	order = JSON.ObjectFromString(D(curr_sources))
	
	oc = ObjectContainer(title2='Set External Host Options')
	
	c = 0
	for h in common.INTERNAL_SOURCES:
		if h['name'] == host['name']:
			common.INTERNAL_SOURCES.remove(h)
			break
		c += 1
	
	reorder = False
	if option == '1':
		host['enabled'] = False
	elif option == '2':
		host['enabled'] = True
	elif option == '3':
		reorder = True
	
	if reorder == True:
		common.INTERNAL_SOURCES.insert(0,host)
	else:
		common.INTERNAL_SOURCES.insert(c,host)
	curr_sources = E(JSON.StringFromObject(common.INTERNAL_SOURCES))
	
	title_msg = "%02d | Enabled: %s | Host: %s | Working: %s | Streaming:%s | Downloading:%s | Speed: %s s. | Captcha: %s" % (c, common.GetEmoji(type=host['enabled'], mode='simple', session=session), host['name'], common.GetEmoji(type=host['working'], mode='simple', session=session), common.GetEmoji(type=str(host['streaming']), mode='simple', session=session), common.GetEmoji(type=str(host['downloading']), mode='simple', session=session), host['speed'], common.GetEmoji(type=str(host['captcha']), mode='simple', session=session))
	
	if host['enabled'] == True:
		oc.add(DirectoryObject(key = Callback(SetHostOptions, session=session, n=E(JSON.StringFromObject(host)), curr_sources=curr_sources, option='1'), title = 'Disable Host', summary = title_msg, thumb = R(ICON_OK)))
	else:
		oc.add(DirectoryObject(key = Callback(SetHostOptions, session=session, n=E(JSON.StringFromObject(host)), curr_sources=curr_sources, option='2'), title = 'Enable Host', summary = title_msg, thumb = R(ICON_NOTOK)))
		
	oc.add(DirectoryObject(key = Callback(ExtHosts, session=session, n=E(JSON.StringFromObject(host)), curr_sources=curr_sources), title = 'Move to Top in Host List', summary = title_msg, thumb = R(ICON_UPARROW)))
	
	oc.add(DirectoryObject(title = "Tools", summary='Tools for hosts', key = Callback(IntHostTools, choice=None, myhost=host['name']), thumb = R(ICON_TOOLS)))
	
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
def ExtProxies(session, refresh=False, n=None, curr_proxies=None, **kwargs):

	oc = ObjectContainer(title2='Proxies')
	
	if refresh == True:
		common.interface.init()
		
	proxies = JSON.ObjectFromString(D(common.interface.getProxies()))
	
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
			oc.add(DirectoryObject(key = Callback(ExtProxies, session=session, n=E(JSON.StringFromObject(proxy)), curr_proxies=E(JSON.StringFromObject(proxies))), title = title_msg, summary = title_msg, thumb = R(ICON_PROXY_DEFAULT)))
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

####################################################################################################
@route(PREFIX + "/IntHostTools")
def IntHostTools(choice=None, myhost=None, mssg=None):
	
	oc = ObjectContainer(title2='%s Tools' % myhost.title())

	if choice != None:
		if choice == 'openload_unpair':
			Thread.Create(common.OpenLoadUnpair)
			time.sleep(7)
			mssg = 'UnPairing will be completed in a few seconds. Please return to previous screen.'
		if choice == 'show_dump_log':
			oc = ObjectContainer(title2='%s Log' % myhost.title())
			items = common.interface.getHostsLoggerTxts(choice=myhost, dumpToLog=False)
			if len(items) > 0:
				Thread.Create(common.interface.getHostsLoggerTxts, {}, myhost, True)
				if len(items) > 100:
					msg = '%s Log has too many entries to display (last 100 shown here), full-text will be written to Channel Log !' % myhost.title()
					oc.add(DirectoryObject(title=msg, summary=msg, key=Callback(MyMessage, title='Info', msg=msg), thumb=R(ICON_INFO)))
					for i in range(0,100):
						if 'ERROR' in items[i]:
							oc.add(DirectoryObject(title=items[i], summary=items[i], key=Callback(MyMessage, title='Error', msg=items[i]), thumb=R(ICON_ALERT)))
						elif 'FAIL' in items[i]:
							oc.add(DirectoryObject(title=items[i], summary=items[i], key=Callback(MyMessage, title='Fail', msg=items[i]), thumb=R(ICON_WARNING)))
						else:
							oc.add(DirectoryObject(title=items[i], summary=items[i], key=Callback(MyMessage, title='Info', msg=items[i]), thumb=R(ICON_INFO)))
				elif len(items) > 0:
					for i in items:
						if 'ERROR' in i:
							oc.add(DirectoryObject(title=i, summary=i, key=Callback(MyMessage, title='Error', msg=i), thumb=R(ICON_ALERT)))
						elif 'FAIL' in i:
							oc.add(DirectoryObject(title=i, summary=i, key=Callback(MyMessage, title='Fail', msg=i), thumb=R(ICON_WARNING)))
						else:
							oc.add(DirectoryObject(title=i, summary=i, key=Callback(MyMessage, title='Info', msg=i), thumb=R(ICON_INFO)))
			else:
				mssg = '%s Log has no entries !' % myhost.title()
			
		if mssg != None:
			return MC.message_container('Info', mssg)	
	else:
		oc.add(DirectoryObject(key=Callback(IntHostTools, choice='show_dump_log', myhost=myhost),
			title=u'Show/Dump log',
			thumb = R(ICON_TOOLS),
			summary=u'List the logged events and dumps to Channel log'))
		if myhost == 'openload':
			oc.add(DirectoryObject(key=Callback(IntHostTools, choice='openload_unpair', myhost=myhost),
				title=u'*Paired* - UnPair OpenLoad' if common.host_openload.isPairingDone() == True else u'*Not Paired*',
				thumb = R(ICON_TOOLS),
				summary=u'UnPair with OpenLoad'))

	if len(oc) == 0:
		return MC.message_container('Info', 'No tools available for %s' % myhost)

	return oc
	
####################################################################################################
@route(PREFIX + "/IntProviderTools")
def IntProviderTools(choice=None, provider=None, mssg=None):
	
	oc = ObjectContainer(title2='%s Tools' % provider.title())

	if choice != None:
		if choice == 'show_dump_log':
			oc = ObjectContainer(title2='%s Log' % provider.title())
			items = common.interface.getProvidersLoggerTxts(choice=provider, dumpToLog=False)
			if len(items) > 0:
				Thread.Create(common.interface.getProvidersLoggerTxts, {}, provider, True)
				if len(items) > 100:
					msg = '%s Log has too many entries to display (last 100 shown here), full-text will be written to Channel Log !' % provider.title()
					oc.add(DirectoryObject(title=msg, summary=msg, key=Callback(MyMessage, title='Info', msg=msg), thumb=R(ICON_INFO)))
					for i in range(0,100):
						if 'ERROR' in items[i]:
							oc.add(DirectoryObject(title=items[i], summary=items[i], key=Callback(MyMessage, title='Error', msg=items[i]), thumb=R(ICON_ALERT)))
						elif 'FAIL' in items[i]:
							oc.add(DirectoryObject(title=items[i], summary=items[i], key=Callback(MyMessage, title='Fail', msg=items[i]), thumb=R(ICON_WARNING)))
						else:
							oc.add(DirectoryObject(title=items[i], summary=items[i], key=Callback(MyMessage, title='Info', msg=items[i]), thumb=R(ICON_INFO)))
				elif len(items) > 0:
					for i in items:
						if 'ERROR' in i:
							oc.add(DirectoryObject(title=i, summary=i, key=Callback(MyMessage, title='Error', msg=i), thumb=R(ICON_ALERT)))
						elif 'FAIL' in i:
							oc.add(DirectoryObject(title=i, summary=i, key=Callback(MyMessage, title='Fail', msg=i), thumb=R(ICON_WARNING)))
						else:
							oc.add(DirectoryObject(title=i, summary=i, key=Callback(MyMessage, title='Info', msg=i), thumb=R(ICON_INFO)))
			else:
				mssg = '%s Log has no entries !' % provider.title()
			
		if mssg != None:
			return MC.message_container('Info', mssg)	
	else:
		oc.add(DirectoryObject(key=Callback(IntProviderTools, choice='show_dump_log', provider=provider),
			title=u'Show/Dump log',
			thumb = R(ICON_TOOLS),
			summary=u'List the logged events and dumps to Channel log'))

	if len(oc) == 0:
		return MC.message_container('Info', 'No tools available for %s' % provider)

	return oc
	
######################################################################################
@route(PREFIX + "/clearcache")
def ClearCache(**kwargs):
	
	common.CACHE.clear()
	common.CACHE_META.clear()
	HTTP.ClearCache()
	tools.ClearCache(tools.caches_path)

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
	
	msg = ''
	pref_cook = Prefs["reqkey_cookie"]
	if pref_cook !=None and len(pref_cook) > 0:
		msg = 'Please clear or update your reqkey Prefs field.'
	
	return MC.message_container('Reset Cookies', 'Cookies have been reset and token text dumped to log (if required) ! %s' % msg)
	
######################################################################################
@route(PREFIX + "/ResetExtOptions")
def ResetExtOptions(session, **kwargs):

	if AuthTools.CheckAdmin() == False:
		return MC.message_container('Admin Access Only', 'Only the Admin can perform this action !')
	
	FilterExt_Search.clear()
	FilterExt.clear()
	
	del common.OPTIONS_PROVIDERS[:]
	del common.OPTIONS_PROXY[:]
	del common.INTERNAL_SOURCES[:]
	Dict['OPTIONS_PROXY'] = None
	Dict['OPTIONS_PROVIDERS'] = None
	Dict['INTERNAL_SOURCES'] = None
	Dict['INTERNAL_SOURCES_QUALS'] = None
	Dict['INTERNAL_SOURCES_SIZES'] = None
	Dict['INTERNAL_SOURCES_RIPTYPE'] = None
	Dict['INTERNAL_SOURCES_FILETYPE'] = None
	Dict.Save()
	
	Thread.Create(SleepAndUpdateThread,{},True,False,session)
	
	return MC.message_container('Reset Options', 'Interface Options have been Reset !')
	
######################################################################################
@route(PREFIX + "/ResetAllOptions")
def ResetAllOptions(session, doReset=False, **kwargs):

	if AuthTools.CheckAdmin() == False:
		return MC.message_container('Admin Access Only', 'Only the Admin can perform this action !')
	
	if doReset == False:
		oc = ObjectContainer(title2 = 'Confirm Factory Reset', no_cache=common.isForceNoCache())
		oc.add(DirectoryObject(key = Callback(tools.DevToolsC, title='save_config'), title = 'INFO - Make a Backup', summary = 'Make a Backup Config. of your Channel Options.', thumb = R(ICON_SAVE)))
		oc.add(DirectoryObject(key = Callback(Options, session=session), title = 'No', summary = 'Return to Options Menu', thumb = R(ICON_NOTOK)))
		oc.add(DirectoryObject(key = Callback(ResetAllOptions, session=session, doReset=True), title = 'Yes', summary = 'This will erase all information stored in the Plugin Dictionary (Bookmarks, Recent Watchlist, Searches, Device Options, etc.)', thumb = R(ICON_OK)))
		oc.add(DirectoryObject(key = Callback(MainMenu),title = '<< Main Menu',thumb = R(ICON)))
		return oc
	
	for i in Dict:
		Dict[i] = None
	Dict.Reset()
	Dict.Save()
	
	del common.OPTIONS_PROVIDERS[:]
	del common.OPTIONS_PROXY[:]
	del common.INTERNAL_SOURCES[:]
	common.DOWNLOAD_OPTIONS = {'movie':[], 'show':[]}
	common.INTERNAL_SOURCES_SIZES = list(common.INTERNAL_SOURCES_SIZES_CONST)
	common.INTERNAL_SOURCES_QUALS = list(common.INTERNAL_SOURCES_QUALS_CONST)
	common.INTERNAL_SOURCES_RIPTYPE = list(common.INTERNAL_SOURCES_RIPTYPE_CONST)
	common.INTERNAL_SOURCES_FILETYPE = list(common.INTERNAL_SOURCES_FILETYPE_CONST)

	# common.INTERNAL_SOURCES_QUALS = [{'label':'4K','enabled': 'True'},{'label':'1080p','enabled': 'True'},{'label':'720p','enabled': 'True'},{'label':'480p','enabled': 'True'},{'label':'360p','enabled': 'True'}]
	# common.INTERNAL_SOURCES_RIPTYPE = [{'label':'BRRIP','enabled': 'True'},{'label':'PREDVD','enabled': 'True'},{'label':'CAM','enabled': 'True'},{'label':'TS','enabled': 'True'},{'label':'SCR','enabled': 'True'},{'label':'UNKNOWN','enabled': 'True'}]
	# common.INTERNAL_SOURCES_FILETYPE = [{'label':'Movie/Show','enabled': 'True'},{'label':'Trailer','enabled': 'True'},{'label':'Behind the scenes','enabled': 'False'},{'label':'Music Video','enabled': 'False'},{'label':'Deleted Scenes','enabled': 'False'},{'label':'Interviews','enabled': 'False'},{'label':'Misc.','enabled': 'False'}]
	# common.INTERNAL_SOURCES_SIZES = [{'label':'> 2GB','enabled': 'True','LL':2*common.TO_GB,'UL':100*common.TO_GB},{'label':'1GB - 2GB','enabled': 'True','LL':1*common.TO_GB,'UL':2*common.TO_GB},{'label':'0.5GB - 1GB','enabled': 'True','LL':0.5*common.TO_GB,'UL':1*common.TO_GB},{'label':'0GB - 0.5GB','enabled': 'True','LL':1,'UL':0.5*common.TO_GB},{'label':'0GB','enabled': 'False','LL':0,'UL':0}]
	
	FilterExt_Search.clear()
	FilterExt.clear()
	
	Thread.Create(SleepAndUpdateThread, {}, session=session)
	
	return MC.message_container('Reset All Options', 'All Dictionary stored Options have been Reset to Factory Defaults !')
	
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
	
	oc = ObjectContainer(title2 = title, no_cache=common.isForceNoCache())
	
	if title == CAT_GROUPS[0]:
		elems = CAT_WHATS_HOT
	elif title == CAT_GROUPS[1]:
		elems = CAT_REGULAR
	elif title == CAT_GROUPS[2]:
		elems = CAT_FILTERS
		
	if title == CAT_GROUPS[1]:
		for title in elems:
			oc.add(DirectoryObject(
				key = Callback(ShowCategory, title = title, session=session),
				title = title
				)
			)
	elif title == CAT_GROUPS[3]:
		
		page_data, error = common.GetPageElements(url=fmovies.BASE_URL + '/fmovies')
		if page_data == None:
			bool, noc, page_data = testSite(url=fmovies.BASE_URL + '/fmovies')
			if bool == False:
				return noc

		notices_all = []
		try:
			# Developer Notice
			try:
				notice_txt = ""
				for notice in fmovies.DEV_NOTICE:
					notice_txt += notice
				if notice_txt != "":
					notices_all.append(notice_txt.strip())
			except:
				pass
			
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
			try:
				notices_m = page_data.xpath(".//*[@id='body-wrapper']/div/div[@class='alert alert-default notice']/p[1]/text()[1]")
				notice_txt = ""
				for notice in notices_m:
					notice_txt += notice
				if notice_txt != "":
					notices_all.append(notice_txt.strip())
			except:
				pass
				
			# Listing page
			try:
				page_data_listing, error = common.GetPageElements(url=fmovies.BASE_URL + '/movies')
				if error != '':
					notices_all.append("%s for %s" % (error.strip(), fmovies.BASE_URL + '/movies'))
				error = page_data_listing.xpath(".//*[@id='body-wrapper']//div[@class='alert alert-danger']//p[1]//text()")[0]
				error_msg = page_data_listing.xpath(".//*[@id='body-wrapper']//div[@class='alert alert-danger']//p[3]//text()")[0]
				error = "Site Error: %s %s" % (error, error_msg)
				notices_all.append(error.strip())
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
				try:
					LOC = random.choice(SITE_NEWS_LOCS)
					page_data, error = common.GetPageElements(url=LOC)
					SITE_NEWS_LOCS.remove(LOC)
					
					try:
						error = page_data.xpath(".//*[@id='body-wrapper']//div[@class='alert alert-danger']//p[1]//text()")[0]
						error_msg = page_data.xpath(".//*[@id='body-wrapper']//div[@class='alert alert-danger']//p[3]//text()")[0]
						error = "Site Error: %s %s" % (error, error_msg)
						notices_all.append(error.strip())
					except:
						pass
					
					notices = page_data.xpath(".//*[@id='movie']//div[@class='alert alert-warning']//b//text()")
					if notices[0] == '':
						notices = ['No other site news Available.']
				except:
					notices = ['No other site news Available.']
			else:
				notices = ['Could not connect to site.']
		except:
			notices = ['Could not connect to site.']
			
		for notice in notices:
			notices_all.append(notice)
			
		for notice in notices_all:
			notice = unicode(notice)
			oc.add(DirectoryObject(
				title = notice,
				key = Callback(MC.message_container, header='Site News', message=notice),
				summary = notice,
				thumb = R(ICON_INFO)
				)
			)
	else:
		for title in elems:
			if title == CAT_FILTERS[3]:
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title, session=session),
					title = title
					)
				)
			else:
				oc.add(DirectoryObject(
					key = Callback(SortMenu, title = title, session=session),
					title = title
					)
				)
			
	if common.UsingOption(key=common.DEVICE_OPTIONS[0], session=session):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search, session = session), thumb = R(ICON_SEARCH), title='Search', summary='Search', prompt='Search for...'))
	return oc

######################################################################################
@route(PREFIX + "/sortMenu")
def SortMenu(title, session=None, **kwargs):

	oc = ObjectContainer(title2 = title, no_cache=common.isForceNoCache())
	is9anime = 'False'
	
	# Test for the site url initially to report a logical error
	if title in CAT_WHATS_HOT_REGULAR:
		url = fmovies.BASE_URL + '/home'
	elif title in CAT_WHATS_HOT_ANIME:
		url = common.ANIME_URL
		is9anime = 'True'
	else:
		url = fmovies.BASE_URL + '/home'
	
	page_data, error = common.GetPageElements(url = url)
	
	if page_data == None:
		bool, noc, page_data = testSite(url=url)
		if bool == False:
			return noc
			
	try:
		error = page_data.xpath(".//*[@id='body-wrapper']//div[@class='alert alert-danger']//p[1]//text()")[0]
		error_msg = page_data.xpath(".//*[@id='body-wrapper']//div[@class='alert alert-danger']//p[3]//text()")[0]
		error = "Site Error: %s %s" % (error, error_msg)
	except:
		pass
		
	if error != '':
		return MC.message_container(title, error)
	
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
				key = Callback(ShowCategory, title = title, urlpath = urlpath, key = key, session = session),
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
					key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb, session = session),
					title = name + " (" + quality + ")",
					summary = GetMovieInfo(summary=summary, urlPath=more_info_link, referer=url, session=session),
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
			elif title == CAT_WHATS_HOT[8]: # Anime section starts here
				elems = page_data.xpath(".//div[@data-name='updated']//*//div[@class='item']")
			elif title == CAT_WHATS_HOT[9]:
				elems = page_data.xpath(".//div[@data-name='updated-sub']//*//div[@class='item']")
			elif title == CAT_WHATS_HOT[10]:
				elems = page_data.xpath(".//div[@data-name='updated-dub']//*//div[@class='item']")
			elif title == CAT_WHATS_HOT[11]:
				elems = page_data.xpath(".//div[@data-name='top-week']//*//div[@class='item']")
			elif title == CAT_WHATS_HOT[12]:
				elems = page_data.xpath(".//div[@class='widget']//div[@class='list-film']//*//div[@class='item']")
			elif title == CAT_WHATS_HOT[13]:
				elems = page_data.xpath(".//div[@class='widget list-link']//div[@data-name='ongoing']//div[@class='item']")
			elif title == CAT_WHATS_HOT[14]:
				elems = page_data.xpath(".//div[@class='widget list-link']//div[@data-name='requested']//div[@class='item']")
			
			for elem in elems:
				eps_nos = ''
				title_eps_no = ''
				
				if is9anime == 'False':
					name = elem.xpath(".//a[@class='name']//text()")[0]
					loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
					thumb_t = elem.xpath(".//a[@class='poster']//@src")[0]
					thumb = thumb_t if 'url' not in thumb_t else thumb_t.split('url=')[1]
					summary = 'Plot Summary on Item Page.'
					
					try:
						eps_nos = elem.xpath(".//div[@class='status']//span//text()")[0]
						eps_no_i = str(int(eps_nos.strip()))
						title_eps_no = ' (Eps:'+eps_no_i+')'
						eps_nos = ' Episodes: ' + eps_no_i
					except:
						pass
				else:
					if title in [CAT_WHATS_HOT[13],CAT_WHATS_HOT[14]]:
						name = elem.xpath(".//a//text()")[0]
						loc = elem.xpath(".//a//@href")[0]
						thumb_t = elem.xpath(".//img//@src")[0]
						thumb = thumb_t if 'url' not in thumb_t else thumb_t.split('url=')[1]
						summary = 'Plot Summary on Item Page.'
					else:
						name = elem.xpath(".//a[@class='name']//text()")[0]
						loc = elem.xpath(".//a[@class='name']//@href")[0]
						thumb_t = elem.xpath(".//a[@class='poster']//@src")[0]
						thumb = thumb_t if 'url' not in thumb_t else thumb_t.split('url=')[1]
						summary = 'Plot Summary on Item Page.'
				
					try:
						eps_nosx = elem.xpath(".//div[@class='status']//text()")[0].strip()
						title_eps_no = ' (Eps:'+eps_nosx+')'
						eps_nos = ' Episodes: ' + eps_nosx
					except:
						pass
				
				try:
					more_info_link = elem.xpath(".//@data-tip")[0]
				except:
					more_info_link = None

				oc.add(DirectoryObject(
					key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb, session = session, is9anime=is9anime),
					title = name + title_eps_no,
					summary = GetMovieInfo(summary=summary, urlPath=more_info_link, referer=url, session=session, is9anime=is9anime) + eps_nos,
					thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
					)
				)
	
	if common.UsingOption(key=common.DEVICE_OPTIONS[0], session=session):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search, session = session), thumb = R(ICON_SEARCH), title='Search', summary='Search', prompt='Search for...'))
	if len(oc) == 1:
		return MC.message_container(title, 'No Videos Available')
	return oc
	
######################################################################################
@route(PREFIX + "/showcategory")
def ShowCategory(title, key=' ', urlpath=None, page_count='1', session=None, **kwargs):
	
	is9anime = 'False'
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
			newurl = (common.ANIME_URL + '/newest' + '?page=%s' % page_count)
			is9anime = 'True'
		elif title == CAT_REGULAR[1]:
			newurl = (fmovies.BASE_URL + '/movies' + '?page=%s' % page_count)
		elif title == CAT_REGULAR[2]:
			newurl = (fmovies.BASE_URL + '/tv-series' + '?page=%s' % page_count)
		elif title == CAT_REGULAR[3]:
			newurl = (fmovies.BASE_URL + '/top-imdb' + '?page=%s' % page_count)
		elif title == CAT_REGULAR[4]:
			newurl = (fmovies.BASE_URL + '/most-watched' + '?page=%s' % page_count)
		elif title == CAT_REGULAR[5]:
			newurl = (fmovies.BASE_URL + fmovies.SITE_MAP)
		
	page_data, error = common.GetPageElements(url=newurl)
	
	try:
		error = page_data.xpath(".//*[@id='body-wrapper']//div[@class='alert alert-danger']//p[1]//text()")[0]
		error_msg = page_data.xpath(".//*[@id='body-wrapper']//div[@class='alert alert-danger']//p[3]//text()")[0]
		error = "Site Error: %s %s" % (error, error_msg)
	except:
		pass
		
	if error != '':
		return MC.message_container(title, error)
	
	elems = []
	if title == CAT_REGULAR[5]: # Site-Map
		if len(fmovies.SITE_MAP_HTML_ELEMS) == 0:
			elems_all = page_data.xpath(".//*[@id='body-wrapper']/div/div/div[2]/ul/li[9]/ul/li")
			fmovies.SITE_MAP_HTML_ELEMS = elems_all
		else:
			elems_all = fmovies.SITE_MAP_HTML_ELEMS
		last_page_no = int(len(elems_all)/50)
		limit_x = (int(page_count)-1) * 50
		limit_y = int(page_count) * 50
		for i in range(limit_x, limit_y):
			elems.append(elems_all[i])
	elif title == CAT_REGULAR[0]: # Anime
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row']//div[@class='item']")
		last_page_no = int(page_count)
		try:
			last_page_no = int(page_data.xpath(".//*[@id='body-wrapper']//span[@class='total']//text()")[0])
		except:
			pass
	else:
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row movie-list']//div[@class='item']")
		last_page_no = int(page_count)
		try:
			last_page_no = int(page_data.xpath(".//*[@id='body-wrapper']//ul[@class='pagination'][1]//li[last()-1]//text()")[0])
		except:
			pass
		
	if key != ' ':
		oc = ObjectContainer(title2 = title + '|' + key.title() + '|Page ' + str(page_count) + ' of ' + str(last_page_no), no_cache=common.isForceNoCache())
	else:
		oc = ObjectContainer(title2 = title + '|Page ' + str(page_count) + ' of ' + str(last_page_no), no_cache=common.isForceNoCache())
		
	for elem in elems:
		if title == CAT_REGULAR[4] and False:
			name = elem.xpath(".//a//text()")[0]
			if '...' in name:
				name = elem.xpath(".//a//@title")[0]
			loc = fmovies.BASE_URL + elem.xpath(".//a//@href")[0]
			thumb = None
			summary = ''
			eps_nos = ''
			title_eps_no = ''
			more_info_link = None
		else:
			name = elem.xpath(".//a[@class='name']//text()")[0]
			if title == CAT_REGULAR[0]:
				loc = elem.xpath(".//a[@class='name']//@href")[0]
			else:
				loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
			thumb_t = elem.xpath(".//a[@class='poster']//@src")[0]
			thumb = thumb_t if 'url' not in thumb_t else thumb_t.split('url=')[1]
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
			key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb, session = session),
			title = name + title_eps_no,
			summary = GetMovieInfo(summary=summary, urlPath=more_info_link, referer=newurl, session=session, is9anime=is9anime) + eps_nos,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
			)
		)
		
	if int(page_count) < last_page_no:
		oc.add(NextPageObject(
			key = Callback(ShowCategory, title=title, key=key, urlpath=urlpath, page_count=str(int(page_count) + 1), session=session),
			title = "Next Page (" + str(int(page_count) + 1) +'/'+ str(last_page_no) + ") >>",
			thumb = R(ICON_NEXT)
			)
		)
		
	if common.UsingOption(key=common.DEVICE_OPTIONS[0], session=session):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search, session = session), thumb = R(ICON_SEARCH), title='Search', summary='Search', prompt='Search for...'))

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
def EpisodeDetail(title, url, thumb, session, dataEXS=None, dataEXSAnim=None, **kwargs):

	page_data, error = common.GetPageElements(url=url)
	if error != '':
		return MC.message_container("Error", "Error: %s." % error)
	if page_data == None:
		return MC.message_container("Unknown Error", "Error: The page was not received. Please try again.")
		
	is9anime = 'True' if common.ANIME_KEY in url.lower() else 'False'
	servers_list_new = []
		
	client_id = '%s-%s' % (Client.Product, session)
	if client_id not in CUSTOM_TIMEOUT_DICT.keys():
		CUSTOM_TIMEOUT_DICT[client_id] = {}
		
	servers_list = {}
	episodes_list = []
	server_lab = []
	episodes = []
	episodes_XS = []
	imdb_id = None
	isTvSeries = False
	isMovieWithMultiPart = False
	directors = 'Not Available'
	roles = 'Not Available'
	serverts = 0
	similar_reccos = []
	tags = 'Not Available'
	
	oc = ObjectContainer(title2 = title, no_cache=common.isForceNoCache())
		
	if dataEXS==None and dataEXSAnim==None and is9anime == 'False':
		if Prefs["use_debug"]:
			Log("============================= Processing bmovies ===============================")
		
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
				thumb_t = page_data.xpath(".//*[@id='info']//div//img")[0]
				thumb = thumb_t if 'url' not in thumb_t else thumb_t.split('url=')[1]
		except:
			try:
				if thumb == None:
					thumb_t = page_data.xpath(".//*[@id='info']//div//img//@src")[0]
					thumb = thumb_t if 'url' not in thumb_t else thumb_t.split('url=')[1]
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
		oc = ObjectContainer(title2 = title + item_unav, art = art, no_cache=common.isForceNoCache())
		
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
			directors = (','.join(common.removeAccents(x) for x in directors0))
			if directors.strip() == '...':
				directors = 'Not Available'
		except:
			directors = 'Not Available'
		
		try:
			roles0 = page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][1]//dd[2]//a//text()")
			roles = (','.join(common.removeAccents(x) for x in roles0))
			if roles == '':
				roles = 'Not Available'
		except:
			roles = 'Not Available'
		
		try:
			servers = page_data.xpath(".//*[@id='servers']//div[@class='server row']")
		except:
			servers = []
		
		summary += '\n '
		summary += 'Actors: ' + (roles) + '\n '
		summary += 'Directors: ' + (directors) + '\n '
		
		if str(duration) == 'Not Available':
			summary += 'Runtime: ' + (str(duration)) + '\n '
			duration = 0
		else:
			summary += 'Runtime: ' + (str(duration)) + ' min.' + '\n '
		
		summary += 'Year: ' + (year) + '\n '
		summary += 'Genre: ' + (genre) + '\n '
		summary += 'IMDB rating: ' + (rating) + '\n '

		try:
			summary = unicode(common.ascii_only(summary))
			#summary = unicode(str(summary).replace('"','').replace('\u00',''))
		except:
			summary = 'Not Available'
			
		try:
			similar_reccos = []
			similar_reccos_elems = page_data.xpath(".//*[@id='movie']//div[@class='row movie-list']//div[@class='item']")

			for elem in similar_reccos_elems:
				similar_reccos_name = elem.xpath(".//a[@class='name']//text()")[0]
				similar_reccos_loc = elem.xpath(".//a[@class='name']//@href")[0]
				thumb_t = elem.xpath(".//a[@class='poster']//@src")[0]
				similar_reccos_thumb = thumb_t if 'url' not in thumb_t else thumb_t.split('url=')[1]
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
			
			if label.lower() != 'mycloud' or (label.lower() == 'mycloud' and common.MY_CLOUD_DISABLED == False):
				if label in common.host_gvideo.FMOVIES_SERVER_MAP:
					label = common.host_gvideo.FMOVIES_SERVER_MAP[label]
				if 'Server F' in label:
					label = label.replace('Server F','Google-F')
				if 'Server G' in label:
					label = label.replace('Server G','Google-G')
				
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
			
	############################# Data ############################
	
	if dataEXSAnim != None or is9anime == 'True':
		if Prefs["use_debug"]:
			Log("============================= Processsing 9anime ===============================")
		try:
			title = page_data.xpath("//*[@id='movie']//h1[@class='title']//text()")[0]
		except:
			pass
			
		title = unicode(common.ascii_only(title))
			
		try:
			item_unav = ''
			errs = page_data.xpath(".//*[@id='movie']//div[@class='alert alert-primary notice'][2]//text()")
			for err in errs:
				if 'There is no server for this movie right now, please try again later.' in err:
					item_unav = ' ' + common.GetEmoji(type='neg', session=session)
					break
		except:
			pass
			
		isTvSeries = False
		try:
			item_type = page_data.xpath(".//div[@id='movie']/@data-type")[0]
			if item_type == 'series' or item_type == 'ova':
				isTvSeries = True
		except:
			pass
			
			
		try:
			if thumb == None:
				thumb_t = page_data.xpath(".//*[@id='info']//div//img")[0]
				thumb = thumb_t if 'url' not in thumb_t else thumb_t.split('url=')[1]
		except:
			try:
				if thumb == None:
					thumb_t = page_data.xpath(".//*[@id='info']//div//img//@src")[0]
					thumb = thumb_t if 'url' not in thumb_t else thumb_t.split('url=')[1]
			except:
				thumb = R(ICON_UNAV)
			
		try:
			serverts = page_data.xpath(".//body//@data-ts")[0]
		except:
			serverts = 0
		
		try:
			art = page_data.xpath(".//meta[@property='og:image'][1]//@content")[0]
		except:
			art = 'https://cdn.rawgit.com/coder-alpha/FMoviesPlus.bundle/master/Contents/Resources/art-default.jpg'
		oc = ObjectContainer(title2 = title + item_unav, art = art, no_cache=common.isForceNoCache())
		
		try:
			summary = page_data.xpath(".//*[@id='info']//div[@class='desc']//text()")
			summary = summary[0]
		except:
			try:
				summary = page_data.xpath(".//div[@class='shortcontent']/text()")
				summary = summary[0]
			except:
				summary = 'Summary Not Available.'
		
		try:
			trailer = page_data.xpath(".//*[@id='control']//div['item mbtb watch-trailer hidden-xs']//@data-url")[0]
		except:
			trailer = None
		
		try:
			try:
				year = str(page_data.xpath(".//dt[contains(text(),'Date')]//following-sibling::dd[1]//text()")[0].strip()[-4:])
				year = str(int(year))
			except:
				year = str(page_data.xpath(".//dt[contains(text(),'Premiered')]//following-sibling::dd[1]//text()")[0].strip()[-4:])
				year = str(int(year))
		except:
			year = 'Not Available'
			
		try:
			rating = str(page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][2]//dd[1]//text()")[0].split('/')[0])
		except:
			rating = 'Not Available'
			
		try:
			if isTvSeries == True:
				duration = int(page_data.xpath(".//dd[contains(text(),'min')]//text()")[0].strip('/episode').strip(' min'))
			else:
				duration = int(eval(page_data.xpath(".//dd[contains(text(),'min') or contains(text(),'hr')]/text()")[0].replace('hr.','*60+').strip(' min')))
		except:
			duration = 'Not Available'

		try:
			genre0 = page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][1]//dd[3]//a//text()")
			genre = (','.join(str(x) for x in genre0))
			if genre == '':
				genre = 'Not Available'
		except:
			genre = 'Not Available'
		
		directors = 'Not Available'
		roles = 'Not Available'
		
		try:
			servers = page_data.xpath(".//*[@id='servers']//div[@class='server row']")
		except:
			servers = []
		
		summary += '\n '
		summary += 'Actors: ' + (roles) + '\n '
		summary += 'Directors: ' + (directors) + '\n '
		
		if str(duration) == 'Not Available':
			summary += 'Runtime: ' + (str(duration)) + '\n '
			duration = 0
		else:
			summary += 'Runtime: ' + (str(duration)) + ' min.' + '\n '
		
		summary += 'Year: ' + (year) + '\n '
		summary += 'Genre: ' + (genre) + '\n '
		summary += 'Rating: ' + (rating) + '\n '

		try:
			summary = unicode(common.ascii_only(summary))
			#summary = unicode(str(summary).replace('"','').replace('\u00',''))
		except:
			summary = 'Not Available'
			
		try:
			similar_reccos = []
			similar_reccos_elems = page_data.xpath(".//*[@id='movie']//div[@class='row']//div[@class='item']")

			for elem in similar_reccos_elems:
				similar_reccos_name = elem.xpath(".//a[@class='name']//text()")[0]
				similar_reccos_loc = elem.xpath(".//a[@class='name']//@href")[0]
				thumb_t = elem.xpath(".//a[@class='poster']//@src")[0]
				similar_reccos_thumb = thumb_t if 'url' not in thumb_t else thumb_t.split('url=')[1]
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
		isMovieWithMultiPart = False
		
		for server in servers:
			label = server.xpath(".//label[@class='name col-md-3 col-sm-4']//text()[2]")[0].strip()
			
			if label.lower() != 'mycloud' or (label.lower() == 'mycloud' and common.MY_CLOUD_DISABLED == False):
				if label in common.host_gvideo.FMOVIES_SERVER_MAP:
					label = common.host_gvideo.FMOVIES_SERVER_MAP[label]
				if 'Server F' in label:
					label = label.replace('Server F','Google-F')
				if 'Server G' in label:
					label = label.replace('Server G','Google-G')
				
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
				
	##### Fix numbering #####
	seq = range(1, len(servers_list_new))
	if len(servers_list_new) > 0:
		#Log(server_lab)
		#Log(servers_list_new)
		
		new_map = []

		for eps in servers_list_new:
			eps_items = {}
			for label in server_lab:
				eps_item = {}
				info = eps[label]
				ep_c = info['quality'].strip()
				eps_item[label] = info
				try:
					if int(ep_c) != seq[0]:
						eps_item[label]['quality'] = str(seq[0])
						eps_item[label]['loc'] = None
					if int(ep_c) > seq[0] and label == server_lab[len(server_lab)-1]:
						seq.remove(seq[0])
					if int(ep_c) in seq and label == server_lab[len(server_lab)-1]:
						seq.remove(int(ep_c))
				except:
					pass
				eps_items[label] = eps_item[label]
			new_map.append(eps_items)
		#Log(new_map)
		servers_list_new = new_map
	############################
	
	if dataEXS != None or common.ES_API_URL.lower() in url:
		if Prefs["use_debug"]:
			Log("============================= Processsing API-Fetch ===============================")
	
		json_data = None
		if dataEXS == None:
			json_data, error = common.GetPageAsString(url=url)
			if error != '':
				return MC.message_container(title, error)
			json_data = json.loads(json_data)
			
			dataEXS_d = {}
			name = json_data['title']
			try:
				thumb = json_data['images']['poster']
			except:
				thumb = ICON_UNAV
			try:
				art = json_data['images']['fanart']
			except:
				art = ART
			try:
				banner = json_data['images']['banner']
			except:
				banner = None
			rating = json_data['rating']['percentage']
			year = json_data['year']
			genres = []
			summary = 'Plot Summary on Item Page'
			trailer = None
			runtime = None
			num_seasons = None
			cert = None
			
			if '/anime/' in url:
				type = json_data['type']
				type = 'anime'
				subtype = json_data['type']
				num_seasons = json_data['num_seasons']
				id = json_data['_id']
				genres = json_data['genres']
			elif '/show/' in url:
				type = 'show'
				subtype = 'show'
				num_seasons = json_data['num_seasons']
				id = json_data['imdb_id']
				summary = json_data['synopsis']
			elif '/movie/' in url:
				summary = json_data['synopsis']
				genres = json_data['genres']
				id = json_data['imdb_id']
				runtime = json_data['runtime']
				trailer = json_data['trailer']
				cert = json_data['certification']
				type = 'movie'
				subtype = 'movie'
				
			loc = common.ES_API_URL + '/%s/%s' % (type,id)
			
			dataEXS_d = {}
			dataEXS_d['title'] = name
			dataEXS_d['id'] = id
			dataEXS_d['thumb'] = thumb
			dataEXS_d['art'] = art
			dataEXS_d['banner'] = banner
			dataEXS_d['rating'] = float(rating)/10.0
			dataEXS_d['year'] = year
			dataEXS_d['summary'] = summary
			dataEXS_d['genres'] = genres
			dataEXS_d['type'] = type
			dataEXS_d['subtype'] = subtype
			dataEXS_d['trailer'] = trailer
			dataEXS_d['runtime'] = runtime
			dataEXS_d['num_seasons'] = num_seasons
			dataEXS_d['certification'] = cert
			dataEXS_d['itemurl'] = loc
			
		else:
			dataEXS_d = JSON.ObjectFromString(D(dataEXS))
		
		title = dataEXS_d['title']
		imdb_id = dataEXS_d['id']
		thumb = dataEXS_d['thumb']
		art = dataEXS_d['art']
		banner = dataEXS_d['banner']
		rating = dataEXS_d['rating']
		year = dataEXS_d['year']
		summary = dataEXS_d['summary']
		genre0 = dataEXS_d['genres']
		type = dataEXS_d['type']
		subtype = dataEXS_d['subtype']
		trailer = dataEXS_d['trailer']
		duration = dataEXS_d['runtime']
		num_seasons = dataEXS_d['num_seasons']
		cert = dataEXS_d['certification']
		
		if type == 'show' or (type == 'anime' and subtype == 'show'):
			isTvSeries = True
			if json_data == None:
				json_data, error = common.GetPageAsString(url=dataEXS_d['itemurl'])
				if error != '':
					return MC.message_container(title, error)
				json_data = json.loads(json_data)
			summary = json_data['synopsis']
			duration = json_data['runtime']
			genres0 = json_data['genres']
			episodes_XS = json_data['episodes']
			rating = float(json_data['rating']['percentage'])/10.0

		try:
			genre = (','.join(str(x.title()) for x in genre0))
			if genre == '':
				genre = 'Not Available'
		except:
			genre = 'Not Available'
			
	try:
		summary = unicode(common.ascii_only(summary))
		#summary = unicode(str(summary).replace('"','').replace('\u00',''))
	except:
		summary = 'Not Available'

	# trailer
	try:
		if trailer != None:
			url_serv = URLService.ServiceIdentifierForURL(trailer)
			if url_serv!= None:
				oc.add(VideoClipObject(
					url = trailer,
					title = 'Trailer',
					thumb = GetThumb(thumb, session=session),
					art = art,
					summary = summary)
				)
	except:
		pass
		
	if isTvSeries and len(episodes_XS) > 0:
		# case for presenting tv-series with synopsis via external listing
		if Prefs["use_debug"]:
			Log("case for presenting tv-series with synopsis via external listing")
		
		seasons = []
		
		for json_item in episodes_XS:
			if int(json_item['season']) not in seasons:
				seasons.append(int(json_item['season']))
				season_object            = SeasonObject()
				season_object.title      = 'Season {0}'.format(json_item['season'])
				season_object.index      = int(json_item['season'])
				season_object.show       = title
				season_object.thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback = ICON_UNAV)
				season_object.art = Resource.ContentsOfURLWithFallback(url = art, fallback = ART)
				season_object.rating_key = '%s-%s' % (imdb_id, season_object.index)
				season_object.key        = Callback(season_menuES, title=season_object.title, show_title=season_object.show, season_index=season_object.index, dataEXSJsonUrl=url, session=session)
				oc.add(season_object)
				
		if len(seasons)-1 != max(seasons):
			for i in range(1,max(seasons)):
				if i not in seasons:
					seasons.append(i)
					season_object            = SeasonObject()
					season_object.title      = 'Season {0}'.format(i)
					season_object.index      = i
					season_object.show       = title
					season_object.thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback = ICON_UNAV)
					season_object.art = Resource.ContentsOfURLWithFallback(url = art, fallback = ART)
					season_object.rating_key = '%s-%s' % (imdb_id, season_object.index)
					season_object.key        = Callback(season_menuES, title=season_object.title, show_title=season_object.show, season_index=season_object.index, dataEXSJsonUrl=url, session=session)
					oc.add(season_object)

		oc.objects.sort(key=lambda season_object: season_object.index)
		
	elif len(episodes) > 0 and isTvSeries:
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
			c_not_missing += 1
		
		
		######################################################################################
		##### Fix air date sequence #####
		
		episodes_list_new = []
		ord_date_bk = 0
		for item in episodes_list:
			ord_date = item['air_date']
			if ord_date != '':
				ord_date = common.stripDay(ord_date)
				ord_date = common.convertMonthToInt(ord_date)
			try:
				ord_date_s = ord_date.replace(' ','').strip().split(',')
				ord_date = '%04d%02d%02d' % (int(ord_date_s[2]), int(ord_date_s[0]), int(ord_date_s[1]))
				ord_date = str(ord_date)
				ord_date_bk = int(ord_date)
			except:
				counter_str = '%08d' % (ord_date_bk + 1)
				ord_date = str(counter_str)
				ord_date_bk += 1
				
			item['ord_date'] = ord_date
			episodes_list_new.append(item)
			
		episodes_list_new = sorted(episodes_list_new, key=lambda k: k['ord_date'], reverse=False)
		#Log(episodes_list_new)
		episodes_list = episodes_list_new

		######################################################################################
		
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
				desc = unicode('%s : %s' % (episodes_list[qual_i]['air_date'] , episodes_list[qual_i]['desc']))
			except:
				desc = 'Episode Summary Not Available.'
				
			desc = common.ascii_only(desc)
			
			try:
				oc.add(DirectoryObject(
					key = Callback(TvShowDetail, tvshow=title, title=title_s, url=url, servers_list_new=E(JSON.StringFromObject(servers_list_new[c])), server_lab=E(JSON.StringFromObject(server_lab)), summary=desc+'\n '+summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, serverts=serverts, session=session, season=SeasonN, episode=episode, imdb_id=imdb_id),
					title = title_s,
					summary = desc+ '\n ' +summary,
					art = art,
					thumb = Resource.ContentsOfURLWithFallback(url = GetThumb(thumb, session=session), fallback = GetThumb(ICON_UNAV, session=session))
					)
				)
				c_not_missing = qual_i
				c += 1
			except Exception as e:
				Log('ERROR init.py>EpisodeDetail>Tv1 %s, %s' % (e.args, title_s))
				pass
			
		if SeasonN > 0 or True: # enable for all - even if this might be a single season
			oc.add(DirectoryObject(
			key = Callback(Search, query = common.cleantitle.removeParanthesisAndSeason(title, SeasonN), session = session, mode='other seasons', thumb=thumb, summary=summary, is9anime=is9anime),
			title = "Other Seasons",
			summary = 'Other Seasons of ' + common.cleantitle.removeParanthesis(title),
			art = art,
			thumb = R(ICON_OTHERSEASONS)
			))

	elif isTvSeries and len(episodes_XS)==0:
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
					key = Callback(TvShowDetail, tvshow=title, title=title_s, url=url, servers_list_new=E(JSON.StringFromObject(servers_list_new[c])), server_lab=E(JSON.StringFromObject(server_lab)), summary='Episode Summary Not Available.\n ' + summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, serverts=serverts, session=session, season=SeasonN, episode=episode, imdb_id=imdb_id),
					title = title_s,
					summary = 'Episode Summary Not Available.\n ' + summary,
					art = art,
					thumb = Resource.ContentsOfURLWithFallback(url = GetThumb(thumb, session=session), fallback = GetThumb(ICON_UNAV, session=session))
					)
				)
				c += 1
			except Exception as e:
				Log('ERROR init.py>EpisodeDetail>Tv2 %s, %s' % (e.args, title_s))
				pass
		if SeasonN > 0 or True: # enable for all - even if this might be a single season
			oc.add(DirectoryObject(
			key = Callback(Search, query = common.cleantitle.removeParanthesisAndSeason(title, SeasonN), session = session, mode='other seasons', thumb=thumb, summary=summary, is9anime=is9anime),
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
			Thread.Create(common.interface.getExtSources, {}, movtitle=title, year=year, tvshowtitle=None, season=None, episode=None, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY, ver=common.VERSION, imdb_id=imdb_id, session=session)
		
		SeasonN = 0
		oc.title2 = title
			
		c=0
		for eps in servers_list_new:
			try:
				episode = eps[server_lab[0]]['quality']
				title_s = episode
				oc.add(DirectoryObject(
					key = Callback(TvShowDetail, tvshow=title, title=title_s, url=url, servers_list_new=E(JSON.StringFromObject(servers_list_new[c])), server_lab=E(JSON.StringFromObject(server_lab)), summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, serverts=serverts, session=session, season=SeasonN, episode=episode, treatasmovie=True, imdb_id=imdb_id),
					title = title_s,
					summary = summary,
					art = art,
					thumb = Resource.ContentsOfURLWithFallback(url = GetThumb(thumb, session=session), fallback = GetThumb(ICON_UNAV, session=session))
					)
				)
				c += 1
			except Exception as e:
				Log('ERROR init.py>EpisodeDetail>Movie1 %s, %s' % (e.args, title_s))
				pass
				
		if Prefs['disable_extsources'] == False and common.interface.isInitialized():
			oc.add(DirectoryObject(
				key = Callback(ExtSources, movtitle=title, year=year, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, session=session), 
				title = 'External Sources',
				summary = 'List sources of this movie by External Providers.',
				art = art,
				thumb = R(ICON_OTHERSOURCES)
				)
			)
		if Prefs['disable_downloader'] == False and AuthTools.CheckAdmin() == True:
			oc.add(DirectoryObject(
				key = Callback(ExtSourcesDownload, movtitle=title, year=year, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, mode=common.DOWNLOAD_MODE[0], session=session), 
				title = 'Download Sources',
				summary = 'List sources of this movie by External Providers.',
				art = art,
				thumb = R(ICON_OTHERSOURCESDOWNLOAD)
				)
			)
		elif Prefs['disable_downloader'] == False:
			oc.add(DirectoryObject(
				key = Callback(ExtSourcesDownload, movtitle=title, year=year, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, mode=common.DOWNLOAD_MODE[1], session=session), 
				title = 'Request Download',
				summary = 'List sources of this movie by External Providers.',
				art = art,
				thumb = R(ICON_REQUESTS)
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
				Thread.Create(common.interface.getExtSources, {}, movtitle=title, year=year, tvshowtitle=None, season=None, episode=None, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY, ver=common.VERSION, imdb_id=imdb_id, session=session)
		
		# create timeout thread
		if common.USE_CUSTOM_TIMEOUT == True:
			Thread.Create(ThreadTimeoutTimer, {}, Client.Product, E(url), client_id)
		
		watch_title = title
	
		pair_required = False
		for label in server_lab:
			for label_i in servers_list[label]:
				url_s = label_i['loc']
				if common.UsingOption(common.DEVICE_OPTIONS[5], session=session):
					try:
						title_s = ''
						if Prefs["use_debug"]:
							Log("%s - %s" % (url, url_s))
						server_info, isTargetPlay, error, host, sub_url = fmovies.GetApiUrl(url=url, key=url_s, serverts=serverts)
						server_info_t = server_info
						captcha = None
						dlt = None
						if server_info != None:
							qual = common.getHighestQualityLabel(server_info, label_i['quality'])
							title_s = label + ' - ' + qual
						
							pair_required = False
							pair = ''
							status = ''
							isVideoOnline = 'unknown'
							if Prefs["use_linkchecker"]:
								data = server_info
								if isTargetPlay == True:
									pass
								else:
									data = E(JSON.StringFromObject({"server":server_info}))
								isVideoOnline = common.isItemVidAvailable(isTargetPlay=isTargetPlay, data=data, host=host)
								
							if isTargetPlay == True and 'openload' in host and (Prefs['use_openload_pairing'] or not common.is_uss_installed()):
								pair_required, u1 = common.host_openload.isPairingRequired(url=server_info, session=session)
								if pair_required == True:
									a1,a2,captcha,dlt,err = common.host_openload.link_from_api(server_info)
									if common.host_openload.isPairingDone() == False:
										pair = ' *Pairing required* '
									else:
										pair = ' *Paired* '
								else:
									server_info_t = u1
								if Prefs["use_debug"]:
									Log("%s --- %s : Pairing required: %s" % (server_info, pair, pair_required))
								
							if isVideoOnline != str(False):
								status = common.GetEmoji(type=isVideoOnline, session=session) + ' ' + pair
							else:
								status = common.GetEmoji(type=isVideoOnline, session=session)
							
							vco = None
							try:
								redirector_stat = ''
								redirector_enabled = 'false'
								if common.UsingOption(key=common.DEVICE_OPTIONS[2], session=session) and isTargetPlay == False:
									redirector_stat = ' (via Redirector)'
									redirector_enabled = 'true'
									
								if not Prefs['use_openload_pairing'] and 'openload' in host and common.is_uss_installed() and URLService.ServiceIdentifierForURL(server_info) != None:
									durl = server_info
								else:
									durl = "fmovies://" + E(JSON.StringFromObject({"url":url, "server":server_info_t, "title":title, "summary":summary, "thumb":thumb, "art":art, "year":year, "rating":rating, "duration":str(duration), "genre":genre, "roles":roles, "directors":directors, "roles":roles, "isTargetPlay":str(isTargetPlay), "useSSL":Prefs["use_https_alt"], "isVideoOnline":str(isVideoOnline), "useRedirector": redirector_enabled, 'urldata':'','quality':qual, 'pairrequired':pair_required, "host":host, "openloadApiKey":Prefs['control_openload_api_key', "force_transcode":common.UsingOption(key=common.DEVICE_OPTIONS[10], session=session)]}))
									
								vco = VideoClipObject(
									url = durl,
									title = status + title + ' - ' + title_s + redirector_stat,
									thumb = GetThumb(thumb, session=session),
									duration = int(duration) * 60 * 1000,
									year = int(year),
									art = art,
									summary = summary,
									key = AddRecentWatchList(title=title, url=url, summary=summary, thumb=thumb)
									)
								oc.add(vco)
							except Exception as e:
								Log('ERROR init.py>EpisodeDetail>Movie2a %s' % (e.args))
								Log("ERROR: %s with key:%s returned %s" % (url,url_s,server_info))
								Log('ERROR init.py>EpisodeDetail>Movie2a %s' % (title + ' - ' + title_s))
								
							if captcha != None and captcha != False:
								try:
									DumbKeyboard(PREFIX, oc, SolveCaptcha, dktitle = 'Solve Captcha: ' + title, dkHistory = False, dkthumb = captcha, dkart=captcha, url = server_info, dlt = dlt, vco=vco, title=title + ' - ' + title_s + redirector_stat)
									po = create_photo_object(url = captcha, title = 'View Captcha')
									oc.add(po)
								except Exception as e2:
									Log("ERROR: In Setting DumbKeyboard for Captcha %s" % e2)
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
					if common.UsingOption(common.DEVICE_OPTIONS[6], session=session):
						oc.add(MovieObject(
							key = Callback(VideoDetail, title=title, url=url, url_s=url_s, label=label, label_i_qual=label_i['quality'], serverts=serverts, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, libtype='movie', session=session, watch_title=watch_title),
							title = label,
							duration = int(duration) * 60 * 1000,
							year = int(year),
							rating_key = url+url_s,
							summary = summary,
							art = art,
							thumb = GetThumb(thumb, session=session)
							)
						)
					else:
						oc.add(DirectoryObject(
							key = Callback(VideoDetail, title=title, url=url, url_s=url_s, label=label, label_i_qual=label_i['quality'], serverts=serverts, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, libtype='movie', session=session, watch_title=watch_title),
							title = label,
							summary = summary,
							art = art,
							thumb = GetThumb(thumb, session=session)
							)
						)
				
			if common.USE_CUSTOM_TIMEOUT == True:
				if label != server_lab[len(server_lab)-1] and isTimeoutApproaching(clientProd = Client.Product, item = E(url), client_id=client_id, session=session):
					Log("isTimeoutApproaching action")
					break
					#return MC.message_container('Timeout', 'Timeout: Please try again !')

		if Prefs['disable_extsources'] == False and common.interface.isInitialized():
			oc.add(DirectoryObject(
				key = Callback(ExtSources, movtitle=title, year=year, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, session=session), 
				title = 'External Sources',
				summary = 'List sources of this movie by External Providers.',
				art = art,
				thumb = GetThumb(R(ICON_OTHERSOURCES), session=session)
				)
			)
		if Prefs['disable_downloader'] == False and AuthTools.CheckAdmin() == True:
			oc.add(DirectoryObject(
				key = Callback(ExtSourcesDownload, movtitle=title, year=year, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, mode=common.DOWNLOAD_MODE[0], session=session), 
				title = 'Download Sources',
				summary = 'List sources of this movie by External Providers.',
				art = art,
				thumb = GetThumb(R(ICON_OTHERSOURCESDOWNLOAD), session=session)
				)
			)
		elif Prefs['disable_downloader'] == False:
			oc.add(DirectoryObject(
				key = Callback(ExtSourcesDownload, movtitle=title, year=year, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, mode=common.DOWNLOAD_MODE[1], session=session), 
				title = 'Request Download',
				summary = 'List sources of this movie by External Providers.',
				art = art,
				thumb = GetThumb(R(ICON_REQUESTS), session=session)
				)
			)
						
	itemtype = ('show' if isTvSeries else 'movie')
						
	if len(similar_reccos) > 0:
		oc.add(DirectoryObject(
			key = Callback(SimilarRecommendations, title = title, similar_reccos = E(JSON.StringFromObject(similar_reccos)), referer=url, is9anime = is9anime),
			title = "Similar Recommendations",
			summary = 'Discover other %s similar to %s' % (itemtype, title),
			art = art,
			thumb = GetThumb(R(ICON_SIMILAR), session=session)
		)
	)
	
	if roles != 'Not Available':
		oc.add(DirectoryObject(
			key = Callback(MoviesWithPeople, stars = roles, session = session, is9anime = is9anime),
			title = "People Search",
			summary = 'Search for movies/shows based on a person from the current %s' % (itemtype),
			art = art,
			thumb = GetThumb(R(ICON_PEOPLE), session=session)
		)
	)
	
	if tags != 'Not Available':
		oc.add(DirectoryObject(
			key = Callback(MoviesWithTag, tags = tags, session = session, is9anime = is9anime),
			title = "Tag Search",
			summary = 'Search for movies/shows based on a Tag from the current %s' % (itemtype),
			art = art,
			thumb = GetThumb(R(ICON_TAG), session=session)
		)
	)
		
	if Check(title=title,url=url):
		oc.add(DirectoryObject(
			key = Callback(RemoveBookmark, title = title, url = url),
			title = "Remove Bookmark",
			summary = 'Removes the current %s from the Boomark que' % (itemtype),
			art = art,
			thumb = GetThumb(R(ICON_QUEUE), session=session)
		)
	)
	else:
		oc.add(DirectoryObject(
			key = Callback(AddBookmark, title = title, url = url, summary=summary, thumb=thumb),
			title = "Add Bookmark",
			summary = 'Adds the current %s to the Boomark que' % (itemtype),
			art = art,
			thumb = GetThumb(R(ICON_QUEUE), session=session)
		)
	)
	
	return oc
	
	
####################################################################################################
@route(PREFIX + "/TvShowDetail")
def TvShowDetail(tvshow, title, url, servers_list_new, server_lab, summary, thumb, art, year, rating, duration, genre, directors, roles, serverts, session, season=None, episode=None, treatasmovie=False, imdb_id=None, **kwargs):

	try:
		summary = unicode(common.ascii_only(summary))
	except:
		summary = 'Not Available'

	oc = ObjectContainer(title2 = title, art = art, no_cache=common.isForceNoCache())

	servers_list_new = JSON.ObjectFromString(D(servers_list_new))
	
	server_lab = JSON.ObjectFromString(D(server_lab))
	
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
			Thread.Create(common.interface.getExtSources, {}, movtitle=None, year=year, tvshowtitle=tvshowcleaned, season=season, episode=episode, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY, ver=common.VERSION, imdb_id=imdb_id, session=session)
	
	# create timeout thread
	if common.USE_CUSTOM_TIMEOUT == True:
		Thread.Create(ThreadTimeoutTimer, {}, Client.Product, E(url), client_id)
	
	pair_required = False
	for label in server_lab:
		url_s = servers_list_new[label]['loc']
		if url_s != None:
			if common.UsingOption(common.DEVICE_OPTIONS[5], session=session):	
				server_info,isTargetPlay, error, host, sub_url = fmovies.GetApiUrl(url=url, key=url_s, serverts=serverts)
				server_info_t = server_info
				captcha = None
				dlt = None
				if server_info != None:
					pair = ''
					pair_required = False
					status = ''
					isVideoOnline = 'unknown'
					if Prefs["use_linkchecker"]:
						data = server_info
						if isTargetPlay == True:
							pass
						else:
							data = E(JSON.StringFromObject({"server":server_info}))
						isVideoOnline = common.isItemVidAvailable(isTargetPlay=isTargetPlay, data=data, host=host)
						
					if isTargetPlay == True and 'openload' in host and (Prefs['use_openload_pairing'] or not common.is_uss_installed()):
						pair_required, u1 = common.host_openload.isPairingRequired(url=server_info, session=session)
						if pair_required == True:
							a1,a2,captcha,dlt,err = common.host_openload.link_from_api(server_info)
							if common.host_openload.isPairingDone() == False:
								pair = ' *Pairing required* '
							else:
								pair = ' *Paired* '
						else:
							server_info_t = u1
							
						if Prefs["use_debug"]:
							Log("%s --- %s : Pairing required: %s" % (server_info, pair, pair_required))
						
					if isVideoOnline != str(False):
						status = common.GetEmoji(type=isVideoOnline, session=session) + ' ' + pair
					else:
						status = common.GetEmoji(type=isVideoOnline, session=session)
						
					redirector_stat = ''
					redirector_enabled = 'false'
					if common.UsingOption(key=common.DEVICE_OPTIONS[2], session=session) and isTargetPlay == False:
						redirector_stat = ' (via Redirector)'
						redirector_enabled = 'true'
					
					if not Prefs['use_openload_pairing'] and 'openload' in host and common.is_uss_installed() and URLService.ServiceIdentifierForURL(server_info) != None:
						durl = server_info
					else:
						durl = "fmovies://" + E(JSON.StringFromObject({"url":url, "server":server_info_t, "title":title, "summary":summary, "thumb":thumb, "art":art, "year":year, "rating":rating, "duration":str(duration), "genre":genre, "directors":directors, "roles":roles, "isTargetPlay":str(isTargetPlay), "useSSL":Prefs["use_https_alt"], "isVideoOnline":str(isVideoOnline), "useRedirector": redirector_enabled, 'urldata':'', 'pairrequired':pair_required, "host":host, "openloadApiKey":Prefs['control_openload_api_key'], "force_transcode":common.UsingOption(key=common.DEVICE_OPTIONS[10], session=session)}))
					
					vco = None
					try:
						vco = VideoClipObject(
							url = durl,
							title = status + title + ' (' + label + ')' + redirector_stat,
							thumb = GetThumb(thumb, session=session),
							duration = int(duration) * 60 * 1000,
							year = int(year),
							art = art,
							summary = summary,
							key = AddRecentWatchList(title = watch_title, url=url, summary=summary, thumb=thumb)
							)
						oc.add(vco)
					except:
						Log('ERROR init.py>TvShowDetail %s, %s' % (e.args, (title + ' - ' + title_s)))
						Log("ERROR: %s with key:%s returned %s" % (url,url_s,server_info))
						
					if captcha != None and captcha != False:
						try:
							DumbKeyboard(PREFIX, oc, SolveCaptcha, dktitle = 'Solve Captcha: ' + title, dkHistory = False, dkthumb = captcha, dkart=captcha, url = server_info, dlt = dlt, vco=vco, title=title + ' (' + label + ')' + redirector_stat)
							po = create_photo_object(url = captcha, title = 'View Captcha')
							oc.add(po)
						except Exception as e2:
							Log("ERROR: In Setting DumbKeyboard for Captcha %s" % e2)
				else:
					pass
					if Prefs["use_debug"]:
						Log("Video will not be displayed as playback option !")
						Log("ERROR: %s" % error)
						Log("ERROR: %s with key:%s returned %s" % (url,url_s,server_info))
			else:
				if common.UsingOption(common.DEVICE_OPTIONS[6], session=session):
					oc.add(MovieObject(
						key = Callback(VideoDetail, title=title, url=url, url_s=url_s, label=label, label_i_qual=None, serverts=serverts, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, libtype='show', session=session, watch_title=watch_title),
						duration = int(duration) * 60 * 1000,
						year = int(year),
						title = label,
						rating_key = url+url_s,
						summary = summary,
						art = art,
						thumb = GetThumb(thumb, session=session)
						)
					)
				else:
					oc.add(DirectoryObject(
						key = Callback(VideoDetail, title=title, url=url, url_s=url_s, label=label, label_i_qual=None, serverts=serverts, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, libtype='show', session=session, watch_title=watch_title),
						title = label,
						summary = summary,
						art = art,
						thumb = GetThumb(thumb, session=session)
						)
					)
				
			if common.USE_CUSTOM_TIMEOUT == True:
				if label != server_lab[len(server_lab)-1] and isTimeoutApproaching(clientProd = Client.Product, item = E(url), client_id=client_id, session=session):
					Log("isTimeoutApproaching action")
					break
					#return MC.message_container('Timeout', 'Timeout: Please try again !')
		
	if treatasmovie==False and Prefs['disable_extsources'] == False and common.interface.isInitialized():
		oc.add(DirectoryObject(
			key = Callback(ExtSources, tvshowtitle=tvshow, season=season, episode=episode, session=session, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles),
			title = 'External Sources',
			summary = 'List sources of this episode by External Providers.',
			art = art,
			thumb = GetThumb(R(ICON_OTHERSOURCES), session=session)
			)
		)
	
	if treatasmovie==False and Prefs['disable_downloader'] == False and AuthTools.CheckAdmin() == True:
		oc.add(DirectoryObject(
			key = Callback(ExtSourcesDownload, tvshowtitle=tvshow, season=season, episode=episode, session=session, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, mode=common.DOWNLOAD_MODE[0]),
			title = 'Download Sources',
			summary = 'List sources of this episode by External Providers.',
			art = art,
			thumb = GetThumb(R(ICON_OTHERSOURCESDOWNLOAD), session=session)
			)
		)
	elif treatasmovie==False and Prefs['disable_downloader'] == False:
		oc.add(DirectoryObject(
			key = Callback(ExtSourcesDownload, tvshowtitle=tvshow, season=season, episode=episode, session=session, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, mode=common.DOWNLOAD_MODE[1]),
			title = 'Request Download',
			summary = 'List sources of this episode by External Providers.',
			art = art,
			thumb = GetThumb(R(ICON_REQUESTS), session=session)
			)
		)
	
	return oc
	
######################################################################################
@route(PREFIX + "/Videodetail")
def VideoDetail(title, url, url_s, label_i_qual, label, serverts, thumb, summary, art, year, rating, duration, genre, directors, roles, libtype, session=None, watch_title=None, **kwargs):
	
	try:
		summary = unicode(common.ascii_only(summary))
		#summary = unicode(str(summary).replace('"','').replace('\u00',''))
	except:
		summary = 'Not Available'
		
	oc = ObjectContainer(title2=title)
	try:
		# url_s = label_i['loc']
		# label_i_qual = label_i['quality']
		server_info = None
		title_s = ''
		if Prefs["use_debug"]:
			Log("%s - %s" % (url, url_s))
		server_info, isTargetPlay, error, host, sub_url = fmovies.GetApiUrl(url=url, key=url_s, serverts=serverts)
		server_info_t = server_info
		captcha = None
		dlt = None
		if server_info != None:
			if label_i_qual != None:
				qual = common.getHighestQualityLabel(server_info, label_i_qual)
				title_s = label + ' - ' + qual
			else:
				title_s = label
				qual = '480p'
			
			pair_required = False
			pair = ''
			status = ''
			isVideoOnline = 'unknown'
			if Prefs["use_linkchecker"]:
				data = server_info
				if isTargetPlay == True:
					pass
				else:
					data = E(JSON.StringFromObject({"server":server_info}))
				isVideoOnline = common.isItemVidAvailable(isTargetPlay=isTargetPlay, data=data, host=host)
				
			if isTargetPlay == True and 'openload' in host and (Prefs['use_openload_pairing'] or not common.is_uss_installed()):
			
				pair_required, u1 = common.host_openload.isPairingRequired(url=server_info, session=session)
				
				if pair_required == True:
					a1,a2,captcha,dlt,err = common.host_openload.link_from_api(server_info)
					if common.host_openload.isPairingDone() == False:
						pair = ' *Pairing required* '
					else:
						pair = ' *Paired* '
				else:
					server_info_t = u1
					
				if Prefs["use_debug"]:
					Log("%s --- %s : Pairing required: %s" % (server_info, pair, pair_required))
			elif isTargetPlay == True:
				if isVideoOnline != 'true':
					error = common.host_misc_resolvers.error(server_info, Prefs["use_https_alt"])
					if error != '':
						raise Exception(error)
				
			if isVideoOnline != str(False):
				status = common.GetEmoji(type=isVideoOnline, session=session) + ' ' + pair
			else:
				status = common.GetEmoji(type=isVideoOnline, session=session)
				
			try:
				redirector_stat = ''
				redirector_enabled = 'false'
				if common.UsingOption(key=common.DEVICE_OPTIONS[2], session=session) and isTargetPlay == False:
					redirector_stat = ' (via Redirector)'
					redirector_enabled = 'true'
					
				if not Prefs['use_openload_pairing'] and 'openload' in host and common.is_uss_installed() and URLService.ServiceIdentifierForURL(server_info) != None:
					durl = server_info
				else:
					durl = "fmovies://" + E(JSON.StringFromObject({"url":url, "server":server_info_t, "title":title, "summary":summary, "thumb":thumb, "art":art, "year":year, "rating":rating, "duration":str(duration), "genre":genre, "roles":roles, "directors":directors, "roles":roles, "isTargetPlay":str(isTargetPlay), "useSSL":Prefs["use_https_alt"], "isVideoOnline":str(isVideoOnline), "useRedirector": redirector_enabled, 'urldata':'','quality':qual, 'pairrequired':pair_required, "host":host, "openloadApiKey":Prefs['control_openload_api_key'], "force_transcode":common.UsingOption(key=common.DEVICE_OPTIONS[10], session=session)}))
					
				vco = None
				vco = VideoClipObject(
					url = durl,
					title = status + title + ' - ' + title_s + redirector_stat,
					thumb = GetThumb(thumb, session=session),
					duration = int(duration) * 60 * 1000,
					year = int(year),
					art = art,
					summary = summary,
					key = AddRecentWatchList(title=title, url=url, summary=summary, thumb=thumb)
					)
				oc.add(vco)
				
				if captcha != None and captcha != False:
					try:
						DumbKeyboard(PREFIX, oc, SolveCaptcha, dktitle = 'Solve Captcha: ' + title, dkHistory=False, dkthumb=captcha, dkart=captcha, url=server_info, dlt=dlt, vco=vco, title=title + ' - ' + title_s + redirector_stat)
						po = create_photo_object(url = captcha, title = 'View Captcha')
						oc.add(po)
					except Exception as e2:
						Log("ERROR: In Setting DumbKeyboard for Captcha %s" % e2)
				
				try:
					if Prefs['disable_downloader'] == False:
						if isTargetPlay == True:
							if 'rapidvideo' in host:
								vvurls = [{'url':server_info+'&q=720p', 'qual':'720p'},{'url':server_info+'&q=480p', 'qual':'480p'},{'url':server_info+'&q=360p', 'qual':'360p'}]
							elif 'openload' in host:
								vvurls = [{'url':server_info, 'qual':qual}]
							else:
								vvurls = [{'url':server_info, 'qual':qual}]
								
							for vvv in vvurls:
								vv = vvv['url']
								qualx = vvv['qual']
								if Prefs['disable_downloader'] == False and AuthTools.CheckAdmin() == True:
									oc.add(DirectoryObject(
										key = Callback(AddToDownloadsListPre, title=watch_title, purl=url, url=vv, durl=vv, summary=summary, thumb=thumb, year=year, quality=qualx, source=host, type=libtype, resumable=True, source_meta={}, file_meta={}, sub_url=sub_url, mode=common.DOWNLOAD_MODE[0], session=session, admin=True),
										title = '%s | Add to Download Queue' % qualx,
										summary = 'Adds the current video to Download List',
										art = art,
										thumb = GetThumb(R(ICON_OTHERSOURCESDOWNLOAD), session=session)
										)
									)
								elif Prefs['disable_downloader'] == False:
									oc.add(DirectoryObject(
										key = Callback(AddToDownloadsListPre, title=watch_title, purl=url, url=vv, durl=vv, summary=summary, thumb=thumb, year=year, quality=qualx, source=host, type=libtype, resumable=True, source_meta={}, file_meta={}, sub_url=sub_url, mode=common.DOWNLOAD_MODE[1], session=session, admin=False),
										title = '%s | Add to Request Queue' % qualx,
										summary = 'Adds the current video to Request List',
										art = art,
										thumb = GetThumb(R(ICON_REQUESTS), session=session)
										)
									)
						else:
							host_source = 'gvideo' 
							files = json.loads(server_info)
							sortable_list = []
							for file in files:
								furl = file['file']
								res = file['label'].replace('p','')
								if res != '1080':
									res = '0'+res
								ftype = file['type']
								sortable_list.append({'label': res, 'file':furl, 'type':ftype})
							newlist = sorted(sortable_list, key=lambda k: k['label'], reverse=True)
							for file in newlist:
								furl = file['file']
								res = str(int(file['label']))+'p'
								ftype = file['type']
								if Prefs['disable_downloader'] == False and AuthTools.CheckAdmin() == True:
									oc.add(DirectoryObject(
										key = Callback(AddToDownloadsListPre, title=watch_title, purl=url, url=furl, durl=furl, summary=summary, thumb=thumb, year=year, quality=res, source=host_source, type=libtype, resumable=True, source_meta={}, file_meta={}, sub_url=sub_url, mode=common.DOWNLOAD_MODE[0], session=session, admin=True),
										title = '%s | Add to Download Queue' % res,
										summary = 'Adds the current video to Download List',
										art = art,
										thumb = GetThumb(R(ICON_OTHERSOURCESDOWNLOAD), session=session)
										)
									)
								elif Prefs['disable_downloader'] == False:
									oc.add(DirectoryObject(
										key = Callback(AddToDownloadsListPre, title=watch_title, purl=url, url=furl, durl=furl, summary=summary, thumb=thumb, year=year, quality=res, source=host_source, type=libtype, resumable=True, source_meta={}, file_meta={}, sub_url=sub_url, mode=common.DOWNLOAD_MODE[1], session=session, admin=False),
										title = '%s | Add to Request Queue' % res,
										summary = 'Adds the current video to Request List',
										art = art,
										thumb = GetThumb(R(ICON_REQUESTS), session=session)
										)
									)
						
				except Exception as e:
					if Prefs["use_debug"]:
						Log('ERROR init.py>VideoDetail>AddToDownloadsListPre-1 %s' % (e.args))
				
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
		Log('ERROR init.py>VideoDetail>Movie3 %s, %s' % (e, (title + ' - ' + title_s)))
		
		return MC.message_container('Video Unavailable', 'Video Unavailable. Error: %s' % e)

	return oc
	
####################################################################################################
@route(PREFIX + "/ExtSources")
def ExtSources(title, url, summary, thumb, art, rating, duration, genre, directors, roles, movtitle=None, year=None, tvshowtitle=None, season=None, episode=None, session=None, imdb_id=None,refresh=0, **kwargs):

	try:
		summary = unicode(common.ascii_only(summary))
		#summary = unicode(str(summary).replace('"','').replace('\u00',''))
	except:
		summary = 'Not Available'
	
	tvshowcleaned = tvshowtitle
	if tvshowtitle != None:
		tvshowcleaned = tvshowtitle.replace(' ' + str(season),'')
	key = generatemoviekey(movtitle=movtitle, year=year, tvshowtitle=tvshowcleaned, season=season, episode=episode)
	oc_conc = ObjectContainer(title2='External Sources')
	oc = []
	prog = common.interface.checkProgress(key)

	use_prog_conc = common.SHOW_EXT_SRC_WHILE_LOADING
	doSleepForProgress = True
	
	if prog == 0:
		if common.interface.getExtSourcesThreadStatus(key=key) == False or common.interface.checkKeyInThread(key=key) == False:
			#common.interface.clearSources()
			try:
				CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
			except:
				CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
			Thread.Create(common.interface.getExtSources, {}, movtitle=movtitle, year=year, tvshowtitle=tvshowtitle, season=season, episode=episode, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY, ver=common.VERSION, imdb_id=imdb_id, session=session)
		if doSleepForProgress:
			time.sleep(7)
			doSleepForProgress = False
		prog = common.interface.checkProgress(key)
	if prog < 100:
		if doSleepForProgress:
			time.sleep(7)
			doSleepForProgress = False
		prog = common.interface.checkProgress(key)
		if use_prog_conc:
			if prog < 100:
				oc_conc = ObjectContainer(title2='External Sources - Progress %s%s' % (prog, '%'), no_history=True, no_cache=True)
				oc.append(DirectoryObject(
					key = Callback(ExtSources, movtitle=movtitle, tvshowtitle=tvshowtitle, season=season, episode=episode, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, session=session, refresh=int(refresh)+1),
					title = 'Refresh - %s%s Done' % (prog,'%'),
					summary = 'List sources by External Providers.',
					art = art,
					thumb = GetThumb(R(ICON_REFRESH), session=session)
					)
				)
		else:
			return MC.message_container('External Sources', 'Sources are being fetched ! Progress %s%s' % (prog,'%'))
		
	extSour = common.interface.getSources(encode=False, key=key)
	
	if use_prog_conc and prog < 100:
		pass
	elif len(extSour) == 0 and prog == 100:
		return MC.message_container('External Sources', 'No External Sources Available.')
	
	# match key
	filter_extSources = []
	filter_extSources += [i for i in extSour if i['key'] == key]
	
	extSourKey = []
	extSourKey += [i for i in filter_extSources]
	
	if use_prog_conc and prog < 100:
		pass
	if len(extSourKey) == 0 and prog == 100:
		return MC.message_container('External Sources', 'No External Sources Available for this video.')
		
	internal_extSources = extSourKey
	extExtrasSources_urlservice = []
	
	watch_title = movtitle
	if season != None and episode != None:
		watch_title = common.cleantitle.tvWatchTitle(tvshowtitle,season,episode,title)
	
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
		
	internal_extSources = common.FilterBasedOn(internal_extSources)
	
	internal_extSources = common.OrderBasedOn(internal_extSources, use_filesize=common.UsingOption(key=common.DEVICE_OPTIONS[9], session=session))
	
	plexservice_playback_links = []
	plexservice_extras_playback_links = []
	generic_playback_links = []
	filter_extSources = []
	for i in internal_extSources:
		if i not in filter_extSources:
			filter_extSources.append(i)
	internal_extSources = filter_extSources
	
	for source in internal_extSources:
		status = common.GetEmoji(type=source['online'], session=session)
		vidUrl = source['url']
		
		isTargetPlay = True if source['source'] not in ['gvideo','mega'] else False
		isVideoOnline = source['online']
		
		redirector_stat = ''
		redirector_enabled = 'false'
		if common.UsingOption(key=common.DEVICE_OPTIONS[2], session=session) and isTargetPlay == False:
			redirector_stat = '| (via Redirector)'
			redirector_enabled = 'true'
			
		pair_required = False
		if source['source'] == 'openload' and (Prefs['use_openload_pairing'] or not common.is_uss_installed()):
			pair_required = source['misc']['pair']
		
		try:
			file_size = '%s GB' % str(round(float(source['fs'])/common.TO_GB, 3))
		except:
			file_size = '? GB'
			
		if source['vidtype'] in 'Movie/Show':
			if source['titleinfo'] != '':
				titleinfo = ' | ' + source['titleinfo']
			else:
				titleinfo = ''
			title_msg = "%s %s| %s | %s | %s | %s | %s" % (status, source['maininfo'], source['rip'], source['quality'], file_size, source['source']+':'+source['subdomain'] if source['source']=='gvideo' else source['source'], source['provider'])
		else:
			#title_msg = ''
			#titleinfo = source['titleinfo']
			#title_msg = "%s %s| %s | %s | %s | %s | %s | %s" % (status, source['maininfo'], source['vidtype'], source['rip'], source['quality'], file_size, source['source'], source['provider'])
			#extExtrasSources_urlservice.append(source)
			if source['source'] == 'openload':
				title_msg = "%s %s| %s | %s | %s | %s | %s | %s" % (status, source['maininfo'], source['vidtype'], source['rip'], source['quality'], file_size, source['source'], source['provider'])
			elif source['source'] == 'direct':
				title_msg = "%s | %s-%s | %s | %s | %s | %s | %s" % (status, source['vidtype'], source['maininfo'], source['rip'], source['quality'], file_size, source['source'], source['provider'])
			else:
				title_msg = "%s | %s | %s | %s | %s | %s | %s" % (status, source['vidtype'], source['rip'], source['quality'], file_size, source['source'], source['provider'])
			
		if common.DEV_DEBUG == True:
			Log("%s --- %s %s" % (title_msg, source['vidtype'], vidUrl))
			my_i_hosts = common.interface.getHostsPlaybackSupport(encode=False)
			if source['source'] in my_i_hosts.keys():
				Log('Playback: %s' % my_i_hosts[source['source']])
		
		# all source links (not extras) that can be played via the code service
		if vidUrl != None and source['vidtype'] in 'Movie/Show' and source['enabled'] and source['allowsStreaming'] and source['misc']['player'] == 'iplayer' and common.interface.getHostsPlaybackSupport(encode=False)[source['source']]:
			urldata = source['urldata']
			params = source['params']
			
			if not Prefs['use_openload_pairing'] and 'openload' in source['source'] and common.is_uss_installed() and URLService.ServiceIdentifierForURL(vidUrl) != None:
					durl = vidUrl
			else:
				durl = "fmovies://" + E(JSON.StringFromObject({"url":url, "server":vidUrl, "title":title, "summary":summary, "thumb":thumb, "art":art, "year":year, "rating":rating, "duration":str(duration), "genre":genre, "directors":directors, "roles":roles, "isTargetPlay":str(isTargetPlay), "useSSL":Prefs["use_https_alt"], "isVideoOnline":str(isVideoOnline), "useRedirector": redirector_enabled, 'quality':source['quality'], 'urldata':urldata, 'params':params, 'pairrequired':pair_required, "host":source['source'], "openloadApiKey":Prefs['control_openload_api_key'], "force_transcode":common.UsingOption(key=common.DEVICE_OPTIONS[10], session=session)}))
			try:
				oc.append(VideoClipObject(
					url = durl,
					title = title_msg + titleinfo + redirector_stat,
					thumb = GetThumb(thumb, session=session),
					art = art,
					summary = summary,
					key = AddRecentWatchList(title = watch_title, url=url, summary=summary, thumb=thumb)
					)
				)
			except Exception as e:
				if Prefs["use_debug"]:
					Log('ERROR init.py>ExtSources>VideoClipObject-1 %s' % (e.args))
		
		# all source links (extra) that can be played via the code and plex service
		elif source['vidtype'] not in 'Movie/Show' and vidUrl != None and source['enabled'] and source['allowsStreaming']:
			plexservice_extras_playback_links.append(source)
			
		# all source links that can be played via the plex service
		elif vidUrl != None and source['enabled'] and source['allowsStreaming'] and source['misc']['player'] == 'eplayer':
			plexservice_playback_links.append(source)
			
		# all source links that can be attempted via the Generic Playback
		elif vidUrl != None and source['enabled'] and source['allowsStreaming'] and not source['misc']['gp']:
			try:
				generic_playback_links.append((title_msg + source['titleinfo'] + ' | (via Generic Playback)', summary, GetThumb(thumb, session=session), source['params'], duration, genre, vidUrl, source['quality'], watch_title))
			except:
				pass
		if vidUrl != None and source['enabled'] and source['allowsStreaming'] and source['misc']['gp']:
			try:
				generic_playback_links.append((title_msg + source['titleinfo'] + ' | (via Generic Playback)', summary, GetThumb(thumb, session=session), source['params'], duration, genre, vidUrl, source['quality'], watch_title))
			except:
				pass

	if  common.ALT_PLAYBACK:
		for gen_play in generic_playback_links:
			#Log(gen_play)
			title, summary, thumb, params, duration, genres, videoUrl, videoRes, watch_title = gen_play
			try:
				oc.append(CreateVideoObject(url, title, summary, thumb, params, duration, genres, videoUrl, videoRes, watch_title)) # ToDo
			except:
				pass
	
	if common.USE_EXT_URLSERVICES:
		external_extSources = extSourKey
		
		external_extSources = common.FilterBasedOn(external_extSources, use_host=False, use_filesize=False)
		
		extSources_urlservice = []
		for source in external_extSources:
			bool = True
			for i in common.INTERNAL_SOURCES:
				if i['name'] == source['source']:
					bool = False
					break
			if bool == True:
				extSources_urlservice.append(source)
				
		for source in plexservice_extras_playback_links:
			extExtrasSources_urlservice.append(source)
			
		extExtrasSources_urlservice = common.OrderBasedOn(extExtrasSources_urlservice, use_host=False, use_filesize=common.UsingOption(key=common.DEVICE_OPTIONS[9], session=session))
		cx = len(extExtrasSources_urlservice)
		
		for source in plexservice_playback_links:
			extSources_urlservice.append(source)
			
		filter_extSources = []
		dups = []
		for i in extSources_urlservice:
			if i['url'] not in dups:
				filter_extSources.append(i)
				dups.append(i['url'])
		extSources_urlservice = filter_extSources
			
		extSources_urlservice = common.OrderBasedOn(extSources_urlservice, use_host=False, use_filesize=common.UsingOption(key=common.DEVICE_OPTIONS[9], session=session))
		c = len(extSources_urlservice)
		
		if cx > 0:
			ext_summmary = ', '.join('%s (%s)' % (x['label'],'enabled' if str(x['enabled']).lower()=='true' else 'disabled') for x in common.INTERNAL_SOURCES_FILETYPE if 'Movie/Show' not in x['label'])
			ocp = DirectoryObject(title = 'Extras (%s items)' % str(cx), key = Callback(PSExtSources, con_title='Extras (%s items)' % str(cx), extSources_play=E(JSON.StringFromObject(extExtrasSources_urlservice)), session=session, watch_title=watch_title, year=year, summary=summary, thumb=thumb, art=art, url=url, duration=duration, rating=rating, genre=genre), summary=ext_summmary,thumb=R(ICON_PLEX))
			if prog < 100:
				oc.insert(1,ocp)
			else:
				oc.insert(0,ocp)
		if c > 0:
			ocp = DirectoryObject(title = 'External Sources (via Plex-Service) %s links' % str(c), key = Callback(PSExtSources, con_title='External Sources (via Plex-Service) %s links' % str(c), extSources_play=E(JSON.StringFromObject(extSources_urlservice)), session=session, watch_title=watch_title, year=year, summary=summary, thumb=thumb, art=art, url=url, duration=duration, rating=rating, genre=genre), summary='Playable via Plex services that are available and a Generic Player that tries its best to handle the rest.', thumb=R(ICON_PLEX))
			oc.append(ocp)

	if len(oc) == 0:
		return MC.message_container('External Sources', 'No videos based on Filter Selection')
	
	for i in oc:
		oc_conc.add(i)
	return oc_conc
	
####################################################################################################
@route(PREFIX + "/ExtSourcesDownload")
def ExtSourcesDownload(title, url, summary, thumb, art, rating, duration, genre, directors, roles, mode, movtitle=None, year=None, tvshowtitle=None, season=None, episode=None, session=None, imdb_id=None, refresh=0, **kwargs):

	try:
		summary = unicode(common.ascii_only(summary))
		#summary = unicode(str(summary).replace('"','').replace('\u00',''))
	except:
		summary = 'Not Available'
	
	tvshowcleaned = tvshowtitle
	if tvshowtitle != None:
		tvshowcleaned = tvshowtitle.replace(' ' + str(season),'')
	key = generatemoviekey(movtitle=movtitle, year=year, tvshowtitle=tvshowcleaned, season=season, episode=episode)
	oc = ObjectContainer(title2='Download Sources')
	prog = common.interface.checkProgress(key)
	use_prog_conc = common.SHOW_EXT_SRC_WHILE_LOADING
	doSleepForProgress = True
	
	if prog == 0:
		if common.interface.getExtSourcesThreadStatus(key=key) == False or common.interface.checkKeyInThread(key=key) == False:
			#common.interface.clearSources()
			try:
				CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
			except:
				CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
			Thread.Create(common.interface.getExtSources, {}, movtitle=movtitle, year=year, tvshowtitle=tvshowtitle, season=season, episode=episode, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY, ver=common.VERSION, imdb_id=imdb_id, session=session)
		if doSleepForProgress:
			time.sleep(7)
			doSleepForProgress = False
		prog = common.interface.checkProgress(key)
	if prog < 100:
		if doSleepForProgress:
			time.sleep(7)
			doSleepForProgress = False
		prog = common.interface.checkProgress(key)
		
		if use_prog_conc:
			if prog < 100:
				oc = ObjectContainer(title2='Download Sources - Progress %s%s' % (prog, '%'), no_history=True, no_cache=True)
				oc.add(DirectoryObject(
					key = Callback(ExtSourcesDownload, movtitle=movtitle, tvshowtitle=tvshowtitle, season=season, episode=episode, title=title, url=url, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, session=session, mode=mode, refresh=int(refresh)+1),
					title = 'Refresh - %s%s Done' % (prog,'%'),
					summary = 'List sources by External Providers.',
					art = art,
					thumb = GetThumb(R(ICON_REFRESH), session=session)
					)
				)
		else:
			return MC.message_container('Download Sources', 'Sources are being fetched ! Progress %s%s' % (prog,'%'))
	
	watch_title = movtitle
	if season != None and episode != None:
		watch_title = common.cleantitle.tvWatchTitle(tvshowtitle,season,episode,title)
		
	extSour = common.interface.getSources(encode=False, key=key)
	
	if use_prog_conc and prog < 100:
		pass
	elif len(extSour) == 0 and prog == 100:
		return MC.message_container('Download Sources', 'No External Sources Available.')
	
	# match key
	filter_extSources = []
	filter_extSources += [i for i in extSour if i['key'] == key]
	
	extSourKey = []
	extSourKey += [i for i in filter_extSources]
	
	if use_prog_conc and prog < 100:
		pass
	if len(extSourKey) == 0 and prog == 100:
		return MC.message_container('Download Sources', 'No External Sources Available for this video.')
		
	internal_extSources = extSourKey
		
	internal_extSources = common.FilterBasedOn(internal_extSources)
	
	internal_extSources = common.OrderBasedOn(internal_extSources, use_filesize=True)
	
	plexservice_playback_links = []
	plexservice_extras_playback_links = []
	generic_playback_links = []
	filter_extSources = []
	for i in internal_extSources:
		if i not in filter_extSources:
			filter_extSources.append(i)
	internal_extSources = filter_extSources
	
	for source in internal_extSources:
		status = common.GetEmoji(type=source['online'], session=session)
		vidUrl = source['url']
		
		isTargetPlay = True if source['source'] not in ['gvideo','mega'] else False
		isVideoOnline = source['online']
		
		redirector_stat = ''
		redirector_enabled = 'false'
		if common.UsingOption(key=common.DEVICE_OPTIONS[2], session=session) and isTargetPlay == False:
			redirector_stat = '| (via Redirector)'
			redirector_enabled = 'true'
			
		pair_required = False
		if source['source'] == 'openload' and (Prefs['use_openload_pairing'] or not common.is_uss_installed()):
			pair_required = source['misc']['pair']
		
		try:
			fsBytes = int(source['fs'])
			fs = '%s GB' % str(round(float(source['fs'])/common.TO_GB, 3))
		except:
			fsBytes = 0
			fs = None
		
		if source['vidtype'] in 'Movie/Show':
			titleinfo = source['titleinfo'] + ' | ' if source['titleinfo'] != '' else ''
			title_msg = "%s %s| %s | %s | %s | %s | %s | %sSubtitles: %s" % (status, source['maininfo'], source['rip'], source['quality'], fs, source['source']+':'+source['subdomain'] if source['source']=='gvideo' else source['source'], source['provider'], titleinfo, common.GetEmoji(type=True if source['sub_url'] != None else False, session=session))
			watch_title_x = watch_title
		else:
			if source['source'] == 'openload':
				title_msg = "%s %s| %s | %s | %s | %s | %s | %s" % (status, source['maininfo'], source['vidtype'], source['rip'], source['quality'], fs, source['source'], source['provider'])
			elif source['source'] == 'direct':
				title_msg = "%s | %s-%s | %s | %s | %s | %s | %s" % (status, source['vidtype'], source['maininfo'], source['rip'], source['quality'], fs, source['source'], source['provider'])
			else:
				title_msg = "%s | %s | %s | %s | %s | %s | %s" % (status, source['vidtype'], source['rip'], source['quality'], fs, source['source'], source['provider'])
				
			watch_title_x = '%s - %s%s' % (watch_title, source['maininfo'], (' - ' + source['vidtype']) if source['vidtype'].lower() not in source['maininfo'].lower() else '')
			
		if common.DEV_DEBUG == True:
			Log("%s --- %s" % (title_msg, vidUrl))
			my_i_hosts = common.interface.getHostsPlaybackSupport(encode=False)
			if source['source'] in my_i_hosts.keys():
				Log('Playback: %s' % my_i_hosts[source['source']])
		
		# all source links (not extras) that can be played via the code service
		if vidUrl != None and source['enabled'] and source['allowsDownload'] and source['misc']['player'] == 'iplayer' and common.interface.getHostsPlaybackSupport(encode=False)[source['source']] or source['source'] == 'direct':
			
			try:
				libtype='movie' if tvshowtitle == None else 'show'
				oc.add(DirectoryObject(
					key = Callback(AddToDownloadsListPre, title=watch_title_x, purl=url, url=source['url'], durl=source['durl'], sub_url=source['sub_url'], summary=summary, thumb=thumb, year=year, fsBytes=fsBytes, fs=fs, file_ext=source['file_ext'], quality=source['quality'], source=source['source'], source_meta={}, file_meta={}, type=libtype, resumable=source['resumeDownload'], mode=mode, session=session, admin=True if mode==common.DOWNLOAD_MODE[0] else False),
					title = title_msg,
					summary = 'Adds the current video to %s List' % 'Download' if mode==common.DOWNLOAD_MODE[0] else 'Request',
					art = art,
					thumb = GetThumb(R('%s' % ICON_OTHERSOURCESDOWNLOAD if mode==common.DOWNLOAD_MODE[0] else ICON_REQUESTS), session=session)
					)
				)
			except Exception as e:
				if Prefs["use_debug"]:
					Log('ERROR init.py>ExtSourcesDownload>AddToDownloadsListPre-1 %s' % (e.args))

	if len(oc) == 0:
		return MC.message_container('Download Sources', 'No videos based on Filter Selection')
	
	return oc
	
####################################################################################################
	
@route(PREFIX + "/PSExtSources")
def PSExtSources(extSources_play, con_title, session, watch_title, year, summary, thumb, art, url, duration, rating, genre):
	oc = ObjectContainer(title2 = unicode(con_title), no_cache=common.isForceNoCache())
	
	try:
		summary = unicode(common.ascii_only(summary))
		#summary = unicode(str(summary).replace('"','').replace('\u00',''))
	except:
		summary = 'Not Available'
	
	generic_playback_links = []
	
	all_sources = JSON.ObjectFromString(D(extSources_play))
	
	for source in all_sources:
		status = common.GetEmoji(type=source['online'], session=session)
		vidUrl = source['url']
		
		isTargetPlay = True if source['source'] not in ['gvideo','mega'] else False
		isVideoOnline = source['online']
		
		redirector_stat = ''
		redirector_enabled = 'false'
		if common.UsingOption(key=common.DEVICE_OPTIONS[2], session=session) and isTargetPlay == False:
			redirector_stat = '| (via Redirector)'
			redirector_enabled = 'true'
			
		pair_required = False
		if source['source'] == 'openload' and (Prefs['use_openload_pairing'] or not common.is_uss_installed()):
			pair_required = source['misc']['pair']
		
		try:
			file_size = '%s GB' % str(round(float(source['fs'])/common.TO_GB, 3))
		except:
			file_size = '? GB'
			
		if source['vidtype'] in 'Movie/Show':
			if source['titleinfo'] != '':
				titleinfo = ' | ' + source['titleinfo']
			else:
				titleinfo = ''
			title_msg = "%s %s| %s | %s | %s | %s | %s" % (status, source['maininfo'], source['rip'], source['quality'], file_size, source['source']+':'+source['subdomain'] if source['source']=='gvideo' else source['source'], source['provider'])
		else:
			titleinfo = source['titleinfo']
			if source['source'] == 'openload':
				title_msg = "%s %s| %s | %s | %s | %s | %s | %s" % (status, source['maininfo'], source['vidtype'], source['rip'], source['quality'], file_size, source['source'], source['provider'])
			elif source['source'] == 'direct':
				title_msg = "%s | %s-%s | %s | %s | %s | %s | %s" % (status, source['vidtype'], source['maininfo'], source['rip'], source['quality'], file_size, source['source'], source['provider'])
			else:
				title_msg = "%s | %s | %s | %s | %s | %s | %s" % (status, source['vidtype'], source['rip'], source['quality'], file_size, source['source'], source['provider'])
			
		if common.DEV_DEBUG == True:
			Log("%s --- %s" % (title_msg, vidUrl))
			Log("%s" % source)
			my_i_hosts = common.interface.getHostsPlaybackSupport(encode=False)
			if source['source'] in my_i_hosts.keys():
				Log('Playback: %s' % my_i_hosts[source['source']])
		
		# all source links (not extras) that can be played via the code service
		if vidUrl != None and source['enabled'] and source['allowsStreaming'] and source['misc']['player'] == 'iplayer' and common.interface.getHostsPlaybackSupport(encode=False)[source['source']]:
			urldata = source['urldata']
			params = source['params']
			
			if not Prefs['use_openload_pairing'] and 'openload' in source['source'] and common.is_uss_installed() and URLService.ServiceIdentifierForURL(vidUrl) != None:
					durl = vidUrl
			else:
				durl = "fmovies://" + E(JSON.StringFromObject({"url":url, "server":vidUrl, "title":watch_title, "summary":summary, "thumb":thumb, "art":art, "year":year, "rating":rating, "duration":str(duration), "genre":genre, "directors":None, "roles":None, "isTargetPlay":str(isTargetPlay), "useSSL":Prefs["use_https_alt"], "isVideoOnline":str(isVideoOnline), "useRedirector": redirector_enabled, 'quality':source['quality'], 'urldata':urldata, 'params':params, 'pairrequired':pair_required, "host":source['source'], "openloadApiKey":Prefs['control_openload_api_key'], "force_transcode":common.UsingOption(key=common.DEVICE_OPTIONS[10], session=session)}))
			try:
				oc.add(VideoClipObject(
					url = durl,
					title = title_msg + titleinfo + redirector_stat,
					thumb = GetThumb(thumb, session=session),
					art = art,
					summary = summary,
					key = AddRecentWatchList(title = watch_title, url=url, summary=summary, thumb=thumb)
					)
				)
			except Exception as e:
				if Prefs["use_debug"]:
					Log('ERROR init.py>PSExtSources>VideoClipObject-1 %s' % (e.args))
	
		elif vidUrl != None:
			status = common.GetEmoji(type=source['online'], session=session)
			if source['vidtype'] in 'Movie/Show':
				title_msg = "%s %s| %s | %s | %s | %s" % (status, source['maininfo'], source['rip'], source['quality'], source['source'], source['provider'])
			else:
				if source['source'] == 'openload':
					title_msg = "%s %s| %s | %s | %s | %s | %s" % (status, source['maininfo'], source['vidtype'], source['rip'], source['quality'], source['source'], source['provider'])
				elif source['source'] == 'direct':
					title_msg = "%s | %s-%s | %s | %s | %s | %s" % (status, source['vidtype'], source['maininfo'], source['rip'], source['quality'], source['source'], source['provider'])
				else:
					title_msg = "%s | %s | %s | %s | %s | %s" % (status, source['vidtype'], source['rip'], source['quality'], source['source'], source['provider'])
			
			try:
				url_serv = URLService.ServiceIdentifierForURL(vidUrl)
				if url_serv != None and source['enabled'] == True:
					oc.add(VideoClipObject(
						url = vidUrl,
						title = title_msg + source['titleinfo'] + ' | (via Plex Service %s)' % url_serv,
						thumb = GetThumb(thumb, session=session),
						art = art,
						summary = summary,
						key = AddRecentWatchList(title = watch_title, url=url, summary=summary, thumb=thumb)
						)
					)
				elif source['enabled'] == True:
					generic_playback_links.append((title_msg + source['titleinfo'] + ' | (via Generic Playback)', summary, GetThumb(thumb, session=session), source['params'], duration, genre, vidUrl, source['quality'], watch_title))
			except:
				try:
					generic_playback_links.append((title_msg + source['titleinfo'] + ' | (via Generic Playback)', summary, GetThumb(thumb, session=session), source['params'], duration, genre, vidUrl, source['quality'], watch_title))
				except:
					Log('Error in Adding --- %s : %s' % (vidUrl, title_msg))
					pass
				
	if  common.ALT_PLAYBACK:
		for gen_play in generic_playback_links:
			#Log(gen_play)
			title, summary, thumb, params, duration, genres, videoUrl, videoRes, watch_title = gen_play
			try:
				oc.add(CreateVideoObject(url, title, summary, thumb, params, duration, genres, videoUrl, videoRes, watch_title)) # ToDo
			except:
				pass
	return oc
	
####################################################################################################
	
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
			
		CUSTOM_TIMEOUT_DICT[client_id]={}
	
####################################################################################################
@route(PREFIX + "/isTimeoutApproaching")	
def isTimeoutApproaching(clientProd, item, client_id, session=None, **kwargs):
	
	# define custom timeouts for each client along with session & item to make it unique for multiple instances
	
	if common.USE_CUSTOM_TIMEOUT == True and common.UsingOption(common.DEVICE_OPTIONS[5], session=session) and Client.Product in CUSTOM_TIMEOUT_CLIENTS:
		if client_id in CUSTOM_TIMEOUT_DICT.keys() and item in CUSTOM_TIMEOUT_DICT[client_id].keys():
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
		
	if client_id in CUSTOM_TIMEOUT_DICT.keys() and item in CUSTOM_TIMEOUT_DICT[client_id].keys():
		CUSTOM_TIMEOUT_DICT[client_id]={}
	return True
	
####################################################################################################
@route(PREFIX + "/GetThumb")	
def GetThumb(thumb, session=None, **kwargs):
	if common.UsingOption(key=common.DEVICE_OPTIONS[1], session=session):
		return None
	
	if thumb != None and thumb == 'N/A':
		thumb = R(ICON_UNAV)
	return thumb

####################################################################################################
@route(PREFIX + "/SimilarRecommendations")	
def SimilarRecommendations(title, similar_reccos, referer=None, is9anime = 'False', session = None, **kwargs):

	oc = ObjectContainer(title2 = 'Similar to ' + title, no_cache=common.isForceNoCache())
	
	similar_reccos = JSON.ObjectFromString(D(similar_reccos))
	
	for elem in similar_reccos:
		name = elem['name']
		if is9anime == 'False':
			loc = fmovies.BASE_URL + elem['loc']
			dataEXSAnim = None
		else:
			loc = elem['loc']
			dataEXSAnim = loc
			
		thumb = elem['thumb']
		eps_nos = elem['eps_nos']
		summary = 'Plot Summary on Item Page.'
		more_info_link = elem['more_info_link']

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb, session = session, dataEXSAnim = dataEXSAnim),
			title = name,
			summary = GetMovieInfo(summary=summary, urlPath=more_info_link, referer=referer, session=session, is9anime=is9anime) + eps_nos,
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
def MoviesWithPeople(stars, session, is9anime='False', **kwargs):

	oc = ObjectContainer(title2 = 'People Search', no_cache=common.isForceNoCache())
	
	roles_s = stars.split(',')
	if len(roles_s) > 0:
		roles_s = sorted(roles_s)
	for role in roles_s:
		role = common.removeAccents(role)
		if is9anime == 'False':
			surl= fmovies.BASE_URL + fmovies.STAR_PATH + role.lower().replace(' ', '-')
		else:
			surl= common.ANIME_URL + fmovies.STAR_PATH + role.lower().replace(' ', '-')
			
		oc.add(DirectoryObject(
			key = Callback(Search, query = role, session = session, surl= surl, mode = 'people', is9anime=is9anime),
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
def MoviesWithTag(tags, session, is9anime='False', **kwargs):

	oc = ObjectContainer(title2 = 'Tag Search', no_cache=common.isForceNoCache())
	
	tags_s = tags.split(',')
	if len(tags_s) > 0:
		tags_s = sorted(tags_s)
	for tag in tags_s:
		tag = re.sub(r'[^0-9a-zA-Z ]', '', tag)
		if len(tag) > 0:
			if is9anime == 'False':
				surl= fmovies.BASE_URL + fmovies.KEYWORD_PATH + tag.lower().replace(' ', '-')
			else:
				surl= common.ANIME_URL + fmovies.KEYWORD_PATH + tag.lower().replace(' ', '-')
			oc.add(DirectoryObject(
				key = Callback(Search, query = tag, session = session, surl= surl, mode = 'tag', is9anime=is9anime),
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
def GetMovieInfo(summary, urlPath, referer=None, session=None, is9anime='False', **kwargs):

	if common.NO_MOVIE_INFO == True or urlPath == None and (summary == None or summary == '') or Prefs['use_web_proxy']:
		return 'Plot Summary on Item Page'
	elif (is9anime == 'False' and common.UsingOption(common.DEVICE_OPTIONS[8], session=session) == True) or (is9anime == 'True' and common.UsingOption(common.DEVICE_OPTIONS[11], session=session) == True):
		return 'Plot Summary on Item Page. Disabled via Device Options.'
	elif summary != None and Prefs["dont_fetch_more_info"]:
		return summary
	elif urlPath == None:
		return summary
	elif Prefs["dont_fetch_more_info"]:
		return 'Plot Summary on Item Page'
		
	try:
		if is9anime == 'False':
			url = fmovies.BASE_URL + '/' + urlPath
		else:
			url = common.ANIME_URL + '/' + urlPath
			
		page_data, error = common.GetPageElements(url=url, referer=referer)
		
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

	#Log("%s %s" % (title, url))
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

	oc = ObjectContainer(title1=title, no_cache=common.isForceNoCache())
	NO_OF_ITEMS_IN_RECENT_LIST = 100
	
	urls_list = []
	items_to_del = []
	items_in_recent = []
	
	for each in Dict:
		longstring = str(Dict[each])
		
		if (('fmovies.' in longstring or 'bmovies.' in longstring) or common.isArrayValueInString(common.EXT_SITE_URLS, longstring) == True) and 'RR44SS' in longstring:
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
		
		ES = ''
		if common.ES_API_URL.lower() in longstring.lower():
			ES = common.EMOJI_EXT
		if common.ANIME_URL.lower() in longstring.lower():
			ES = common.EMOJI_ANIME
		
		if url.replace('fmovies.to',fmovies_base) in items_in_recent or c > NO_OF_ITEMS_IN_RECENT_LIST:
			items_to_del.append(each['key'])
		elif url.replace('fmovies.se',fmovies_base) in items_in_recent or c > NO_OF_ITEMS_IN_RECENT_LIST:
			items_to_del.append(each['key'])
		elif url.replace('fmovies.is',fmovies_base) in items_in_recent or c > NO_OF_ITEMS_IN_RECENT_LIST:
			items_to_del.append(each['key'])
		elif url.replace('bmovies.to',fmovies_base) in items_in_recent or c > NO_OF_ITEMS_IN_RECENT_LIST:
			items_to_del.append(each['key'])
		elif url.replace('bmovies.online',fmovies_base) in items_in_recent or c > NO_OF_ITEMS_IN_RECENT_LIST:
			items_to_del.append(each['key'])
		elif url.replace('bmovies.is',fmovies_base) in items_in_recent or c > NO_OF_ITEMS_IN_RECENT_LIST:
			items_to_del.append(each['key'])
		elif url.replace('bmovies.pro',fmovies_base) in items_in_recent or c > NO_OF_ITEMS_IN_RECENT_LIST:
			items_to_del.append(each['key'])
		else:
			if 'fmovies.' in longstring or 'bmovies.' in longstring:
				url = url.replace(common.client.geturlhost(url),fmovies_base)
			items_in_recent.append(url)
				
			oc.add(DirectoryObject(
				key=Callback(EpisodeDetail, title=stitle, url=url, thumb=thumb, session = session),
				title= '%s%s' % (stitle,ES),
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
			if (('fmovies.' in longstring or 'bmovies.' in longstring) or common.isArrayValueInString(common.EXT_SITE_URLS, longstring) == True) and 'RR44SS' in longstring:
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
def Bookmarks(title, session = None, **kwargs):

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")
	
	oc = ObjectContainer(title1=title, no_cache=common.isForceNoCache())
	
	fmovies_base = fmovies.BASE_URL.replace('https://www.','')
	fmovies_base = fmovies_base.replace('https://','')
	
	items_in_bm = []
	items_to_del = []
	
	for each in Dict:
		longstring = str(Dict[each])
		
		if (('fmovies.' in longstring or 'bmovies.' in longstring) or common.isArrayValueInString(common.EXT_SITE_URLS, longstring) == True) and 'Key5Split' in longstring:	
			stitle = unicode(longstring.split('Key5Split')[0])
			url = longstring.split('Key5Split')[1]
			summary = unicode(longstring.split('Key5Split')[2])
			thumb = longstring.split('Key5Split')[3]
			
			url = url.replace('www.','')
			
			if 'fmovies.to' in url:
				url = url.replace('fmovies.to',fmovies_base)
			elif 'bmovies.to' in url:
				url = url.replace('bmovies.to',fmovies_base)
			elif 'bmovies.online' in url:
				url = url.replace('bmovies.online',fmovies_base)
			elif 'bmovies.is' in url:
				url = url.replace('bmovies.is',fmovies_base)
			elif 'bmovies.pro' in url:
				url = url.replace('bmovies.pro',fmovies_base)
			elif 'fmovies.se' in url:
				url = url.replace('fmovies.se',fmovies_base)
			elif 'fmovies.is' in url:
				url = url.replace('fmovies.is',fmovies_base)
			else:
				if 'fmovies.' in url or 'bmovies.' in url:
					urlhost = common.client.getUrlHost(url)
					url = url.replace(urlhost,fmovies_base)
				
			#Log("BM : %s" % url)
				
			if url not in items_in_bm:
				
				items_in_bm.append(url)
				is9anime = 'False'
				ES = ''
				if common.ES_API_URL.lower() in url.lower():
					ES = common.EMOJI_EXT
				if common.ANIME_URL.lower() in url.lower():
					ES = common.EMOJI_ANIME
					is9anime = 'True'
				
				if fmovies.FILTER_PATH in url or '(All Seasons)' in stitle:
					oc.add(DirectoryObject(
						key=Callback(Search, query=stitle.replace(' (All Seasons)',''), session = session, mode='other seasons', thumb=thumb, summary=summary, is9anime=is9anime),
						title='%s%s' % (stitle,ES),
						thumb=thumb,
						summary=summary
						)
					)
				else:
					oc.add(DirectoryObject(
						key=Callback(EpisodeDetail, title=stitle, url=url, thumb=thumb, session = session),
						title='%s%s' % (stitle,ES),
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
	
#######################################################################################################
@route(PREFIX + '/AddToDownloadsListPre')
def AddToDownloadsListPre(title, year, url, durl, purl, summary, thumb, quality, source, type, resumable, source_meta, file_meta, mode, sub_url=None, fsBytes=None, fs=None, file_ext=None, section_path=None, section_title=None, section_key=None, session=None, admin=False, update=False, **kwargs):
	
	admin = True if str(admin) == 'True' else False
	update = True if str(update) == 'True' else False
	resumable = True if str(resumable) == 'True' else False
	user = common.control.setting('%s-%s' % (session,'user'))
		
	bool = False
	for i_source in common.interface.getHosts(encode=False):
		if i_source['name'].lower() in source.lower() and i_source['downloading']:
			bool = True
			break

	if bool == False:
		return MC.message_container('Download Sources', 'No compatible Download service found for this URL !')
		
	title = common.cleantitle.windows_filename(title)
	tuec = E(title+year+quality+source+url)
		
	#if mode == common.DOWNLOAD_MODE[1]:
	if fs == None or fsBytes == None or int(fsBytes) == 0:
		try:
			if 'openload' in source:
				isPairDone = common.host_openload.isPairingDone()
				online, r1, err, fs_i, furl2, sub_url_t =  common.host_openload.check(url, usePairing = False, embedpage=True)
				if sub_url == None:
					sub_url = sub_url_t
			elif 'rapidvideo' in source:
				vurl, r1, sub_url_t = common.host_rapidvideo.resolve(url, True)
				if sub_url == None:
					sub_url = sub_url_t
				fs_i, err = common.client.getFileSize(vurl, retError=True, retry429=True, cl=2)
			else:
				fs_i, err = common.client.getFileSize(url, retError=True, retry429=True, cl=2)

			if err != '':
				return MC.message_container('Error', 'Error: %s. Please try again later when it becomes available.' % err)
				
			try:
				fsBytes = int(fs_i)
				fs = '%s GB' % str(round(float(fs_i)/common.TO_GB, 3))
			except:
				fsBytes = 0
				fs = '? GB'
				
			if int(fsBytes) < 100 * 1024:
				return MC.message_container('FileSize Error', 'File reporting %s bytes cannot be downloaded. Please try again later when it becomes available.' % fsBytes)

		except Exception as e:
			return MC.message_container('Error', '%s. Sorry but file could not be added.' % e)

	uid = 'Down5Split'+E(title+year+fs+quality+source)
	if Dict[uid] != None:
		EncTxt = Dict[uid]
		EncTxt = JSON.ObjectFromString(D(EncTxt))
		if admin == False and update == False:
			return MC.message_container('Download Sources', 'Item exists in Downloads List')
		elif admin == True and update == True and EncTxt['url'] != url:
			if uid in common.DOWNLOAD_STATS:
				return MC.message_container('Item Update', 'Cannot update a Downloading item.')
			
			EncTxt['url'] = url
			Dict[uid] = E(JSON.StringFromObject(EncTxt))
			Dict.Save()
			return MC.message_container('Item Update', 'Item has been updated with new download url')
		elif admin == True and update == False and EncTxt['url'] != url:
			oc = ObjectContainer(title1='Item exists in Downloads List', no_cache=common.isForceNoCache())
			oc.add(DirectoryObject(key = Callback(AddToDownloadsListPre, title=title, purl=purl, url=url, durl=durl, summary=summary, thumb=thumb, year=year, quality=quality, source=source, source_meta=source_meta, file_meta=file_meta, type=type, resumable=resumable, sub_url=sub_url, fsBytes=fsBytes, fs=fs, file_ext=file_ext, mode=mode, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, update=True), title = 'Update this item'))
			oc.add(DirectoryObject(key = Callback(MyMessage, title='Return', msg='Use back to Return to previous screen'), title = 'Return'))
			return oc
		elif admin == True and update == True and EncTxt['url'] == url:
			return MC.message_container('Item Updated', 'Item url updated.')
		elif admin == True and update == False and EncTxt['url'] == url:
			#return MC.message_container('Item Updated', 'Item url is up to date.')
			pass
		else:
			return MC.message_container('Item Updated', 'Please return to previous screen.')

		#uid = 'Request5Split'+E(title+year+fs+quality+source)
		#if Dict[uid] != None:
		#	return MC.message_container('Requested Sources', 'Item already in Requested List')
			
	if mode == common.DOWNLOAD_MODE[1]:
		if file_ext == None:
			file_ext = '.mp4'

		chunk_size = int(1024.0 * 1024.0 * float(common.DOWNLOAD_CHUNK_SIZE)) # in bytes
		fid = '.'+common.id_generator()
		
		EncTxt = E(JSON.StringFromObject({'title':title, 'year':year, 'url':url, 'durl':durl, 'purl':purl, 'sub_url':sub_url, 'summary':summary, 'thumb':thumb, 'fsBytes':int(fsBytes), 'fs':fs, 'chunk_size':chunk_size, 'file_ext':file_ext, 'quality':quality, 'source':source, 'source_meta':source_meta, 'file_meta':file_meta, 'uid':uid, 'fid':fid, 'type':type, 'resumable':resumable, 'status':common.DOWNLOAD_STATUS[4], 'startPos':0, 'timeAdded':time.time(), 'first_time':time.time(), 'progress':0, 'chunk_speed':0,'avg_speed':0,'avg_speed_curr':0, 'eta':0, 'error':'', 'last_error':'Unknown Error', 'action':common.DOWNLOAD_PROPS[3],'section_path':section_path, 'section_title':section_title, 'section_key':section_key, 'user':user})) 
		Dict[uid] = EncTxt
		Dict.Save()
		return MC.message_container('Requested Sources', 'Successfully added to Requested List')
		
	if 'openload' in source.lower() and Prefs['use_openload_pairing'] == False:
		return MC.message_container('Download Sources', 'Use OpenLoad needs to be enabled under Channel Setting/Prefs.')

		
	if tuec not in Dict['DOWNLOAD_OPTIONS_SECTION_TEMP']:
		Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'][tuec] = {}
		for x in common.DOWNLOAD_OPTIONS.keys():
			Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'][tuec][x] = common.DOWNLOAD_OPTIONS[x]
		Dict.Save()
		
	return AddToDownloadsList(title=title, purl=purl, url=url, durl=durl, summary=summary, thumb=thumb, year=year, quality=quality, source=source, source_meta=source_meta, file_meta=file_meta, type=type, resumable=resumable, sub_url=sub_url, fsBytes=fsBytes, fs=fs, file_ext=file_ext, mode=mode, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, update=update, user=user)
	
######################################################################################
# Adds a movie to the DownloadsList list using the (title + 'Down5Split') as a key for the url
@route(PREFIX + "/addToDownloadsList")
def AddToDownloadsList(title, year, url, durl, purl, summary, thumb, quality, source, type, resumable, source_meta, file_meta, sub_url=None, fsBytes=None, fs=None, file_ext=None, section_path=None, section_title=None, section_key=None, session=None, admin=False, update=False, user=None, **kwargs):

	admin = True if str(admin) == 'True' else False
	update = True if str(update) == 'True' else False
	resumable = True if str(resumable) == 'True' else False
	
	#Log(common.DOWNLOAD_OPTIONS_SECTION_TEMP)
	tuec = E(title+year+quality+source+url)
	
	if resumable != None and str(resumable).lower() == 'true':
		resumable = True
	else:
		resumable = False
	
	if section_path == None:
	
		time.sleep(2)
		
		DOWNLOAD_OPTIONS_SECTION_TEMP = Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'][tuec]
		
		if type not in DOWNLOAD_OPTIONS_SECTION_TEMP.keys() or len(DOWNLOAD_OPTIONS_SECTION_TEMP[type]) == 0:
			if 'Done' in DOWNLOAD_OPTIONS_SECTION_TEMP.keys():
				del Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'][tuec]
				Dict.Save()
				return MC.message_container('Download Sources', 'Item in Downloads Queue... Please return to previous screen.')
			if 'Error' in DOWNLOAD_OPTIONS_SECTION_TEMP.keys():
				del Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'][tuec]
				Dict.Save()
				return MC.message_container('Error', 'Error... Please return to previous screen.')
			return MC.message_container('Download Sources', 'No Download Locations set under Download Options')	
		elif 'Done' in DOWNLOAD_OPTIONS_SECTION_TEMP.keys():
			Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'][tuec] = {}
			Dict.Save()
			return MC.message_container('Download Sources', 'Item in Downloads Queue... Please return to previous screen.')
		elif 'Error' in DOWNLOAD_OPTIONS_SECTION_TEMP.keys():
			Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'][tuec] = {}
			Dict.Save()
			return MC.message_container('Download Sources', 'Error... Please return to previous screen.')
		elif type in DOWNLOAD_OPTIONS_SECTION_TEMP and len(DOWNLOAD_OPTIONS_SECTION_TEMP[type]) > 0:
			LOCS = []
			for item in DOWNLOAD_OPTIONS_SECTION_TEMP[type]:
				if item['enabled']:
					LOCS.append(item)
			if len(LOCS) == 1:
				item = LOCS[0]
				return AddToDownloadsList(title=title, year=year, url=url, durl=durl, purl=purl, summary=summary, thumb=thumb, fs=fs, fsBytes=fsBytes, file_ext=file_ext, quality=quality, source=source, source_meta=source_meta, file_meta=file_meta, type=type, resumable=resumable, sub_url=sub_url, section_path=item['path'], section_title=item['title'], section_key=item['key'], session=session, admin=admin, update=update, user=user)
			else:
				oc = ObjectContainer(title1='Select Location', no_cache=common.isForceNoCache())
				for item in DOWNLOAD_OPTIONS_SECTION_TEMP[type]:
					if item['enabled']:
						oc.add(DirectoryObject(
							key = Callback(AddToDownloadsList, title=title, year=year, url=url, durl=durl, purl=purl, summary=summary, thumb=thumb, fs=fs, fsBytes=fsBytes, file_ext=file_ext, quality=quality, source=source, source_meta=source_meta, file_meta=file_meta, type=type, resumable=resumable, sub_url=sub_url, section_path=item['path'], section_title=item['title'], section_key=item['key'], session=session, admin=admin, update=update, user=user),
							title = '%s | %s' % (item['title'], item['path'])
							)
						)
				if len(oc) == 0:
					return MC.message_container('Download Sources', 'No Download Location set under Download Options')
				return oc
	else:
		isPairDone = True
		pair_required = True
		try:
			if fs == None:
				if 'openload' in source:
					isPairDone = common.host_openload.isPairingDone()
					if isPairDone == False:
						pair_required, u1 = common.host_openload.isPairingRequired(url=url, session=session)
						if pair_required == False:
							fs_i, err = common.client.getFileSize(u1, retError=True, retry429=True, cl=2)
					online, r1, err, fs_i =  common.host_openload.check(url, usePairing = False, embedpage=True)
				else:
					fs_i, err = common.client.getFileSize(url, retError=True, retry429=True, cl=2)

				if err != '':
					raise Exception(e)
					
				try:
					fsBytes = int(fs_i)
					fs = '%s GB' % str(round(float(fs_i)/common.TO_GB, 3))
				except:
					fsBytes = 0
					fs = '? GB'
					
			if int(fsBytes) < 100 * 1024:
				Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'][tuec] = {}
				Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'][tuec]['Error'] = 'Error'
				Dict.Save()
				return MC.message_container('FileSize Error', 'File reporting %s bytes cannot be downloaded. Please try again later when it becomes available.' % fsBytes)
				
			uid = 'Down5Split'+E(title+year+fs+quality+source)
			if Dict[uid] != None:
				if admin == True and update == True:
					pass
				else:
					Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'][tuec] = {}
					Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'][tuec]['Done'] = 'Done'
					Dict.Save()
					return MC.message_container('Download Sources', 'Item already in Downloads List')
					
			if file_ext == None:
				file_ext = '.mp4'

			chunk_size = int(1024.0 * 1024.0 * float(common.DOWNLOAD_CHUNK_SIZE)) # in bytes
			fid = '.'+common.id_generator()
			
			EncTxt = E(JSON.StringFromObject({'title':title, 'year':year, 'url':url, 'durl':durl, 'purl':purl, 'sub_url':sub_url, 'summary':summary, 'thumb':thumb, 'fsBytes':int(fsBytes), 'fs':fs, 'chunk_size':chunk_size, 'file_ext':file_ext, 'quality':quality, 'source':source, 'source_meta':source_meta, 'file_meta':file_meta, 'uid':uid, 'fid':fid, 'type':type, 'resumable':resumable, 'status':common.DOWNLOAD_STATUS[0], 'startPos':0, 'timeAdded':time.time(), 'first_time':time.time(), 'progress':0, 'chunk_speed':0,'avg_speed':0,'avg_speed_curr':0, 'eta':0, 'error':'', 'last_error':'Unknown Error', 'action':common.DOWNLOAD_ACTIONS[4],'section_path':section_path, 'section_title':section_title, 'section_key':section_key, 'user':user})) 
			Dict[uid] = EncTxt
			Dict.Save()
			Thread.Create(download.trigger_que_run)
		except Exception as e:
			err = '{}'.format(e)
			Log(err)
			return MC.message_container('Download Sources', 'Error %s when adding for Downloading ! Please try again later.' % err)
			
		Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'][tuec] = {}
		Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'][tuec]['Done'] = 'Done'
		Dict.Save()

		time.sleep(2)
		
		if 'openload' in source.lower() and isPairDone == False and pair_required == True:
			return MC.message_container('Download Sources', 'Successfully added but requires *Pairing* to Download')
		else:
			return MC.message_container('Download Sources', 'Successfully added to Download List')
	
######################################################################################
# Loads Downloads from Dict.
@route(PREFIX + "/downloads")
def Downloads(title, session = None, status = None, refresh = 0, **kwargs):

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")
	
	oc = ObjectContainer(title1=title, no_cache=common.isForceNoCache())
	
	if status == None:
		N_status = {}
		for dstatus in common.DOWNLOAD_STATUS:
			c = 0
			for each in Dict:
				if 'Down5Split' in each:
					try:
						longstringObjs = JSON.ObjectFromString(D(Dict[each]))
						if longstringObjs['status'] == dstatus  or dstatus == common.DOWNLOAD_STATUS[5]:
							c += 1
					except Exception as e:
						Log('ERROR: Downloads >> %s' % e)
			N_status[dstatus] = c
		for statusx in common.DOWNLOAD_STATUS:
			oc.add(DirectoryObject(
				key = Callback(Downloads, title="%s Downloads" % statusx, status = statusx, session = session),
				title = '%s (%s)' % (statusx, str(N_status[statusx]))
				)
			)
		return oc
	
	items_to_del = []
	doTrigger = False
	
	for each in Dict:
		if 'Down5Split' in each:
			try:
				longstringObjs = JSON.ObjectFromString(D(Dict[each]))
				if longstringObjs['status'] == status or status == common.DOWNLOAD_STATUS[5]:
					timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(longstringObjs['timeAdded'])))
					key = None
					summary = longstringObjs['summary']
					has_sub = False if longstringObjs['sub_url'] == None else True
					
					if status == common.DOWNLOAD_STATUS[0]: # Queued
						wtitle = '%s (%s) | %s | %s - %s | %s | %s - %s | %s | Subtitle:%s' % (longstringObjs['title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['status'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', common.GetEmoji(type=has_sub, mode='simple', session=session))
						key = Callback(DownloadingFilesMenu, title=longstringObjs['title'], uid=longstringObjs['uid'], choice=None, session=session, status=status)
					elif status == common.DOWNLOAD_STATUS[1]: # Downloading
						if each not in common.DOWNLOAD_STATS.keys() and len(common.DOWNLOAD_STATS.keys()) < int(Prefs['download_connections']):
							longstringObjs['status'] = common.DOWNLOAD_STATUS[1]
							longstringObjs['action'] = common.DOWNLOAD_ACTIONS[4]
							Dict[each] = E(JSON.StringFromObject(longstringObjs))
							
							#longstringObjs['status'] = common.DOWNLOAD_STATUS[1]
							#common.DOWNLOAD_STATS[each] = Dict[each]
							#doTrigger = True
							
							EncTxt = E(JSON.StringFromObject(longstringObjs))
							Thread.Create(download.do_download, {}, file_meta_enc=EncTxt)
						elif each not in common.DOWNLOAD_STATS.keys():
							longstringObjs['status'] = common.DOWNLOAD_STATUS[0]
							longstringObjs['action'] = common.DOWNLOAD_ACTIONS[4]
							Dict[each] = E(JSON.StringFromObject(longstringObjs))
							doTrigger = True
						else:
							longstringObjs = common.DOWNLOAD_STATS[each]
							
						try:
							eta = float(longstringObjs['eta'])
						except:
							eta = '?'
							
						if eta == '?' or str(eta) == '0':
							eta_str = 'calculating time'
						elif eta < 0.1:
							eta_str = 'almost done'
						elif eta < 1:
							eta_str = '%02d sec. remaining' % int(int(float(eta) * 60.0))
						elif eta > 60:
							eta_str = '%s hr. %02d min. %02d sec. remaining' % (int(int(eta)/60), (float(int(int(eta)/60))-float(int((float(eta)/60.0)/100)*100)), int(60 * (float(eta) - float(int(eta)))))
						else:
							eta_str = '%s min. %02d sec. remaining' % (int(eta), int(60 * (float(eta) - float(int(eta)))))
							
						wtitle = '%s (%s) | %s | %s - %s | %s | %s - %s | %s | %s MB/s ~ %s MB/s ~ %s MB/s | %s | Subtitle:%s' % (longstringObjs['title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['status'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', str(longstringObjs['chunk_speed']), str(longstringObjs['avg_speed_curr']), str(longstringObjs['avg_speed']), str(eta_str), common.GetEmoji(type=has_sub, mode='simple', session=session))
						key = Callback(DownloadingFilesMenu, title=longstringObjs['title'], uid=longstringObjs['uid'], choice=None, session=session, status=status)
					elif status == common.DOWNLOAD_STATUS[2]: # Completed
						wtitle = '%s (%s) | %s | %s - %s | %s | %s - %s | %s | %s MB/s | Subtitle:%s' % (longstringObjs['title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['status'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', str(longstringObjs['avg_speed_curr']), common.GetEmoji(type=has_sub, mode='simple', session=session))
						key = Callback(DownloadingFilesMenu, title=longstringObjs['title'], uid=longstringObjs['uid'], choice=None, session=session, status=status)
					elif status == common.DOWNLOAD_STATUS[3]: # Failed
						err = longstringObjs['last_error'] if longstringObjs['error'] == '' else longstringObjs['error']
						wtitle = '%s (%s) | %s | %s - %s | %s | %s | %s - %s' % (longstringObjs['title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], str(longstringObjs['progress'])+'%', longstringObjs['status'], err)
						key = Callback(DownloadingFilesMenu, title=longstringObjs['title'], uid=longstringObjs['uid'], choice=None, session=session, status=status)
						summary = '%s | %s' % (wtitle, summary)
					elif status == common.DOWNLOAD_STATUS[4]: # Requested
						if 'user' in longstringObjs.keys() and longstringObjs['user'] != None and AuthTools.CheckAdmin() == True:
							wtitle = '%s (%s) | %s | %s - %s | %s | %s (by %s) - %s | %s | %s MB/s | Subtitle:%s' % (longstringObjs['title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['status'], longstringObjs['user'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', str(longstringObjs['avg_speed_curr']), common.GetEmoji(type=has_sub, mode='simple', session=session))
						else:
							wtitle = '%s (%s) | %s | %s - %s | %s | %s - %s | %s | %s MB/s | Subtitle:%s' % (longstringObjs['title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['status'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', str(longstringObjs['avg_speed_curr']), common.GetEmoji(type=has_sub, mode='simple', session=session))
						key = Callback(DownloadingFilesMenu, title=longstringObjs['title'], uid=longstringObjs['uid'], choice=None, session=session, status=status)
					elif status == common.DOWNLOAD_STATUS[5]: # All
						if longstringObjs['status'] == common.DOWNLOAD_STATUS[1]: # Downloading
							if each not in common.DOWNLOAD_STATS.keys() and len(common.DOWNLOAD_STATS.keys()) < int(Prefs['download_connections']):
								longstringObjs['status'] = common.DOWNLOAD_STATUS[1]
								longstringObjs['action'] = common.DOWNLOAD_ACTIONS[4]
								Dict[each] = E(JSON.StringFromObject(longstringObjs))
								
								EncTxt = E(JSON.StringFromObject(longstringObjs))
								Thread.Create(download.do_download, {}, file_meta_enc=EncTxt)
							elif each not in common.DOWNLOAD_STATS.keys():
								longstringObjs['status'] = common.DOWNLOAD_STATUS[0]
								longstringObjs['action'] = common.DOWNLOAD_ACTIONS[4]
								Dict[each] = E(JSON.StringFromObject(longstringObjs))
								doTrigger = True
							else:
								longstringObjs = common.DOWNLOAD_STATS[each]
								
							try:
								eta = float(longstringObjs['eta'])
							except:
								eta = '?'
								
							if eta == '?' or str(eta) == '0':
								eta_str = 'calculating time'
							elif eta < 0.1:
								eta_str = 'almost done'
							elif eta < 1:
								eta_str = '%02d sec. remaining' % int(int(float(eta) * 60.0))
							elif eta > 60:
								eta_str = '%s hr. %02d min. %02d sec. remaining' % (int(int(eta)/60), (float(int(int(eta)/60))-float(int((float(eta)/60.0)/100)*100)), int(60 * (float(eta) - float(int(eta)))))
							else:
								eta_str = '%s min. %02d sec. remaining' % (int(eta), int(60 * (float(eta) - float(int(eta)))))
								
							wtitle = '%s (%s) | %s | %s - %s | %s | %s - %s | %s | %s MB/s ~ %s MB/s ~ %s MB/s | %s | Subtitle:%s' % (longstringObjs['title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['status'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', str(longstringObjs['chunk_speed']), str(longstringObjs['avg_speed_curr']), str(longstringObjs['avg_speed']), str(eta_str), common.GetEmoji(type=has_sub, mode='simple', session=session))
						else:
							wtitle = '%s (%s) | %s | %s - %s | %s | %s - %s | %s | %s MB/s | Subtitle:%s' % (longstringObjs['title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['status'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', str(longstringObjs['avg_speed_curr']), common.GetEmoji(type=has_sub, mode='simple', session=session))
							
						key = Callback(DownloadingFilesMenu, title=longstringObjs['title'], uid=longstringObjs['uid'], choice=None, session=session, status=longstringObjs['status'])
						
					oc.add(DirectoryObject(
						title = wtitle,
						key = key,
						thumb = GetThumb(longstringObjs['thumb'], session=session),
						tagline = timestr,
						summary = summary
						)
					)
			except Exception as e:
				Log("==============Downloads==============")
				#Log(longstringObjs)
				Log(e)
				#Log(common.DOWNLOAD_STATS)
				items_to_del.append(each)
				
	if len(items_to_del) > 0:
		for each in items_to_del:
			longstringObjs = JSON.ObjectFromString(D(Dict[each]))
			if 'temp_file' in longstringObjs:
				filepath = longstringObjs['temp_file']
				try:
					Core.storage.remove_data_item(filepath)
				except Exception as e:
					Log("=============ClearDownLoadSection Error============")
					Log(e)
			del Dict[each]
		Dict.Save()
		
	if doTrigger == True:
		Thread.Create(download.trigger_que_run)

	if len(oc) == 0:
		return MC.message_container(title, 'No %s section videos available' % status)
			
	oc.objects.sort(key=lambda obj: obj.tagline, reverse=True)
		
	if status != None:
		if status == common.DOWNLOAD_STATUS[3]:
			oc.add(DirectoryObject(
				title = 'Retry All Downloads',
				key = Callback(RetryFailedDownloads, session=session),
				summary = 'Retry Failed Downloads',
				thumb = GetThumb(R(ICON_REFRESH), session=session)
				)
			)
		elif status == common.DOWNLOAD_STATUS[1]:
			oc.add(DirectoryObject(
				title = 'Pause %s Downloads' % status,
				key = Callback(PauseDownloadingDownloads, session=session),
				summary = 'Pause %s Download Entries' % status,
				thumb = GetThumb(R(ICON_ENTER), session=session)
				)
			)
			oc.add(DirectoryObject(
				title = 'Postpone %s Downloads' % status,
				key = Callback(PostponeDownloadingDownloads, session=session),
				summary = 'Postpone %s Download Entries' % status,
				thumb = GetThumb(R(ICON_ENTER), session=session)
				)
			)
		oc.add(DirectoryObject(
			title = 'Refresh %s Downloads' % status,
			key = Callback(Downloads,title="%s Downloads" % status, status=status, session=session, refresh=int(refresh)+1),
			summary = 'Refresh %s Download Entries' % status,
			thumb = GetThumb(R(ICON_REFRESH), session=session)
			)
		)
		oc.add(DirectoryObject(
			title = 'Clear %s Downloads' % status,
			key = Callback(ClearDownLoadSection, status=status, session=session),
			summary = 'Remove %s Download Entries' % status,
			thumb = GetThumb(R(ICON_NOTOK), session=session)
			)
		)
		
	#oc.objects.sort(key=lambda obj: obj.title, reverse=False)
		
	return oc
	
######################################################################################
@route(PREFIX + "/DownloadingFilesMenu")
def DownloadingFilesMenu(title, uid, choice=None, session=None, status=None, confirm=False, refresh=0):
	
	oc = ObjectContainer(title1=title, no_cache=common.isForceNoCache())
	
	if choice == None and uid in Dict:
		try:
			longstringObjs = JSON.ObjectFromString(D(Dict[uid]))
			#status = longstringObjs['status']
			fileinfo = longstringObjs
			
			if status == common.DOWNLOAD_STATUS[1]:
				if uid in common.DOWNLOAD_STATS.keys():
					fileinfo = common.DOWNLOAD_STATS[uid]
				else:
					pass #fileinfo = Dict[uid]
				try:
					eta = float(fileinfo['eta'])
				except:
					eta = '?'
					
				if eta == '?' or str(eta) == '0':
					eta_str = 'calculating time'
				elif eta < 0.1:
					eta_str = 'almost done'
				elif eta < 1:
					eta_str = '%02d sec. remaining' % int(int(float(eta) * 60.0))
				elif eta > 60:
					eta_str = '%s hr. %02d min. %02d sec. remaining' % (int(int(eta)/60), (float(int(int(eta)/60))-float(int((float(eta)/60.0)/100)*100)), int(60 * (float(eta) - float(int(eta)))))
				else:
					eta_str = '%s min. %02d sec. remaining' % (int(eta), int(60 * (float(eta) - float(int(eta)))))
				
				i_title = '%s | %s | %s MB/s ~ %s MB/s ~ %s MB/s | %s - %s | %s' % (str(fileinfo['progress'])+'%', eta_str, str(fileinfo['chunk_speed']), str(fileinfo['avg_speed_curr']), str(fileinfo['avg_speed']), fileinfo['fs'], fileinfo['quality'], common.DOWNLOAD_ACTIONS_K[fileinfo['action']])
			else:
				i_title = '%s | %s MB/s ~ %s MB/s ~ %s MB/s | %s - %s | %s' % (str(fileinfo['progress'])+'%', str(fileinfo['chunk_speed']), str(fileinfo['avg_speed_curr']), str(fileinfo['avg_speed']), fileinfo['fs'], fileinfo['quality'], common.DOWNLOAD_ACTIONS_K[fileinfo['action']])
			i_title = unicode(i_title)
			oc.add(DirectoryObject(
				title = i_title,
				summary = i_title,
				key = Callback(MyMessage, title='Info', msg=i_title),
				thumb = GetThumb(R(ICON_ENTER), session=session)
				)
			)
			
			c = 0
			for opt in common.DOWNLOAD_ACTIONS:
				if (status == common.DOWNLOAD_STATUS[0] and opt in [common.DOWNLOAD_ACTIONS[0], common.DOWNLOAD_ACTIONS[3], common.DOWNLOAD_ACTIONS[4]]) or (status == common.DOWNLOAD_STATUS[1] and opt in [common.DOWNLOAD_ACTIONS[0], common.DOWNLOAD_ACTIONS[1], common.DOWNLOAD_ACTIONS[2], common.DOWNLOAD_ACTIONS[3]]) or (status == common.DOWNLOAD_STATUS[3] and opt in [common.DOWNLOAD_ACTIONS[0], common.DOWNLOAD_ACTIONS[4]]) or (status == common.DOWNLOAD_STATUS[4] and opt in [common.DOWNLOAD_ACTIONS[0], common.DOWNLOAD_ACTIONS[4]]):
					if longstringObjs['action'] != opt and not (opt == common.DOWNLOAD_ACTIONS[2] and longstringObjs['action'] == common.DOWNLOAD_ACTIONS[4]) or status == common.DOWNLOAD_STATUS[3] and not(status == common.DOWNLOAD_STATUS[1] and longstringObjs['action'] in [common.DOWNLOAD_ACTIONS[2], common.DOWNLOAD_ACTIONS[4]]):
						opt_txt = opt
						if opt == common.DOWNLOAD_ACTIONS[3] or (opt == common.DOWNLOAD_ACTIONS[4] and longstringObjs['progress'] != '?' and float(longstringObjs['progress']) > 0):
							postpone_subtext = '(resumable download)' if longstringObjs['resumable']==True else '(non-resumable download)'
							opt_txt = '%s %s' % (opt,postpone_subtext) 
						oc.add(DirectoryObject(
							title = opt_txt,
							summary = common.DOWNLOAD_ACTIONS_INFO[c],
							key = Callback(DownloadingFilesMenu, title=title, uid=uid, choice=opt, session=session, status=status),
							thumb = GetThumb(R(ICON_ENTER), session=session)
							)
						)
				c += 1
			if longstringObjs['section_key'] == None:
				oc.add(DirectoryObject(
					title = 'Set Download Location',
					summary = '%s | Download path: %s' % (longstringObjs['section_title'], longstringObjs['section_path']),
					key = Callback(SetReqDownloadLocation, uid=longstringObjs['uid'], type=longstringObjs['type']),
					thumb = GetThumb(R(ICON_ENTER), session=session)
					)
				)
			else:
				oc.add(DirectoryObject(
					title = '%s | Download path: %s' % (longstringObjs['section_title'], longstringObjs['section_path']),
					summary = '%s | Download path: %s' % (longstringObjs['section_title'], longstringObjs['section_path']),
					key = Callback(MyMessage, title='Download Path', msg=longstringObjs['section_path']),
					thumb = GetThumb(R(ICON_ENTER), session=session)
					)
				)
			if longstringObjs['purl'] != None:
				oc.add(DirectoryObject(
					title = 'Video Page (Other Download Sources)',
					summary = 'Video Page: %s' % longstringObjs['title'],
					key = Callback(EpisodeDetail, title=longstringObjs['title'], url=longstringObjs['purl'], thumb=longstringObjs['thumb'], session = session),
					thumb = GetThumb(R(ICON_ENTER), session=session)
					)
				)
			else:
				oc.add(DirectoryObject(
					title = 'Video Page (Unavailable)',
					summary = 'Video Page: %s' % longstringObjs['title'],
					key = Callback(MyMessage, title='Video Page', msg='This Video Page is Unavailable'),
					thumb = GetThumb(R(ICON_ENTER), session=session)
					)
				)
			if status == common.DOWNLOAD_STATUS[2]:
				oc.add(DirectoryObject(
					title = 'Clear',
					key = Callback(DownloadingFilesMenu, title=longstringObjs['title'], uid=uid, choice=common.DOWNLOAD_ACTIONS[0], session=session, status=status),
					summary = 'Clear %s' % longstringObjs['title'],
					thumb = GetThumb(R(ICON_ENTER), session=session)
					)
				)
			oc.add(DirectoryObject(
				title = 'Refresh',
				key = Callback(DownloadingFilesMenu, title=title, uid=uid, choice=choice, session=session, status=status, confirm=confirm, refresh=int(refresh)+1),
				summary = 'Refresh Stats for %s' % longstringObjs['title'],
				thumb = GetThumb(R(ICON_REFRESH), session=session)
				)
			)
		except Exception as e:
			Log(e)
			return MC.message_container('Unavailable', 'Item removed or no longer available')

		return oc
		
	else:
		if AuthTools.CheckAdmin() == False:
			return MC.message_container('Admin Access Only', 'Only the Admin can perform this action !')
		
		if uid in Dict and choice != None:
			if choice == common.DOWNLOAD_ACTIONS[0] and confirm == False:
				oc = ObjectContainer(title1=unicode('Confirm ?'), no_cache=common.isForceNoCache())
				oc.add(DirectoryObject(title = 'YES - Clear %s Entry' % title, key = Callback(DownloadingFilesMenu, title=title, uid=uid, choice=choice, session=session, status=status, confirm=True), thumb = R(ICON_OK)))
				oc.add(DirectoryObject(title = 'NO - Dont Clear %s Entry' % title, key = Callback(MyMessage, title='No Selected', msg='Return to previous screen'),thumb = R(ICON_NOTOK)))
				return oc
			
			longstringObjs = JSON.ObjectFromString(D(Dict[uid]))
			longstringObjs['action'] = choice
			status = longstringObjs['status']
			doTrigger = True
				
			if status == common.DOWNLOAD_STATUS[0]: # Queued
				if choice == common.DOWNLOAD_ACTIONS[0]:
					if 'temp_file' in longstringObjs:
						filepath = longstringObjs['temp_file']
						try:
							Core.storage.remove_data_item(filepath)
						except Exception as e:
							Log("=============ClearDownLoadSection Error============")
							Log(e)
					del Dict[uid]
				elif choice == common.DOWNLOAD_ACTIONS[4]:
					longstringObjs['timeAdded'] = time.time()
					#doTrigger = True
					EncTxt = E(JSON.StringFromObject(longstringObjs))
					Dict[uid] = EncTxt	
			elif status == common.DOWNLOAD_STATUS[1]: # Downloading
				uid = longstringObjs['uid']
				if uid in common.DOWNLOAD_STATS.keys():
					EncTxt = E(JSON.StringFromObject(longstringObjs))
					Dict[uid] = EncTxt
				else:
					if uid in Dict.keys():
						del Dict[uid]
					if uid in common.DOWNLOAD_TEMP.keys():
						del common.DOWNLOAD_TEMP[uid]
					try:
						DOWNLOAD_TEMP = Dict['DOWNLOAD_TEMP']
						DOWNLOAD_TEMP = JSON.ObjectFromString(D(DOWNLOAD_TEMP))
						if uid in DOWNLOAD_TEMP.keys():
							del DOWNLOAD_TEMP[uid]
							Dict['DOWNLOAD_TEMP'] = E(JSON.StringFromObject(DOWNLOAD_TEMP))
					except:
						pass
			elif status == common.DOWNLOAD_STATUS[2]: # Completed
				uid = longstringObjs['uid']
				if choice == common.DOWNLOAD_ACTIONS[0]:
					del Dict[uid]
			elif status == common.DOWNLOAD_STATUS[3]: # Failed
				#doTrigger = True
				if choice in [common.DOWNLOAD_ACTIONS[2], common.DOWNLOAD_ACTIONS[4]]:
					longstringObjs['status'] = common.DOWNLOAD_STATUS[0]
					EncTxt = E(JSON.StringFromObject(longstringObjs))
					Dict[uid] = EncTxt
				elif choice == common.DOWNLOAD_ACTIONS[3]:
					longstringObjs['status'] = common.DOWNLOAD_STATUS[0]
					longstringObjs['timeAdded'] = time.time() + float(60*60*2)
					EncTxt = E(JSON.StringFromObject(longstringObjs))
					Dict[uid] = EncTxt
				elif choice == common.DOWNLOAD_ACTIONS[0]:
					if 'temp_file' in longstringObjs:
						filepath = longstringObjs['temp_file']
						try:
							Core.storage.remove_data_item(filepath)
						except Exception as e:
							Log("=============ClearDownLoadSection Error============")
							Log(e)
					del Dict[uid]
			elif status == common.DOWNLOAD_STATUS[4]: # Requested
				uid = longstringObjs['uid']
				if choice == common.DOWNLOAD_ACTIONS[0]:
					del Dict[uid]
				elif choice == common.DOWNLOAD_ACTIONS[4]:
					if longstringObjs['section_key'] == None:
						return MC.message_container('Define Location', 'Please define Download Location first !')
					longstringObjs['status'] = common.DOWNLOAD_STATUS[0]
					longstringObjs['timeAdded'] = time.time()
					EncTxt = E(JSON.StringFromObject(longstringObjs))
					Dict[uid] = EncTxt

			Dict.Save()
			
			if doTrigger == True:
				Thread.Create(download.trigger_que_run)
			
			time.sleep(2)
			
			if choice == common.DOWNLOAD_ACTIONS[3]:
				return MC.message_container('%s' % choice, '%s (by 2 hrs.) applied to %s' % (choice, title))
			return MC.message_container('%s' % choice, '%s applied to %s' % (choice, title))
		else:
			return MC.message_container('Unavailable', 'Item removed or no longer available')
	
######################################################################################
@route(PREFIX + "/SetReqDownloadLocation")
def SetReqDownloadLocation(uid, type):

	if AuthTools.CheckAdmin() == False:
		return MC.message_container('Admin Access Only', 'Only the Admin can perform this action !')
		
	oc = ObjectContainer(title1='Select Location', no_cache=common.isForceNoCache())
	
	DOWNLOAD_OPTIONS_SECTION_TEMP = {}
	for x in common.DOWNLOAD_OPTIONS.keys():
		DOWNLOAD_OPTIONS_SECTION_TEMP[x] = common.DOWNLOAD_OPTIONS[x]
	
	for item in DOWNLOAD_OPTIONS_SECTION_TEMP[type]:
		if item['enabled']:
			oc.add(DirectoryObject(
				key = Callback(SetReqDownloadLocationSave, uid=uid, section_title=item['title'], section_key=item['key'], section_path=item['path']),
				title = '%s | %s' % (item['title'], item['path'])
				)
			)

	if len(oc) == 0:
		return MC.message_container('Download Sources', 'No Download Location set under Download Options')
	return oc
	
######################################################################################
@route(PREFIX + "/SetReqDownloadLocationSave")
def SetReqDownloadLocationSave(uid, section_title, section_key, section_path):

	longstringObjs = JSON.ObjectFromString(D(Dict[uid]))
	longstringObjs['section_title'] = section_title
	longstringObjs['section_key'] = section_key
	longstringObjs['section_path'] = section_path
	EncTxt = E(JSON.StringFromObject(longstringObjs))
	Dict[uid] = EncTxt
	Dict.Save()
	return MC.message_container('Download Sources', 'Download Location has been set.')
	
######################################################################################
@route(PREFIX + "/ClearDownLoadSection")
def ClearDownLoadSection(status, session, confirm=False):

	if AuthTools.CheckAdmin() == False:
		return MC.message_container('Admin Access Only', 'Only the Admin can perform this action !')

	if confirm == False:
		oc = ObjectContainer(title1=unicode('Confirm ?'), no_cache=common.isForceNoCache())
		oc.add(DirectoryObject(title = 'YES - Clear %s Entries' % status, key = Callback(ClearDownLoadSection, status=status, session=session, confirm=True),thumb = R(ICON_OK)))
		oc.add(DirectoryObject(title = 'NO - Dont Clear %s Entries' % status, key = Callback(MyMessage, title='No Selected', msg='Return to previous screen'),thumb = R(ICON_NOTOK)))
		return oc

	items_to_del = []
	
	for each in Dict:
		if 'Down5Split' in each:
			try:
				longstringObjs = JSON.ObjectFromString(D(Dict[each]))
				if longstringObjs['status'] == status or status == common.DOWNLOAD_STATUS[5]:
					items_to_del.append(each)
				elif longstringObjs['status'] not in common.DOWNLOAD_STATUS:
					items_to_del.append(each)
			except Exception as e:
				Log("=============ClearDownLoadSection Error============")
				Log(e)
				
	if len(items_to_del) > 0:
		for each in items_to_del:
			if status == common.DOWNLOAD_STATUS[1]: # Downloading
				longstringObjs = JSON.ObjectFromString(D(Dict[each]))
				longstringObjs['action'] = common.DOWNLOAD_ACTIONS[0]
				uid = longstringObjs['uid']
				EncTxt = E(JSON.StringFromObject(longstringObjs))
				Dict[uid] = EncTxt
			elif status == common.DOWNLOAD_STATUS[3]: # Failed
				longstringObjs = JSON.ObjectFromString(D(Dict[each]))
				if 'temp_file' in longstringObjs:
					filepath = longstringObjs['temp_file']
					try:
						Core.storage.remove_data_item(filepath)
					except Exception as e:
						Log("=============ClearDownLoadSection Error============")
						Log(e)
				del Dict[each]
			elif status == common.DOWNLOAD_STATUS[5]: # All
				longstringObjs = JSON.ObjectFromString(D(Dict[each]))
				if longstringObjs['status'] == common.DOWNLOAD_STATUS[1]: # Downloading
					longstringObjs['action'] = common.DOWNLOAD_ACTIONS[0]
					uid = longstringObjs['uid']
					EncTxt = E(JSON.StringFromObject(longstringObjs))
					Dict[uid] = EncTxt
				elif longstringObjs['status'] == common.DOWNLOAD_STATUS[3]: # Failed
					if 'temp_file' in longstringObjs:
						filepath = longstringObjs['temp_file']
						try:
							Core.storage.remove_data_item(filepath)
						except Exception as e:
							Log("=============ClearDownLoadSection Error============")
							Log(e)
					del Dict[each]
				else:
					del Dict[each]
			else: # Queued, Completed
				del Dict[each]
		Dict.Save()
		
		if status == common.DOWNLOAD_STATUS[1]:
			time.sleep(7)

	return MC.message_container('Clear %s' % status, 'Download %s Videos Cleared' % status)

######################################################################################
@route(PREFIX + "/PauseDownloadingDownloads")
def PauseDownloadingDownloads(session):

	if AuthTools.CheckAdmin() == False:
		return MC.message_container('Admin Access Only', 'Only the Admin can perform this action !')

	for each in Dict:
		if 'Down5Split' in each:
			longstringObjs = JSON.ObjectFromString(D(Dict[each]))
			if longstringObjs['status'] == common.DOWNLOAD_STATUS[1]:
				uid = longstringObjs['uid']
				longstringObjs['action'] = common.DOWNLOAD_ACTIONS[1]
				EncTxt = E(JSON.StringFromObject(longstringObjs))
				Dict[uid] = EncTxt
	
	return MC.message_container('Pause Downloads', 'All Current Downloads have been Paused')
	
######################################################################################
@route(PREFIX + "/PostponeDownloadingDownloads")
def PostponeDownloadingDownloads(session):

	if AuthTools.CheckAdmin() == False:
		return MC.message_container('Admin Access Only', 'Only the Admin can perform this action !')

	for each in Dict:
		if 'Down5Split' in each:
			longstringObjs = JSON.ObjectFromString(D(Dict[each]))
			if longstringObjs['status'] == common.DOWNLOAD_STATUS[1]:
				uid = longstringObjs['uid']
				longstringObjs['action'] = common.DOWNLOAD_ACTIONS[3]
				EncTxt = E(JSON.StringFromObject(longstringObjs))
				Dict[uid] = EncTxt
	
	return MC.message_container('Postpone Downloads', 'All Current Downloads have been Postponed (by 2hrs.)')
	
######################################################################################
@route(PREFIX + "/RetryFailedDownloads")
def RetryFailedDownloads(session):

	if AuthTools.CheckAdmin() == False:
		return MC.message_container('Admin Access Only', 'Only the Admin can perform this action !')

	items_to_change = []
	
	for each in Dict:
		if 'Down5Split' in each:
			try:
				longstringObjs = JSON.ObjectFromString(D(Dict[each]))
				if longstringObjs['status'] == common.DOWNLOAD_STATUS[3]:
					items_to_change.append(each)
			except Exception as e:
				Log("============RetryFailedDownloads=============")
				Log(e)
				
	if len(items_to_change) > 0:
		for each in items_to_change:
			file_meta_enc = Dict[each]
			file_meta = JSON.ObjectFromString(D(file_meta_enc))
			
			file_meta['status'] = common.DOWNLOAD_STATUS[0]
			file_meta['action'] = common.DOWNLOAD_ACTIONS[4]
			
			Dict[each] = E(JSON.StringFromObject(file_meta))
			
		Dict.Save()
		Thread.Create(download.trigger_que_run)
		
		time.sleep(7)

	return MC.message_container('Retry Failed', 'Failed Videos have been added to Queue')
	
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
	
	if longstring != None and common.isArrayValueInString(common.EXT_SITE_URLS, longstring) == True:
		return True
	
	if longstring != None and url in longstring:
		return True

	surl = url.replace(fmovies_urlhost,'fmovies.to')
	longstring = Dict[title+'-'+E(surl)]
	if longstring != None and surl in longstring:
		return True
		
	surl = url.replace(fmovies_urlhost,'bmovies.to')
	longstring = Dict[title+'-'+E(surl)]
	if longstring != None and surl in longstring:
		return True
		
	surl = url.replace(fmovies_urlhost,'bmovies.online')
	longstring = Dict[title+'-'+E(surl)]
	if longstring != None and surl in longstring:
		return True
		
	surl = url.replace(fmovies_urlhost,'bmovies.club')
	longstring = Dict[title+'-'+E(surl)]
	if longstring != None and surl in longstring:
		return True
		
	surl = url.replace(fmovies_urlhost,'bmovies.ru')
	longstring = Dict[title+'-'+E(surl)]
	if longstring != None and surl in longstring:
		return True
		
	surl = url.replace(fmovies_urlhost,'bmovies.is')
	longstring = Dict[title+'-'+E(surl)]
	if longstring != None and surl in longstring:
		return True
		
	surl = url.replace(fmovies_urlhost,'bmovies.pro')
	longstring = Dict[title+'-'+E(surl)]
	if longstring != None and surl in longstring:
		return True
	
	surl = url.replace(fmovies_urlhost,'fmovies.se')
	longstring = Dict[title+'-'+E(surl)]
	if longstring != None and surl in longstring:
		return True
		
	surl = url.replace(fmovies_urlhost,'fmovies.is')
	longstring = Dict[title+'-'+E(surl)]
	if longstring != None and surl in longstring:
		return True
		
	surl = url.replace(fmovies_urlhost,'fmovies.is')
	longstring = Dict[title+'-'+E(surl)]
	if longstring != None and surl in longstring:
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
		del Dict[title+'-'+E(url.replace(fmovies_urlhost,'bmovies.to'))]
	except:
		pass
	try:
		del Dict[title+'-'+E(url.replace(fmovies_urlhost,'bmovies.online'))]
	except:
		pass
	try:
		del Dict[title+'-'+E(url.replace(fmovies_urlhost,'bmovies.club'))]
	except:
		pass
	try:
		del Dict[title+'-'+E(url.replace(fmovies_urlhost,'bmovies.ru'))]
	except:
		pass
	try:
		del Dict[title+'-'+E(url.replace(fmovies_urlhost,'bmovies.is'))]
	except:
		pass
	try:
		del Dict[title+'-'+E(url.replace(fmovies_urlhost,'bmovies.pro'))]
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
			if ('bmovies.' in url or 'fmovies.' in url) or common.isArrayValueInString(common.EXT_SITE_URLS, url) == True and 'http' in url and 'RR44SS' not in url:
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
			if (each.find('fmovies') != -1 or each.find('bmovies') != -1 or each.find(common.TITLE.lower()) != -1) and 'MyCustomSearch' in each:
				remove_list.append(each)
			elif common.isArrayValueInString(common.EXT_SITE_URLS, each) == True and 'MyCustomSearch' in each:
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
def Search(query=None, surl=None, page_count='1', mode='default', thumb=None, summary=None, is9anime='False', session=None, **kwargs):

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")

	last_page_no = page_count
	query2 = None
	
	if page_count=='1' and mode == 'default':
		Thread.Create(AnimeSearchExt,{},query,session)
	
	if surl != None:
		if mode == 'people' or mode == 'tag':
			url = surl + '?page=%s' % (str(page_count))
		else:
			url = surl + '&page=%s' % (str(page_count))
	else:
		if mode == 'default':
			timestr = str(int(time.time()))
			Dict[common.TITLE.lower() +'MyCustomSearch'+query] = query + 'MyCustomSearch' + timestr
			Dict.Save()
			url = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
		elif mode == 'other seasons':
			if is9anime == 'False':
				url = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?type=series&page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
			else:
				url = common.ANIME_URL + fmovies.SEARCH_PATH + '?type=series&page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
		else:
			url = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))

	page_data, error = common.GetPageElements(url=url, timeout=7)
	if page_data == None and mode == 'other seasons':
		url = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
		page_data, error = common.GetPageElements(url=url, timeout=7)
		
	elems = []
	errorB = False
	try:
		if is9anime == 'False':
			elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row movie-list']//div[@class='item']")
		else:
			elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row']//div[@class='item']")
		last_page_no = int(page_count)
		last_page_no = int(page_data.xpath(".//*[@id='body-wrapper']//ul[@class='pagination'][1]//li[last()-1]//text()")[0])
	except Exception as e:
		Log("__init.py__ > Search > Error: %s" % e)
		errorB = True
		pass
	no_elems = len(elems)
	
	if errorB==True and no_elems == 0 and mode == 'other seasons':
		if is9anime == 'False':
			xurl = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
		else:
			xurl = common.ANIME_URL + fmovies.SEARCH_PATH + '?page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
		page_data, error = common.GetPageElements(url=xurl, timeout=7)
		try:
			if is9anime == 'False':
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row movie-list']//div[@class='item']")
			else:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row']//div[@class='item']")
			last_page_no = int(page_count)
			last_page_no = int(page_data.xpath(".//*[@id='body-wrapper']//ul[@class='pagination'][1]//li[last()-1]//text()")[0])
			errorB = False
		except:
			errorB = True
			pass
		no_elems = len(elems)
		
	try:
		oc = ObjectContainer(title2 = 'Search Results for %s' % query, no_cache=common.isForceNoCache())

		if mode == 'default':
			oc = ObjectContainer(title2 = 'Search Results|Page ' + str(page_count) + ' of ' + str(last_page_no), no_cache=common.isForceNoCache())
		elif mode == 'tag':
			oc = ObjectContainer(title2 = 'Tag: ' + query, no_cache=common.isForceNoCache())
		elif mode == 'people':
			oc = ObjectContainer(title2 = 'People: ' + query, no_cache=common.isForceNoCache())
		else:
			oc = ObjectContainer(title2 = 'Other Seasons for ' + query, no_cache=common.isForceNoCache())
			
		if no_elems > 0:
			for elem in elems:
				name = elem.xpath(".//a[@class='name']//text()")[0]
				if is9anime == 'False':
					loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
				else:
					loc = elem.xpath(".//a[@class='name']//@href")[0]
				thumb_t = elem.xpath(".//a[@class='poster']//@src")[0]
				thumbx = thumb_t if 'url' not in thumb_t else thumb_t.split('url=')[1]
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
					key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumbx, session = session),
					title = name + title_eps_no,
					summary = GetMovieInfo(summary=summary, urlPath=more_info_link, referer=url, session=session) + eps_nos,
					thumb = Resource.ContentsOfURLWithFallback(url = thumbx, fallback=ICON_UNAV)
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
		
	oc_ext = []
	if Prefs['disable_extsources'] == False and common.interface.isInitialized() and page_count=='1' and mode == 'default':
		if common.SEARCH_EXT_SOURCES_FROM_SEARCH_MENU == True:
			try:
				oc_ext = SearchExt(query=query, query2=query2, append='true', session=session)
			except:
				pass
		else:
			oc_ext.append(DirectoryObject(
					key = Callback(SearchExt, query=query, session=session),
					title = 'Search in External Sources',
					summary = 'Search for a possible match in External Sources',
					thumb = R(ICON_SEARCH)
					)
				)
				
	if page_count=='1' and mode == 'default' and len(common.ANIME_SEARCH) > 0:
		for o in common.ANIME_SEARCH:
			try:
				oc.add(o)
			except:
				pass
				
	if page_count=='1' and mode == 'default' and len(oc_ext) > 0:
		for o in oc_ext:
			try:
				oc.add(o)
			except:
				pass
			
	if len(oc) == 0:
		try:
			error = page_data.xpath(".//*[@id='body-wrapper']//div[@class='alert alert-danger']//p[1]//text()")[0]
			error_msg = page_data.xpath(".//*[@id='body-wrapper']//div[@class='alert alert-danger']//p[3]//text()")[0]
			error = "Site Error: %s %s" % (error, error_msg)
		except:
			pass
			
		if error != '':
			return MC.message_container('Search Error', error)
	
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
				key = Callback(Search, query = query, session = session, surl = surl, page_count = str(int(page_count) + 1), mode=mode, is9anime=is9anime),
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
@route(PREFIX + "/AnimeSearchExt")
def AnimeSearchExt(query=None, session=None, **kwargs):

	del common.ANIME_SEARCH[:]
	
	url = common.ANIME_SEARCH_URL % String.Quote(query, usePlus=True)
	page_data, error = common.GetPageElements(url=url, timeout=7)
	
	if page_data != None:
		items = page_data.xpath("//*[@id='body-wrapper']//div[@class='item']")
		for i in items:
			try:
				thumb = i.xpath(".//@src")[0]
				title = i.xpath(".//a[@class='name']//text()")[0]
				url = i.xpath(".//@href")[0]
				summary = 'Available on item page.'
				dobj = DirectoryObject(
					key = Callback(EpisodeDetail, title=title, url=url, thumb=thumb, session=session, dataEXSAnim=url),
					title = '%s %s' % (common.EMOJI_ANIME, title),
					summary = summary,
					thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback=ICON_UNAV)
				)
				common.ANIME_SEARCH.append(dobj)
			except Exception as e:
				Log(e)
	
####################################################################################################
@route(PREFIX + "/SearchExt")
def SearchExt(query=None, query2=None, session=None, xtitle=None, xyear=None, xtype=None, ximdbid=None, xsummary=None, xthumb=None, xitem=None, append='false', final='false', **kwargs):

	if str(append).lower() == 'false' and str(final).lower() == 'false' and xtitle == None:
		oc = ObjectContainer(title2='Search In External Sources', no_cache=common.isForceNoCache())
	elif xtitle != None:
		oc = ObjectContainer(title2='%s (%s)' % (xtitle, xyear), no_cache=common.isForceNoCache())
		if xtype == 'movie':
			key = generatemoviekey(movtitle=xtitle, year=xyear, tvshowtitle=None, season=None, episode=None)
			if common.interface.getExtSourcesThreadStatus(key=key) == False:
				try:
					CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
				except:
					CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
					
				Thread.Create(common.interface.getExtSources, {}, movtitle=xtitle, year=xyear, tvshowtitle=None, season=None, episode=None, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY, ver=common.VERSION, session=session)
		else:
			xitem = None
	
		dobj = DirectoryObject(
			key = Callback(DoIMDBExtSources, title=xtitle, year=xyear, type=xtype, imdbid=ximdbid, summary=xsummary, item=xitem, thumb=xthumb, session=session), 
			title = '%s (%s) - Sources' % (xtitle, xyear),
			summary = xsummary,
			thumb = GetThumb(R(ICON_OTHERSOURCES), session=session))
		oc.add(dobj)
		
		if xtype == 'movie':
			if Prefs['disable_downloader'] == False and AuthTools.CheckAdmin() == True:
				dobj = DirectoryObject(
					key = Callback(DoIMDBExtSources, title=xtitle, year=xyear, type=xtype, imdbid=ximdbid, summary=xsummary, item=xitem, thumb=xthumb, session=session, extype='download'), 
					title = '%s (%s) - Download Sources' % (xtitle, xyear),
					summary = xsummary,
					thumb = GetThumb(R(ICON_OTHERSOURCESDOWNLOAD), session=session))
				oc.add(dobj)
			elif Prefs['disable_downloader'] == False:
				dobj = DirectoryObject(
					key = Callback(DoIMDBExtSources, title=xtitle, year=xyear, type=xtype, imdbid=ximdbid, summary=xsummary, item=xitem, thumb=xthumb, session=session, extype='download'), 
					title = '%s (%s) - Request Download' % (xtitle, xyear),
					summary = xsummary,
					thumb = GetThumb(R(ICON_REQUESTS), session=session))
				oc.add(dobj)
			
		oc.add(DirectoryObject(
			key = Callback(MainMenu),
			title = '<< Main Menu',
			thumb = R(ICON)
			)
		)
			
		return oc
		#else:
		#return MC.message_container('Search Results', 'No Videos Available in External Sources - Please refine your Search term')	
	else:
		oc = []

	try:
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
		
		extSearches = list(set(extSearches))
		
		for extS in extSearches:
			title, year = extS
			res = common.interface.searchOMDB(title, year, ver=common.VERSION)
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
			items = common.interface.searchOMDB(title, year, doSearch=True, ver=common.VERSION)
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
			
			summary = unicode(common.ascii_only(summary))
			
			xthumb = GetThumb(thumb, session=session)
			
			xitem = E(JSON.StringFromObject(item))
			
			if '–' in year:
				y = year.split('–')
				year = str(y[0]).strip()
			
			if str(final).lower() == 'true':
				if type == 'movie':
					key = generatemoviekey(movtitle=mtitle, year=year, tvshowtitle=tvtitle, season=season, episode=episode)
					if common.interface.getExtSourcesThreadStatus(key=key) == False:
						Thread.Create(common.interface.getExtSources, {}, movtitle=mtitle, year=year, tvshowtitle=tvtitle, season=season, episode=episode, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY, ver=common.VERSION, session=session)
				
				dobj = DirectoryObject(
					key = Callback(DoIMDBExtSources, title=title, year=year, type=type, imdbid=imdbid, summary=summary, thumb=xthumb, session=session), 
					title = common.EMOJI_EXT+watch_title,
					summary = summary,
					thumb = xthumb)
			else:
				dobj = DirectoryObject(
					key = Callback(SearchExt, query=query, query2=query2, session=session, xtitle=title, xyear=year, xtype=type, ximdbid=imdbid, xsummary=summary, xthumb=xthumb, xitem=xitem, append='false', final='false'), 
					title = common.EMOJI_EXT+watch_title,
					summary = summary,
					thumb = xthumb)
				
			if str(append).lower() == 'true':
				oc.append(dobj)
			else:
				oc.add(dobj)
				
	except Exception as e:
		Log.Exception("init.py>SearchExt() >> : >>> %s" % (e))
	
	if len(oc) == 0 and append == False:
		return MC.message_container('Search Results', 'No Videos Available in External Sources - Please refine your Search term')
	
	return oc
	
####################################################################################################
@route(PREFIX + "/DoIMDBExtSources")
def DoIMDBExtSources(title, year, type, imdbid, season=None, episode=None, episodeNr='1', summary=None, simpleSummary=False, thumb=None, item=None, session=None, final=False, extype='source', doSearch=None, **kwargs):

	if type == 'movie':
	
		if item == None or doSearch == None:
			res = common.interface.searchOMDB(title, year, ver=common.VERSION)
			try:
				item = json.loads(res.content)
			except:
				item = None
		else:
			item = JSON.ObjectFromString(D(item))
		
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
		
		summary = unicode(common.ascii_only(summary))

		if extype == 'source':
			return ExtSources(movtitle=title, year=year, title=title, url=None, summary=summary, thumb=thumb, art=None, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, season=season, episode=episode, session=session)
		else:
			if Prefs['disable_downloader'] == False and AuthTools.CheckAdmin() == True:
				return ExtSourcesDownload(movtitle=title, year=year, title=title, url=None, summary=summary, thumb=thumb, art=None, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, season=season, episode=episode, session=session, mode=common.DOWNLOAD_MODE[0])
			elif Prefs['disable_downloader'] == False:
				return ExtSourcesDownload(movtitle=title, year=year, title=title, url=None, summary=summary, thumb=thumb, art=None, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, season=season, episode=episode, session=session, mode=common.DOWNLOAD_MODE[1])
	else:
	
		if season != None:
			season = str(int(season))
		if episode != None:
			episode = str(int(episode))
	
		if season == None:
			oc = ObjectContainer(title2='%s (%s)' % (title, year), no_cache=common.isForceNoCache())
			try:
				res = common.interface.requestOMDB(t=title, y=year, Season=str(1), i=imdbid, ver=common.VERSION)
				SeasonNR = int(json.loads(res.content)['totalSeasons'])
				for i in range(1,SeasonNR+1):
					oc.add(DirectoryObject(key = Callback(DoIMDBExtSources, title=title, year=year, type=type, imdbid=imdbid, thumb=thumb, summary=summary, season=str(i), episode=None, session=session), 
						title = '*%s (Season %s)' % (title, str(i)),
						thumb = thumb))
				DumbKeyboard(PREFIX, oc, DoIMDBExtSourcesSeason, dktitle = 'Input Season No.', dkthumb=R(ICON_DK_ENABLE), dkNumOnly=True, dkHistory=False, title=title, year=year, type=type, imdbid=imdbid, thumb=thumb, summary=summary, session=session)
			except:
				DumbKeyboard(PREFIX, oc, DoIMDBExtSourcesSeason, dktitle = 'Input Season No.', dkthumb=R(ICON_DK_ENABLE), dkNumOnly=True, dkHistory=False, title=title, year=year, type=type, imdbid=imdbid, thumb=thumb, summary=summary, session=session)
	
		elif episode == None:
			oc = ObjectContainer(title2='%s (Season %s)' % (title, season), no_cache=common.isForceNoCache())
			
			try:
				CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
			except:
				CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
			
			x_title=title
			x_year=year
			x_season=season
			x_imdbid=imdbid
			x_thumb=thumb
			
			res = common.interface.getOMDB(title=x_title, year=x_year, season=x_season, episode=str(1), imdbid=x_imdbid, ver=common.VERSION)
			try:
				item = json.loads(json.dumps(res))
			except Exception as e:
				item = None
			
			genre = None
			rating = None
			duration = None
			
			if item!=None and len(item) > 0:
				try:
					genre = item['genre']
				except:
					genre = None
				try:
					rating = item['imdb_rating']
				except:
					rating = None
				try:
					duration = item['runtime'].replace('min','').strip()
				except:
					duration = None
			
			DumbKeyboard(PREFIX, oc, DoIMDBExtSourcesEpisode, dktitle = 'Input Episode No.', dkthumb=R(ICON_DK_ENABLE), dkNumOnly=True, dkHistory=False, title=title, year=year, type=type, imdbid=imdbid, thumb=thumb, season=season, summary=summary, session=session, genres=genre, rating=rating, runtime=duration)
			
			for e in range(int(episodeNr),1000):
				time.sleep(1.0)
				res = common.interface.getOMDB(title=x_title, year=x_year, season=x_season, episode=str(e), imdbid=x_imdbid, ver=common.VERSION)
				
				try:
					item = json.loads(json.dumps(res))
				except Exception as e:
					Log("init.py>DoIMDBExtSources() >> episode: >>> %s" % (e))
					item = None
				
				if item==None or len(item) == 0:
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
				title = common.EMOJI_EXT+watch_title,
				summary = summary,
				thumb = thumb))
				
				time.sleep(0.1)
				
				if int(episodeNr) + 9 == e:
					oc.add(DirectoryObject(
					key = Callback(DoIMDBExtSources, title=x_title, year=x_year, type=type, imdbid=x_imdbid, thumb=x_thumb, season=season, episodeNr=str(e+1), session=session), 
					title = 'Next Page >>',
					thumb = R(ICON_NEXT)))
					break
					
		elif final == False:
			try:
				CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
			except:
				CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
				
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
			
			watch_title = 'S%02dE%02d - %s' % (int(season), int(episode), title)
			if int(season) > 99 and int(episode) > 99:
				watch_title = 'S%03dE%03d - %s' % (int(season), int(episode), title)
			elif int(episode) > 99:
				watch_title = 'S%02dE%03d - %s' % (int(season), int(episode), title)
			
			oc = ObjectContainer(title2='%s (Season %s)' % (title, season), no_cache=common.isForceNoCache())
			
			oc.add(DirectoryObject(
				key = Callback(DoIMDBExtSources, title=title, year=year, type=type, imdbid=imdbid, item=E(JSON.StringFromObject(item)), season=season, episode=episode, session=session, final=True), 
				title = common.EMOJI_EXT+watch_title,
				summary = summary,
				thumb = thumb)
			)
			
			if Prefs['disable_downloader'] == False and AuthTools.CheckAdmin() == True:
				oc.add(DirectoryObject(
					key = Callback(ExtSourcesDownload, tvshowtitle=title, season=season, episode=episode, session=session, title=title, url=None, summary=summary, thumb=thumb, art=None, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, mode=common.DOWNLOAD_MODE[0]),
					title = 'Download Sources',
					summary = 'List sources of this episode by External Providers.',
					thumb = GetThumb(R(ICON_OTHERSOURCESDOWNLOAD), session=session)
					)
				)
			elif Prefs['disable_downloader'] == False:
				oc.add(DirectoryObject(
					key = Callback(ExtSourcesDownload, tvshowtitle=title, season=season, episode=episode, session=session, title=title, url=None, summary=summary, thumb=thumb, art=None, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, mode=common.DOWNLOAD_MODE[1]),
					title = 'Request Download',
					summary = 'List sources of this episode by External Providers.',
					art = art,
					thumb = GetThumb(R(ICON_REQUESTS), session=session)
					)
				)
		
			key = generatemoviekey(movtitle=None, year=year, tvshowtitle=title, season=season, episode=episode)
			if common.interface.getExtSourcesThreadStatus(key=key) == False:
				Thread.Create(common.interface.getExtSources, {}, movtitle=None, year=year, tvshowtitle=title, season=season, episode=episode, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY, ver=common.VERSION, session=session)
				
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
			
			if Prefs['disable_downloader'] == False and AuthTools.CheckAdmin() == True:
				return ExtSourcesDownload(tvshowtitle=title, year=year, title=title, url=None, summary=summary, thumb=thumb, art=None, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, season=season, episode=episode, session=session, mode=common.DOWNLOAD_MODE[0])
			elif Prefs['disable_downloader'] == False:
				return ExtSourcesDownload(tvshowtitle=title, year=year, title=title, url=None, summary=summary, thumb=thumb, art=None, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles, season=season, episode=episode, session=session, mode=common.DOWNLOAD_MODE[1])
			
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
def DoIMDBExtSourcesEpisode(query, title, year, type, imdbid, season, summary, thumb, session, genres=None, rating=None, runtime=None, **kwargs):

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
		Thread.Create(common.interface.getExtSources, {}, movtitle=None, year=year, tvshowtitle=title, season=season, episode=episode, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=CACHE_EXPIRY, ver=common.VERSION, session=session)
		
	item = {}
	item['poster'] = thumb
	item['plot'] = summary
	if runtime == None:
		item['runtime'] = 'Not Available'
	else:
		item['runtime'] = runtime
	if rating == None:
		item['imdb_rating'] = 'Not Available'
	else:
		item['imdb_rating'] = rating
	item['actors'] = 'Not Available'
	item['director'] = 'Not Available'
	if genres == None:
		item['genre'] = 'Not Available'
	else:
		item['genre'] = genres
	item['released'] = 'Not Available'
	
	oc = ObjectContainer(title2='%s (%s)' % (title, watch_title), no_cache=common.isForceNoCache())
	oc.add(DirectoryObject(
		key = Callback(DoIMDBExtSources, title=title, year=year, type=type, imdbid=imdbid, item=E(JSON.StringFromObject(item)), simpleSummary=True, season=season, episode=episode, session=session, final=True), 
		title = common.EMOJI_EXT+watch_title,
		summary =  '%s : %s' % (watch_title,summary),
		thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback = ICON_UNAV)))
		
	if Prefs['disable_downloader'] == False and AuthTools.CheckAdmin() == True:
		oc.add(DirectoryObject(
			key = Callback(ExtSourcesDownload, tvshowtitle=title, season=season, episode=episode, session=session, title=title, url=None, summary=summary, thumb=thumb, art=None, year=year, rating=item['imdb_rating'], genre=item['genre'], duration=item['runtime'], directors=item['director'], roles=item['actors'], mode=common.DOWNLOAD_MODE[0]),
			title = 'Download Sources',
			summary = 'List sources of this episode by External Providers.',
			thumb = GetThumb(R(ICON_OTHERSOURCESDOWNLOAD), session=session)
			)
		)
	elif Prefs['disable_downloader'] == False:
		oc.add(DirectoryObject(
			key = Callback(ExtSourcesDownload, tvshowtitle=title, season=season, episode=episode, session=session, title=title, url=None, summary=summary, thumb=thumb, art=None, year=year, rating=item['imdb_rating'], genre=item['genre'], duration=item['runtime'], directors=item['director'], roles=item['actors'], mode=common.DOWNLOAD_MODE[0]),
			title = 'Request Sources',
			summary = 'List sources of this episode by External Providers.',
			thumb = GetThumb(R(ICON_REQUESTS), session=session)
			)
		)
	
	return oc
	
####################################################################################################
@route(PREFIX + "/searchQueueMenu")
def SearchQueueMenu(title, session = None, **kwargs):

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")

	oc = ObjectContainer(title2='Search Using Term', no_cache=common.isForceNoCache())
	
	urls_list = []
	items_to_delete = []
	items_to_convert = []
	
	for each in Dict:
		query = Dict[each]
		try:
			if (each.find('fmovies') != -1 or each.find('bmovies') != -1 or each.find(common.TITLE.lower()) != -1) and 'MyCustomSearch' in each and query != 'removed':
				timestr = '1483228800'
				if 'MyCustomSearch' in query:
					split_query = query.split('MyCustomSearch')
					query = split_query[0]
					timestr = split_query[1]
					if (each.find('fmovies') != -1 or each.find('bmovies') != -1):
						items_to_delete.append(each)
						items_to_convert.append({'key': query, 'time': timestr})
					
				urls_list.append({'key': query, 'time': timestr})
				
			elif (each.find('fmovies') != -1 or each.find('bmovies') != -1 or each.find(common.TITLE.lower()) != -1) and 'MyCustomSearch' in each and query == 'removed':
				items_to_delete.append(each)
		except:
			pass
			
	if len(urls_list) == 0:
		return MC.message_container(title, 'No Items Available')
		
	if len(items_to_delete) > 0:
		for i in items_to_delete:
			Dict[i] = None
		for i in items_to_convert:
			query = i['key']
			timestr = i['time']
			Dict[common.TITLE.lower() +'MyCustomSearch'+query] = query + 'MyCustomSearch' + timestr
			
		Dict.Save()
		
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
		oc.add(DirectoryObject(key = Callback(Search, query = query, session = session, page_count='1'), title = query, tagline = timestr, thumb = R(ICON_SEARCH)))

	return oc
	
######################################################################################
@route(PREFIX + "/Help")
def Help():

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")

	oc = ObjectContainer(title2 = 'Help', no_cache=common.isForceNoCache())
	help_page_links, error = common.GetPageAsString(url=common.Help_Videos)
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
def FilterSetup(title, session, key1 = None, key2val = None, mode='add', update=True, **kwargs):

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")

	oc = ObjectContainer(title2 = title, no_cache=common.isForceNoCache())
	
	if len(Filter) == 0:
		# Initialize Filter Data
		FilterSetupData()
		
	if len(Filter) == 0:
		return MC.message_container("Filter Setup Error", "Sorry but the Filter could not be created !")
	#Log(Filter)
		
	if len(Filter_Search) == 0:
		# Set defaults for 'Sort' & 'Order'
		Filter_Search['sort'] = 'post_date'
		Filter_Search['order'] = 'desc'
	
	if key1 == None:
		for f_key in sorted(Filter):
			oc.add(DirectoryObject(
				key = Callback(FilterSetup, title = title, session = session, key1 = f_key),
				title = f_key.title()
				)
			)
	else:
		oc = ObjectContainer(title2 = title + ' (' + key1.title() + ')', no_cache=common.isForceNoCache())
		
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
					key = Callback(FilterSetup, title = title, session = session, key1 = key1, key2val = Filter[key1][f2_key], update = MakeSelections(key1=key1, key2val=key2val, mode='rem', k2v= Filter[key1][f2_key]), mode='rem'),
					title = key_title
					)
				)
			elif selected != '':
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title, session = session, key1 = key1, key2val = Filter[key1][f2_key], update = MakeSelections(key1=key1, key2val=key2val, mode='rem', k2v= Filter[key1][f2_key]), mode='rem'),
					title = key_title
					)
				)
			else:
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title, session = session, key1 = key1, key2val = Filter[key1][f2_key], update = MakeSelections(key1=key1, key2val=key2val, mode=mode, k2v=Filter[key1][f2_key])),
					title = key_title
					)
				)
		
		oc.add(DirectoryObject(
			key = Callback(FilterSetup, title = title, session = session, key1 = None, key2val = None, update = MakeSelections(key1=key1, key2val=key2val, mode=mode, k2v=key2val)),
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
		key = Callback(Search, surl=searchUrl, session = session),
		title = '<<< Submit Search >>>',
		summary = searchStringDesc
		)
	)
	
	oc.add(DirectoryObject(
		key = Callback(ClearFilter, session = session),
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
def ClearFilter(session, **kwargs):
	Filter_Search.clear()
	
	oc = ObjectContainer(title2 = "Filter Reset", no_cache=common.isForceNoCache())
	oc.add(DirectoryObject(
		key = Callback(FilterSetup, title=CAT_FILTERS[3], session=session),
		title = CAT_FILTERS[3]
		)
	)
	return oc

######################################################################################
@route(PREFIX + "/filtersetupdata-%s" % time.time())
def FilterSetupData(**kwargs):

	try:
		url = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?keyword=fmovies+%s' % time.time()
		page_data, error = common.GetPageElements(url=url)
		
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
@route(PREFIX + "/filterextsetup")
def FilterExtSetup(title, session, key1 = None, key2val = None, mode='add', update=True, **kwargs):

	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")

	oc = ObjectContainer(title2 = title, no_cache=common.isForceNoCache())
	
	if len(FilterExt_Search) == 0:
		# Set defaults for 'Sort' & 'Order'
		FilterExt_Search['sort'] = 'last added'
		FilterExt_Search['order'] = '-1'
		FilterExt_Search['type'] = 'movies'
	elif key1=='type' and key2val != None:
		FilterExt_Search['type'] = key2val
		
	if (key1==None and len(FilterExt.keys()) == 0) or key1=='type':
		FilterExtSetupData(seltype=FilterExt_Search['type'])
		if FilterExt_Search['type'] == 'animes':
			FilterExt_Search['sort'] = 'year'
		elif FilterExt_Search['type'] == 'movies':
			FilterExt_Search['sort'] = 'last added'
		elif FilterExt_Search['type'] == 'shows':
			FilterExt_Search['sort'] = 'updated'
		
	if len(FilterExt) == 0:
		return MC.message_container("Filter Setup Error", "Sorry but the Filter could not be created !")
	#Log(FilterExt)
		
	
	if key1 == None:
		for f_key in sorted(FilterExt):
			oc.add(DirectoryObject(
				key = Callback(FilterExtSetup, title = title, key1 = f_key, session = session),
				title = f_key.title()
				)
			)
	else:
		oc = ObjectContainer(title2 = title + ' (' + key1.title() + ')', no_cache=common.isForceNoCache())
		
		for f2_key in sorted(FilterExt[key1]):
		
			selected = ''
			# This indicates selected item
	
			if (key2val != None and key2val == FilterExt[key1][f2_key]):
				if (mode == 'add' or key1 == 'sort' or key1 == 'order' or key1 == 'type' or key1 == 'genre'):
					selected = ' ' + common.GetEmoji(type='pos', mode='simple', session=session)
			
			elif (key1 != 'sort' and key1 != 'order'  and key1 != 'type' and key1 != 'genre' and key1 in FilterExt_Search and FilterExt[key1][f2_key] in FilterExt_Search[key1]):
				selected = ' ' + common.GetEmoji(type='pos', mode='simple', session=session)
			
			elif (key2val == None and key1 in FilterExt_Search and FilterExt[key1][f2_key] in FilterExt_Search[key1]):
				selected = ' ' + common.GetEmoji(type='pos', mode='simple', session=session)
				
				
			key_title = f2_key.title() + selected
			if key1 == 'quality' or 'mode: and' in f2_key.lower(): # dont Camelcase quality values and Mode in Genre
				key_title = f2_key + selected
			
			if mode == 'rem' and selected != '':
				oc.add(DirectoryObject(
					key = Callback(FilterExtSetup, title = title, session = session, key1 = key1, key2val = FilterExt[key1][f2_key], update = MakeSelectionsExt(key1=key1, key2val=key2val, mode='rem', k2v= FilterExt[key1][f2_key]), mode='rem'),
					title = key_title
					)
				)
			elif selected != '':
				oc.add(DirectoryObject(
					key = Callback(FilterExtSetup, title = title, session = session, key1 = key1, key2val = FilterExt[key1][f2_key], update = MakeSelectionsExt(key1=key1, key2val=key2val, mode='rem', k2v= FilterExt[key1][f2_key]), mode='rem'),
					title = key_title
					)
				)
			else:
				oc.add(DirectoryObject(
					key = Callback(FilterExtSetup, title = title, session = session, key1 = key1, key2val = FilterExt[key1][f2_key], update = MakeSelectionsExt(key1=key1, key2val=key2val, mode=mode, k2v=FilterExt[key1][f2_key])),
					title = key_title
					)
				)
		
		oc.add(DirectoryObject(
			key = Callback(FilterExtSetup, title = title, session = session, key1 = None, key2val = None, update = MakeSelectionsExt(key1=key1, key2val=key2val, mode=mode, k2v=key2val)),
			title = 'Continue Filter Setup >>'
			)
		)
		
	# Build search string
	searchStringDesc = ('Listing %s using ' + common.GetKeyFromVal(FilterExt['sort'],FilterExt_Search['sort']) + ' in ' + common.GetKeyFromVal(FilterExt['order'],FilterExt_Search['order']) + ' order.') % FilterExt_Search['type'].title()
	
	for k1 in FilterExt_Search:
		if k1 != 'sort' and k1 != 'order' and k1 != 'type':
			if k1 == 'genre':
				if 'genre' in FilterExt_Search:
					searchStringDesc += (' Filter ' + k1.title() + ' has %s.') % FilterExt_Search['genre'].title()
				else:
					searchStringDesc += ' Filter ' + k1.title() + ' has ALL genres.'
					
	filter_genre = 'All'
	if 'genre' in FilterExt_Search.keys():
		filter_genre = common.GetKeyFromVal(FilterExt['genre'],FilterExt_Search['genre'])

	oc.add(DirectoryObject(
		key = Callback(ShowCategoryES, title='External Listing', filter=E(JSON.StringFromObject(FilterExt_Search)), session = session),
		title = '%s > %s > %s > %s >' % (common.GetKeyFromVal(FilterExt['type'],FilterExt_Search['type']), common.GetKeyFromVal(FilterExt['sort'],FilterExt_Search['sort']), filter_genre, common.GetKeyFromVal(FilterExt['order'],FilterExt_Search['order'])),
		summary = searchStringDesc
		)
	)
	
	oc.add(DirectoryObject(
		key = Callback(ClearFilterExt, session = session),
		title = 'Reset Listing Filter'
		)
	)
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu'
		)
	)
	
	return oc
	
######################################################################################
@route(PREFIX + "/makeselectionsext")
def MakeSelectionsExt(key1, key2val, mode, k2v, **kwargs):
	
	if k2v != key2val or key1 == None or key2val == None:
		return False
	
	# Update FilterExt_Search based on previous selection
	# ToDo: This will deselect
	if (key1 != 'genre' and key1 != 'type' and key1 != 'sort' and key1 != 'order' and key1 != None and key2val != None and key1 in FilterExt_Search and key2val in FilterExt_Search[key1] and mode == 'rem'):
		FilterExt_Search[key1].remove(key2val)
		if len(FilterExt_Search[key1]) == 0:
			del FilterExt_Search[key1]
	
	# This indicates selected item
	elif (key1 != None and key2val != None and (key1 not in FilterExt_Search or key2val not in FilterExt_Search[key1]) and mode == 'add'):
		if key1 != None and key2val != None:
			if key1 == 'type' or key1 == 'sort' or key1 == 'order' or key1 == 'genre':
				FilterExt_Search[key1] = key2val
			else:
				if key1 not in FilterExt_Search:
					FilterExt_Search[key1] = []
				if key2val not in FilterExt_Search[key1]:
					FilterExt_Search[key1].append(key2val)
		
	return True

######################################################################################
@route(PREFIX + "/clearfilterext")
def ClearFilterExt(session, **kwargs):

	FilterExt_Search.clear()
	FilterExt.clear()
	
	oc = ObjectContainer(title2 = "Filter Reset", no_cache=common.isForceNoCache())
	oc.add(DirectoryObject(
		key = Callback(FilterExtSetup, title=CAT_FILTERS[3], session = session),
		title = CAT_FILTERS[3]
		)
	)
	return oc

######################################################################################
@route(PREFIX + "/filterextsetupdata-%s" % time.time())
def FilterExtSetupData(seltype, **kwargs):

	try:
		FilterExt['sort']={}
		Filter_sort={'movies':{'Trending':'trending', 'Last Added':'last added', 'Rating':'rating', 'Title':'title','Year':'year'},'shows':{'Trending':'trending', 'Updated':'updated', 'Rating':'rating', 'Title':'name', 'Year':'year'},'animes':{'Year':'year', 'Rating':'rating', 'Title':'name'}}
		FilterExt['order']={'Ascending':'+1', 'Descending':'-1'}
		FilterExt['genre']={}
		Filter_genre={'movies': ['action','adventure','animation','comedy','crime','disaster','documentary','drama','eastern','family','fan-film','fantasy','film-noir','history','holiday','horror','indie','music','mystery','none','road','romance','science-fiction','short','sports','sporting-event','suspense','thriller','tv-movie','war','western'],
			'shows': ['action','adventure','animation','comedy','crime','disaster','documentary','drama','eastern','family','fan-film','fantasy','film-noir','history','holiday','horror','indie','music','mystery','none','road','romance','science-fiction','short','sports','sporting-event','suspense','thriller','tv-movie','war','western'],
			'animes': ['Action','Ecchi','Harem','Romance','School','Supernatural','Drama','Comedy','Mystery','Police','Sports','Mecha','Sci-Fi','Slice of Life','Fantasy','Adventure','Gore','Music','Psychological','Shoujo Ai','Yuri','Magic','Horror','Thriller','Gender Bender','Parody','Historical','Racing','Demons','Samurai','Super Power','Military','Dementia','Mahou Shounen','Game','Martial Arts','Vampire','Kids','Mahou Shoujo','Space','Shounen Ai']
		}
		#FilterExt['country']={}
		FilterExt['type']={'Movies':'movies', 'Shows':'shows', 'Animes':'animes'}
		#FilterExt['release']={}
			
		# Get Genre info
		FilterExt['genre'] = {}
		if 'genre' in FilterExt_Search.keys():
			del FilterExt_Search['genre']
		for i in range(0, len(Filter_genre[seltype])):
			genre = Filter_genre[seltype][i]
			FilterExt['genre'][genre.title()] = genre
			
		# Get Sort info
		FilterExt['sort'] = {}
		if 'sort' in FilterExt_Search.keys():
			del FilterExt_Search['sort']
		FilterExt['sort'] = Filter_sort[seltype]
			
	except Exception as e:
		Log.Exception("init.py>FilterExtSetupData() >> : >>> %s" % (e))
		# Empty partial Filter if failed - error will be reported when using Filter
		FilterExt.clear()

######################################################################################
@route(PREFIX + "/showcategoryes")
def ShowCategoryES(title, filter=None, page_count='1', last_page_no=None, session=None, **kwargs):
	
	if filter != None:
		filter = JSON.ObjectFromString(D(filter))
		
		#Log(filter)
		
		if 'genre' in filter.keys():
			genre = filter['genre']
		else:
			genre = 'ALL'
		searchString = '%s/%s?sort=%s&order=%s&genre=%s' % (filter['type'], page_count, filter['sort'], filter['order'], genre)
		
		# Build Filter-Search Url
		#http://movies-v2.api-fetch.website/movies/1?sort=trending&limit=50&year=2017&genre=Comedy&order=-1
		apiUrl = common.ES_API_URL + '/%s' % urllib2.quote(searchString, safe='%/_-+=&?')
		
		if last_page_no == None:
			pagesUrl = common.ES_API_URL + '/%s' % filter['type']
			pages_data, error = common.GetPageAsString(url=pagesUrl)
			#Log(pages_data)
			#Log(error)
			if error != '':
				return MC.message_container(title, error)
			
			last_page_no = len(json.loads(pages_data))
	else:
		return MC.message_container(title, 'Filter error')
		
	oc = ObjectContainer(title2 = title + '|Page %s of %s' % (str(page_count), str(last_page_no)) , no_cache=common.isForceNoCache())
	
	page_data, error = common.GetPageAsString(url=apiUrl)
	
	if error != '':
		return MC.message_container(title, error)
		
	page_data_json = json.loads(page_data)
		
		
	for elem in page_data_json:
		
		name = elem['title']
		try:
			thumb = elem['images']['poster']
		except:
			thumb = None
		try:
			art = elem['images']['fanart']
		except:
			art = None
		try:
			banner = elem['images']['banner']
		except:
			banner = None
		rating = elem['rating']['percentage']
		year = elem['year']
		genres = []
		summary = 'Plot Summary on Item Page'
		trailer = None
		runtime = None
		num_seasons = None
		cert = None
		
		if filter['type'] == 'animes':
			type = elem['type']
			type = 'anime'
			subtype = elem['type']
			num_seasons = elem['num_seasons']
			id = elem['_id']
			genres = elem['genres']
		elif filter['type'] == 'shows':
			type = filter['type'][0:-1]
			subtype = 'show'
			num_seasons = elem['num_seasons']
			id = elem['imdb_id']
		elif filter['type'] == 'movies':
			summary = elem['synopsis']
			genres = elem['genres']
			id = elem['imdb_id']
			runtime = elem['runtime']
			trailer = elem['trailer']
			cert = elem['certification']
			type = filter['type'][0:-1]
			subtype = 'movie'
			
		loc = common.ES_API_URL + '/%s/%s' % (type,id)
		
		data = {}
		data['title'] = name
		data['id'] = id
		data['thumb'] = thumb
		data['art'] = art
		data['banner'] = banner
		data['rating'] = float(rating)/10.0
		data['year'] = year
		data['summary'] = summary
		data['genres'] = genres
		data['type'] = type
		data['subtype'] = subtype
		data['trailer'] = trailer
		data['runtime'] = runtime
		data['num_seasons'] = num_seasons
		data['certification'] = cert
		data['itemurl'] = loc
		
		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb, dataEXS=E(JSON.StringFromObject(data)), session = session),
			title = "%s (%s)" % (name,year),
			summary = summary,
			art = art,
			thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON_UNAV)
			)
		)
		
	if int(page_count) < int(last_page_no):
		oc.add(NextPageObject(
			key = Callback(ShowCategoryES, title=title, filter=E(JSON.StringFromObject(filter)), page_count=str(int(page_count) + 1), last_page_no=last_page_no, session=session),
			title = "Next Page (" + str(int(page_count) + 1) +'/'+ str(last_page_no) + ") >>",
			thumb = R(ICON_NEXT)
			)
		)
		
	if common.UsingOption(key=common.DEVICE_OPTIONS[0], session=session):
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search, session = session), thumb = R(ICON_SEARCH), title='Search', summary='Search', prompt='Search for...'))

	if len(oc) == 1:
		return MC.message_container(title, 'No More Videos Available')
		
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu',
		thumb = R(ICON)
		)
	)
	
	return oc

################################################################################
@route(PREFIX + "/season_menuES")
def season_menuES(title, show_title, season_index, dataEXSJsonUrl, session):
	object_container = ObjectContainer(title2=title)

	json_data, error = common.GetPageAsString(url=dataEXSJsonUrl)
	if error != '':
		return MC.message_container(title, error)
	json_data = json.loads(json_data)
	
	#Log(json_data)
	#Log(json_data['episodes'])

	if json_data and 'episodes' in json_data:
		episodes = []

		try:
			thumb = json_data['images']['poster']
		except:
			thumb = None
		try:
			art = json_data['images']['fanart']
		except:
			art = None
			
		rating = json_data['rating']['percentage']
		
		runtime = json_data['runtime']
			
		genres0 = json_data['genres']
		try:
			genres = (','.join(str(x.title()) for x in genres0))
			if genres == '':
				genres = 'Not Available'
		except:
			genres = 'Not Available'

		eps = []
		for json_item in json_data['episodes']:
			if int(json_item['season']) == int(season_index):
				episode				= {}
				episode['title']	= u'{0}. {1}'.format(json_item['episode'], json_item['title'] if json_item['title'] != None else 'Title Unavailable')
				episode['summary']	= json_item['overview'] if json_item['overview'] != None else 'Summary Unavailable'
				episode['index']	= int(json_item['episode'])
				episodes.append(episode)
				eps.append(episode['index'])
				#Log(episode['title'])
		
		if len(eps) == 0:
			eps.append(20)
		
		if len(eps)-1 != max(eps):
			for i in range(1,max(eps)):
				if i not in eps:
					episode				= {}
					episode['title']	= u'{0}. {1}'.format(i, 'Title Unavailable')
					episode['summary']	= 'Summary Unavailable'
					episode['index']	= i
					episodes.append(episode)
					eps.append(episode['index'])

		episodes.sort(key=lambda episode: episode['index'])

		for episode in episodes:
			directory_object 			= DirectoryObject()
			directory_object.title		= unicode(episode['title'])
			directory_object.summary	= unicode(episode['summary'])
			directory_object.thumb		= Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON_UNAV)
			directory_object.art		= Resource.ContentsOfURLWithFallback(url=art, fallback=ART)
			#directory_object.key		= Callback(episode_menuES, show_title=show_title, season_index=season_index, episode_index=episode['index'], dataEXSJsonUrl=dataEXSJsonUrl, session=session)
			directory_object.key		= Callback(DoIMDBExtSourcesEpisode, query=episode['index'], title=json_data['title'], year=json_data['year'], type='show', imdbid=json_data['_id'], season=season_index, summary=episode['summary'], thumb=thumb, session=session, genres=genres, rating=rating, runtime=runtime)
			object_container.add(directory_object)

	return object_container

################################################################################
@route(PREFIX + "/episode_menuES")
def episode_menuES(show_title, season_index, episode_index, dataEXSJsonUrl, session):
	object_container = ObjectContainer()

	json_data, error = common.GetPageAsString(url=dataEXSJsonUrl)
	if error != '':
		return MC.message_container(title, error)
	json_data = json.loads(json_data)

	if json_data and 'episodes' in json_data:
		for json_item in json_data['episodes']:
			if int(json_item['season']) == int(season_index) and int(json_item['episode']) == int(episode_index):
				
				episode_object = EpisodeObject()
				episode_object.title   = json_item['title']
				episode_object.summary = json_item['overview']
				tvdb_id = json_item['tvdb_id']
				object_container.add(episode_object)

	return object_container

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
	
	RED_URL = None
	if fmovies.BASE_URL != Prefs["new_base_url"]:
		if common.CHECK_BASE_URL_REDIRECTION == True:
			RED_URL = common.client.request(fmovies.BASE_URL, output='geturl', timeout=7)
		if RED_URL != None and fmovies.BASE_URL not in RED_URL:
			Log("***Base URL has been overridden and set based on redirection: %s ***" % RED_URL)
			fmovies.BASE_URL = RED_URL
		else:
			fmovies.BASE_URL = Prefs["new_base_url"]
		del common.CACHE_COOKIE[:]
		HTTP.Headers['Referer'] = fmovies.BASE_URL
		common.BASE_URL = fmovies.BASE_URL
	
	try:
		common.CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
	except:
		common.CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
	
	if changed == True:
		DumpPrefs(changed=changed)
	
	ClearCache()
	# common.CACHE.clear()
	# common.CACHE_META.clear()
	# HTTP.ClearCache()
	
	common.set_control_settings()
	
	ValidateMyPrefs()
	
	if common.interface.isInitialized():
		download.resetDownloadThrottler()
		Thread.Create(download.trigger_que_run)
	
	return
	
######################################################################################
@route(PREFIX + "/DumpPrefs")
def DumpPrefs(changed=False, **kwargs):
	Log("=================FMoviesPlus Prefs=================")
	Log(common.TITLE + ' v. %s %s' % (common.VERSION, common.TAG))
	Log("Channel Preferences:")
	Log("Base site url: %s" % (fmovies.BASE_URL))
	Log("Cache Expiry Time (in mins.): %s" % (Prefs["cache_expiry_time"]))
	Log("No Extra Info. for Nav. Pages (Speeds Up Navigation): %s" % (Prefs["dont_fetch_more_info"]))
	Log("Use SSL Web-Proxy: %s" % (Prefs["use_web_proxy"]))
	Log("Use Alternate SSL/TLS: %s" % (Prefs["use_https_alt"]))
	Log("Disable External Sources: %s" % (Prefs["disable_extsources"]))
	Log("Disable Downloading Sources: %s" % (Prefs["disable_downloader"]))
	Log("Number of concurrent Download Threads: %s" % (Prefs["download_connections"]))
	Log("Limit Aggregate Download Speed (KB/s): %s" % (Prefs["download_speed_limit"]))
	Log("Use LinkChecker for Videos: %s" % (Prefs["use_linkchecker"]))
	Log("Use Openload: %s" % (Prefs["use_openload_pairing"]))
	Log("Use PhantomJS: %s" % (Prefs["use_phantomjs"]))
	Log("Auth Admin through Plex.tv: %s" % (Prefs["plextv"]))
	Log("Enable Debug Mode: %s" % (Prefs["use_debug"]))
	Log("=============================================")
	
	if changed == False:
		ValidatePrefs(changed=False)

######################################################################################
@route(PREFIX + "/ClientInfo")
def ClientInfo(session, **kwargs):

	if session != None:
		common.setPlexTVUser(session)

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
def DumpDeviceOptions(session, **kwargs):

	Log("=================FMoviesPlus Device Options=================")
	Log("Device Options:")
	
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

# ToDo
####################################################################################################
@route(PREFIX+'/videoplayback')
def CreateVideoObject(url, title, summary, thumb, params, duration, genres, videoUrl, videoRes, watch_title, include_container=False, **kwargs):

	videoUrl = videoUrl.decode('unicode_escape')
	
	if include_container:
		video = MovieObject(
			key = Callback(CreateVideoObject, url=url, title=title, summary=summary, thumb=thumb, params=params, duration=duration, genres=genres, videoUrl=videoUrl, videoRes=videoRes, watch_title=watch_title, include_container=True),
			rating_key = url + title,
			title = title,
			summary = summary,
			thumb = thumb,
			items = [
				MediaObject(
						container = Container.MP4,	 # MP4, MKV, MOV, AVI
						video_codec = VideoCodec.H264, # H264
						audio_codec = AudioCodec.AAC,  # ACC, MP3
						audio_channels = 2,			# 2, 6
						video_resolution = int(videoRes.replace('p','')),
						parts = [PartObject(key=Callback(PlayVideo,videoUrl=videoUrl, params=params, retResponse=include_container, url=url, title=title, summary=summary, thumb=thumb, watch_title=watch_title))],
						optimized_for_streaming = True
				)
			]
		)
	else:
		video = VideoClipObject(
			key = Callback(CreateVideoObject, url=url, title=title, summary=summary, thumb=thumb, params=params, duration=duration, genres=genres, videoUrl=videoUrl, videoRes=videoRes, watch_title=watch_title, include_container=True),
			rating_key = url + title,
			title = title,
			summary = summary,
			thumb = thumb,
			items = [
				MediaObject(
						container = Container.MP4,	 # MP4, MKV, MOV, AVI
						video_codec = VideoCodec.H264, # H264
						audio_codec = AudioCodec.AAC,  # ACC, MP3
						audio_channels = 2,			# 2, 6
						video_resolution = int(videoRes.replace('p','')),
						parts = [PartObject(key=Callback(PlayVideo,videoUrl=videoUrl, params=params, retResponse=include_container, url=url, title=title, summary=summary, thumb=thumb, watch_title=watch_title))],
						optimized_for_streaming = True
				)
			]
		)
  
	if include_container:
		return ObjectContainer(objects=[video])
	else:
		return video

####################################################################################################
@route(PREFIX+'/PlayVideo.mp4')
@indirect
def PlayVideo(videoUrl, params, retResponse, url, title, summary, thumb, watch_title, **kwargs):

	if 'googleusercontent.com' in videoUrl:
		pass
	elif common.client.geturlhost(videoUrl) in common.host_misc_resolvers.supported_hosts:
		videoUrl, params_enc, b = common.host_misc_resolvers.resolve(videoUrl, Prefs["use_https_alt"])
		#params = JSON.ObjectFromString(D(params_enc))
		params = params_enc
		if videoUrl != None:
			videoUrl = videoUrl[len(videoUrl)-1]['file']
	elif '.mp4' not in videoUrl and 'mime=video/mp4' not in videoUrl:
		page_data, error = common.GetPageAsString(url=videoUrl)
		reg_exs = [[r'\[{.*mp4.*}]',0],[r'{.*mp4.*}',0],[r'\({.*mp4.*?}\)',0]]
		for regex in reg_exs:	
			try:
				p = re.findall(regex[0], page_data)[regex[1]]
				if p[0:1] == '(' and p[-1:] == ')':
					p = p[1:-1]
				if '[' not in p[0:2]:
					st = "[" + p + "]"
				else:
					st = p
				st = st.replace('\'','"')
				Log("json1: %s" % st)
				try:
					links = json.loads(st)
					if 'sources' in p:
						links = links['sources']
				except:
					sta = []
					for parts in p.split(','):
						p1 = re.findall(r'[a-z].*?:', parts)[0][0:-1]
						sta.append(parts.replace(p1, "\""+p1+"\""))
					st = ','.join(str(x) for x in sta)
					st = st.replace('""','"')
					if '[' not in st[0:2]:
						st = "[" + st + "]"
					Log("json2: %s" % st)
					links = json.loads(st)
					if 'sources' in p:
						links = links['sources']
				Log("links: %s" % links)
				for link in links:
					if 'mp4' in link:
						Log("link: %s" % link)
						break
				if 'file:' in p:
					link = link['file']
				elif 'src:' in p:
					link = link['src']
				else:
					link = re.findall(r'http.*mp4', p)[0]
				pre = 'https://'
				if 'http://' in link:
					pre = 'http://'
				link = link.replace('https://','').replace('http://','').replace('https:','').replace('http:','').replace('//','')
				if 'http' not in link:
					link = pre + link
				videoUrl = link
				break
			except Exception as e:
				Log(e)
				pass

	http_headers = {'User-Agent': common.client.USER_AGENT}
	http_cookies = None
	
	if params != None:
		params = JSON.ObjectFromString(D(params))
		
		if params != '':
			if 'headers' in params.keys():
				headers = params['headers']
				if headers != None and headers != '':
					for key in headers.keys():
						http_headers[key] = headers[key]
						
			if 'cookie' in params.keys():
				cookie = params['cookie']
				if cookie != None and cookie != '':
					headers['Cookie'] = cookie
					http_cookies = cookie
					http_headers['Cookie'] = cookie

	#Log.Debug("Playback via Generic for URL: %s" % videoUrl)
	#Log("http_headers : %s" % http_headers)
	#Log("http_cookies : %s" % http_cookies)
	#Log(common.client.request(videoUrl, headers=http_headers, output='chunk')[0:20])
	
	if '.m3u8' in videoUrl:
		return IndirectResponse(VideoClipObject, key=HTTPLiveStreamURL(url=PlayAndAdd(url=url, title=title, summary=summary, thumb=thumb, videoUrl=videoUrl, watch_title=watch_title)), http_headers=http_headers, post_headers=http_headers, http_cookies=http_cookies)
	else:
		return IndirectResponse(VideoClipObject, key=PlayAndAdd(url=url, title=title, summary=summary, thumb=thumb, videoUrl=videoUrl, watch_title=watch_title), http_headers=http_headers, post_headers=http_headers, http_cookies=http_cookies)
	
####################################################################################################
@route(common.PREFIX+'/PlayAndAdd')
def PlayAndAdd(url, title, summary, thumb, videoUrl, watch_title, **kwargs):

	addfile = AddRecentWatchList(title=watch_title, url=url, summary=summary, thumb=thumb)
	
	return videoUrl
	
####################################################################################################
def SolveCaptcha(query, url, dlt, vco, title, page_url, **kwargs):

	try:
		resp = common.host_openload.SolveCaptcha(query, url, dlt)
	except Exception as e:
		if Prefs['use_debug']:
			Log("SolveCaptcha Error resp: %s" % e)
		resp = None
	
	if Prefs['use_debug']:
		Log("SolveCaptcha resp: %s" % resp)
	
	if resp == None:
		return MC.message_container('Captcha Unsolved', 'Captcha Not Solved. Incorrect response !')
	else:
		oc = ObjectContainer(title2 = title , no_cache=common.isForceNoCache())
		durl = vco.url
		durl = durl.replace('fmovies://','')
		durl = JSON.ObjectFromString(D(durl))
		durl['url'] = resp
		durl['title'] = title
		durl = "fmovies://" + E(JSON.StringFromObject(durl))
		vco.url = durl
		vco.title = title
		oc.add(vco)
		oc.add(DirectoryObject(key = Callback(MainMenu), title = '<< Main Menu',thumb = R(ICON)))
		return oc
		#return MC.message_container('Captcha Solved', 'Captcha Solved Successfully')
		
####################################################################################################
def create_photo_object(url, title, include_container=False, **kwargs):
	po = PhotoObject(
		key=Callback(create_photo_object, url=url, include_container=True),
		rating_key=url,
		source_title=title,
		title=title,
		thumb=url,
		items=[
			MediaObject(parts=[
				PartObject(key=url)
				])
			]
		)
	if include_container:
		return ObjectContainer(objects=[po])
	return po
	
####################################################################################################
@route(common.PREFIX+'/MyMessage')
def MyMessage(title, msg, **kwargs):	
	return MC.message_container(title,msg)