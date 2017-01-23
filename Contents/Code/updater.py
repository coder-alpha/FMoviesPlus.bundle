################################################################################
import common, re, urllib, os

ICON_OK = "icon-ok.png"
ICON_WARNING = "icon-warning.png"
ICON_ERROR = "icon-error.png"
ICON_UPDATER = "icon-updater.png"
ICON_RELEASES = "icon-releases.png"
ICON_NEXT = "icon-next.png"

FEED_URL = 'https://github.com/{0}/releases.atom'
################################################################################

@route(common.PREFIX + '/updatechannel')
def menu(title):
	oc = ObjectContainer(title2=title)

	# Plugin Version
	ver, version_result, version_result_str, version_result_summary, tag = test_version()
	url = 'https://github.com/{0}/archive/{1}.zip'.format(common.GITHUB_REPOSITORY, tag)
	oc.add(DirectoryObject(key=Callback(update, url=url, ver=ver), title='Plugin version: {0}'.format(version_result_str), summary=version_result_summary, thumb=get_test_thumb(version_result)))
	oc.add(DirectoryObject(key=Callback(updateold,title='Older Releases (Pre '+ver+')', feed=FEED_URL, ver=ver), title= 'Pre '+ ver + ' Releases', summary='Update to an Older Release. Please note an older release might not have updater support.', thumb=R(ICON_RELEASES)))
	
	return oc

# This gets the release name
def get_latest_version():
	try:
		release_feed_url = ('https://github.com/{0}/releases.atom'.format(common.GITHUB_REPOSITORY))
		release_feed_data = RSS.FeedFromURL(release_feed_url, cacheTime=0, timeout=15)
		link = release_feed_data.entries[0].link
		tags = link.split('/')
		tag = tags[len(tags)-1]
		summary = cleanSummary((release_feed_data.entries[0].content[0]))
		return (release_feed_data.entries[0].title, summary, tag)
	except Exception as exception:
		Log.Error('Checking for new releases failed: {0}'.format(repr(exception)))

################################################################################
def update_available():

	try:
		latest_version_str, summ, tag = get_latest_version()
		latest_version_str = getOnlyVersionNumber(latest_version_str)
		
		if latest_version_str:
			#latest_version  = map(int, latest_version_str.split('.'))
			#current_version = map(int, common.VERSION.split('.'))
			latest_version  = latest_version_str
			current_version = common.VERSION
			return (float(latest_version) > float(current_version), latest_version_str, summ, tag)
		return (False, None, None, None)
	except:
		return (False, None, None, None)

################################################################################
@route(common.PREFIX + '/update')
def update(url, ver):
		
	if ver:
		msg = 'Plugin updated to version {0}'.format(ver)
		msgH = 'Update successful'
		try:
			zip_data = Archive.ZipFromURL(url)
			
			for name in zip_data.Names():
				data	= zip_data[name]
				parts   = name.split('/')
				shifted = Core.storage.join_path(*parts[1:])
				full	= Core.storage.join_path(Core.bundle_path, shifted)

				if '/.' in name:
					continue

				if name.endswith('/'):
					Core.storage.ensure_dirs(full)
				else:
					if Core.storage.file_exists(full):
						os.remove(full)
						Core.storage.save(full, data)
					else:
						Core.storage.save(full, data)
		except Exception as exception:
			msg = 'Error: ' + str(exception)
			msgH = 'Update failed'
		
		try:
			os.remove(zip_data)
		except Exception as exception:
			pass
		
		return ObjectContainer(header=msgH, message=msg)
	else:
		return ObjectContainer(header='Update failed', message='Version not found !')

################################################################################
@route(common.PREFIX + '/updateold')
def updateold(title, feed, ver):

	oc = ObjectContainer(title2=title)
	try:
		release_feed_url = (feed.format(common.GITHUB_REPOSITORY))
		release_feed_data = RSS.FeedFromURL(release_feed_url, cacheTime=0, timeout=15)
		version_result_str = ''
		itemsN = len(release_feed_data.entries)
		if itemsN > 1:
			for x in range(1, itemsN):
				entry = release_feed_data.entries[x]
				link = entry.link
				tags = link.split('/')
				tag = tags[len(tags)-1]
				summary = cleanSummary(entry.content[0])
				title = entry.title
				version_result_str = title
				url = 'https://github.com/{0}/archive/{1}.zip'.format(common.GITHUB_REPOSITORY, tag)
				ver = getOnlyVersionNumber(title)
				oc.add(DirectoryObject(key=Callback(update, url=url, ver=ver), title='Plugin version: {0}'.format(ver), summary='Click to update to '+ver+' version. - ' + summary, thumb=R(ICON_UPDATER)))
			oc.objects.sort(key=lambda obj: obj.title, reverse=True)
			oc.add(DirectoryObject(key=Callback(updateold,title='Older Releases (pre '+version_result_str+')', feed=FEED_URL+'?after='+tag, ver=ver), title='Older Releases (pre '+version_result_str+')', summary='Update to an Older Release', thumb=R(ICON_NEXT)))
			return oc
		else:
			return ObjectContainer(header='Older Releases', message='No More Releases Available prior to ' + ver)
	except Exception as exception:
		return ObjectContainer(header='Error', message=str(exception))

def test_version():
	update_avail, latest_version, summ, tag = update_available()
	if not update_avail:
		result		 = True
		result_str	 = common.VERSION
		result_summary = 'Running latest version.'
	else:
		result		 = 'Update'
		result_str	 = common.VERSION + ' ({0} available)'.format(latest_version)
		result_summary = 'Click to update to latest version.'
	return (latest_version, result, result_str, result_summary + ' - ' + summ, tag)
	
def get_test_thumb(result):
    if result == True:
        return R(ICON_OK)
    elif result == 'Warning':
        return R(ICON_WARNING)
    elif result == 'Update':
        return R(ICON_UPDATER)
    elif result == False:
        return R(ICON_ERROR)

# clean tag names based on your release naming convention
def getOnlyVersionNumber(verStr):
	latest_version_str = verStr.lower().replace(' ','')
	latest_version_str = latest_version_str.lower().replace('ver.','')
	latest_version_str = latest_version_str.lower().replace('v','')
	return latest_version_str
	
# clean tag names based on your release naming convention
def cleanSummary(summary):
	summary = summary['value']
	summary = summary.replace('<p>','- ')
	summary = summary.replace('</p>','')
	summary = summary.replace('<ul>','-')
	summary = summary.replace('</ul>','')
	summary = summary.replace('<li>','- ')
	summary = summary.replace('</li>','')
	summary = summary.replace('\n',' ')
	summary = summary.replace('</br>',' ')
	summary = summary.replace('<br />',' - ')
	summary = summary.replace('<br/>',' - ')
	summary = summary.replace('&amp;','&')
	return summary.lstrip()