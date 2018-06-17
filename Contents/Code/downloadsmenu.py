import re, urllib, urllib2, json, sys, time, random, urlparse
import common, updater, fmovies, tools, download, playback
from DumbTools import DumbKeyboard
import AuthTools
from __builtin__ import eval

TITLE = common.TITLE
PREFIX = common.PREFIX

MC = common.NewMessageContainer(common.PREFIX, common.TITLE)

#######################################################################################################
@route(PREFIX + '/AddToDownloadsListPre')
def AddToDownloadsListPre(title, year, url, durl, purl, summary, thumb, quality, source, type, resumable, source_meta, file_meta, mode, sub_url=None, fsBytes=None, fs=None, file_ext=None, vidtype=None, section_path=None, section_title=None, section_key=None, session=None, admin=False, update=False, params=None, riptype=None, **kwargs):
	
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
		err = ''
		try:
			if 'openload' in source:
				isPairDone = common.host_openload.isPairingDone()
				openload_vars =  common.host_openload.check(url, usePairing=False, embedpage=True)
				online, r1, err, fs_i, furl2, sub_url_t = openload_vars
				if sub_url == None:
					sub_url = sub_url_t
			elif 'rapidvideo' in source:
				vurl, r1, sub_url_t = common.host_rapidvideo.resolve(url, True)
				if sub_url == None:
					sub_url = sub_url_t
				fs_i, err = common.client.getFileSize(vurl, retError=True, retry429=True, cl=2)
			elif 'streamango' in source:
				vurl, r1, sub_url_t = common.host_streamango.resolve(url, True)
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
			Log.Error('init.py > AddToDownloadsListPre : %s - %s' % (e,err))
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
			oc.add(DirectoryObject(key = Callback(AddToDownloadsListPre, title=title, purl=purl, url=url, durl=durl, summary=summary, thumb=thumb, year=year, quality=quality, source=source, source_meta=source_meta, file_meta=file_meta, type=type, resumable=resumable, sub_url=sub_url, fsBytes=fsBytes, fs=fs, file_ext=file_ext, mode=mode, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, update=True, params=params, riptype=riptype), title = 'Update this item'))
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
		
		EncTxt = E(JSON.StringFromObject({'title':title, 'year':year, 'url':url, 'durl':durl, 'purl':purl, 'sub_url':sub_url, 'summary':summary, 'thumb':thumb, 'fsBytes':int(fsBytes), 'fs':fs, 'chunk_size':chunk_size, 'file_ext':file_ext, 'quality':quality, 'source':source, 'source_meta':source_meta, 'file_meta':file_meta, 'uid':uid, 'fid':fid, 'type':type, 'vidtype':vidtype, 'resumable':resumable, 'status':common.DOWNLOAD_STATUS[4], 'startPos':0, 'timeAdded':time.time(), 'first_time':time.time(), 'progress':0, 'chunk_speed':0,'avg_speed':0,'avg_speed_curr':0, 'eta':0, 'error':'', 'last_error':'Unknown Error', 'action':common.DOWNLOAD_PROPS[3],'section_path':section_path, 'section_title':section_title, 'section_key':section_key, 'user':user})) 
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
		
	return AddToDownloadsList(title=title, purl=purl, url=url, durl=durl, summary=summary, thumb=thumb, year=year, quality=quality, source=source, source_meta=source_meta, file_meta=file_meta, type=type, vidtype=vidtype, resumable=resumable, sub_url=sub_url, fsBytes=fsBytes, fs=fs, file_ext=file_ext, mode=mode, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, update=update, user=user,params=params, riptype=riptype)
	
######################################################################################
# Adds a movie to the DownloadsList list using the (title + 'Down5Split') as a key for the url
@route(PREFIX + "/addToDownloadsList")
def AddToDownloadsList(title, year, url, durl, purl, summary, thumb, quality, source, type, resumable, source_meta, file_meta, sub_url=None, fsBytes=None, fs=None, file_ext=None, vidtype=None, section_path=None, section_title=None, section_key=None, session=None, admin=False, update=False, user=None, params=None, riptype=None, **kwargs):

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
				return AddToDownloadsList(title=title, year=year, url=url, durl=durl, purl=purl, summary=summary, thumb=thumb, fs=fs, fsBytes=fsBytes, file_ext=file_ext, quality=quality, source=source, source_meta=source_meta, file_meta=file_meta, type=type, vidtype=vidtype, resumable=resumable, sub_url=sub_url, section_path=item['path'], section_title=item['title'], section_key=item['key'], session=session, admin=admin, update=update, user=user, params=params, riptype=riptype)
			else:
				oc = ObjectContainer(title1='Select Location', no_cache=common.isForceNoCache())
				for item in DOWNLOAD_OPTIONS_SECTION_TEMP[type]:
					if item['enabled']:
						oc.add(DirectoryObject(
							key = Callback(AddToDownloadsList, title=title, year=year, url=url, durl=durl, purl=purl, summary=summary, thumb=thumb, fs=fs, fsBytes=fsBytes, file_ext=file_ext, quality=quality, source=source, source_meta=source_meta, file_meta=file_meta, type=type, vidtype=vidtype, resumable=resumable, sub_url=sub_url, section_path=item['path'], section_title=item['title'], section_key=item['key'], session=session, admin=admin, update=update, user=user, params=params, riptype=riptype),
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
					online, r1, err, fs_i, r2, r3 =  common.host_openload.check(url, usePairing = False, embedpage=True)
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
			
			EncTxt = E(JSON.StringFromObject({'title':title, 'year':year, 'url':url, 'durl':durl, 'purl':purl, 'sub_url':sub_url, 'summary':summary, 'thumb':thumb, 'fsBytes':int(fsBytes), 'fs':fs, 'chunk_size':chunk_size, 'file_ext':file_ext, 'quality':quality, 'source':source, 'source_meta':source_meta, 'file_meta':file_meta, 'uid':uid, 'fid':fid, 'type':type, 'vidtype':vidtype, 'resumable':resumable, 'status':common.DOWNLOAD_STATUS[0], 'startPos':0, 'timeAdded':time.time(), 'first_time':time.time(), 'progress':0, 'chunk_speed':0,'avg_speed':0,'avg_speed_curr':0, 'eta':0, 'error':'', 'last_error':'Unknown Error', 'action':common.DOWNLOAD_ACTIONS[4],'section_path':section_path, 'section_title':section_title, 'section_key':section_key, 'user':user, 'params':params, 'riptype':riptype})) 
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
						thumb = common.GetThumb(longstringObjs['thumb'], session=session),
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
			if each in common.DOWNLOAD_STATS.keys():
				del common.DOWNLOAD_STATS[each]
				
			try:
				encoded_str = Dict[each]
				decoded_str = D(encoded_str)
				longstringObjs = JSON.ObjectFromString(decoded_str)
				Log(longstringObjs)
				if 'temp_file' in longstringObjs:
					filepath = longstringObjs['temp_file']
					try:
						Core.storage.remove_data_item(filepath)
					except Exception as e:
						Log("=============ClearDownLoadSection Error============")
						Log(e)
				Log("Deleting: %s" % longstringObjs['title'])
				del Dict[each]
			except:
				Log("Deleting: %s" % each)
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
				thumb = common.GetThumb(R(common.ICON_REFRESH), session=session)
				)
			)
		elif status == common.DOWNLOAD_STATUS[1]:
			oc.add(DirectoryObject(
				title = 'Pause %s Downloads' % status,
				key = Callback(PauseDownloadingDownloads, session=session),
				summary = 'Pause %s Download Entries' % status,
				thumb = common.GetThumb(R(common.ICON_ENTER), session=session)
				)
			)
			oc.add(DirectoryObject(
				title = 'Postpone %s Downloads' % status,
				key = Callback(PostponeDownloadingDownloads, session=session),
				summary = 'Postpone %s Download Entries' % status,
				thumb = common.GetThumb(R(common.ICON_ENTER), session=session)
				)
			)
		oc.add(DirectoryObject(
			title = 'Refresh %s Downloads' % status,
			key = Callback(Downloads,title="%s Downloads" % status, status=status, session=session, refresh=int(refresh)+1),
			summary = 'Refresh %s Download Entries' % status,
			thumb = common.GetThumb(R(common.ICON_REFRESH), session=session)
			)
		)
		oc.add(DirectoryObject(
			title = 'Clear %s Downloads' % status,
			key = Callback(ClearDownLoadSection, status=status, session=session),
			summary = 'Remove %s Download Entries' % status,
			thumb = common.GetThumb(R(common.ICON_NOTOK), session=session)
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
				thumb = common.GetThumb(R(common.ICON_ENTER), session=session)
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
							thumb = common.GetThumb(R(common.ICON_ENTER), session=session)
							)
						)
				c += 1
			if longstringObjs['section_key'] == None:
				oc.add(DirectoryObject(
					title = 'Set Download Location',
					summary = '%s | Download path: %s' % (longstringObjs['section_title'], longstringObjs['section_path']),
					key = Callback(SetReqDownloadLocation, uid=longstringObjs['uid'], type=longstringObjs['type']),
					thumb = common.GetThumb(R(common.ICON_ENTER), session=session)
					)
				)
			else:
				oc.add(DirectoryObject(
					title = '%s | Download path: %s' % (longstringObjs['section_title'], longstringObjs['section_path']),
					summary = '%s | Download path: %s' % (longstringObjs['section_title'], longstringObjs['section_path']),
					key = Callback(MyMessage, title='Download Path', msg=longstringObjs['section_path']),
					thumb = common.GetThumb(R(common.ICON_ENTER), session=session)
					)
				)
			if longstringObjs['purl'] != None:
				oc.add(DirectoryObject(
					title = 'Video Page (Other Download Sources)',
					summary = 'Video Page: %s' % longstringObjs['title'],
					key = Callback(EpisodeDetail, title=longstringObjs['title'], url=longstringObjs['purl'], thumb=longstringObjs['thumb'], session = session),
					thumb = common.GetThumb(R(common.ICON_ENTER), session=session)
					)
				)
			else:
				oc.add(DirectoryObject(
					title = 'Video Page (Unavailable)',
					summary = 'Video Page: %s' % longstringObjs['title'],
					key = Callback(MyMessage, title='Video Page', msg='This Video Page is Unavailable'),
					thumb = common.GetThumb(R(common.ICON_ENTER), session=session)
					)
				)
			if status == common.DOWNLOAD_STATUS[2]:
				oc.add(DirectoryObject(
					title = 'Clear',
					key = Callback(DownloadingFilesMenu, title=longstringObjs['title'], uid=uid, choice=common.DOWNLOAD_ACTIONS[0], session=session, status=status),
					summary = 'Clear %s' % longstringObjs['title'],
					thumb = common.GetThumb(R(common.ICON_ENTER), session=session)
					)
				)
			oc.add(DirectoryObject(
				title = 'Refresh',
				key = Callback(DownloadingFilesMenu, title=title, uid=uid, choice=choice, session=session, status=status, confirm=confirm, refresh=int(refresh)+1),
				summary = 'Refresh Stats for %s' % longstringObjs['title'],
				thumb = common.GetThumb(R(common.ICON_REFRESH), session=session)
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
				oc.add(DirectoryObject(title = 'YES - Clear %s Entry' % title, key = Callback(DownloadingFilesMenu, title=title, uid=uid, choice=choice, session=session, status=status, confirm=True), thumb = R(common.ICON_OK)))
				oc.add(DirectoryObject(title = 'NO - Dont Clear %s Entry' % title, key = Callback(MyMessage, title='No Selected', msg='Return to previous screen'),thumb = R(common.ICON_NOTOK)))
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
		oc.add(DirectoryObject(title = 'YES - Clear %s Entries' % status, key = Callback(ClearDownLoadSection, status=status, session=session, confirm=True),thumb = R(common.ICON_OK)))
		oc.add(DirectoryObject(title = 'NO - Dont Clear %s Entries' % status, key = Callback(MyMessage, title='No Selected', msg='Return to previous screen'),thumb = R(common.ICON_NOTOK)))
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