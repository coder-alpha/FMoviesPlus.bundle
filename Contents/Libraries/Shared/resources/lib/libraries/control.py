# -*- coding: utf-8 -*-

'''
    Specto Add-on
    Copyright (C) 2015 lambda

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import os, base64, jsunpack, json, io, time
import random, string

tmdb_key = jsunpack.jsunpack_keys()
tvdb_key = base64.urlsafe_b64decode('MUQ2MkYyRjkwMDMwQzQ0NA==')
fanarttv_key = base64.urlsafe_b64decode('YTc4YzhmZWRjN2U3NTE1MjRkMzkyNmNhMmQyOTU3OTg=')
trakt_key = base64.urlsafe_b64decode('NDFjYzI1NjY5Y2Y2OTc0NTg4ZjA0MTMxYjcyZjc4MjEwMzdjY2I1ZTdlMjMzNDVjN2MxZTk3NGI4MGI5ZjI1NQ==')
trakt_secret = base64.urlsafe_b64decode('Y2I4OWExYTViN2ZlYmJiMDM2NmQ3Y2EyNzJjZDc4YTU5MWQ1ODI2Y2UyMTQ1NWVmYzE1ZDliYzQ1ZWNjY2QyZQ==')
all_uc_api = 'WXpFeE1qZzROV0k0WTJWall6Rm1aR1ZtWlRNNU1tVXdaR1E1WlRneVlqRT0='
openload_api = 'WW1ReU9USmxNalkzTjJZd016RTFOenBmWjNnMU5GTkROUT09'
flix_up = 'Wm0xd0xXUmxiVzg2Wm0xd0xXUmxiVzh0TWpBeE9BPT0='

loggertxt = []
setting_dict = {}
control_json = {}
doPrint = False
phantomjs_choices = ["No","Yes - Threads Only","Yes - Universally"]

ThreadsType = {'0':'Main', '1':'Interface', '2':'Download', '3':'AutoPilot' ,'4':'Provider', '5':'Host', '6':'Proxy', '5':'Thread'}
Threads = []

def setting(key):
	if key in setting_dict.keys():
		return setting_dict[key]
	else:
		return None

def get_setting(key):
	return setting(key)

def set_setting(key, value):
	if key == base64.b64decode('Y29udHJvbF9hbGxfdWNfYXBpX2tleQ==') and (value == None or value == '' or len(value) == 0):
		value = base64.b64decode(base64.b64decode(all_uc_api))
	elif key == base64.b64decode('Y29udHJvbF9vcGVubG9hZF9hcGlfa2V5') and (value == None or value == '' or len(value) == 0 or ':' not in value):
		value = base64.b64decode(base64.b64decode(openload_api))
	elif key == base64.b64decode('Y29udHJvbF9mbGl4YW5pdHlfdXNlcl9wYXNz') and (value == None or value == '' or len(value) == 0 or ':' not in value):
		value = base64.b64decode(base64.b64decode(flix_up))
	
	setting_dict[key] = value
	
def AddThread(name, desc, start_time, type, persist_bool, uid, thread=None):
	Threads.append({'name':name, 'desc':desc, 'start_time':start_time, 'type':ThreadsType[type], 'persist':persist_bool, 'uid':uid, 'thread':thread})
	
def RemoveThread(uid):
	for t in Threads:
		if t['uid'] == uid:
			Threads.remove(t)
			break
	
def getThreads():
	return Threads
	
def id_generator(size=9, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))
	
def savePermStore():
	try:
		bkup_file = 'control.json'
		with io.open(bkup_file, 'w', encoding='utf8') as f:
			data = json.dumps(control_json, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
			f.write(unicode(data))
		return True
	except Exception as e:
		log2('Error reading/saving file control.json ! %s' % e, type='CRITICAL')
		pass
		
	return False
	
def loadPermStore():
	try:
		bkup_file = 'control.json'
		file_read = None
		with io.open(bkup_file, 'r', encoding='utf8') as f:
			file_read = f.read()
			
		if file_read != None:
			ret = json.loads(file_read)
			log2('Loaded file control.json !')
			return ret

	except Exception as e:
		if os.path.exists(bkup_file):
			log2('Error loading/reading file control.json ! %s' % e, type='CRITICAL')
		else:
			log2('File not found ! Error loading/reading file control.json ! %s' % e, type='CRITICAL')
		pass

	log2('Error Loading file control.json !', type='CRITICAL')
	return None
	
def log2(err='', type='INFO', logToControl=True, doPrint=True):
	try:
		msg = '%s: %s > %s : %s' % (time.ctime(time.time()), type, 'control', err)
		if logToControl == True:
			log(msg)
		if doPrint == True:
			print msg
	except Exception as e:
		log('Error in Logging: %s >>> %s' % (msg,e))

def log(msg):
	try:
		if isinstance(msg, unicode):
			msg = msg.encode('utf-8')
		loggertxt.append(msg)
		#print('%s' % msg)
	except Exception as e:
		pass  # just give up

# set default values for script testing - these will be updated once plugin initializes
set_setting('use_openload_pairing', True)
set_setting('is_uss_installed', False)
set_setting('use_https_alt', True)
set_setting('control_all_uc_api_key', None)
set_setting('control_openload_api_key',None)
set_setting('is_control_openload_api_key', False)
set_setting('use_phantomjs', False)
set_setting('%s-%s' % (None,'Use-PhantomJS'), False)
set_setting('ca', 'CA2017')
set_setting('vspapi', 'QTZlTDI5WExMakFFNXdMNA==')
set_setting('vspapicount', 50)
set_setting('control_flixanity_user_pass', None)
set_setting('control_concurrent_src_threads', 4)