import re, urllib, urllib2, json, sys, time, random, urlparse
import main, common, updater, fmovies, tools, download, playback
from DumbTools import DumbKeyboard
import AuthTools
from __builtin__ import eval

TITLE = common.TITLE
PREFIX = common.PREFIX

MC = common.NewMessageContainer(common.PREFIX, common.TITLE)

REMOVE_ENTRY_WHEN_ALL_EPS_IN_DOWNLOADS = False
SOURCE_SEARCH_TIMEOUT = float(5*60) # 5 min.

ITEM_FOR_UPDATE = {}

#######################################################################################################
@route(PREFIX + '/AddToAutoPilotDownloads')
def AddToAutoPilotDownloads(title, year, type, purl=None, thumb=None, summary=None, quality=None, file_size=None, riptype='BRRIP', season=None, season_end=None, episode_start=None, episode_end=None, vidtype=None, section_path=None, section_title=None, section_key=None, session=None, admin=False, all_seasons=False, edit=False, mode=None, sub_mand=False, scheduled=False, smart_add=False, **kwargs):

	try:
		admin = True if str(admin) == 'True' else False
		all_seasons = True if str(all_seasons) == 'True' else False
		edit = True if str(edit) == 'True' else False
		sub_mand = True if str(sub_mand) == 'True' else False
		scheduled = True if str(scheduled) == 'True' else False
		smart_add = True if str(smart_add) == 'True' else False
		
		ret = False
		retInAQ = False
		
		title = common.cleantitle.windows_filename(title)
		
		if (type == 'show' and season == None) or (all_seasons == True):
			season = '1'
			episode_start = '1'
			episode_end = '1'
			all_seasons = True
			
		try:
			if season_end == None:
				season_end = '1'
			season_end = int(season_end)
		except:
			season_end = 1
			
		ts = '%s:%s' % (title,season)
		if ts in ITEM_FOR_UPDATE.keys():
			if ITEM_FOR_UPDATE[ts] == False and (quality != None or file_size != None):
				oc = ObjectContainer(title1='Item Added Already !', no_cache=common.isForceNoCache())
				oc.add(DirectoryObject(key = Callback(Downloads, title=" Downloads", session = session), title = "<< Downloads", thumb = common.GetThumb(R(common.ICON_DOWNLOADS), session=session)))
				oc.add(DirectoryObject(key = Callback(main.MainMenu), title = '<< Main Menu', thumb = common.GetThumb(R(common.ICON), session=session)))
				return oc
			elif ITEM_FOR_UPDATE[ts] == True and (quality != None or file_size != None):
				oc = ObjectContainer(title1='Item Updated Already !', no_cache=common.isForceNoCache())
				oc.add(DirectoryObject(key = Callback(Downloads, title="Downloads", session = session), title = "<< Downloads", thumb = common.GetThumb(R(common.ICON_DOWNLOADS), session=session)))
				oc.add(DirectoryObject(key = Callback(main.MainMenu), title = '<< Main Menu', thumb = common.GetThumb(R(common.ICON), session=session)))
				return oc
			elif ITEM_FOR_UPDATE[ts] == True and quality == None or file_size == None:
				del ITEM_FOR_UPDATE[ts]
			
		res = None
		if year == None:
			try:
				res = common.interface.requestOMDB(title=title, season=None if season==None else str(season), ver=common.VERSION)
				res_item = json.loads(json.dumps(res.content))
				res_item = json.loads(res_item)
				year = res_item['Year'][:4]
			except:
				pass
			try:
				seasonNR = int(res_item['totalSeasons'])
			except:
				seasonNR = None
			if seasonNR != None and seasonNR > season_end:
				season_end = seasonNR
			else:
				season_end = season_end
				
		if year == None:
			return main.MyMessage(title='Error', msg='OMDB is not reachable at the moment. Please try again after some time.')
		
		first_ep_idx = episode_start
		last_ep_idx = episode_end
		
		if type=='show' and edit == False and (quality == None and file_size == None):
			try:
				if res == None:
					res = common.interface.requestOMDB(title=title, season=str(season), ver=common.VERSION, timeout=7)
				try:
					episodesTot1 = len(json.loads(res.content)['Episodes'])
					episodesTot2 = int(json.loads(res.content)['Episodes'][len(json.loads(res.content)['Episodes'])-1]['Episode'])
					episode_end = last_ep_idx = max(episodesTot1,episodesTot2,int(last_ep_idx))
				except:
					pass
			except:
				pass

		if ret == False and edit == False:
			for i in common.DOWNLOAD_AUTOPILOT[type]:
				if type == 'movie':
					if i['title'] == title and i['year'] == year:
						ret = True
						retInAQ = True
						break
				elif type == 'show':
					if i['short_title'] == title and int(i['season']) == int(season):
						ret = True
						retInAQ = True
						last_ep_idx_t = int(i['episode_end'])
						if int(last_ep_idx) <= int(last_ep_idx_t):
							last_ep_idx = int(last_ep_idx_t)+1
						elif int(last_ep_idx) > int(last_ep_idx_t):
							last_ep_idx = int(last_ep_idx)
						if int(first_ep_idx) <= int(i['episode_end']):
							first_ep_idx = int(i['episode_end'])+1
							
			if ret == False:
				for uid in Dict:
					if 'Down5Split' in uid:
						EncTxt = None
						try:
							EncTxt = Dict[uid]
							EncTxt = JSON.ObjectFromString(D(EncTxt))
						except:
							pass
						try:
							if EncTxt != None:
								if type == 'movie':
									if EncTxt['title'] == title and EncTxt['year'] == year:
										ret = True
										break
								elif type == 'show':
									if EncTxt['title'] == title and EncTxt['year'] == year and EncTxt['season'] == season:
										ret = True
										last_ep_idx_t = EncTxt['episode']
										if int(last_ep_idx) <= int(last_ep_idx_t):
											last_ep_idx = int(last_ep_idx_t)+1
										elif int(last_ep_idx) > int(last_ep_idx_t):
											last_ep_idx = int(last_ep_idx)
										if int(first_ep_idx) <= int(EncTxt['episode']):
											first_ep_idx = int(EncTxt['episode'])+1
						except:
							pass

		if ret == True:
			if edit == False:
				if mode == None:
					if retInAQ == True:
						oc = ObjectContainer(title1='Add New or Replace Existing AutoPilot Items ?', no_cache=common.isForceNoCache())
						oc.add(DirectoryObject(
							key = Callback(AddToAutoPilotDownloads, title=title, year=year, type=type, purl=purl, thumb=thumb, summary=summary, quality=quality, file_size=file_size, riptype=riptype, season=season, season_end=season_end, episode_start=episode_start, episode_end=episode_end, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, all_seasons=all_seasons, edit=edit, mode='add', sub_mand=sub_mand, scheduled=scheduled, smart_add=smart_add),
							title = "Add as New Items"
							)
						)
						oc.add(DirectoryObject(
							key = Callback(AddToAutoPilotDownloads, title=title, year=year, type=type, purl=purl, thumb=thumb, summary=summary, quality=quality, file_size=file_size, riptype=riptype, season=season, season_end=season_end, episode_start=episode_start, episode_end=episode_end, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, all_seasons=all_seasons, edit=edit, mode='replace', sub_mand=sub_mand, scheduled=scheduled, smart_add=smart_add),
							title = "Replace Existing Items"
							)
						)
						return oc
					else:
						mode = 'add'
				if mode == 'add' and type == 'show':
					episode_start = first_ep_idx
					episode_end = last_ep_idx
				edit = True
			elif edit == True:
				pass
			else:
				pass
				# oc = ObjectContainer(title1='Item exists', no_cache=common.isForceNoCache())
				# oc.add(DirectoryObject(key = Callback(Downloads, title="Downloads", session = session), title = "<< Downloads", thumb = common.GetThumb(R(common.ICON_DOWNLOADS), session=session)))
				# oc.add(DirectoryObject(key = Callback(main.MainMenu), title = '<< Main Menu', thumb = common.GetThumb(R(common.ICON), session=session)))
				# return oc
				#return main.MyMessage(title='Return', msg='Item exists. Use back to Return to previous screen')
		
		if (quality == None and file_size == None) or (ret == True and edit == False):
			if ret == True:
				oc = ObjectContainer(title1='Update Quality or FileSize', no_cache=common.isForceNoCache())
			else:
				oc = ObjectContainer(title1='Select Quality or FileSize', no_cache=common.isForceNoCache())
			oc.add(DirectoryObject(
				key = Callback(AddToAutoPilotDownloads, title=title, year=year, type=type, purl=purl, thumb=thumb, summary=summary, quality=quality, file_size='%s:%s'%(0,100*common.TO_GB), riptype=riptype, season=season, season_end=season_end, episode_start=episode_start, episode_end=episode_end, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, all_seasons=all_seasons, edit=edit, mode=mode, sub_mand=sub_mand, scheduled=scheduled, smart_add=smart_add),
				title = "Enabled: %s | File-Size: %s" % (common.GetEmoji(type=True if file_size=='%s:%s'%(0,100*common.TO_GB) else False, mode='simple', session=session), 'Largest Available File')
				)
			)
			for item in common.INTERNAL_SOURCES_SIZES:
				if item['enabled']:
					oc.add(DirectoryObject(
						key = Callback(AddToAutoPilotDownloads, title=title, year=year, type=type, purl=purl, thumb=thumb, summary=summary, quality=quality, file_size='%s:%s'%(item['LL'],item['UL']), riptype=riptype, season=season, season_end=season_end, episode_start=episode_start, episode_end=episode_end, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, all_seasons=all_seasons, edit=edit, mode=mode, sub_mand=sub_mand, scheduled=scheduled, smart_add=smart_add),
						title = "Enabled: %s | File-Size: %s" % (common.GetEmoji(type=True if file_size=='%s:%s'%(item['LL'],item['UL']) else False, mode='simple', session=session), item['label'])
						)
					)
			for item in common.INTERNAL_SOURCES_QUALS:
				if item['enabled']:
					oc.add(DirectoryObject(
						key = Callback(AddToAutoPilotDownloads, title=title, year=year, type=type, purl=purl, thumb=thumb, summary=summary, quality=item['label'], file_size=file_size, riptype=riptype, season=season, season_end=season_end, episode_start=episode_start, episode_end=episode_end, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, all_seasons=all_seasons, edit=edit, mode=mode, sub_mand=sub_mand, scheduled=scheduled, smart_add=smart_add),
						title = "Enabled: %s | Quality: %s" % (common.GetEmoji(type=True if quality==item['label'] else False, mode='simple', session=session), item['label'])
						)
					)
			for item in common.INTERNAL_SOURCES_RIPTYPE:
				if 'BRRIP' in item['label']:
					oc.add(DirectoryObject(
						key = Callback(AddToAutoPilotDownloads, title=title, year=year, type=type, purl=purl, thumb=thumb, summary=summary, quality=quality, file_size=file_size, riptype=item['label'], season=season, season_end=season_end, episode_start=episode_start, episode_end=episode_end, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, all_seasons=all_seasons, edit=edit, mode=mode, sub_mand=sub_mand, scheduled=scheduled, smart_add=smart_add),
						title = "Enabled: %s | Rip-Type: %s" % (common.GetEmoji(type=True if riptype==item['label'] else False, mode='simple', session=session), item['label'])
						)
					)
			oc.add(DirectoryObject(
				key = Callback(AddToAutoPilotDownloads, title=title, year=year, type=type, purl=purl, thumb=thumb, summary=summary, quality=quality, file_size=file_size, riptype=riptype, season=season, season_end=season_end, episode_start=episode_start, episode_end=episode_end, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, all_seasons=all_seasons, edit=edit, mode=mode, sub_mand=not sub_mand, scheduled=scheduled, smart_add=smart_add),
				title = "Prefer Source with Subtitle: %s" % common.GetEmoji(type=sub_mand, mode='simple', session=session)
				)
			)
			oc.add(DirectoryObject(
				key = Callback(AddToAutoPilotDownloads, title=title, year=year, type=type, purl=purl, thumb=thumb, summary=summary, quality=quality, file_size=file_size, riptype=riptype, season=season, season_end=season_end, episode_start=episode_start, episode_end=episode_end, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, all_seasons=all_seasons, edit=edit, mode=mode, sub_mand=sub_mand, scheduled=not scheduled, smart_add=smart_add),
				title = "Run Later via Scheduler: %s" % common.GetEmoji(type=scheduled, mode='simple', session=session)
				)
			)
			if type == 'show':
				oc.add(DirectoryObject(
					key = Callback(AddToAutoPilotDownloads, title=title, year=year, type=type, purl=purl, thumb=thumb, summary=summary, quality=quality, file_size=file_size, riptype=riptype, season=season, season_end=season_end, episode_start=episode_start, episode_end=episode_end, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, all_seasons=all_seasons, edit=edit, mode=mode, sub_mand=sub_mand, scheduled=scheduled, smart_add=not smart_add),
					title = "Smart Add for To Be Aired Episodes: %s" % common.GetEmoji(type=smart_add, mode='simple', session=session)
					)
				)
			
			if len(oc) == 0:
				return MC.message_container('Quality or FileSize', 'A Quality or FileSize selection needs to be enabled under Interface Options')
			else:
				return oc
				
		if section_path == None or section_title == None:
			if ret == True or edit == True:
				oc = ObjectContainer(title1='Update Location & Ep. Index', no_cache=common.isForceNoCache())
			else:
				oc = ObjectContainer(title1='Select Location & Ep. Index', no_cache=common.isForceNoCache())
				
			for item in common.DOWNLOAD_OPTIONS[type]:
				if item['enabled']:
					oc.add(DirectoryObject(
						key = Callback(AddToAutoPilotDownloads, title=title, year=year, type=type, purl=purl, thumb=thumb, summary=summary, quality=quality, file_size=file_size, riptype=riptype, season=season, season_end=season_end, episode_start=episode_start, episode_end=episode_end, vidtype=vidtype, section_path=item['path'], section_title=item['title'], section_key=item['key'], session=session, admin=admin, all_seasons=all_seasons, edit=edit, mode=mode, sub_mand=sub_mand, scheduled=scheduled, smart_add=smart_add),
						thumb = common.GetThumb(R(common.ICON_SAVE), session=session),
						title = '%s | %s' % (item['title'], item['path'])
						)
					)		
			if len(oc) == 0:
				return MC.message_container('Download Sources', 'No Download Location set under Download Options')
			else:
				if type == 'show':
					DumbKeyboard(PREFIX, oc, AddToAutoPilotDownloadsInputEp, dktitle = 'Ep. Start Index:%s' % episode_start, dkthumb=common.GetThumb(R(common.ICON_DK_ENABLE), session=session), dkNumOnly=True, dkHistory=False, title=title, year=year, type=type, purl=purl, thumb=thumb, summary=summary, quality=quality, file_size=file_size, riptype=riptype, season=season, season_end=season_end, episode_start=episode_start, episode_end=episode_end, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, all_seasons=all_seasons, ep_id='start', edit=edit, mode=mode, sub_mand=sub_mand, scheduled=scheduled, smart_add=smart_add)
					DumbKeyboard(PREFIX, oc, AddToAutoPilotDownloadsInputEp, dktitle = 'Ep. End Index:%s' % episode_end, dkthumb=common.GetThumb(R(common.ICON_DK_ENABLE), session=session), dkNumOnly=True, dkHistory=False, title=title, year=year, type=type, purl=purl, thumb=thumb, summary=summary, quality=quality, file_size=file_size, riptype=riptype, season=season, season_end=season_end, episode_start=episode_start, episode_end=episode_end, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, all_seasons=all_seasons, ep_id='end', edit=edit, mode=mode, sub_mand=sub_mand, scheduled=scheduled, smart_add=smart_add)
				oc.add(DirectoryObject(key = Callback(Downloads, title="Downloads", session = session), title = "<< Downloads", thumb = common.GetThumb(R(common.ICON_DOWNLOADS), session=session)))
				oc.add(DirectoryObject(key = Callback(main.MainMenu), title = '<< Main Menu', thumb = common.GetThumb(R(common.ICON), session=session)))
				return oc

		if type == 'show':
			if int(episode_start) > int(episode_end):
				return MC.message_container('Episode Index', 'Episode Start Index cannot be greater than End Index')
					
		uid = common.makeUID(title, year, quality, file_size, purl, season, episode_start)
		
		if season_end == None:
			season_end = season
		
		if type == 'show':
			item = {'title':title, 'year':year, 'season':season, 'season_end':season_end, 'episode':int(episode_start), 'thumb':thumb, 'summary':summary, 'episode_start':int(episode_start), 'episode_end':int(episode_end), 'quality':quality, 'file_size':file_size, 'riptype':riptype, 'vidtype':vidtype, 'section_path':section_path, 'section_title':section_title, 'section_key':section_key, 'admin':admin, 'timeAdded':time.time(), 'first_time':time.time(), 'type':type, 'session':session, 'purl':purl, 'status':common.DOWNLOAD_AUTOPILOT_STATUS[3], 'fsBytes':0, 'uid':uid, 'all_seasons':all_seasons, 'sub_mand':sub_mand, 'scheduled':scheduled, 'smart_add':smart_add, 'smart_add_active':False}
		else:
			item = {'title':title, 'year':year, 'season':season, 'season_end':season_end, 'episode':episode_start, 'thumb':thumb, 'summary':summary, 'quality':quality, 'file_size':file_size, 'riptype':riptype, 'vidtype':vidtype, 'section_path':section_path, 'section_title':section_title, 'section_key':section_key, 'admin':admin, 'timeAdded':time.time(), 'first_time':time.time(), 'type':type, 'session':session, 'purl':purl, 'status':common.DOWNLOAD_AUTOPILOT_STATUS[3], 'fsBytes':0, 'uid':uid, 'all_seasons':all_seasons, 'sub_mand':sub_mand, 'scheduled':scheduled, 'smart_add':smart_add, 'smart_add_active':False}
			
		if mode == 'replace':
			save_bool = False
			items_to_remove = []
			for i in common.DOWNLOAD_AUTOPILOT[type]:
				if type == 'movie':
					if i['title'] == title and i['year'] == year:
						items_to_remove.append(i)
						save_bool = True
						break
				elif type == 'show':
					if i['short_title'] == title and int(i['season']) == int(season):
						try:
							assert int(episode_start) <= int(i['episode']) <= int(episode_end)
							items_to_remove.append(i)
							save_bool = True
						except AssertionError:
							pass
			if save_bool == True:
				for i in items_to_remove:
					common.DOWNLOAD_AUTOPILOT[type].remove(i)
				Dict['DOWNLOAD_AUTOPILOT'] = E(JSON.StringFromObject(common.DOWNLOAD_AUTOPILOT))
				Dict.Save()
				time.sleep(3)
		
		Thread.Create(AutoPilotDownloadThread, {}, item)
		ts = '%s:%s' % (title,season)
		
		if edit == True:
			ITEM_FOR_UPDATE[ts] = True
			return MC.message_container('Updated in AutoPilot Download Queue', 'The item has been Updated in AutoPilot Download Queue')
		else:
			ITEM_FOR_UPDATE[ts] = False
			return MC.message_container('Added to AutoPilot Download Queue', 'The item has been Added to AutoPilot Download Queue')
		
	except Exception as e:
		err = '{}'.format(e)
		Log('ERROR: downloadsmenu.py > AddToAutoPilotDownloads: %s' % err)
		return MC.message_container('Error', 'Error in AutoPilot Download Queue')
		
####################################################################################################
@route(PREFIX + "/AddToAutoPilotDownloadsInputEp")
def AddToAutoPilotDownloadsInputEp(query, title, year, type, purl=None, thumb=None, summary=None, quality=None, file_size=None, riptype='BRRIP', season=None, season_end=None, episode_start=None, episode_end=None, vidtype=None, section_path=None, section_title=None, section_key=None, session=None, admin=False, all_seasons=False, ep_id='start', edit=False, mode=None, sub_mand=False, scheduled=False, smart_add=False, **kwargs):

	if ep_id == 'start':
		try:
			episode_start = str(int(query))
		except:
			episode_start = '1'
	else:
		try:
			episode_end = str(int(query))
		except:
			episode_end = '1'

	return AddToAutoPilotDownloads(title=title, year=year, type=type, purl=purl, thumb=thumb, summary=summary, quality=quality, file_size=file_size, riptype=riptype, season=season, season_end=season_end, episode_start=episode_start, episode_end=episode_end, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, all_seasons=all_seasons, edit=edit, mode=mode, sub_mand=sub_mand, scheduled=scheduled, smart_add=smart_add)

#######################################################################################################
def AutoPilotDownloadThread(item):
	
	tuid = common.id_generator(16)
	common.control.AddThread('AutoPilotDownloadThread', 'Auto Pilot Download Thread > %s' % createAutoPilotThreadTitle(item), time.time(), '3', False, tuid)
		
	try:
		type = item['type']
		if type == 'show':
			SHOW_QUEUE = []
			orig_title = item['title']
			year = item['year']
			season_start = item['season']
			season_end = max(season_start,item['season_end'])
			episode_start = item['episode_start']
			episode_end = item['episode_end']
			all_seasons = item['all_seasons']
			
			for sx in range(int(season_start), int(season_end)+1):
				if all_seasons == True:
					try:
						time.sleep(1000)
						res = common.interface.requestOMDB(title=orig_title, year=str(int(year)+sx-1), season=str(sx), ver=common.VERSION)
						res_item = json.loads(json.dumps(res.content))
						res_item = json.loads(res_item)
						episode_end_t = len(res_item['Episodes'])
						if episode_end_t > episode_end:
							episode_end = episode_end_t
					except Exception as e:
						Log(e)
					
				for ix in range(int(episode_start), int(episode_end)+1):
					item_x = item.copy()
					item_x['season'] = str(sx)
					item_x['episode'] = str(ix)
					new_title = '%s S%sE%s' % (orig_title, item_x['season'], item_x['episode'])
					item_x['short_title'] = orig_title
					item_x['title'] = new_title
					
					if int(episode_end) < 100:
						watch_title = '%s S%sE%02d' % (orig_title,int(item_x['season']),int(item_x['episode']))
					else:
						watch_title = '%s S%sE%03d' % (orig_title,int(item_x['season']),int(item_x['episode']))
					
					item_x['watch_title'] = watch_title
					
					uid = common.makeUID(orig_title, int(year)+sx-1, item_x['quality'], item_x['file_size'], item_x['purl'], item_x['season'], item_x['episode'])
					item_x['uid'] = uid
					
					common.DOWNLOAD_AUTOPILOT[type].append(item_x)
					SHOW_QUEUE.append(item_x)
					
					Dict['DOWNLOAD_AUTOPILOT'] = E(JSON.StringFromObject(common.DOWNLOAD_AUTOPILOT))
					Dict.Save()
				
			c=0
			for i in SHOW_QUEUE:
				common.DOWNLOAD_AUTOPILOT[type][c]['timeAdded'] = time.time()
				if 'scheduled' not in i.keys() or i['scheduled'] == False:
					i['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[0]
					AutoPilotDownloadThread1(i)
				else:
					i['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[5]
				c += 1
		else:
			item_x = item.copy()
			orig_title = item['title']
			item_x['short_title'] = orig_title
			item_x['watch_title'] = orig_title
			
			common.DOWNLOAD_AUTOPILOT[type].append(item_x)
			
			Dict['DOWNLOAD_AUTOPILOT'] = E(JSON.StringFromObject(common.DOWNLOAD_AUTOPILOT))
			Dict.Save()
			
			c = len(common.DOWNLOAD_AUTOPILOT[type])-1
			common.DOWNLOAD_AUTOPILOT[type][c]['timeAdded'] = time.time()
			if 'scheduled' not in item_x.keys() or item_x['scheduled'] == False:
				item_x['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[0]
				AutoPilotDownloadThread1(item_x)
			else:
				item_x['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[5]
			
		Dict['DOWNLOAD_AUTOPILOT'] = E(JSON.StringFromObject(common.DOWNLOAD_AUTOPILOT))
		Dict.Save()
	except Exception as e:
		err = '{}'.format(e)
		Log('ERROR: downloadsmenu.py > AutoPilotDownloadThread: %s' % err)
		
	common.control.RemoveThread(tuid)
	
#######################################################################################################
def createAutoPilotThreadTitle(item):

	watch_title = 'AutoPilot Thread'
	try:
		type = item['type']
		year = item['year']
		if type == 'show':
			orig_title = item['title']
			season = int(item['season'])
			episode_start = int(item['episode_start'])
			episode_end = int(item['episode_end'])
			if int(episode_end) < 100:
				watch_title = '%s S%s (E%02d-E%02d) (%s)' % (orig_title,season,episode_start,episode_end,year)
			else:
				watch_title = '%s S%s (E%03d-E%03d) (%s)' % (orig_title,season,episode_start,episode_end,year)
		else:
			watch_title = '%s (%s)' % (item['title'],year)
	except Exception as e:
		err = '{}'.format(e)
		Log('ERROR: downloadsmenu.py > createAutoPilotThreadTitle: %s' % err)
	return watch_title
	
AutoPilotDownloadThread1_Singleton = []
#######################################################################################################
def AutoPilotDownloadThread1(item=None, runForWaiting=False):
	
	run_via_scheduler = False
	tuid = common.id_generator(16)
	if item == None:
		run_via_scheduler = True
		common.control.AddThread('AutoPilotDownloadThread1', 'Auto Pilot Download Thread > Scheduler', time.time(), '3', False, tuid)
		
	while len(AutoPilotDownloadThread1_Singleton) > 0:
		time.sleep(1.0)
		
	AutoPilotDownloadThread1_Singleton.append(True)
	
	try:
		removeEntry = False
		removeEntry_item = None
		
		if item == None: # runs via Scheduler and after Initialization (plugin restart)
		
			items_for_removal = {}
		
			for type in common.DOWNLOAD_AUTOPILOT.keys():
				items_for_removal[type] = []
				for item in common.DOWNLOAD_AUTOPILOT[type]:
					if (item['status'] == common.DOWNLOAD_AUTOPILOT_STATUS[2]):
						items_for_removal[type].append(item)
					elif 'smart_add_active' in item.keys() and 'first_time' in item.keys() and item['smart_add_active'] == True and float(time.time() - item['first_time']) > float(60*60*24*15):
						items_for_removal[type].append(item)
					if (item['status'] != common.DOWNLOAD_AUTOPILOT_STATUS[2] and runForWaiting == False) or (runForWaiting == True and (item['status'] == common.DOWNLOAD_AUTOPILOT_STATUS[0] or item['status'] == common.DOWNLOAD_AUTOPILOT_STATUS[3])) or (item['status'] == common.DOWNLOAD_AUTOPILOT_STATUS[0] and float(time.time() - item['timeAdded']) > float(60*60)):
						sources = None
						start_time = time.time()
						item['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[0]
						item['timeAdded'] = start_time
						if item['type'] == 'show':
							key = main.generatemoviekey(movtitle=None, year=item['year'], tvshowtitle=item['short_title'], season=item['season'], episode=str(item['episode']))
							prog = common.interface.checkProgress(key)
							while (prog > 0 and prog < 100):
								time.sleep(5)
								prog = common.interface.checkProgress(key)
								if (time.time() - start_time) > SOURCE_SEARCH_TIMEOUT:
									Log('ERROR: downloadsmenu.py > AutoPilotDownloadThread1: Source Searching Timeout Reached !')
									break
							sources = common.interface.getExtSources(movtitle=None, year=item['year'], tvshowtitle=item['short_title'], season=item['season'], episode=str(item['episode']), proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=common.CACHE_EXPIRY_TIME, ver=common.VERSION, imdb_id=None, session=item['session'], timeout=SOURCE_SEARCH_TIMEOUT, forceRet=True)
						else:
							key = main.generatemoviekey(movtitle=item['title'], year=item['year'], tvshowtitle=None, season=None, episode=None)
							prog = common.interface.checkProgress(key)
							while (prog > 0 and prog < 100):
								time.sleep(5)
								prog = common.interface.checkProgress(key)
								if (time.time() - start_time) > SOURCE_SEARCH_TIMEOUT:
									Log('ERROR: downloadsmenu.py > AutoPilotDownloadThread1: Source Searching Timeout Reached !')
									break
							sources = common.interface.getExtSources(movtitle=item['title'], year=item['year'], tvshowtitle=None, season=None, episode=None, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=common.CACHE_EXPIRY_TIME, ver=common.VERSION, imdb_id=None, session=item['session'], timeout=SOURCE_SEARCH_TIMEOUT, forceRet=True)
							
						if sources != None:
							bool, fsBytes, removeEntry = AutoPilotDownloadThread2(item, sources)
							item['fsBytes'] = fsBytes
							item['timeAdded'] = time.time()
							if bool == True:
								item['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[2]
								if removeEntry == True:
									removeEntry_item = item
									if item['type'] != 'show' or REMOVE_ENTRY_WHEN_ALL_EPS_IN_DOWNLOADS == False:
										try:
											#common.DOWNLOAD_AUTOPILOT[item['type']].remove(item)
											items_for_removal[item['type']].append(item)
											item['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[6]
										except:
											pass
							else:
								item['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[1]
						else:
							item['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[4]
								
					if REMOVE_ENTRY_WHEN_ALL_EPS_IN_DOWNLOADS == True and removeEntry_item != None and removeEntry_item['type'] == 'show':
						for i in common.DOWNLOAD_AUTOPILOT['show']:
							if i['status'] == common.DOWNLOAD_AUTOPILOT_STATUS[2] and i['short_title'] == removeEntry_item['short_title'] and i['season'] == removeEntry_item['season']:
								try:
									#common.DOWNLOAD_AUTOPILOT[type].remove(i)
									items_for_removal[item['type']].append(i)
									i['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[6]
								except:
									pass
		else: # runs when added
			sources = None
			start_time = time.time()
			type = item['type']
			if type == 'show':
				key = main.generatemoviekey(movtitle=None, year=item['year'], tvshowtitle=item['short_title'], season=item['season'], episode=str(item['episode']))
				prog = common.interface.checkProgress(key)
				while (prog > 0 and prog < 100):
					time.sleep(5)
					prog = common.interface.checkProgress(key)
					if (time.time() - start_time) > SOURCE_SEARCH_TIMEOUT:
						Log('ERROR: downloadsmenu.py > AutoPilotDownloadThread1: Source Searching Timeout Reached !')
						break
				sources = common.interface.getExtSources(movtitle=None, year=item['year'], tvshowtitle=item['short_title'], season=item['season'], episode=str(item['episode']), proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=common.CACHE_EXPIRY_TIME, ver=common.VERSION, imdb_id=None, session=item['session'], timeout=SOURCE_SEARCH_TIMEOUT, forceRet=True)
			else:
				key = main.generatemoviekey(movtitle=item['title'], year=item['year'], tvshowtitle=None, season=None, episode=None)
				prog = common.interface.checkProgress(key)
				while (prog > 0 and prog < 100):
					time.sleep(5)
					prog = common.interface.checkProgress(key)
					if (time.time() - start_time) > SOURCE_SEARCH_TIMEOUT:
						Log('ERROR: downloadsmenu.py > AutoPilotDownloadThread1: Source Searching Timeout Reached !')
						break
				sources = common.interface.getExtSources(movtitle=item['title'], year=item['year'], tvshowtitle=None, season=None, episode=None, proxy_options=common.OPTIONS_PROXY, provider_options=common.OPTIONS_PROVIDERS, key=key, maxcachetime=common.CACHE_EXPIRY_TIME, ver=common.VERSION, imdb_id=None, session=item['session'], timeout=SOURCE_SEARCH_TIMEOUT, forceRet=True)

			if sources != None:
				bool, fsBytes, removeEntry = AutoPilotDownloadThread2(item, sources)
				item['fsBytes'] = fsBytes
				item['timeAdded'] = time.time()
				if bool == True:
					item['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[2]
					if removeEntry == True:
						removeEntry_item = item
						if type != 'show' or REMOVE_ENTRY_WHEN_ALL_EPS_IN_DOWNLOADS == False:
							try:
								#common.DOWNLOAD_AUTOPILOT[type].remove(item)
								items_for_removal[item['type']].append(item)
								item['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[6]
							except:
								pass
				else:
					item['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[1]
			else:
				item['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[4]
					
			if REMOVE_ENTRY_WHEN_ALL_EPS_IN_DOWNLOADS == True and removeEntry_item != None and removeEntry_item['type'] == 'show':
				for i in common.DOWNLOAD_AUTOPILOT['show']:
					if i['status'] == common.DOWNLOAD_AUTOPILOT_STATUS[2] and i['short_title'] == removeEntry_item['short_title'] and i['season'] == removeEntry_item['season']:
						try:
							#common.DOWNLOAD_AUTOPILOT[type].remove(i)
							items_for_removal[item['type']].append(i)
							i['status'] = common.DOWNLOAD_AUTOPILOT_STATUS[6]
						except:
							pass
		
		items_for_smart_add = {}
		
		# remove completed entries
		for type_r in items_for_removal.keys():
			items_for_smart_add[type_r] = {}
			for item_r in items_for_removal[type_r]:
				for item_i in common.DOWNLOAD_AUTOPILOT[type_r]:
					if item_r['uid'] == item_i['uid']:
						try:
							bool, lastep = verifyForSmart(item_i)
							common.DOWNLOAD_AUTOPILOT[type_r].remove(item_i)
							if bool == True:
								item_i['episode'] = lastep + 1
								item_i['first_time'] = time.time()
								item_i['smart_add_active'] = True
								items_for_smart_add[type_r].append(item_i)
						except:
							pass
						break
						
		for type_r in items_for_smart_add.keys():
			for item_a in items_for_smart_add[type_r]:
				common.DOWNLOAD_AUTOPILOT[type_r].append(item_a)

		Dict['DOWNLOAD_AUTOPILOT'] = E(JSON.StringFromObject(common.DOWNLOAD_AUTOPILOT))
		Dict.Save()
	except Exception as e:
		err = '{}'.format(e)
		Log('ERROR: downloadsmenu.py > AutoPilotDownloadThread1: %s' % err)
		
	if run_via_scheduler == True:
		common.control.RemoveThread(tuid)
		
	del AutoPilotDownloadThread1_Singleton[:]

#######################################################################################################
def verifyForSmart(item):

	lastep = 0
	no_items = 0
	if 'smart_add' in item.keys() and item['smart_add'] == True:
		for i in common.DOWNLOAD_AUTOPILOT['show']:
			if item['short_title'] == i['short_title'] and item['season'] == i['season']:
				no_items += 1
				if i['episode'] > lastep:
					lastep = int(i['episode'])
	
	if no_items == 1:
		return True, lastep
	else:
		return False, lastep
	
#######################################################################################################
def AutoPilotDownloadThread2(item, sources):

	try:
		sources = JSON.ObjectFromString(D(sources))
		sources = common.FilterBasedOn(sources)
		sources = common.OrderBasedOn(sources, use_filesize=True)
		
		loops = [0]
		sub_bool = [False]
		if ('sub_mand' in item.keys() and item['sub_mand'] == True):
			sub_bool = [True, False]
			loops = [0,1]
		
		for loop in loops:
			for s in sources:
				try:
					fsBytes = int(s['fs'])
					fs = '%s GB' % str(round(float(s['fs'])/common.TO_GB, 3))
				except:
					fsBytes = 0
					fs = None
				
				doSkip = False
				removeEntry = True
				eps = 0
				eps_done = 0
				
				if item['riptype'] != s['rip']:
					doSkip = True
					
				if doSkip == False:
					if item['type'] != s['vidtype'].lower():
						doSkip = True
				
				if doSkip == False:
					if item['type'] == 'show':
						for i in common.DOWNLOAD_AUTOPILOT['show']:
							if item['short_title'] == i['short_title'] and item['season'] == i['season']:
								eps += 1
							if item['short_title'] == i['short_title'] and item['season'] == i['season'] and item['status'] == common.DOWNLOAD_AUTOPILOT_STATUS[2]:
								eps_done += 1
							if item['short_title'] == i['short_title'] and item['season'] == i['season'] and fsBytes == i['fsBytes']:
								doSkip = True
				
					if eps - eps_done > 1 and REMOVE_ENTRY_WHEN_ALL_EPS_IN_DOWNLOADS == True:
						removeEntry = False

				if doSkip == False:
					if (sub_bool[loop] == True and s['sub_url'] != None) or sub_bool[loop] == False:
						if item['quality'] == s['quality']:
							AutoPilotDownloadThread3(item, s, fsBytes, fs)
							return True, fsBytes, removeEntry
						elif item['file_size'] != None and fs != None:
							i_fs = item['file_size'].split(':')
							if fsBytes >= int(float(str(i_fs[0]))) and fsBytes < int(float(str(i_fs[1]))):
								AutoPilotDownloadThread3(item, s, fsBytes, fs)
								return True, fsBytes, removeEntry
				
		return False, 0, False
	except Exception as e:
		err = '{}'.format(e)
		Log('ERROR: downloadsmenu.py > AutoPilotDownloadThread2: %s' % err)
		return False, 0, False 
		
#######################################################################################################
def AutoPilotDownloadThread3(item, s, fsBytes, fs):

	try:
		AddToDownloadsList(title=item['short_title'] if item['type']=='show' else item['title'], purl=item['purl'], url=s['url'], durl=s['durl'], summary=item['summary'], thumb=item['thumb'], year=item['year'], quality=s['quality'], source=s['source'], source_meta={}, file_meta={}, type=item['type'], vidtype=item['vidtype'], resumable=s['resumeDownload'], sub_url=s['sub_url'], fsBytes=fsBytes, fs=fs, file_ext=s['file_ext'], mode=common.DOWNLOAD_MODE[0], section_path=item['section_path'], section_title=item['section_title'], section_key=item['section_key'], session=item['session'], admin=item['admin'], params=s['params'], riptype=s['rip'], season=item['season'], episode=item['episode'], provider=s['provider'], page_url=s['page_url'], seq=s['seq'])
	except Exception as e:
		err = '{}'.format(e)
		Log('ERROR: downloadsmenu.py > AutoPilotDownloadThread3: %s' % err)

#######################################################################################################
@route(PREFIX + '/AddToDownloadsListPre')
def AddToDownloadsListPre(title, year, url, durl, purl, summary, thumb, quality, source, type, resumable, source_meta, file_meta, mode, sub_url=None, fsBytes=None, fs=None, file_ext=None, vidtype=None, section_path=None, section_title=None, section_key=None, session=None, admin=False, update=False, params=None, riptype=None, season=None, episode=None, provider=None, page_url=None, seq=0, force_add=False, uid_upd=None, **kwargs):

	try:
		admin = True if str(admin) == 'True' else False
		update = True if str(update) == 'True' else False
		resumable = True if str(resumable) == 'True' else False
		force_add = True if str(force_add) == 'True' else False
		user = common.control.setting('%s-%s' % (session,'user'))
			
		bool = False
		for i_source in common.interface.getHosts(encode=False):
			if i_source['name'].lower() in source.lower() and i_source['downloading']:
				bool = True
				break

		if bool == False:
			return MC.message_container('Download Sources', 'No compatible Download service found for this URL !')
			
		title = common.cleantitle.windows_filename(title)
		tuec = E(title+year+quality+source+url+str(season)+str(episode))
			
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
					if common.DEV_DEBUG == True and Prefs["use_debug"]:
						Log('Url: %s | FileSize: %s | Error: %s' % (url, fs_i, err))
					try:
						ret_val_resolvers = None
						# check if file-link valid using fs of 1MB
						if fs_i != None and float(fs_i) > float(1024*1024): # 1MB
							pass
						else:
							# ret_val_resolvers is always a tuple with first val. of returned list of urls and second of error...
							ret_val_resolvers = common.interface.getHostResolverMain().resolve(url, page_url=page_url)
							err = ret_val_resolvers[1]
							if err != '':
								Log('Host URL: %s' % url)
								Log('Host URL Resolved: %s' % ret_val_resolvers[0])
								Log('Host Error: %s' % err)
							else:
								vurl = ret_val_resolvers[0]
								headers = None
								try:
									if vurl != None and len(vurl) >= seq:
										vurl = vurl[seq]
									else:
										vurl = vurl[0]
									params = json.loads(base64.b64decode(ret_val_resolvers[2]))
									if 'headers' in params.keys():
										headers = params['headers']
								except:
									pass
								fs_i, err = common.client.getFileSize(vurl, headers=headers, retError=True, retry429=True, cl=2)
								if common.DEV_DEBUG == True and Prefs["use_debug"]:
									Log('Host URL: %s | FileSize: %s | Host URL Resolved: %s' % (url, fs_i, vurl))
					except Exception as e:
						err = '%s' % e
						if common.DEV_DEBUG == True and Prefs["use_debug"]:
							Log(e)
							Log('Host URLs: %s' % ret_val_resolvers[0])
							
				if err != '':
					return MC.message_container('Error', 'Error: %s. Please try again later when it becomes available.' % err)
					
				try:
					fsBytes = int(fs_i)
					fs = '%s GB' % str(round(float(fs_i)/common.TO_GB, 3))
				except:
					fsBytes = 0
					fs = '? GB'
					
				if float(fsBytes) < float(1024*1024): # 1MB
					return MC.message_container('FileSize Error', 'File reporting %s bytes cannot be downloaded. Please try again later when it becomes available.' % fsBytes)

			except Exception as e:
				Log('ERROR: downloadsmenu.py > AddToDownloadsListPre : %s - %s' % (e,err))
				return MC.message_container('Error', '%s. Sorry but file could not be added.' % e)

		uid = 'Down5Split'+E(title+year+fs+quality+source+str(season)+str(episode))
		uid_alts = common.uidAltExists(uid)
		
		if uid_upd != None:
			uid = uid_upd
		else:
			if len(uid_alts) > 0:
				uid = uid_alts[len(uid_alts)-1]
		
		if force_add == False and Dict[uid] != None:

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
				
				for u_i in uid_alts:
					EncTxt_t = Dict[u_i]				
					EncTxt_t = JSON.ObjectFromString(D(EncTxt_t))
					timestr_t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(EncTxt_t['timeAdded'])))
			
					if EncTxt_t['status'] == common.DOWNLOAD_STATUS[2]:
						t_exists = 'Item in Completed Downloads %s | %s' % (EncTxt_t['section_path'],timestr_t)
						oc.add(DirectoryObject(title = '<< %s >>' % t_exists, key = Callback(main.MyMessage, title='Item Exists', msg=t_exists)))
					else:
						oc.add(DirectoryObject(key = Callback(AddToDownloadsListPre, title=title, purl=purl, url=url, durl=durl, summary=summary, thumb=thumb, year=year, quality=quality, source=source, source_meta=source_meta, file_meta=file_meta, type=type, resumable=resumable, sub_url=sub_url, fsBytes=fsBytes, fs=fs, file_ext=file_ext, mode=mode, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, update=True, params=params, riptype=riptype, season=season, episode=episode, provider=provider, page_url=page_url, seq=seq, uid_upd=u_i), title = 'Update item. %s | %s | %s' % (EncTxt_t['section_path'],EncTxt_t['fid'],timestr_t)))
							
				oc.add(DirectoryObject(key = Callback(AddToDownloadsListPre, title=title, purl=purl, url=url, durl=durl, summary=summary, thumb=thumb, year=year, quality=quality, source=source, source_meta=source_meta, file_meta=file_meta, type=type, resumable=resumable, sub_url=sub_url, fsBytes=fsBytes, fs=fs, file_ext=file_ext, mode=mode, vidtype=vidtype, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, update=False, params=params, riptype=riptype, season=season, episode=episode, provider=provider, page_url=page_url, seq=seq, force_add=True), title = 'Add as New < Item will be duplicated >'))	
				oc.add(DirectoryObject(key = Callback(Downloads, title=" Downloads", session = session), title = "<< Downloads"))
				oc.add(DirectoryObject(key = Callback(main.MainMenu), title = '<< Main Menu'))
				return oc
			elif admin == True and update == True and EncTxt['url'] == url:
				return MC.message_container('Item Updated', 'Item url updated.')
			elif admin == True and update == False and EncTxt['url'] == url:
				#return MC.message_container('Item Updated', 'Item url is up to date.')
				pass
			elif EncTxt['url'] != url:
				pass
			else:
				return MC.message_container('Item Updated', 'Please return to previous screen.')

			#uid = 'Request5Split'+E(title+year+fs+quality+source+'%s' % season + '%s' % episode)
			#if Dict[uid] != None:
			#	return MC.message_container('Requested Sources', 'Item already in Requested List')
				
		if mode == common.DOWNLOAD_MODE[1]:
			if file_ext == None:
				file_ext = '.mp4'

			chunk_size = int(1024.0 * 1024.0 * float(common.DOWNLOAD_CHUNK_SIZE)) # in bytes
			fid = '.'+common.id_generator()
			
			EncTxt = E(JSON.StringFromObject({'title':title, 'year':year, 'url':url, 'durl':durl, 'purl':purl, 'sub_url':sub_url, 'summary':summary, 'thumb':thumb, 'fsBytes':int(fsBytes), 'fs':fs, 'chunk_size':chunk_size, 'file_ext':file_ext, 'quality':quality, 'source':source, 'source_meta':source_meta, 'file_meta':file_meta, 'uid':uid, 'fid':fid, 'type':type, 'vidtype':vidtype, 'resumable':resumable, 'status':common.DOWNLOAD_STATUS[4], 'startPos':0, 'timeAdded':time.time(), 'first_time':time.time(), 'progress':0, 'chunk_speed':0,'avg_speed':0,'avg_speed_curr':0, 'eta':0, 'error':'', 'last_error':'Unknown Error', 'action':common.DOWNLOAD_PROPS[3],'section_path':section_path, 'section_title':section_title, 'section_key':section_key, 'user':user, 'provider':provider})) 
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
			
		return AddToDownloadsList(title=title, purl=purl, url=url, durl=durl, summary=summary, thumb=thumb, year=year, quality=quality, source=source, source_meta=source_meta, file_meta=file_meta, type=type, vidtype=vidtype, resumable=resumable, sub_url=sub_url, fsBytes=fsBytes, fs=fs, file_ext=file_ext, mode=mode, section_path=section_path, section_title=section_title, section_key=section_key, session=session, admin=admin, update=update, user=user,params=params, riptype=riptype, season=season, episode=episode, provider=provider, page_url=page_url, seq=seq, force_add=force_add)
	except Exception as e:
		err = '{}'.format(e)
		Log('Error AddToDownloadsListPre: %s' % err)
		return MC.message_container('Error', '%s. Sorry but file could not be added.' % err)
	
######################################################################################
# Adds a movie to the DownloadsList list using the (title + 'Down5Split') as a key for the url
@route(PREFIX + "/addToDownloadsList")
def AddToDownloadsList(title, year, url, durl, purl, summary, thumb, quality, source, type, resumable, source_meta, file_meta, sub_url=None, fsBytes=None, fs=None, file_ext=None, vidtype=None, section_path=None, section_title=None, section_key=None, session=None, admin=False, update=False, user=None, params=None, riptype=None, season=None, episode=None, provider=None, page_url=None, seq=0, force_add=False, **kwargs):

	admin = True if str(admin) == 'True' else False
	update = True if str(update) == 'True' else False
	resumable = True if str(resumable) == 'True' else False
	force_add = True if str(force_add) == 'True' else False
	
	#Log(common.DOWNLOAD_OPTIONS_SECTION_TEMP)
	tuec = E(title+year+quality+source+url+str(season)+str(episode))
	
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
				return AddToDownloadsList(title=title, year=year, url=url, durl=durl, purl=purl, summary=summary, thumb=thumb, fs=fs, fsBytes=fsBytes, file_ext=file_ext, quality=quality, source=source, source_meta=source_meta, file_meta=file_meta, type=type, vidtype=vidtype, resumable=resumable, sub_url=sub_url, section_path=item['path'], section_title=item['title'], section_key=item['key'], session=session, admin=admin, update=update, user=user, params=params, riptype=riptype, season=season, episode=episode, provider=provider, page_url=page_url, seq=seq, force_add=force_add)
			else:
				oc = ObjectContainer(title1='Select Location', no_cache=common.isForceNoCache())
				for item in DOWNLOAD_OPTIONS_SECTION_TEMP[type]:
					if item['enabled']:
						oc.add(DirectoryObject(
							key = Callback(AddToDownloadsList, title=title, year=year, url=url, durl=durl, purl=purl, summary=summary, thumb=thumb, fs=fs, fsBytes=fsBytes, file_ext=file_ext, quality=quality, source=source, source_meta=source_meta, file_meta=file_meta, type=type, vidtype=vidtype, resumable=resumable, sub_url=sub_url, section_path=item['path'], section_title=item['title'], section_key=item['key'], session=session, admin=admin, update=update, user=user, params=params, riptype=riptype, season=season, episode=episode, provider=provider, page_url=page_url, seq=seq, force_add=force_add),
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
				
			uid = 'Down5Split'+E(title+year+fs+quality+source+str(season)+str(episode))
			if Dict[uid] != None:
				if admin == True and force_add == True:
					uid_c = 0
					while Dict[uid] != None:
						uid_c += 1
						uid = 'Down5Split'+E(title+year+fs+quality+source+str(season)+str(episode))+'-%s' % str(uid_c)
				else:
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
			
			if type == 'show':
				if int(episode) < 100:
					watch_title = '%s S%sE%02d' % (title,int(season),int(episode))
				else:
					watch_title = '%s S%sE%03d' % (title,int(season),int(episode))
			else:
				watch_title = title
	
			EncTxt = E(JSON.StringFromObject({'title':title, 'watch_title':watch_title, 'year':year, 'season':season, 'episode':episode, 'url':url, 'durl':durl, 'purl':purl, 'sub_url':sub_url, 'summary':summary, 'thumb':thumb, 'fsBytes':int(fsBytes), 'fs':fs, 'chunk_size':chunk_size, 'file_ext':file_ext, 'quality':quality, 'source':source, 'source_meta':source_meta, 'file_meta':file_meta, 'uid':uid, 'fid':fid, 'type':type, 'vidtype':vidtype, 'resumable':resumable, 'status':common.DOWNLOAD_STATUS[0], 'startPos':0, 'timeAdded':time.time(), 'first_time':time.time(), 'progress':0, 'chunk_speed':0,'avg_speed':0,'avg_speed_curr':0, 'eta':0, 'error':'', 'last_error':'Unknown Error', 'action':common.DOWNLOAD_ACTIONS[4],'section_path':section_path, 'section_title':section_title, 'section_key':section_key, 'user':user, 'params':params, 'riptype':riptype, 'provider':provider, 'page_url':page_url, 'seq':int(seq)})) 
			
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
def Downloads(title, session = None, status = None, refresh = 0, isDir='N', item=None, **kwargs):

	if not common.interface.isInitialized():
		return MC.message_container(common.MSG0, '%s. Progress %s%s (%s)' % (common.MSG1, common.interface.getProvidersInitStatus(), '%', common.interface.getCurrentProviderInProcess()))
	
	oc = ObjectContainer(title1=title, no_cache=common.isForceNoCache())
	
	try:
		if status == None:
			N_status = {}
			for dstatus in common.DOWNLOAD_STATUS:
				c = 0
				if dstatus == common.DOWNLOAD_STATUS[6]: # AutoPilot Queue
					for k in common.DOWNLOAD_AUTOPILOT.keys():
						c += len(common.DOWNLOAD_AUTOPILOT[k])
					N_status[dstatus] = c
				else:
					c = 0
					for each in Dict:
						if 'Down5Split' in each:
							try:
								longstringObjs = JSON.ObjectFromString(D(Dict[each]))
								if longstringObjs['status'] == dstatus  or dstatus == common.DOWNLOAD_STATUS[5]: # All
									c += 1
							except Exception as e:
								Log('ERROR: Downloads >> %s' % e)
					N_status[dstatus] = c
			for statusx in common.DOWNLOAD_STATUS:
				oc.add(DirectoryObject(
					key = Callback(Downloads, title="%s Downloads" % statusx, status = statusx, session = session, isDir='N'),
					title = '%s (%s)' % (statusx, str(N_status[statusx]))
					)
				)
			oc.add(DirectoryObject(key = Callback(Downloads, title="Downloads", session = session, refresh = int(refresh)+1), title = "Refresh"))
			oc.add(DirectoryObject(key = Callback(main.MainMenu), title = '<< Main Menu', thumb = R(common.ICON)))
			return oc
		
		items_to_del = []
		doTrigger = False
		first_episode = 0
		last_episode = 1
		
		if status == common.DOWNLOAD_STATUS[6]: # Auto-Pilot
			doSave = False
			shows_array = {}
			for k in common.DOWNLOAD_AUTOPILOT.keys():
				for i in common.DOWNLOAD_AUTOPILOT[k]:
					try:
						q_fs = i['quality'] if i['quality'] != None else i['file_size']
						rip = i['riptype']
						try:
							q_fs1 = q_fs.split(':')
							q_fs_t = '%s GB - %s GB' % (str(round(float(q_fs1[0])/common.TO_GB, 3)), str(round(float(q_fs1[1])/common.TO_GB, 3)))
							q_fs = q_fs_t
						except:
							pass

						timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(i['timeAdded'])))
						ooc = None
						addShow = False
						if k == 'show':
							show_t = '%s:%s'%(i['short_title'],i['season'])
							if isDir == 'N':
								if show_t not in shows_array.keys():
									ooc = DirectoryObject(title=show_t, 
										thumb = common.GetThumb(i['thumb'], session=session),
										summary = i['summary'],
										tagline = timestr,
										key = Callback(Downloads, title=show_t, session=session, status=status, isDir='Y', item=E(JSON.StringFromObject(i)))
									)
									shows_array[show_t] = ooc
								elif isDir == 'Y':
									addShow = True
							if isDir == 'Y' and show_t == title:
								addShow = True
								wtitle = '%s | %s | %s | %s | %s | %s' % (i['watch_title'], k.title(), rip, q_fs, i['status'], timestr)
								last_episode = i['episode']
								first_episode_x = int(i['episode'])
								if first_episode == 0:
									first_episode = first_episode_x
								if first_episode_x < first_episode:
									first_episode = first_episode_x
								Log('Item: %s %s %s' % (title, int(i['season']), int(i['episode'])))
						elif k == 'extras':
							if isDir == 'N':
								addShow = True
								wtitle = '%s (%s) | %s - %s | %s | %s | %s | %s' % (i['title'], i['year'], k.title(), i['vidtype'], rip, q_fs, i['status'], timestr)
						else:
							if isDir == 'N':
								addShow = True
								wtitle = '%s (%s) | %s | %s | %s | %s | %s' % (i['title'], i['year'], k.title(), rip, q_fs, i['status'], timestr)
						
						if ooc != None:
							oc.add(ooc)
						else:
							if addShow == True:
								#key = Callback(main.MyMessage, title='Info', msg=wtitle)
								key = Callback(DownloadingFilesMenu, title=i['watch_title'], uid=i['uid'], session=session, status=status, autopilot=True, type=k)
								
								do = DirectoryObject(
									title = wtitle,
									thumb = common.GetThumb(i['thumb'], session=session),
									summary = i['summary'],
									tagline = timestr,
									key = key
								)
								oc.add(do)
					except Exception as e:
						Log("==============Downloads==============")
						#Log(longstringObjs)
						Log(e)
						common.DOWNLOAD_AUTOPILOT[k].remove(i)
						doSave = True

			if doSave == True:
				Dict['DOWNLOAD_AUTOPILOT'] = E(JSON.StringFromObject(common.DOWNLOAD_AUTOPILOT))
				Dict.Save()
		else:
			for each in Dict:
				if 'Down5Split' in each:
					try:
						longstringObjs = JSON.ObjectFromString(D(Dict[each]))
						if 'watch_title' not in longstringObjs.keys():
							if longstringObjs['type'] == 'show':
								try:
									if int(longstringObjs['episode']) < 100:
										longstringObjs['watch_title'] = '%s S%sE%02d' % (longstringObjs['title'],int(longstringObjs['season']),int(longstringObjs['episode']))
									else:
										longstringObjs['watch_title'] = '%s S%sE%03d' % (longstringObjs['title'],int(longstringObjs['season']),int(longstringObjs['episode']))
								except Exception as e:
									Log('Error in Downloads > %s' % e)
									longstringObjs['watch_title'] = longstringObjs['title']
							else:
								longstringObjs['watch_title'] = longstringObjs['title']
							
						if longstringObjs['status'] == status or status == common.DOWNLOAD_STATUS[5]: # All
							timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(longstringObjs['timeAdded'])))
							key = None
							summary = longstringObjs['summary']
							has_sub = False if longstringObjs['sub_url'] == None else True
							
							if status == common.DOWNLOAD_STATUS[0]: # Queued
								wtitle = '%s (%s) | %s | %s - %s | %s [%s] | %s - %s | %s | Subtitle:%s' % (longstringObjs['watch_title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['provider'] if 'provider' in longstringObjs.keys() else 'N/A', longstringObjs['status'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', common.GetEmoji(type=has_sub, mode='simple', session=session))
								key = Callback(DownloadingFilesMenu, title=longstringObjs['watch_title'], uid=longstringObjs['uid'], choice=None, session=session, status=status)
							elif status == common.DOWNLOAD_STATUS[1]: # Downloading
								if each not in common.DOWNLOAD_STATS.keys() and len(common.DOWNLOAD_STATS.keys()) < int(Prefs['download_connections']):
									longstringObjs['status'] = common.DOWNLOAD_STATUS[1] # Downloading
									longstringObjs['action'] = common.DOWNLOAD_ACTIONS[4] # Start Download
									Dict[each] = E(JSON.StringFromObject(longstringObjs))
									
									#longstringObjs['status'] = common.DOWNLOAD_STATUS[1]
									#common.DOWNLOAD_STATS[each] = Dict[each]
									#doTrigger = True
									
									EncTxt = E(JSON.StringFromObject(longstringObjs))
									Thread.Create(download.do_download, {}, file_meta_enc=EncTxt)
								elif each not in common.DOWNLOAD_STATS.keys():
									longstringObjs['status'] = common.DOWNLOAD_STATUS[0] # Queued
									longstringObjs['action'] = common.DOWNLOAD_ACTIONS[4] # Start Download
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
									
								wtitle = '%s (%s) | %s | %s - %s | %s [%s] | %s - %s | %s | %s MB/s ~ %s MB/s ~ %s MB/s | %s | Subtitle:%s' % (longstringObjs['watch_title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['provider'] if 'provider' in longstringObjs.keys() else 'N/A', longstringObjs['status'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', str(longstringObjs['chunk_speed']), str(longstringObjs['avg_speed_curr']), str(longstringObjs['avg_speed']), str(eta_str), common.GetEmoji(type=has_sub, mode='simple', session=session))
								key = Callback(DownloadingFilesMenu, title=longstringObjs['watch_title'], uid=longstringObjs['uid'], choice=None, session=session, status=status)
							elif status == common.DOWNLOAD_STATUS[2]: # Completed
								wtitle = '%s (%s) | %s | %s - %s | %s [%s] | %s - %s | %s | %s MB/s | Subtitle:%s' % (longstringObjs['watch_title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['provider'] if 'provider' in longstringObjs.keys() else 'N/A', longstringObjs['status'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', str(longstringObjs['avg_speed_curr']), common.GetEmoji(type=has_sub, mode='simple', session=session))
								key = Callback(DownloadingFilesMenu, title=longstringObjs['watch_title'], uid=longstringObjs['uid'], choice=None, session=session, status=status)
							elif status == common.DOWNLOAD_STATUS[3]: # Failed
								err = longstringObjs['last_error'] if longstringObjs['error'] == '' else longstringObjs['error']
								wtitle = '%s (%s) | %s | %s - %s | %s | %s | %s - %s' % (longstringObjs['watch_title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], str(longstringObjs['progress'])+'%', longstringObjs['status'], err)
								key = Callback(DownloadingFilesMenu, title=longstringObjs['watch_title'], uid=longstringObjs['uid'], choice=None, session=session, status=status)
								summary = '%s | %s' % (wtitle, summary)
							elif status == common.DOWNLOAD_STATUS[4]: # Requested
								if 'user' in longstringObjs.keys() and longstringObjs['user'] != None and AuthTools.CheckAdmin() == True:
									wtitle = '%s (%s) | %s | %s - %s | %s | %s (by %s) - %s | %s | %s MB/s | Subtitle:%s' % (longstringObjs['watch_title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['status'], longstringObjs['user'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', str(longstringObjs['avg_speed_curr']), common.GetEmoji(type=has_sub, mode='simple', session=session))
								else:
									wtitle = '%s (%s) | %s | %s - %s | %s | %s - %s | %s | %s MB/s | Subtitle:%s' % (longstringObjs['watch_title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['status'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', str(longstringObjs['avg_speed_curr']), common.GetEmoji(type=has_sub, mode='simple', session=session))
								key = Callback(DownloadingFilesMenu, title=longstringObjs['watch_title'], uid=longstringObjs['uid'], choice=None, session=session, status=status)
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
										
									wtitle = '%s (%s) | %s | %s - %s | %s | %s - %s | %s | %s MB/s ~ %s MB/s ~ %s MB/s | %s | Subtitle:%s' % (longstringObjs['watch_title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['status'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', str(longstringObjs['chunk_speed']), str(longstringObjs['avg_speed_curr']), str(longstringObjs['avg_speed']), str(eta_str), common.GetEmoji(type=has_sub, mode='simple', session=session))
								else:
									wtitle = '%s (%s) | %s | %s - %s | %s | %s - %s | %s | %s MB/s | Subtitle:%s' % (longstringObjs['watch_title'], longstringObjs['year'], longstringObjs['type'].title(), longstringObjs['fs'], longstringObjs['quality'], longstringObjs['source'], longstringObjs['status'], common.DOWNLOAD_ACTIONS_K[longstringObjs['action']], str(longstringObjs['progress'])+'%', str(longstringObjs['avg_speed_curr']), common.GetEmoji(type=has_sub, mode='simple', session=session))
									
								key = Callback(DownloadingFilesMenu, title=longstringObjs['watch_title'], uid=longstringObjs['uid'], choice=None, session=session, status=longstringObjs['status'])
								
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
						#items_to_del.append(each)
					
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
					Log("Deleting: %s" % longstringObjs['watch_title'])
					del Dict[each]
				except:
					Log("Deleting: %s" % each)
					del Dict[each]
				
			Dict.Save()
		
		if doTrigger == True:
			Thread.Create(download.trigger_que_run)

		if len(oc) == 0:
			return MC.message_container(title, 'No %s section videos available' % status)
				
		if isDir == 'Y':
			oc.objects.sort(key=lambda obj: obj.title, reverse=False)
		else:
			oc.objects.sort(key=lambda obj: obj.tagline, reverse=not common.UsingOption(key=common.DEVICE_OPTIONS[12], session=session))
			
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
			if isDir == 'Y':
				i = json.loads(D(item))
				oc.add(DirectoryObject(
					title = 'Update Entry for %s' % title,
					key = Callback(AddToAutoPilotDownloads, title=i['short_title'], year=i['year'], type=i['type'], purl=i['purl'], thumb=i['thumb'], summary=i['summary'], quality=None, file_size=None, riptype=i['riptype'], season=i['season'], season_end=i['season'], episode_start=int(first_episode), episode_end=int(last_episode), vidtype=i['vidtype'], section_path=None, section_title=None, section_key=None, session=session, admin=i['admin'], all_seasons=False, edit=False, mode=None),
					summary = 'Update Entry for %s' % title,
					thumb = common.GetThumb(R(common.ICON_UPDATER), session=session)
					)
				)
			oc.add(DirectoryObject(
				title = 'Refresh %s Downloads' % status,
				key = Callback(Downloads,title=title, status=status, session=session, refresh=int(refresh)+1, isDir=isDir, item=item),
				summary = 'Refresh %s Download Entries' % status,
				thumb = common.GetThumb(R(common.ICON_REFRESH), session=session)
				)
			)
			if isDir == 'Y':
				oc.add(DirectoryObject(
					title = 'Clear %s %s Downloads' % (title, status),
					key = Callback(ClearDownLoadSection, status=status, session=session, dir=title),
					summary = 'Remove %s %s Download Entries' % (title, status),
					thumb = common.GetThumb(R(common.ICON_NOTOK), session=session)
					)
				)
			else:
				oc.add(DirectoryObject(
				title = 'Clear %s Downloads' % status,
				key = Callback(ClearDownLoadSection, status=status, session=session),
				summary = 'Remove %s Download Entries' % status,
				thumb = common.GetThumb(R(common.ICON_NOTOK), session=session)
				)
			)
			
		#oc.objects.sort(key=lambda obj: obj.title, reverse=False)
		oc.add(DirectoryObject(key = Callback(main.MainMenu), title = '<< Main Menu', thumb = R(common.ICON)))
			
		return oc
	except Exception as e:
		Log.Error(e)
		return MC.message_container('Downloads', 'An error occurred. Please try again !')
	
######################################################################################
@route(PREFIX + "/DownloadingFilesMenu")
def DownloadingFilesMenu(title, uid, choice=None, session=None, status=None, confirm=False, refresh=0, autopilot=False, type=None):
	
	oc = ObjectContainer(title1=title, no_cache=common.isForceNoCache())
	
	confirm = True if str(confirm) == 'True' else False
	autopilot = True if str(autopilot) == 'True' else False
	
	if autopilot == True:
		k = type
		for i in common.DOWNLOAD_AUTOPILOT[k]:
				try:
					if choice == common.DOWNLOAD_ACTIONS[0] and confirm == False and uid == i['uid']:
						oc = ObjectContainer(title1=unicode('Confirm ?'), no_cache=common.isForceNoCache())
						oc.add(DirectoryObject(title = 'YES - Clear %s Entry' % title, key = Callback(DownloadingFilesMenu, title=title, uid=uid, choice=choice, session=session, status=status, confirm=True, autopilot=autopilot, type=type), thumb = R(common.ICON_OK)))
						oc.add(DirectoryObject(title = 'NO - Dont Clear %s Entry' % title, key = Callback(main.MyMessage, title='No Selected', msg='Return to previous screen'),thumb = R(common.ICON_NOTOK)))
						return oc
						
					elif choice == common.DOWNLOAD_ACTIONS[0] and confirm == True and uid == i['uid']:
						common.DOWNLOAD_AUTOPILOT[k].remove(i)
						Dict['DOWNLOAD_AUTOPILOT'] = E(JSON.StringFromObject(common.DOWNLOAD_AUTOPILOT))
						Dict.Save()
						return MC.message_container('Removed', 'Item has been removed')
					else:
						if uid == i['uid']:
							q_fs = i['quality'] if i['quality'] != None else i['file_size']
							try:
								q_fs1 = q_fs.split(':')
								q_fs_t = '%s GB - %s GB' % (str(round(float(q_fs1[0])/common.TO_GB, 3)), str(round(float(q_fs1[1])/common.TO_GB, 3)))
								q_fs = q_fs_t
							except:
								pass

							timestr = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(i['timeAdded'])))
							if k == 'show':
								wtitle = '%s | %s | %s | %s | %s' % (i['watch_title'], k.title(), q_fs, i['status'], timestr)
							elif k == 'extras':
								wtitle = '%s (%s) | %s - %s | %s | %s | %s' % (i['title'], i['year'], k.title(), i['vidtype'], q_fs, i['status'], timestr)
							else:
								wtitle = '%s (%s) | %s | %s | %s | %s' % (i['title'], i['year'], k.title(), q_fs, i['status'], timestr)
							
							key = Callback(DownloadingFilesMenu, title=i['watch_title'], uid=i['uid'], choice=common.DOWNLOAD_ACTIONS[0], session=session, status=status, autopilot=autopilot, type=type)
							oc.add(DirectoryObject(
								title = 'Delete Entry - %s' % i['watch_title'],
								thumb = common.GetThumb(i['thumb'], session=session),
								summary = 'Delete this entry from the Auto-Pilot list',
								tagline = timestr,
								key = key
								)
							)
							oc.add(DirectoryObject(
								title = 'Update Entry for %s' % i['watch_title'],
								key = Callback(AddToAutoPilotDownloads, title=i['title'], year=i['year'], type=i['type'], purl=i['purl'], thumb=i['thumb'], summary=i['summary'], quality=None, file_size=None, riptype=i['riptype'], season=None, season_end=None, episode_start=None, episode_end=None, vidtype=i['vidtype'], section_path=None, section_title=None, section_key=None, session=session, admin=i['admin'], all_seasons=False, edit=False, mode=None),
								summary = 'Update Entry for %s' % i['watch_title'],
								thumb = common.GetThumb(R(common.ICON_UPDATER), session=session)
								)
							)
							return oc

				except Exception as e:
					Log("==============Downloads==============")
					#Log(longstringObjs)
					Log(e)
		return MC.message_container('Unavailable', 'Item removed or no longer available')
	else:
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
					key = Callback(main.MyMessage, title='Info', msg=i_title),
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
						key = Callback(main.MyMessage, title='Download Path', msg=longstringObjs['section_path']),
						thumb = common.GetThumb(R(common.ICON_ENTER), session=session)
						)
					)
				if longstringObjs['purl'] != None:
					oc.add(DirectoryObject(
						title = 'Video Page (Other Download Sources)',
						summary = 'Video Page: %s' % longstringObjs['title'],
						key = Callback(main.EpisodeDetail, title=longstringObjs['title'], url=longstringObjs['purl'], thumb=longstringObjs['thumb'], session = session),
						thumb = common.GetThumb(R(common.ICON_ENTER), session=session)
						)
					)
				else:
					oc.add(DirectoryObject(
						title = 'Video Page (Unavailable)',
						summary = 'Video Page: %s' % longstringObjs['title'],
						key = Callback(main.MyMessage, title='Video Page', msg='This Video Page is Unavailable'),
						thumb = common.GetThumb(R(common.ICON_ENTER), session=session)
						)
					)
				if status == common.DOWNLOAD_STATUS[2]:
					oc.add(DirectoryObject(
						title = 'Clear',
						key = Callback(DownloadingFilesMenu, title=longstringObjs['watch_title'], uid=uid, choice=common.DOWNLOAD_ACTIONS[0], session=session, status=status),
						summary = 'Clear %s' % longstringObjs['watch_title'],
						thumb = common.GetThumb(R(common.ICON_ENTER), session=session)
						)
					)
				oc.add(DirectoryObject(
					title = 'Refresh',
					key = Callback(DownloadingFilesMenu, title=title, uid=uid, choice=choice, session=session, status=status, confirm=confirm, refresh=int(refresh)+1),
					summary = 'Refresh Stats for %s' % longstringObjs['watch_title'],
					thumb = common.GetThumb(R(common.ICON_REFRESH), session=session)
					)
				)
			except Exception as e:
				Log(e)
				return MC.message_container('Unavailable', 'Item removed or no longer available')

			oc.add(DirectoryObject(key = Callback(main.MainMenu), title = '<< Main Menu', thumb = R(common.ICON)))
			return oc
			
		else:
			if AuthTools.CheckAdmin() == False:
				return MC.message_container('Admin Access Only', 'Only the Admin can perform this action !')
			
			if uid in Dict and choice != None:
				if choice == common.DOWNLOAD_ACTIONS[0] and confirm == False:
					oc = ObjectContainer(title1=unicode('Confirm ?'), no_cache=common.isForceNoCache())
					oc.add(DirectoryObject(title = 'YES - Clear %s Entry' % title, key = Callback(DownloadingFilesMenu, title=title, uid=uid, choice=choice, session=session, status=status, confirm=True), thumb = R(common.ICON_OK)))
					oc.add(DirectoryObject(title = 'NO - Dont Clear %s Entry' % title, key = Callback(main.MyMessage, title='No Selected', msg='Return to previous screen'),thumb = R(common.ICON_NOTOK)))
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
def ClearDownLoadSection(status, session, dir=None, confirm=False):

	if AuthTools.CheckAdmin() == False:
		return MC.message_container('Admin Access Only', 'Only the Admin can perform this action !')

	if confirm == False:
		oc = ObjectContainer(title1=unicode('Confirm ?'), no_cache=common.isForceNoCache())
		oc.add(DirectoryObject(title = 'YES - Clear %s Entries' % status, key = Callback(ClearDownLoadSection, status=status, session=session, dir=dir, confirm=True),thumb = R(common.ICON_OK)))
		oc.add(DirectoryObject(title = 'NO - Dont Clear %s Entries' % status, key = Callback(main.MyMessage, title='No Selected', msg='Return to previous screen'),thumb = R(common.ICON_NOTOK)))
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
				
	if status == common.DOWNLOAD_STATUS[6]: # Auto-Pilot
		if dir == None:
			common.DOWNLOAD_AUTOPILOT = common.DOWNLOAD_AUTOPILOT_CONST.copy()
		else:
			for i in common.DOWNLOAD_AUTOPILOT['show']:
				short_title = '%s:%s' % (i['short_title'], i['season'])
				if short_title == dir:
					items_to_del.append(i)
			for ix in items_to_del:
				for i in common.DOWNLOAD_AUTOPILOT['show']:
					short_title_ix = '%s:%s' % (ix['short_title'], ix['season'])
					short_title_i = '%s:%s' % (i['short_title'], i['season'])
					if short_title_ix == short_title_i:
						common.DOWNLOAD_AUTOPILOT['show'].remove(i)
						
			del items_to_del[:]
			Dict['DOWNLOAD_AUTOPILOT'] = E(JSON.StringFromObject(common.DOWNLOAD_AUTOPILOT))
			Dict.Save()
		
	elif len(items_to_del) > 0:
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
			elif status == common.DOWNLOAD_STATUS[6]: # Auto-Pilot
				common.DOWNLOAD_AUTOPILOT = common.DOWNLOAD_AUTOPILOT_CONST.copy()
				Dict['DOWNLOAD_AUTOPILOT'] = E(JSON.StringFromObject(common.DOWNLOAD_AUTOPILOT))
				break
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
	