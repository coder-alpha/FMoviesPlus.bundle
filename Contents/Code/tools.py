#!/usr/bin/env python

# Modified from 
# https://github.com/Twoure/KissNetwork.bundle/blob/dev/Contents/Services/Shared%20Code/kbase.pys
# Author: Twoure
#

import os, io
import shutil
import json, time
import common, fmovies, AuthTools, externals

TITLE = common.TITLE
PREFIX = common.PREFIX

ICON_TOOLS = "icon-tools.png"

# general
identifier = 'com.plexapp.plugins.fmoviesplus'
prefix = common.PREFIX
channel_title = 'FMoviesPlus'
list_view_clients   = ['Android', 'iOS']
user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
user_agent_mobile = 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Mobile Safari/537.36'

# storage
PLEX_CACHE_DIR = 'Plex'

# path constants
bundle_path = os.path.join(os.getcwd().lstrip('\\\?').split('Plug-in Support')[0], 'Plug-ins', channel_title+'.bundle')
modules_path = os.path.join(bundle_path, 'Contents', 'Libraries', 'Shared')
resources_path = os.path.join(bundle_path, 'Contents', 'Resources')
app_support_path = os.path.join(bundle_path.split('Plug-ins')[0])
support_path = os.path.join(app_support_path, 'Plug-in Support')
data_path = os.path.join(support_path, 'Data', identifier)
caches_path = os.path.join(support_path, 'Caches', identifier)

MC = common.NewMessageContainer(PREFIX, TITLE)

BACKUP_KEYS = ['DOWNLOAD_OPTIONS','INTERNAL_SOURCES_QUALS', 'INTERNAL_SOURCES_SIZES', 'INTERNAL_SOURCES_RIPTYPE', 'INTERNAL_SOURCES_FILETYPE', 'OPTIONS_PROVIDERS', 'OPTIONS_PROXY', 'INTERNAL_SOURCES']
	
####################################################################################################
@route(PREFIX + "/DevToolsC")
def DevToolsC(title=None, header=None, message=None, **kwargs):
	"""Tools to Remove all Covers/URLs cached files"""
	
	if not common.interface.isInitialized():
		return MC.message_container("Please wait..", "Please wait a few seconds for the Interface to Load & Initialize plugins")
		
	if AuthTools.CheckAdmin() == False:
		return MC.message_container('Admin Access Only', 'Only the Admin can perform this action !')

	oc = ObjectContainer(title2='Tools', header=header, message=message)

	if title:
		if title == 'plex_cache':
			count = ClearCache(caches_path, Datetime.Delta())
			message = 'Cleaned {} Cached files'.format(count)
			Log(u'\n----------Removed {} Cached files from {}----------'.format(count, caches_path))
		elif title == 'save_bm':
			count = SaveBookmarks()
			message = 'Saved {} Bookmarks'.format(count)
			Log(u'\n----------Saved {} Bookmarks to {}----------'.format(count, resources_path))
		elif title == 'load_bm':
			count = LoadBookmarks()
			if count == -1:
				message='Bookmarks file (bookmarks.json) does not exist in Resource folder !'
			else:
				message = 'Loaded {} Bookmarks'.format(count)
			Log(u'\n----------Loaded {} Bookmarks from {}----------'.format(count, resources_path))
		elif title == 'save_config':
			bool = SaveConfig()
			if bool == True:
				message = 'Saved Config file'
				Log(u'\n----------Saved Config to {}----------'.format(resources_path))
			else:
				message = 'Error: Could not Save Config file (config.json)'
		elif title == 'load_config':
			bool = LoadConfig()
			if bool == True:
				message = 'Loaded Config file'
				Log(u'\n----------Loaded Config from {}----------'.format(resources_path))
			else:
				message='Error: Could not Load Config file (config.json)'
		elif title == 'check_externals':
			if len(externals.BUSY_BOOL) > 0:
				message = 'Checking externals. Please wait and try again.'
			else:
				Thread.Create(externals.checkRoutine)
				time.sleep(7)
				if len(externals.BUSY_BOOL) > 0:
					message = 'Checking externals. Please wait and try again.'
				else:
					if len(externals.CHECK_ROUTINE_LOG) > 0:
						for item in externals.CHECK_ROUTINE_LOG:
							oc.add(DirectoryObject(title=item,key=Callback(MyMessage, 'Info', item)))
						return oc
					else:
						message = 'Could not retrieve output from externals.'
		elif title == 'set_base_url':
			base_urls = ["https://fmovies.is","https://fmovies.to","https://fmovies.se","https://bmovies.is","https://bmovies.to","https://bmovies.pro","https://bmovies.online","https://bmovies.club","https://bmovies.ru"]
			oc = ObjectContainer(title2='Set Base URL')
			for u in base_urls:
				ch = common.GetEmoji(type=True) if u == fmovies.BASE_URL else common.GetEmoji(type=False)
				oc.add(DirectoryObject(title='%s | Base URL : %s' % (ch, u),key=Callback(SetBaseUrl, url=u)))
			return oc

		return MC.message_container('Info', message)

	# oc.add(DirectoryObject(key=Callback(DevToolsC, title='plex_cache'),
		# title=u'Reset {} Cache'.format(PLEX_CACHE_DIR),
		# thumb = R(ICON_TOOLS),
		# summary=u'Remove cached files from {} directory.'.format(caches_path)))
	oc.add(DirectoryObject(key=Callback(DevToolsC, title='save_bm'),
		title=u'Save Bookmarks',
		thumb = R(ICON_TOOLS),
		summary=u'Save Bookmarks to the Resource dir. (file: bookmarks.json)'))
	oc.add(DirectoryObject(key=Callback(DevToolsC, title='load_bm'),
		title=u'Load Bookmarks',
		thumb = R(ICON_TOOLS),
		summary=u'Load Bookmarks from the Resource dir. (file: bookmarks.json)'))
	oc.add(DirectoryObject(key=Callback(DevToolsC, title='save_config'),
		title=u'Save Config',
		thumb = R(ICON_TOOLS),
		summary=u'Save Config to the Resource dir. (file: config.json). Device Options (all clients), Bookmarks, Recent WatchList, SearchQue, Downloads and Interface Options can be saved and restored using Config file.'))
	oc.add(DirectoryObject(key=Callback(DevToolsC, title='load_config'),
		title=u'Load Config',
		thumb = R(ICON_TOOLS),
		summary=u'Load Config from the Resource dir. (file: config.json). Device Options (all clients), Bookmarks, Recent WatchList, SearchQue, Downloads and Interface Options can be saved and restored using Config file.'))
	oc.add(DirectoryObject(key=Callback(DevToolsC, title='check_externals'),
		title=u'Check Externals',
		thumb = R(ICON_TOOLS),
		summary=u'Check externals like PhantomJS and Cryptodome have been installed or not'))
	oc.add(DirectoryObject(key=Callback(DevToolsC, title='set_base_url'),
		title=u'Set Base URL',
		thumb = R(ICON_TOOLS),
		summary=u'Set the Base URL to be used by the Channel'))

	return oc
	
####################################################################################################
def ClearCache(itemname, timeout=None, **kwargs):
	"""Clear old Cached URLs depending on input timeout"""

	if timeout==None:
		timeout = Datetime.Delta()
	cachetime = Datetime.Now()
	count = 0
	if Prefs["use_debug"]:
		Log.Debug('* Clearing \'{}\' items older than {}'.format(itemname, str(cachetime - timeout)))
	path = Core.storage.data_item_path(itemname)
	Core.storage.ensure_dirs(path)
	
	for dirpath, dirnames, filenames in Core.storage.walk(path):
		for filename in filenames:
			filepath = Core.storage.join_path(dirpath, filename)
			if (Datetime.FromTimestamp(Core.storage.last_modified(filepath)) + timeout) <= cachetime:
				if Core.storage.dir_exists(filepath):
					continue
				Core.storage.remove_data_item(filepath)
				count += 1

	if Prefs["use_debug"]:
		Log.Debug('* Cleaned {} Cached files from {} : {}'.format(count, itemname, path))
	return count
	
######################################################################################
def SaveBookmarks(**kwargs):

	fmovies_base = fmovies.BASE_URL.replace('https://www.','')
	fmovies_base = fmovies_base.replace('https://','')
	
	items_in_bm = []
	
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
				if 'fmovies.' in longstring or 'bmovies.' in longstring:
					urlhost = common.client.getUrlHost(url)
					url = url.replace(urlhost,fmovies_base)
				
			#Log("BM : %s" % url)
				
			if url not in items_in_bm:
				items_in_bm.append({'title':stitle,'url':url,'summary':summary,'thumb':thumb})
					
	if len(items_in_bm) > 0:
		bkup_file = Core.storage.join_path(resources_path, 'bookmarks.json')
		with io.open(bkup_file, 'wb') as f:
			json.dump(items_in_bm, f, indent=4, sort_keys=True, separators=(',', ': '))
		return len(items_in_bm)
	else:
		return 0
		
######################################################################################
def LoadBookmarks(**kwargs):

	items_in_bm = []
	file_read = None
	
	bkup_file = Core.storage.join_path(resources_path, 'bookmarks.json')
	
	if Core.storage.file_exists(bkup_file) and (Core.storage.file_size(bkup_file) != 0):
		with io.open(bkup_file, 'r') as f:
			file_read = f.read()
			
		if file_read != None:
			items_in_bm = json.loads(file_read)
		
		for item in items_in_bm:
		
			title = item['title']
			url = item['url']
			summary = item['summary']
			thumb = item['thumb']
			
			Dict[title+'-'+E(url)] = (title + 'Key5Split' + url +'Key5Split'+ summary + 'Key5Split' + thumb)
		
		if len(items_in_bm) > 0:
			Dict.Save()

		return len(items_in_bm)
	else:
		return -1
	
######################################################################################
def SaveConfig(**kwargs):
		
	fmovies_base = fmovies.BASE_URL.replace('https://www.','')
	fmovies_base = fmovies_base.replace('https://','')
	
	config = {}
	items_in_recent = []
	items_in_recentlisting = []
	items_in_bm = []
	items_in_downloads = []
	items_in_searchque = []
	items_device_opts = []
	
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
				if 'fmovies.' in longstring or 'bmovies.' in longstring:
					urlhost = common.client.getUrlHost(url)
					url = url.replace(urlhost,fmovies_base)
				
			#Log("BM : %s" % url)
				
			if url not in items_in_bm:
				items_in_bm.append({'title':stitle,'url':url,'summary':summary,'thumb':thumb})
				
	urls_list = []
	items_to_del = []
	
	for each in Dict:
		longstring = str(Dict[each])
		
		if (('fmovies.' in longstring or 'bmovies.' in longstring) or common.isArrayValueInString(common.EXT_SITE_URLS, longstring) == True) and 'RR44SS' in longstring:
			longstringsplit = longstring.split('RR44SS')
			urls_list.append({'key': each, 'time': longstringsplit[4], 'val': longstring})
				
	if len(urls_list) > 0:
		
		newlist = sorted(urls_list, key=lambda k: k['time'], reverse=True)

		fmovies_base = fmovies.BASE_URL.replace('https://www.','')
		fmovies_base = fmovies_base.replace('https://','')
		
		for each in newlist:
		
			longstring = each['val']
			longstringsplit = longstring.split('RR44SS')
			stitle = unicode(longstringsplit[0])
			url = longstringsplit[1]
			summary = unicode(longstringsplit[2])
			thumb = longstringsplit[3]
			timestr = longstringsplit[4]
			
			#Log("%s %s" % (stitle, url))
			url = url.replace('www.','')
			
			ES = ''
			if common.ES_API_URL.lower() in longstring.lower():
				ES = common.EMOJI_EXT
			if common.ANIME_URL.lower() in longstring.lower():
				ES = common.EMOJI_ANIME
			
			if url.replace('fmovies.to',fmovies_base) in items_in_recent:
				items_to_del.append(each['key'])
			elif url.replace('bmovies.to',fmovies_base) in items_in_recent:
				items_to_del.append(each['key'])
			elif url.replace('bmovies.online',fmovies_base) in items_in_recent:
				items_to_del.append(each['key'])
			elif url.replace('bmovies.is',fmovies_base) in items_in_recent:
				items_to_del.append(each['key'])
			elif url.replace('bmovies.pro',fmovies_base) in items_in_recent:
				items_to_del.append(each['key'])
			elif url.replace('fmovies.se',fmovies_base) in items_in_recent:
				items_to_del.append(each['key'])
			elif url.replace('fmovies.is',fmovies_base) in items_in_recent:
				items_to_del.append(each['key'])
			else:
				if 'fmovies.' in longstring or 'bmovies.' in longstring:
					url = url.replace(common.client.geturlhost(url),fmovies_base)
				items_in_recent.append(url)
				items_in_recentlisting.append({'title':stitle, 'url':url, 'summary':summary, 'thumb':thumb, 'time':timestr})

	for each in Dict:
		longstring = str(Dict[each])
		
		if 'Down5Split' in each:	
			items_in_downloads.append({'uid': each.replace('Down5Split',''), 'val': JSON.ObjectFromString(D(longstring))})
			
		if 'MyCustomSearch' in each and 'removed' not in longstring and 'MyCustomSearch' in longstring:
			split_query = longstring.split('MyCustomSearch')
			query = split_query[0]
			timestr = split_query[1]	
			items_in_searchque.append({'key': query, 'time': timestr})
		
		for dev_opt in common.DEVICE_OPTIONS:
			if dev_opt in each:
				items_device_opts.append({'key':each, 'val':longstring})

	config['bookmarks'] = items_in_bm
	config['recent'] = items_in_recentlisting
	config['downloads'] = items_in_downloads
	config['searchque'] = items_in_searchque
	config['device_options'] = items_device_opts
	config['channelinfo'] = {'title':common.TITLE, 'version':common.VERSION, 'tag':common.TAG, 'repo':common.GITHUB_REPOSITORY, 'prefix':common.PREFIX}
		
	for key in BACKUP_KEYS:
		if Dict[key] != None:
			config[key] = JSON.ObjectFromString(D(Dict[key]))
	
	try:
		bkup_file = Core.storage.join_path(resources_path, 'config.json')
		
		with io.open(bkup_file, 'wb') as f:
			json.dump(config, f, indent=4, sort_keys=True, separators=(',', ': '))
		return True
	except Exception as e:
		Log.Exception("tools.py>SaveConfig >> : >>> %s" % (e))
	return False
		
######################################################################################
def LoadConfig(**kwargs):
	
	items_in_bm = []
	items_in_recent = []
	items_in_downloads = []
	items_in_searchque = []
	items_device_opts = []
	file_read = None
	config = {}
	
	try:
		bkup_file = Core.storage.join_path(resources_path, 'config.json')
		if Core.storage.file_exists(bkup_file) and (Core.storage.file_size(bkup_file) != 0):
			with io.open(bkup_file, 'r') as f:
				file_read = f.read()
				
			if file_read != None:
				try:
					config = json.loads(file_read)
				except:
					raise Exception('Config file seems invalid !')
					
				items_in_bm = config['bookmarks']
				items_in_recent = config['recent']
				items_in_downloads = config['downloads']
				items_in_searchque = config['searchque']
				items_device_opts = config['device_options']
				
			if len(config.keys()) == 0:
				raise Exception('Config file seems invalid !')
			
			for item in items_in_bm:
				title = item['title']
				url = item['url']
				summary = item['summary']
				thumb = item['thumb']
				Dict[title+'-'+E(url)] = (title + 'Key5Split' + url +'Key5Split'+ summary + 'Key5Split' + thumb)
				
			for item in items_in_recent:
				title = item['title']
				url = item['url']
				summary = item['summary']
				thumb = item['thumb']
				timestr = item['time']
				Dict[timestr+'RR44SS'+title+'RR44SS'] = title + 'RR44SS' + url +'RR44SS'+ summary + 'RR44SS' + thumb + 'RR44SS' + timestr
				
			for item in items_in_downloads:
				Dict['Down5Split'+item['uid']] = E(JSON.StringFromObject(item['val']))
				
			for item in items_in_searchque:
				query = item['key']
				timestr = item['time']
				Dict[common.TITLE.lower() +'MyCustomSearch'+query] = query + 'MyCustomSearch' + timestr
				
			for item in items_device_opts:
				key = item['key']
				val = item['val']
				Dict[key] = val
			
			for key in BACKUP_KEYS:
				if key in config:
					Dict[key] = E(JSON.StringFromObject(config[key]))
					
			Dict.Save()
			
			try:
				common.DOWNLOAD_OPTIONS = JSON.ObjectFromString(D(Dict['DOWNLOAD_OPTIONS']))
			except:
				pass
				
			try:
				common.INTERNAL_SOURCES_QUALS = JSON.ObjectFromString(D(Dict['INTERNAL_SOURCES_QUALS']))
			except:
				pass
				
			try:
				common.INTERNAL_SOURCES_SIZES = JSON.ObjectFromString(D(Dict['INTERNAL_SOURCES_SIZES']))
			except:
				pass
				
			try:
				common.INTERNAL_SOURCES_RIPTYPE = JSON.ObjectFromString(D(Dict['INTERNAL_SOURCES_RIPTYPE']))
			except:
				pass
				
			try:
				common.INTERNAL_SOURCES_FILETYPE = JSON.ObjectFromString(D(Dict['INTERNAL_SOURCES_FILETYPE']))
			except:
				pass
				
			try:
				common.OPTIONS_PROVIDERS = JSON.ObjectFromString(D(Dict['OPTIONS_PROVIDERS']))
			except:
				pass
				
			try:
				common.OPTIONS_PROXY = JSON.ObjectFromString(D(Dict['OPTIONS_PROXY']))
			except:
				pass
				
			try:
				common.INTERNAL_SOURCES = JSON.ObjectFromString(D(Dict['INTERNAL_SOURCES']))
			except:
				pass
			
			return True
		else:
			return False
	except Exception as e:
		Log.Exception("tools.py>LoadConfig >> : >>> %s" % (e))
	return False
	
####################################################################################################
@route(PREFIX+'/SetBaseUrl')
def SetBaseUrl(url):
	fmovies.BASE_URL = url
	return MyMessage('Set Base URL','Base URL set to %s' % fmovies.BASE_URL)
	
####################################################################################################
@route(PREFIX+'/MyMessage')
def MyMessage(title, msg, **kwargs):	
	return MC.message_container(title,msg)
