#!/usr/bin/env python

# Modified from 
# https://github.com/Twoure/KissNetwork.bundle/blob/dev/Contents/Services/Shared%20Code/kbase.pys
# Author: Twoure
#

import os, io
import shutil
import json
import common, fmovies

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

MC = common.NewMessageContainer(common.PREFIX, common.TITLE)

ES_API_URL = 'http://movies-v2.api-fetch.website'
	
####################################################################################################
@route(common.PREFIX + '/devtools-cache')
def DevToolsC(title=None, header=None, message=None):
	"""Tools to Remove all Covers/URLs cached files"""

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

	return oc
	
####################################################################################################
def ClearCache(itemname, timeout=None):
	"""Clear old Cached URLs depending on input timeout"""

	if timeout==None:
		timeout = Datetime.Delta()
	cachetime = Datetime.Now()
	count = 0
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

	Log.Debug('* Cleaned {} Cached files from {} : {}'.format(count, itemname, path))
	return count
	
######################################################################################
def SaveBookmarks(**kwargs):

	fmovies_base = fmovies.BASE_URL.replace('https://www.','')
	fmovies_base = fmovies_base.replace('https://','')
	
	items_in_bm = []
	
	for each in Dict:
		longstring = str(Dict[each])
		
		if ('fmovies.' in longstring or ES_API_URL.lower() in longstring) and 'Key5Split' in longstring:	
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
	