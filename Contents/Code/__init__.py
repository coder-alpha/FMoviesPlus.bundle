######################################################################################
#
#	FMovies.se by Coder Alpha
# 	https://github.com/coder-alpha/FMoviesPlus.bundle
#
######################################################################################

import main

TITLE = main.TITLE
PREFIX = main.PREFIX

######################################################################################

def Start():

	Thread.Create(main.SleepAndUpdateThread, {}, session='Generic')
	Thread.Create(main.SleepPersistAndUpdateCookie)
	
	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(main.common.ART)
	#DirectoryObject.thumb = R(common.ICON_LIST)
	DirectoryObject.art = R(main.common.ART)
	#VideoClipObject.thumb = R(common.ICON_UNAV)
	VideoClipObject.art = R(main.common.ART)
	
	main.common.CACHE.clear()
	main.common.CACHE_META.clear()
	HTTP.ClearCache()
	
	for x in main.CAT_WHATS_HOT_REGULAR:
		main.CAT_WHATS_HOT.append(x)
	for x in main.CAT_WHATS_HOT_ANIME:
		main.CAT_WHATS_HOT.append(x)
	
	try:
		main.CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
	except:
		main.CACHE_EXPIRY = main.common.CACHE_EXPIRY_TIME
		
	HTTP.CacheTime = main.CACHE_EXPIRY
	Log.Debug("HTTP Cache Time set to %s min." % int(main.CACHE_EXPIRY/60))
	
	HTTP.Headers['User-Agent'] = main.common.client.randomagent()
	main.fmovies.BASE_URL = Prefs["new_base_url"]
	RED_URL = None
	if main.common.CHECK_BASE_URL_REDIRECTION == True:
		try:
			RED_URL = main.common.client.getRedirectingUrl(main.fmovies.BASE_URL).strip("/")
			if RED_URL != None and 'http' in RED_URL and main.fmovies.BASE_URL != RED_URL:
				Log("***Base URL has been overridden and set based on redirection: %s ***" % RED_URL)
				main.fmovies.BASE_URL = RED_URL
		except Exception as e:
			Log("Error in geturl : %s ; Red. Resp: %s" % (e, RED_URL))
	HTTP.Headers['Referer'] = main.fmovies.BASE_URL
	main.common.BASE_URL = main.fmovies.BASE_URL
	
	main.DumpPrefs()
	main.ValidateMyPrefs()
	
	# convert old style bookmarks to new
	if main.common.DEV_BM_CONVERSION and len(main.CONVERT_BMS) == 0:
		main.convertbookmarks()

######################################################################################
# Menu hierarchy
@route(PREFIX + "/MainMenu")
def MainMenu(**kwargs):
	
	return main.Main()
	
####################################################################################################
# ValidatePrefs
####################################################################################################
@route(PREFIX + "/ValidatePrefs")
def ValidatePrefs():

	return main.ValidatePrefs2()