#
# Coder Alpha
# https://github.com/coder-alpha
#
# Adapted/Inspired from SS-Plex
# Author mikew : https://github.com/mikew
# https://forums.plex.tv/discussion/48412/rel-ss-plex/p1
# http://mikew.github.io/ss-plex.bundle/
# 

import os, io, time, traceback, base64, json
import requests
import common
from resources.lib.libraries import workers

from __builtin__ import sum

DLT = []
Dict['DOWNLOAD_RATE_LIMIT_BUFFER'] = []
Dict['DOWNLOAD_RATE_LIMIT_TIME'] = []
REMAP_EXTRAS = {'behind the scenes':'behindthescenes', 'deleted scenes':'deleted', 'featurette':'featurette', 'interviews':'interview', 'misc.':'scene', 'music video':'short', 'trailer':'trailer'}

AUTOPILOT_SCHEDULER = [False]
AUTOPILOT_SCHEDULER_POST_REFRESH = []

QUEUE_RUN_ITEMS = {}
WAIT_AND_RETRY_ON_429 = True
CONNECTION_TIMEOUT = 60
FLAG_3D = '.3D.HSBS'

def query_pms(path):
	return 'http://127.0.0.1:32400%s' % path

def refresh_section(section_title, section_key):
	
	if Prefs['use_debug']:
		Log("** Refreshing User Library Section Title: %s Section Key: %s **" % (section_title, section_key))
	
	HTTP.Request(query_pms('/library/sections/%s/refresh' % section_key), immediate = True)
	
	# try:
		# s = requests.Session()
		# s.get(query_pms('/library/sections/%s/refresh' % section_key))
	# except Exception as e:
		# Log(e)

# params: movie, show
def section_info(section):
	
	#strobj = HTTP.Request(query_pms('/library/sections'))
	#Log(strobj)
	xmlobj = XML.ElementFromURL(query_pms('/library/sections'), cacheTime = 0)
	query = '//Directory[@type="%s"]' % section
	matching = filter(lambda el: '.none' not in el.get('agent'), xmlobj.xpath(query))
	locations_dir = []
	
	try:
		for directory in matching:
			#Log(directory.get('title'))
			locations = directory.xpath('./Location')
			c = 0
			for location in locations:
				path = location.get('path')
				#Log(path)
				if directory.get('type') == section:
					locations_dir.append([directory.get('key'), directory.get('type'), directory.get('title'), location.get('path')])
		
			if len(locations_dir) == 0:
				locations_dir.append([directory.get('key'), directory.get('type'), directory.get('title'), locations[0].get('path')])
	except:
		pass
		
	return locations_dir

##############################################################################################
	
class DownloadThrottler(object):
	def __init__(self):
		self.threadRun = True
		self.DOWNLOAD_RATE_LIMIT_BUFFER = []
		self.updateTime = 1 # 1 sec.
		self.throttle = False
		self.throttleStateSleepTime = 0.0
	
	def addBytes(self, b):
		self.DOWNLOAD_RATE_LIMIT_BUFFER.append(b)
		
	def reset(self):
		del self.DOWNLOAD_RATE_LIMIT_BUFFER[:]
		self.throttle = False
		self.throttleStateSleepTime = 0.0
		
	def getThrottleState(self):
		return self.throttle
		
	def getThrottleStateSleepTime(self):
		return self.throttleStateSleepTime
		
	def start(self):
		Thread.Create(self.DownloadThrottlerThread)
		
	def DownloadThrottlerThread(self):
		while self.threadRun:
			time.sleep(self.updateTime)
			
			tot_down_size_KB = float(sum(self.DOWNLOAD_RATE_LIMIT_BUFFER)/1024.0)
			download_speed_limit_KBps = float(Prefs['download_speed_limit'])
			if tot_down_size_KB > 0 and download_speed_limit_KBps > 0:
				tot_down_speed_KBps = round(float(tot_down_size_KB/self.updateTime), 3)
				if Prefs['use_debug']:
					Log('Download Throttler:---> Timestamp:%s | Total Down Speed: %s KB/s | Speed Limit: %s KB/s' % (time.time(), tot_down_speed_KBps, download_speed_limit_KBps))
				
				if tot_down_speed_KBps > download_speed_limit_KBps:
					self.throttle = True
					self.throttleStateSleepTime = round(tot_down_speed_KBps/download_speed_limit_KBps,3)
					if Prefs['use_debug']:
						Log("Download Throttler:---> Sleep for %s sec." % self.throttleStateSleepTime)
					time.sleep(self.throttleStateSleepTime)
					
			self.reset()
			
def resetDownloadThrottler():
	if len(DLT) > 0:
		DLT[0].reset()
	
##############################################################################################
	
class Downloader(object):
	def __init__(self):
		self.dlthrottle = None

	def setDownloadThrottler(self, d):
		self.dlthrottle = d
	
	def download(self, file_meta_enc):
	
		tuid = None
		url = ''
		error = ''
		progress = 0
		startPos = 0 
		purgeKey = ''
		try:
			file_meta = JSON.ObjectFromString(D(file_meta_enc))
			title = file_meta['title']
			url = file_meta['url']
			furl = url
			
			page_url = None
			if 'page_url' in file_meta.keys():
				page_url = file_meta['page_url']
				
			seq = 0
			if 'seq' in file_meta.keys():
				seq = file_meta['seq']

			durl = file_meta['durl']
			purl = file_meta['purl']
			year = file_meta['year']
			summary = file_meta['summary']
			thumb = file_meta['thumb']
			fs = file_meta['fs']
			fsBytes = file_meta['fsBytes']
			chunk_size = file_meta['chunk_size']
			quality = file_meta['quality']
			source = file_meta['source']
			uid = file_meta['uid']
			fid = file_meta['fid']
			type = file_meta['type']
			status = file_meta['status']
			startPos = file_meta['startPos']
			timeAdded = file_meta['timeAdded']
			first_time = file_meta['first_time']
			progress = file_meta['progress']
			path = file_meta['section_path']
			
			try:
				vidtype = file_meta['vidtype'].lower()
			except:
				vidtype = 'movie'
				
			try:
				riptype = file_meta['riptype']
				if riptype == None:
					riptype = 'BRRIP'
			except:
				riptype = 'BRRIP'
				
			headers = None
			try:
				params_enc = file_meta['params']
				params = json.loads(base64.b64decode(params_enc))
				if 'headers' in params.keys():
					headers = params['headers']
			except:
				params = None
			
			file_meta['last_error'] = 'Unknown Error'
			file_meta['error'] = 'Unknown Error'
			purgeKey = uid
			total_size_bytes = int(fsBytes) # in bytes
			#Log("total_size_bytes : %s" % str(total_size_bytes))
			error = ''
			
			if common.DOWNLOAD_TEMP == None:
				common.DOWNLOAD_TEMP = {}
			
			chunk_size_n = int(1024.0 * 1024.0 * float(common.DOWNLOAD_CHUNK_SIZE)) # in bytes
			if chunk_size != chunk_size_n:
				chunk_size = chunk_size_n
				file_meta['chunk_size'] = chunk_size
			
			if 'file_ext' in file_meta:
				file_ext = file_meta['file_ext']
				if file_ext == None:
					file_ext = '.mp4'
			else:
				file_ext = '.mp4'
				
			source_meta = {}
			f_meta = {}
			
			if vidtype == 'show':
				item_folder_name = '%s' % (file_meta['title'])
			else:
				item_folder_name = '%s (%s)' % (file_meta['title'], file_meta['year'])
		
			fname, fname_e = create_fname(file_meta, vidtype, riptype, file_ext, fid + common.DOWNLOAD_FMP_EXT)
			if fname == None:
				raise fname_e
				
			tuid = common.id_generator(16)
			common.control.AddThread('download', 'Download File: %s' % fname, time.time(), '2', False, tuid)
				
			abs_path = Core.storage.join_path(path, item_folder_name, fname)
			directory = Core.storage.join_path(path, item_folder_name)
			
			file_meta['temp_file'] = abs_path
			
			startPos = verifyStartPos(startPos, abs_path)
			
			sub_url_t = None
			if 'openload' in source.lower():
				furl, error, sub_url_t, page_html = common.host_openload.resolve(furl)
				# check if file-link valid using fs of 1MB
				if error == '':
					fs_r, error = common.client.getFileSize(furl, headers=headers, retError=True, retry429=True, cl=2)
				if error != '' or furl == None or float(fs_r) < float(1024*1024):
					furl, error, sub_url_t, page_html = common.host_openload.resolve(durl)
				if error != '' or furl == None:
					Log('OpenLoad URL-f: %s' % furl)
					Log('OpenLoad URL-d: %s' % durl)
					Log('OpenLoad Error: %s' % error)
					download_failed(url, error, progress, startPos, purgeKey)
					common.control.RemoveThread(tuid)
					return
			elif 'rapidvideo' in source.lower():
				furl, error, sub_url_t = common.host_rapidvideo.resolve(furl)
				# check if file-link valid using fs of 1MB
				if error == '':
					fs_r, error = common.client.getFileSize(furl, headers=headers, retError=True, retry429=True, cl=2)
				if error != '' or furl == None or float(fs_r) < float(1024*1024):
					furl, error, sub_url_t = common.host_rapidvideo.resolve(durl)
				if error != '' or furl == None:
					Log('RapidVideo URL: %s' % furl)
					Log('RapidVideo Error: %s' % error)
					download_failed(url, error, progress, startPos, purgeKey)
					common.control.RemoveThread(tuid)
					return
			elif 'streamango' in source.lower():
				furl, error, sub_url_t = common.host_streamango.resolve(furl)
				# check if file-link valid using fs of 1MB
				if error == '':
					fs_r, error = common.client.getFileSize(furl, headers=headers, retError=True, retry429=True, cl=2)
				if error != '' or furl == None or float(fs_r) < float(1024*1024):
					furl, error, sub_url_t = common.host_streamango.resolve(durl)
				if error != '' or furl == None:
					Log('Streamango URL: %s' % furl)
					Log('Streamango Error: %s' % error)
					download_failed(url, error, progress, startPos, purgeKey)
					common.control.RemoveThread(tuid)
					return
			elif 'direct' in source.lower():
				furl, error, params_enc  = common.host_direct.resolve(furl)
				if error != '' or furl == None or float(fs_r) < float(1024*1024):
					furl, error, params_enc = common.host_direct.resolve(durl)
				if error != '' or furl == None:
					Log('Direct host URL: %s' % furl)
					Log('Direct host Error: %s' % error)
					download_failed(url, error, progress, startPos, purgeKey)
					common.control.RemoveThread(tuid)
					return
				try:
					params = json.loads(base64.b64decode(params_enc))
					if 'headers' in params.keys():
						headers = params['headers']
				except:
					pass
			else:
				# check if file-link valid using fs of 1MB
				fs_r, error = common.client.getFileSize(furl, headers=headers, retError=True, retry429=True, cl=2)
				if common.DEV_DEBUG == True and Prefs["use_debug"]:
					Log('Url: %s | Curr. FileSize: %s | Orig. FileSize: %s' % (furl, fs_r, fsBytes))
				if fs_r != None and float(fs_r) > float(1024*1024): # 1MB
					if common.DEV_DEBUG == True and Prefs["use_debug"]:
						Log('File Health Looks Good with current download url !')
				else:
					# ret_val_resolvers is always a tuple with first val. of returned url and second of error...
					ret_val_resolvers = common.interface.getHostResolverMain().resolve(furl, page_url=page_url)
					error = ret_val_resolvers[1]
					if error == '' and furl == ret_val_resolvers[0]:
						fs_r, error = common.client.getFileSize(furl, headers=headers, retError=True, retry429=True, cl=2)
					if error != '' or float(fs_r) < float(1024*1024):
						ret_val_resolvers  = common.interface.getHostResolverMain().resolve(durl, page_url=page_url)
						error = ret_val_resolvers[1]
					if error == '':
						try:
							furl = ret_val_resolvers[0]	
							try:
								if furl != None and len(furl) >= seq:
									furl = furl[seq]
								else:
									furl = furl[0]
								params = json.loads(base64.b64decode(ret_val_resolvers[2]))
								if 'headers' in params.keys():
									headers = params['headers']
							except:
								pass
							fs_r, error = common.client.getFileSize(furl, headers=headers, retError=True, retry429=True, cl=2, timeout=30.0)
							if common.DEV_DEBUG == True and Prefs["use_debug"]:
								Log('Url: %s | FileSize: %s | Error: %s' % (furl, fs_r, error))
						except Exception as e:
							error = '%s' % e	
					if error != '' or float(fs_r) < float(1024*1024):
						if common.DEV_DEBUG == True and Prefs["use_debug"]:
							Log('Host URL-f: %s' % furl)
							Log('Host URL-d: %s' % durl)
							Log('Host params: %s' % params)
							Log('Host FileSize: %s' % fs_r)
							Log('Host Error: %s' % error)
						download_failed(url, error, progress, startPos, purgeKey)
						common.control.RemoveThread(tuid)
						return
					else:
						if common.DEV_DEBUG == True and Prefs["use_debug"]:
							Log('Host URL-f: %s' % furl)
							Log('Host URL-d: %s' % durl)
					
			if sub_url_t != None:
				file_meta['sub_url'] = sub_url_t
			
			if Prefs['use_debug']:
				Log('Save path: %s' % abs_path)
				Log('File url: %s' % furl)
			
			# ToDo
			# https://support.plex.tv/articles/200220677-local-media-assets-movies/
			fname, fname_e = create_fname(file_meta, vidtype, riptype, file_ext)
			if fname == None:
				raise fname_e
			
			final_abs_path = Core.storage.join_path(path, item_folder_name, fname)
			
			# subtitle
			sub_fname = fname.replace(file_ext,'') + '.en.srt'
			sub_file_path = Core.storage.join_path(directory, sub_fname)
			
			write_mode = 'wb'
			chunk_speed = 0
			avg_speed = 0
			avg_speed_curr = 0
			eta = 0
			bytes_read = 0
			r = None
			err = ''
			
			if source != 'mega':
				time.sleep(2) # reduce 429 -- too many requests error
				if common.USE_DOWNLOAD_RESUME_GEN == True and Core.storage.file_exists(abs_path):
					if Prefs['use_debug']:
						Log('**Resuming download from position: %s**' % startPos)
					r, err = resume_download(furl, startPos, headers=headers)
					
					if WAIT_AND_RETRY_ON_429 == True and (r == None or r.status_code == 429):
						time.sleep(5)
						r, err = resume_download(furl, startPos, headers=headers)
					
					if r == None or (r.status_code != 200 and r.status_code != 206):
						if Prefs['use_debug']:
							Log('Could not Resume (HTTP Code: %s) - New download' % str(r.status_code))
						r, err = request_download(furl, headers=headers)
					else:
						write_mode = 'ab'
						bytes_read = startPos
				else:
					if Prefs['use_debug']:
						Log('**New download**')
					r, err = request_download(furl, headers=headers)
					
					if WAIT_AND_RETRY_ON_429 == True and (r == None or r.status_code == 429):
						time.sleep(5)
						r, err = request_download(furl, headers=headers)
						
			if r == None or err != '':
				raise Exception(err)
			
			file_meta_temp = file_meta
			file_meta_temp['status'] = common.DOWNLOAD_STATUS[1]
			file_meta_temp['progress'] = '?'
			file_meta_temp['chunk_speed'] = '?'
			file_meta_temp['avg_speed'] = '?'
			file_meta_temp['avg_speed_curr'] = '?'
			file_meta_temp['eta'] = '?'
				
			common.DOWNLOAD_TEMP[purgeKey] = E(JSON.StringFromObject(file_meta_temp))
			Dict['DOWNLOAD_TEMP'] = E(JSON.StringFromObject(common.DOWNLOAD_TEMP))
			Dict[purgeKey] = E(JSON.StringFromObject(file_meta_temp))
			Dict.Save()
			common.DOWNLOAD_STATS[purgeKey] = file_meta_temp
			del QUEUE_RUN_ITEMS[purgeKey]

			FMPdownloader = None
			
			try:
				try:
					if not os.path.exists(directory):
						os.makedirs(directory)
						while os.path.exists(directory) == False:
							time.sleep(1)
				except OSError as e:
					raise Exception('%s' % e)
				if source == 'mega' or r.status_code == 200 or r.status_code == 206:
					
					if source == 'mega':
						megaDL = common.host_mega.mega.Mega()
						megaDL.setBufferSize(chunk_size)
						FMPdownloader = megaDL.download_url(furl)
						
						if common.USE_DOWNLOAD_RESUME_MEGA == True and Core.storage.file_exists(abs_path):
							if Prefs['use_debug']:
								Log('**Resuming download**')
							dl_info = FMPdownloader.next()
							furl = "%s/%s" % (dl_info['url'],dl_info['name'])
							r = resume_download(furl, startPos, headers=headers)
							
							if r.status_code == 200 or r.status_code == 206:
								FMPdownloader = r.iter_content(chunk_size)
								write_mode = 'ab'
								bytes_read = startPos
							else:
								if Prefs['use_debug']:
									Log.Error('**Could not Resume (HTTP Code: %s) - New download**' % str(r.status_code))
						else:
							if Prefs['use_debug']:
								Log('**New download**')
							FMPdownloader.next()	# Start the download.
					else:
						FMPdownloader = r.iter_content(chunk_size)
					
					try:
						with io.open(abs_path, write_mode) as f:
							
							last_time = first_time_avg = time.time()
							bytes_read_curr = 0
							
							for chunk in FMPdownloader:
								
								f.write(chunk)
								
								if bytes_read == 0:
									file_meta['first_time'] = time.time()
									
								chunk_size = float(len(chunk))
								bytes_read_curr += chunk_size
								bytes_read += chunk_size
								curr_time = time.time()
								delta_time = (curr_time - last_time)+0.0001 # avoid delta_time == 0
								if bytes_read > 0:
									self.dlthrottle.addBytes(chunk_size)
									chunk_speed = round(chunk_size/float(delta_time * float(1000 * 1024)),2)
									avg_speed = round(float(bytes_read)/float((time.time() - first_time) * float(1000 * 1024)),2)
									avg_speed_curr = round(float(bytes_read_curr)/float((time.time() - first_time_avg) * float(1000 * 1024)),2)
									rem_bytes = float(total_size_bytes) - float(bytes_read)
									eta = round(float(((float(rem_bytes) / (1024.0*1024.0))/float(avg_speed_curr))/60.0), 2)
									progress = round(float(100) * float(bytes_read)/float(total_size_bytes), 2)
									last_time = curr_time
									
									file_meta['status'] = common.DOWNLOAD_STATUS[1]
									file_meta['progress'] = progress
									file_meta['chunk_speed'] = chunk_speed
									file_meta['avg_speed'] = avg_speed
									file_meta['avg_speed_curr'] = avg_speed_curr
									file_meta['eta'] = eta
									
								longstringObjs = JSON.ObjectFromString(D(Dict[purgeKey]))
								action = longstringObjs['action']
								if action in [common.DOWNLOAD_ACTIONS[3]]:
									Dict[purgeKey] = E(JSON.StringFromObject(file_meta))
								if action == common.DOWNLOAD_ACTIONS[0]: # cancel
									try:
										f.close()
									except:
										pass
									try:
										r.close()
									except:
										pass
									end_download_by_user(title, url, purgeKey)
									common.control.RemoveThread(tuid)
									return
								elif action == common.DOWNLOAD_ACTIONS[1]: # pause
									while action == common.DOWNLOAD_ACTIONS[1]:
										curr_time = time.time()
										delta_time = (curr_time - last_time)+0.0001 # avoid delta_time == 0
										chunk_speed = round(chunk_size/float(delta_time * float(1000 * 1024)),2)
										avg_speed = round(float(bytes_read)/float((time.time() - first_time) * float(1000 * 1024)),2)
										avg_speed_curr = round(float(bytes_read_curr)/float((time.time() - first_time_avg) * float(1000 * 1024)),2)
										rem_bytes = float(total_size_bytes) - float(bytes_read)
										eta = round(float(((float(rem_bytes) / (1024.0*1024.0))/float(avg_speed_curr))/60.0), 2)
										progress = round(float(100) * float(bytes_read)/float(total_size_bytes), 2)
										file_meta['progress'] = progress
										file_meta['chunk_speed'] = chunk_speed
										file_meta['avg_speed'] = avg_speed
										file_meta['avg_speed_curr'] = avg_speed_curr
										common.DOWNLOAD_STATS[purgeKey] = file_meta
										common.DOWNLOAD_STATS[purgeKey]['action'] = action
										time.sleep(1)
										longstringObjs = JSON.ObjectFromString(D(Dict[purgeKey]))
										action = longstringObjs['action']
										#Log('Action: %s' % action)
										
								elif action == common.DOWNLOAD_ACTIONS[2]: # resume
									common.DOWNLOAD_STATS[purgeKey]['action'] = common.DOWNLOAD_ACTIONS[4]
									
								elif action == common.DOWNLOAD_ACTIONS[3]: # postpone
									try:
										f.close()
									except:
										pass
									try:
										r.close()
									except:
										pass
									postpone_download_by_user(title, url, progress, bytes_read, purgeKey)
									common.control.RemoveThread(tuid)
									return
								else:
									pass
								
								common.DOWNLOAD_STATS[purgeKey] = file_meta
								
								if self.dlthrottle.getThrottleState() == True and progress < 99 and action == common.DOWNLOAD_ACTIONS[4]:
									last_state = file_meta['action']
									file_meta['action'] = common.DOWNLOAD_PROPS[2]
									common.DOWNLOAD_STATS[purgeKey] = file_meta
									while self.dlthrottle.getThrottleState() == True:
										curr_time = time.time()
										delta_time = (curr_time - last_time)+0.0001 # avoid delta_time == 0
										chunk_speed = round(chunk_size/float(delta_time * float(1000 * 1024)),2)
										avg_speed = round(float(bytes_read)/float((time.time() - first_time) * float(1000 * 1024)),2)
										avg_speed_curr = round(float(bytes_read_curr)/float((time.time() - first_time_avg) * float(1000 * 1024)),2)
										eta = round(float(((float(rem_bytes) / (1024.0*1024.0))/float(avg_speed_curr))/60.0), 2)
										progress = round(float(100) * float(bytes_read)/float(total_size_bytes), 2)
										file_meta['progress'] = progress
										file_meta['chunk_speed'] = chunk_speed
										file_meta['avg_speed'] = avg_speed
										file_meta['avg_speed_curr'] = avg_speed_curr
										file_meta['eta'] = eta
										
										common.DOWNLOAD_STATS[purgeKey] = file_meta
										time.sleep(0.1)
										
									file_meta['action'] = last_state
									common.DOWNLOAD_STATS[purgeKey] = file_meta
									
							if (progress < 5):
								raise Exception('Error downloading file.')
								
							try:
								f.close()
							except:
								pass
							progress = 100
							file_renamed_inc = True
							c = 1
							exact_same_file = False
							
							while (file_renamed_inc):
								CRC_Of_Files = []
								while Core.storage.file_exists(final_abs_path):
									try:
										crc_file = common.md5(final_abs_path)
										CRC_Of_Files.append(crc_file)
									except Exception as error:
										Log('Error download.py >>> CRC check : %s' % error)	
										
									fname, fname_e = create_fname(file_meta, vidtype, riptype, file_ext, c=str(c))
									if fname == None:
										raise fname_e
									
									# new progressive name
									final_abs_path = Core.storage.join_path(directory, fname)
									
									# subtitle
									sub_fname = fname.replace(file_ext,'') + '.en.srt'
									sub_file_path = Core.storage.join_path(directory, sub_fname)
									
									c += 1
									
								try:
									crc_new_file = common.md5(abs_path)
									if crc_new_file in CRC_Of_Files:
										Log('CRC New File %s:%s' % (crc_new_file, abs_path))
										Log('CRC Old File : %s' % (CRC_Of_Files))
										
										exact_same_file = True
								except Exception as error:
									Log('Error download.py >>> CRC compare : %s' % error)
								try:
									if exact_same_file == True:
										try:
											Core.storage.remove_data_item(abs_path)
											time.sleep(1)
										except Exception as e:
											Log('Error download.py >>> CRC based removal : %s' % e)
									else:
										os.rename(abs_path, final_abs_path)
										download_subtitle(file_meta['sub_url'], sub_file_path, params=params)
										
									file_renamed_inc = False
									
								except Exception as error:
									Log('Error download.py >>> %s : %s' % (error, final_abs_path))
									
								if (c > 5):
									raise Exception(error)
							
							# file_meta['status'] = common.DOWNLOAD_STATUS[2]
							# file_meta['progress'] = progress
							# Dict[purgeKey] = E(JSON.StringFromObject(file_meta)) 
							# Dict.Save()
							
							download_completed(final_abs_path, file_meta['section_title'], file_meta['section_key'], purgeKey, exact_same_file)
							
					except Exception as error:
						st = traceback.format_exc()
						Log(st)
						try:
							f.close()
						except:
							pass
						raise Exception(error)
				else:
					raise Exception('Error response - HTTP Code:%s' % r.status_code)
					
			except Exception as error:
				error = '%s' % error
				Dict[purgeKey] = E(JSON.StringFromObject(file_meta))
				download_failed(url, error, progress, bytes_read, purgeKey)

			if r != None:
				try:
					r.close()
				except:
					pass
					
			common.control.RemoveThread(tuid)
		except Exception as e:
			error = '%s' % e
			Log.Error(e)
			download_failed(url, error, progress, startPos, purgeKey)
			common.control.RemoveThread(tuid)
		
##############################################################################################

def create_fname(file_meta, vidtype, riptype, file_ext, file_ext_temp='', c='0'):

	try:
		#Log('creating fname : %s\n%s\n%s\n%s\n%s\n%s' % (file_meta, vidtype, riptype, file_ext, file_ext_temp, c))
		#Log('%s (%s)' % (file_meta['watch_title'], file_meta['year']))

		if str(c) == '0':
			if vidtype in 'movie/show':
				if vidtype == 'show':
					if '3D-' in riptype:
						fname = '%s (%s)%s%s%s' % (file_meta['watch_title'], file_meta['year'], FLAG_3D, file_ext, file_ext_temp)
					else:
						fname = '%s (%s)%s%s' % (file_meta['watch_title'], file_meta['year'], file_ext, file_ext_temp)
				else:
					if '3D-' in riptype:
						fname = '%s (%s)%s%s%s' % (file_meta['title'], file_meta['year'], FLAG_3D, file_ext, file_ext_temp)
					else:
						fname = '%s (%s)%s%s' % (file_meta['title'], file_meta['year'], file_ext, file_ext_temp)
			else:
				if '3D-' in riptype:
					fname = '%s (%s)-%s%s%s%s' % (file_meta['title'], file_meta['year'], REMAP_EXTRAS[vidtype], FLAG_3D, file_ext, file_ext_temp)
				else:
					fname = '%s (%s)-%s%s%s' % (file_meta['title'], file_meta['year'], REMAP_EXTRAS[vidtype], file_ext, file_ext_temp)
		else:
			if vidtype in 'movie/show':
				if vidtype == 'show':
					if '3D-' in riptype:
						fname = '%s (%s)%s-%s%s%s' % (file_meta['watch_title'], file_meta['year'], FLAG_3D, str(c), file_ext, file_ext_temp)
					else:
						fname = '%s (%s)-%s%s%s' % (file_meta['watch_title'], file_meta['year'], str(c), file_ext, file_ext_temp)
				else:
					if '3D-' in riptype:
						fname = '%s (%s)%s-%s%s%s' % (file_meta['title'], file_meta['year'], FLAG_3D, str(c), file_ext, file_ext_temp)
					else:
						fname = '%s (%s)-%s%s%s' % (file_meta['title'], file_meta['year'], str(c), file_ext, file_ext_temp)
			else:
				if '3D-' in riptype:
					fname = '%s (%s)-%s%s-%s%s%s' % (file_meta['title'], file_meta['year'], REMAP_EXTRAS[vidtype], FLAG_3D, str(c), file_ext, file_ext_temp)
				else:
					fname = '%s (%s)-%s-%s%s%s' % (file_meta['title'], file_meta['year'], REMAP_EXTRAS[vidtype], str(c), file_ext, file_ext_temp)
			
		return fname, ''
	except Exception as e:
		Log('Error in download.create_fname : %s' % e)
	return None, e
	
def do_download(file_meta_enc):

	tuid = common.id_generator(16)
	common.control.AddThread('do_download', 'Initiate Download', time.time(), '2', False, tuid)
	
	if len(common.DOWNLOAD_STATS.keys()) >= int(Prefs['download_connections']):
		#Log(common.DOWNLOAD_STATS)
		longstringObjs = JSON.ObjectFromString(D(file_meta_enc))
		uid = longstringObjs['uid']
		if uid in QUEUE_RUN_ITEMS.keys():
			del QUEUE_RUN_ITEMS[uid]
		if Prefs['use_debug']:
			Log("Downlod connections limit reached (%s of %s). This item will be queued !" % (str(len(common.DOWNLOAD_STATS.keys())), Prefs['download_connections']))
		common.control.RemoveThread(tuid)
		return

	downloader = Downloader()
	
	while len(DLT) == 0:
		time.sleep(1)
	
	downloader.setDownloadThrottler(DLT[0])
	#thread_i = workers.Thread(downloader.download(file_meta_enc))
	#thread_i.start()
	Thread.Create(downloader.download, {}, file_meta_enc)
	
	common.control.RemoveThread(tuid)
	
def download_subtitle(url, sub_file_path, params=None):
	
	try:
		if url == None:
			return
		if params != None and 'headers' in params.keys():
			headers = params['headers']
		else:
			headers = None
		if Prefs['use_debug']:
			Log('Download Subtitle : %s to %s' % (url, sub_file_path))
		r = None
		r, err = request_download(url, headers=headers)
		if err != '' or r == None:
			raise Exception(err)
		if r.status_code == 200:
			FMPdownloaderSub = r.iter_content(1024*64)
			with io.open(sub_file_path, 'wb') as f:
				for chunk in FMPdownloaderSub:
					f.write(chunk)
			f.close()
		else:
			raise("HTTP Error: %s" % str(r.status_code))
	except Exception as e:
		Log(e)
		if r != None:
			r.close()
	
def request_download(url, headers=None):

	try:
		r = requests.get(url, headers=headers, stream=True, verify=False, allow_redirects=True, timeout=CONNECTION_TIMEOUT)
		return r, ''
	except Exception as e:
		err = '%s' % e
		Log.Error(e)
		return None, err
	
def resume_download(url, resume_byte_pos, headers=None):
	try:
		resume_header = {'Range': 'bytes=%s-' % int(resume_byte_pos)}
		if headers != None:
			for h in headers.keys():
				resume_header[h] = headers[h]
		r = requests.get(url, headers=resume_header, stream=True, verify=False, allow_redirects=True, timeout=CONNECTION_TIMEOUT)
		return r, ''
	except Exception as e:
		err = '%s' % e
		Log.Error(e)
		return None, err
	
def download_completed(final_abs_path, section_title, section_key, purgeKey, fileExists=False):

	file_meta = common.DOWNLOAD_STATS[purgeKey]
	file_meta['status'] = common.DOWNLOAD_STATUS[2]
	file_meta['action'] = common.DOWNLOAD_PROPS[0]
	file_meta['progress'] = 100
	Dict[purgeKey] = E(JSON.StringFromObject(file_meta))
	
	if purgeKey in common.DOWNLOAD_STATS.keys():
		del common.DOWNLOAD_STATS[purgeKey]
		
	if purgeKey in common.DOWNLOAD_TEMP.keys():
		del common.DOWNLOAD_TEMP[purgeKey]
		Dict['DOWNLOAD_TEMP'] = E(JSON.StringFromObject(common.DOWNLOAD_TEMP))
		Dict.Save()

	if Prefs['use_debug']:
		if fileExists == True:
			Log('Download Completed, but file with same name and crc match exists - File discarded')
		else:	
			Log('Download Completed - %s' % final_abs_path)
		
	if fileExists == False and common.UsingOption(key=common.GLOBAL_OPTIONS[1], session='None') == False and AUTOPILOT_SCHEDULER[0] == False:
		Thread.Create(refresh_section, {}, section_title, section_key)
		
	if fileExists == False and common.UsingOption(key=common.GLOBAL_OPTIONS[1], session='None') == False and AUTOPILOT_SCHEDULER[0] == True:
		AUTOPILOT_SCHEDULER_POST_REFRESH.append([section_title, section_key])
		
	Thread.Create(trigger_que_run)
	
def post_autopilot_refresh():

	tuid = common.id_generator(16)
	common.control.AddThread('PostAutoPilotRefreshSections', 'Refresh Sections after AutoPilot Scheduler', time.time(), '3', False, tuid)
	try:
		if len(AUTOPILOT_SCHEDULER_POST_REFRESH) > 0 and AUTOPILOT_SCHEDULER[0] == True:
			AUTOPILOT_SCHEDULER_POST_REFRESH = list(set(AUTOPILOT_SCHEDULER_POST_REFRESH))
			
			for i in AUTOPILOT_SCHEDULER_POST_REFRESH:
				refresh_section(i[0], i[1])
		
	except Exception as e:
		Log(e)
		
	try:
		del AUTOPILOT_SCHEDULER[:]
		del AUTOPILOT_SCHEDULER_POST_REFRESH[:]
		AUTOPILOT_SCHEDULER.append(False)
	except:
		pass
	
	common.control.RemoveThread(tuid)
	
def download_failed(url, error, progress, startPos, purgeKey):

	Log('Download Failed: Error - %s' % error)
	Log('Download Failed: URL - %s' % url)
	
	if purgeKey in common.DOWNLOAD_STATS.keys():
		del common.DOWNLOAD_STATS[purgeKey]
		
	file_meta_enc = Dict[purgeKey]
	file_meta = JSON.ObjectFromString(D(file_meta_enc))
	file_meta['status'] = common.DOWNLOAD_STATUS[3]
	file_meta['error'] = error
	file_meta['last_error'] = error
	file_meta['action'] = common.DOWNLOAD_PROPS[1]
	file_meta['progress'] = progress
	file_meta['startPos'] = startPos
	file_meta['timeAdded'] = time.time()
	Dict[purgeKey] = E(JSON.StringFromObject(file_meta))
	
	uid = file_meta['uid']
	if uid in QUEUE_RUN_ITEMS.keys():
		del QUEUE_RUN_ITEMS[uid]
	
	if purgeKey in common.DOWNLOAD_TEMP.keys():
		del common.DOWNLOAD_TEMP[purgeKey]
		Dict['DOWNLOAD_TEMP'] = E(JSON.StringFromObject(common.DOWNLOAD_TEMP))
	
	Dict.Save()
	
	Thread.Create(trigger_que_run,{},[purgeKey])
	
def end_download_by_user(title, url, purgeKey):

	file_meta = JSON.ObjectFromString(D(Dict[purgeKey]))
	filepath = file_meta['temp_file']
	try:
		Core.storage.remove_data_item(filepath)
		time.sleep(1)
	except Exception as e:
		Log("=============end_download_by_user Error-1============")
		Log(e)
		
	try:
		dir_path = os.path.dirname(filepath)
		num_files = os.listdir(dir_path)
		if len(num_files) == 0:
			os.rmdir(dir_path)
	except Exception as e:
		Log("=============end_download_by_user Error-2============")
		Log(e)
		
	if purgeKey in common.DOWNLOAD_STATS.keys():
		del common.DOWNLOAD_STATS[purgeKey]
		
	if purgeKey in common.DOWNLOAD_TEMP.keys():
		del common.DOWNLOAD_TEMP[purgeKey]
		Dict['DOWNLOAD_TEMP'] = E(JSON.StringFromObject(common.DOWNLOAD_TEMP))
		
	del Dict[purgeKey]
	Dict.Save()
	
	if Prefs['use_debug']:
		Log('Download Cancelled by User: %s' % title)
		Log('Download Cancelled: URL - %s' % url)
	
	Thread.Create(trigger_que_run,{},[purgeKey])
	
def postpone_download_by_user(title, url, progress, startPos, purgeKey):

	file_meta = JSON.ObjectFromString(D(Dict[purgeKey]))
	file_meta['status'] = common.DOWNLOAD_STATUS[0]
	file_meta['action'] = common.DOWNLOAD_ACTIONS[3]
	file_meta['progress'] = progress
	file_meta['startPos'] = startPos
	file_meta['timeAdded'] = time.time() + float(60*60*2)
	Dict[purgeKey] = E(JSON.StringFromObject(file_meta))
	
	if purgeKey in common.DOWNLOAD_STATS.keys():
		del common.DOWNLOAD_STATS[purgeKey]
		
	if purgeKey in common.DOWNLOAD_TEMP.keys():
		del common.DOWNLOAD_TEMP[purgeKey]
		Dict['DOWNLOAD_TEMP'] = E(JSON.StringFromObject(common.DOWNLOAD_TEMP))
			
	Dict.Save()
	
	if Prefs['use_debug']:
		Log('Download Postponed by User: %s' % title)
		Log('Download Postponed: URL - %s' % url)
	
	Thread.Create(trigger_que_run)
	
trigger_que_run_singleton = []
def trigger_que_run(skip = []):

	while len(trigger_que_run_singleton) > 0:
		time.sleep(1.0)
		
	trigger_que_run_singleton.append(True)
	tuid = common.id_generator(16)
	common.control.AddThread('trigger_que_run', 'Updates Download Items Run/Status', time.time(), '2', False, tuid)
	
	time.sleep(3)
	items_for_que_run = []
	Dict_Temp = {}
	
	try:
		try:
			for each in Dict:
				if 'Down5Split' in each:
					try:
						file_meta = JSON.ObjectFromString(D(Dict[each]))
						if file_meta['uid'] not in skip:
							if file_meta['status'] == common.DOWNLOAD_STATUS[0] and file_meta['action'] == common.DOWNLOAD_ACTIONS[4] and (time.time() - float(file_meta['timeAdded'])) > 0:
								Dict_Temp[each] = Dict[each]
							elif file_meta['status'] == common.DOWNLOAD_STATUS[0] and file_meta['action'] == common.DOWNLOAD_ACTIONS[3] and (time.time() - float(file_meta['timeAdded'])) > 0:
								Dict_Temp[each] = Dict[each]
					except Exception as e:
						Log(e)
		except Exception as e:
			Log(e)
					
		save_dict = False
		try:
			for each in Dict_Temp:
				try:
					file_meta = JSON.ObjectFromString(D(Dict_Temp[each]))
					if file_meta['status'] == common.DOWNLOAD_STATUS[0] and file_meta['action'] == common.DOWNLOAD_ACTIONS[4] and (time.time() - float(file_meta['timeAdded'])) > 0:
						EncTxt = Dict_Temp[each]
						items_for_que_run.append({'label':str(file_meta['timeAdded']), 'data':EncTxt, 'uid':file_meta['uid']})
						QUEUE_RUN_ITEMS[file_meta['uid']] = False
					elif file_meta['status'] == common.DOWNLOAD_STATUS[0] and file_meta['action'] == common.DOWNLOAD_ACTIONS[3] and (time.time() - float(file_meta['timeAdded'])) > 0:
						file_meta['action'] = common.DOWNLOAD_ACTIONS[4]
						EncTxt = E(JSON.StringFromObject(file_meta))
						Dict[each] = EncTxt
						save_dict = True
						items_for_que_run.append({'label':str(file_meta['timeAdded']), 'data':EncTxt, 'uid':file_meta['uid']})
						QUEUE_RUN_ITEMS[file_meta['uid']] = False
				except Exception as e:
					Log(e)
				if save_dict == True:
					Dict.Save()
		except Exception as e:
			Log(e)

		if len(items_for_que_run) > 0:
			newlistSorted = sorted(items_for_que_run, key=lambda k: k['label'], reverse=False)
			
			for i in newlistSorted:
				try:
					time.sleep(1)
					EncTxt = i['data']
					uid = i['uid']
					Thread.Create(do_download, {}, file_meta_enc=EncTxt)
					while (uid in QUEUE_RUN_ITEMS.keys()):
						time.sleep(2.0)
				except Exception as e:
					Log(e)
	except Exception as e:
		Log(e)
	
	common.control.RemoveThread(tuid)
	del trigger_que_run_singleton[:]

def move_unfinished_to_failed():

	common.DOWNLOAD_TEMP = Dict['DOWNLOAD_TEMP']
	items_to_del = []
	#Log(common.DOWNLOAD_TEMP)
	
	if common.DOWNLOAD_TEMP != None:
		
		try:
			common.DOWNLOAD_TEMP = JSON.ObjectFromString(D(common.DOWNLOAD_TEMP))
		except:
			common.DOWNLOAD_TEMP = {}
			
		if len(common.DOWNLOAD_TEMP.keys()) > 0:
			if Prefs['use_debug']:
				Log("Moving Unfinished Downloads to Failed !")
			
		c = 0
		for key in common.DOWNLOAD_TEMP.keys():
			try:
				file_meta_enc = common.DOWNLOAD_TEMP[key]
				uid = None
				file_meta = JSON.ObjectFromString(D(file_meta_enc))
				uid = file_meta['uid']
				if uid in Dict:
					file_meta = JSON.ObjectFromString(D(Dict[uid]))
				file_meta['status'] = common.DOWNLOAD_STATUS[3]
				file_meta['action'] = common.DOWNLOAD_PROPS[1]
				if 'temp_file' in file_meta:
					filepath = file_meta['temp_file']
					if Core.storage.file_exists(filepath):
						bytes_read = os.path.getsize(filepath)
						total_size_bytes = file_meta['fsBytes']
						rem_bytes = float(total_size_bytes) - float(bytes_read)
						progress = round(float(100) * float(bytes_read)/float(total_size_bytes), 2)
					else:
						bytes_read = 0
						progress = 0
					file_meta['progress'] = progress
					file_meta['startPos'] = bytes_read
					
				Dict[uid] = E(JSON.StringFromObject(file_meta))
			except Exception as e:
				Log("=============== move_unfinished_to_failed =================")
				Log(e)
				Log(file_meta)
				if uid != None:
					items_to_del.append(uid)
			
		if len(items_to_del) > 0:
			for each in items_to_del:
				try:
					del Dict[each]
				except Exception as e:
					Log(e)
		
		del Dict['DOWNLOAD_TEMP']
		common.DOWNLOAD_TEMP = {}
		Dict.Save()
		
def move_failed_to_queued():

	items_to_change = []
	
	try:
		for each in Dict:
			if 'Down5Split' in each:
				try:
					longstringObjs = JSON.ObjectFromString(D(Dict[each]))
					if longstringObjs['status'] == common.DOWNLOAD_STATUS[3]:
						items_to_change.append(each)
				except Exception as e:
					Log("============ move_failed_to_queued =============")
					Log(e)
	except Exception as e:
		Log(e)
	
	if len(items_to_change) > 0:
		if Prefs['use_debug']:
			Log("Moving Failed Downloads to Queued !")
		
		for each in items_to_change:
			file_meta_enc = Dict[each]
			file_meta = JSON.ObjectFromString(D(file_meta_enc))
			
			file_meta['status'] = common.DOWNLOAD_STATUS[0]
			file_meta['action'] = common.DOWNLOAD_ACTIONS[4]
			
			Dict[each] = E(JSON.StringFromObject(file_meta))
			
		Dict.Save()
		time.sleep(2)
		
def verifyStartPos(startPos, filepath):
	try:
		if filepath != None and Core.storage.file_exists(filepath):
			bytes_read = os.path.getsize(filepath)
			if startPos != bytes_read:
				if Prefs['use_debug']:
					Log('Using start pos based on current file-size: %s. Old was: %s. File: %s' % (bytes_read, startPos, filepath))
				startPos = bytes_read
	except:
		pass
	return startPos
	
def DownloadInit():

	tuid = common.id_generator(16)
	common.control.AddThread('DownloadInit', 'Initialize Downloader', time.time(), '2', False, tuid)
	
	move_unfinished_to_failed()
	time.sleep(1)
	if common.UsingOption(key=common.GLOBAL_OPTIONS[0], session='None') == True:
		move_failed_to_queued()
		time.sleep(1)
	dlt = DownloadThrottler()
	DLT.append(dlt)
	DLT[0].start()
	Thread.Create(trigger_que_run)
	
	common.control.RemoveThread(tuid)
	return
	