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
	
	#Thread.Create(Initialize)
	

######################################################################################
# Menu hierarchy
######################################################################################
@route(PREFIX + "/MainMenu")
def MainMenu(**kwargs):
	
	return main.Main()
	
####################################################################################################
# ValidatePrefs
####################################################################################################
@route(PREFIX + "/ValidatePrefs")
def ValidatePrefs():

	return main.ValidatePrefs2()
	
####################################################################################################
# Initialize
####################################################################################################
@route(PREFIX + "/Initialize")
def Initialize():

	main.validateBaseUrl()
	main.ValidateMyPrefs()
	main.DumpPrefs()
	
	# convert old style bookmarks to new
	if main.common.DEV_BM_CONVERSION and len(main.CONVERT_BMS) == 0:
		main.convertbookmarks()