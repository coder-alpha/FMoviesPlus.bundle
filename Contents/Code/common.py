################################################################################
TITLE = "FMoviesPlus"
VERSION = '0.62' # Release notation (x.y - where x is major and y is minor)
TAG = ''
GITHUB_REPOSITORY = 'coder-alpha/FMoviesPlus.bundle'
PREFIX = "/video/fmoviesplus"
################################################################################

import time, base64, unicodedata, re, random, string
from resources.lib.libraries import control, client, cleantitle, jsfdecoder, jsunpack
from resources.lib.resolvers import host_openload, host_gvideo, host_mega, host_rapidvideo
import interface
from __builtin__ import ord, format, eval

host_misc_resolvers = SharedCodeService.misc

try:
	client.setIP4(setoveride=True)
	Log('IPv6 disabled and IPv4 set as default')
except:
	Log('Error disabling IPv6 and setting IPv4 as default')
	pass

BASE_URL = "https://bmovies.to"
	
JSEngines_ALLowed = ['Node']
Engine_OK = False
try:
	# Twoure's check routine - https://github.com/Twoure/9anime.bundle/tree/dev
	import execjs_110 as execjs
	execjs.eval("{a:true,b:function (){}}")
	
	for engine in JSEngines_ALLowed:
		if engine.lower() in execjs.get().name.lower():
			Engine_OK = True
			break
	if Engine_OK:
		Log('execjs loaded from v1.1.0')
		Log('execjs using engine: %s' % execjs.get().name)
	else:
		Log.Error('execjs Unsupported engine: %s' % execjs.get().name)
		execjs = None
except Exception as e:
	Log.Error('Failed to import execjs >>> {}'.format(e))
	execjs = None
	
try:
	from Cryptodome.Cipher import AES
	Log('Cryptodome loaded successfully')
except Exception as e:
	Log.Error('Failed to import Cryptodome >>> {}. Please install PyCryptodome (https://github.com/Legrandin/pycryptodome) and copy the library to FMoviesPlus.bundle\Contents\Libraries\Shared\ location'.format(e))

CACHE = {}
CACHE_META = {}
CACHE_EXPIRY_TIME = 3600 # 1 Hour
CACHE_EXPIRY = 3600
CACHE_COOKIE = []
TOKEN_CODE = []
TO_GB = float(1024*1024*1024)
DOWNLOAD_CHUNK_SIZE = 1.0 # in MB

# Help videos on Patebin
Help_Videos = "https://pastebin.com/raw/BMMHQund"

# Vibrant Emoji's (might not be supported on all clients)
EMOJI_LINK = u'\U0001F517'
EMOJI_GREEN_HEART = u'\U0001F49A'
EMOJI_BROKEN_HEART = u'\U0001F494'
EMOJI_VIDEO_CAMERA = u'\U0001F3A5'
EMOJI_CASSETTE = u'\U0001F4FC'
EMOJI_CINEMA = u'\U0001F3A6'
EMOJI_TV = u'\U0001F4FA'
EMOJI_ANIME = u'\u2318'
EMOJI_EXT = u'*'

# Simple Emoji's
EMOJI_HEART = u'\u2665'
EMOJI_TICK = u'\u2713'
EMOJI_CROSS = u'\u2717'
EMOJI_QUESTION = u'?'

# Text Emoji equivalent
EMOJI_TXT_POS = u'(v)'
EMOJI_TXT_NEG = u'(x)'
EMOJI_TXT_QUES = u'(?)'

INTERFACE_OPTIONS_LABELS = {'Provider':'Provider', 'Host':'Host', 'Proxy':'Proxy'}

OPTIONS_PROXY = []
INTERNAL_SOURCES = []
OPTIONS_PROVIDERS = []

#INTERNAL_SOURCES_QUALS = [{'label':'4K','enabled': 'True'},{'label':'1080p','enabled': 'True'},{'label':'720p','enabled': 'True'},{'label':'480p','enabled': 'True'},{'label':'360p','enabled': 'True'}]
#INTERNAL_SOURCES_RIPTYPE = [{'label':'BRRIP','enabled': 'True'},{'label':'PREDVD','enabled': 'True'},{'label':'CAM','enabled': 'True'},{'label':'TS','enabled': 'True'},{'label':'SCR','enabled': 'True'},{'label':'UNKNOWN','enabled': 'True'}]
#INTERNAL_SOURCES_FILETYPE = [{'label':'Movie/Show','enabled': 'True'},{'label':'Trailer','enabled': 'True'},{'label':'Interviews','enabled': 'False'},{'label':'Behind the scenes','enabled': 'False'},{'label':'Music Video','enabled': 'False'},{'label':'Deleted Scenes','enabled': 'False'},{'label':'Misc.','enabled': 'False'}]
#INTERNAL_SOURCES_SIZES = [{'label':'> 2GB','enabled': 'True','LL':2*TO_GB,'UL':100*TO_GB},{'label':'1GB - 2GB','enabled': 'True','LL':1*TO_GB,'UL':2*TO_GB},{'label':'0.5GB - 1GB','enabled': 'True','LL':0.5*TO_GB,'UL':1*TO_GB},{'label':'0GB - 0.5GB','enabled': 'True','LL':1,'UL':0.5*TO_GB},{'label':'0GB','enabled': 'False','LL':0,'UL':0}]

INTERNAL_SOURCES_SIZES_CONST = [{'label':'> 2GB','enabled': 'True','LL':2*TO_GB,'UL':100*TO_GB},{'label':'1GB >= 2GB','enabled': 'True','LL':1*TO_GB,'UL':2*TO_GB},{'label':'0.5GB >= 1GB','enabled': 'True','LL':0.5*TO_GB,'UL':1*TO_GB},{'label':'0GB >= 0.5GB','enabled': 'True','LL':999999,'UL':0.5*TO_GB},{'label':'0GB','enabled': 'False','LL':0,'UL':999999}]
INTERNAL_SOURCES_QUALS_CONST = [{'label':'4K','enabled': 'True'},{'label':'1080p','enabled': 'True'},{'label':'720p','enabled': 'True'},{'label':'480p','enabled': 'True'},{'label':'360p','enabled': 'True'}]
INTERNAL_SOURCES_RIPTYPE_CONST = [{'label':'BRRIP','enabled': 'True'},{'label':'PREDVD','enabled': 'True'},{'label':'CAM','enabled': 'True'},{'label':'TS','enabled': 'True'},{'label':'SCR','enabled': 'True'},{'label':'UNKNOWN','enabled': 'True'}]
INTERNAL_SOURCES_FILETYPE_CONST = [{'label':'Movie/Show','enabled':'True'},{'label':'Trailer','enabled':'True'},{'label':'Featurette','enabled':'False'},{'label':'Interviews','enabled':'False'},{'label':'Behind the scenes','enabled':'False'},{'label':'Music Video','enabled':'False'},{'label':'Deleted Scenes','enabled':'False'},{'label':'Misc.','enabled':'False'}]
INTERNAL_SOURCES_SIZES = list(INTERNAL_SOURCES_SIZES_CONST)
INTERNAL_SOURCES_QUALS = list(INTERNAL_SOURCES_QUALS_CONST)
INTERNAL_SOURCES_RIPTYPE = list(INTERNAL_SOURCES_RIPTYPE_CONST)
INTERNAL_SOURCES_FILETYPE = list(INTERNAL_SOURCES_FILETYPE_CONST)

DEVICE_OPTIONS = ['Dumb-Keyboard','List-View','Redirector','Simple-Emoji','Vibrant-Emoji','Multi-Link-View','Full-poster display','Use-PhantomJS','No-Extra-Page-Info','Use-FileSize-Sorting','Force-Transcoding','No-Extra-Page-Info (Anime)']
DEVICE_OPTION = {DEVICE_OPTIONS[0]:'The awesome Keyboard for Search impaired devices',
				DEVICE_OPTIONS[1]:'Force List-View of Playback page listing sources',
				DEVICE_OPTIONS[2]:'Required in certain cases - *Experimental (refer forum)',
				DEVICE_OPTIONS[3]:'Enable Simple Emoji Icons (%s|%s - Supported by Most Clients)' % (EMOJI_TICK,EMOJI_CROSS),
				DEVICE_OPTIONS[4]:'Enable Vibrant Emoji Icons (%s|%s - Supported by Limited Clients)' % (EMOJI_GREEN_HEART,EMOJI_BROKEN_HEART),
				DEVICE_OPTIONS[5]:'Shows All Video Items in single container - makes many requests to server',
				DEVICE_OPTIONS[6]:'Shows Uncropped Poster - client compatibility is untested',
				DEVICE_OPTIONS[7]:'Use PhantomJS - For parsing links. Binary download required',
				DEVICE_OPTIONS[8]:'No-Extra-Page-Info - Speeds up navigation by not downloading detailed item info',
				DEVICE_OPTIONS[9]:'Use-FileSize-Sorting - Uses FileSize instead of Resolution info provided by site which can be inaccurate',
				DEVICE_OPTIONS[10]:'Force-Transcoding - Sets the item\'s container property to null in order to force transcoding by PMS',
				DEVICE_OPTIONS[11]:'No-Extra-Page-Info (Anime) - Speeds up navigation by not downloading detailed item info'}
DEVICE_OPTION_CONSTRAINTS = {DEVICE_OPTIONS[2]:[{'Pref':'use_https_alt','Desc':'Use Alternate SSL/TLS','ReqValue':'disabled'}]}
DEVICE_OPTION_CONSTRAINTS2 = {DEVICE_OPTIONS[5]:[{'Option':6,'ReqValue':False}], DEVICE_OPTIONS[6]:[{'Option':5,'ReqValue':False}]}
DEVICE_OPTION_PROPOGATE_TO_CONTROL = {DEVICE_OPTIONS[7]:True}

DOWNLOAD_OPTIONS = {'movie':[], 'show':[]}
DOWNLOAD_OPTIONS_SECTION_TEMP = {}
DOWNLOAD_MODE = ['Add','Request']
Dict['DOWNLOAD_OPTIONS_SECTION_TEMP'] = {}
DOWNLOAD_STATUS = ['Queued','Downloading','Completed','Failed','Requested','All']
DOWNLOAD_ACTIONS = ['Cancel Download','Pause Download','Resume Download','Postpone Download','Start Download']
DOWNLOAD_ACTIONS_K = {'Cancel Download':'Cancelled','Pause Download':'Paused','Resume Download':'Resumed','Postpone Download':'Postponed','Start Download':'Started','Done':'Done','Limbo':'Limbo','Live':'Live','Throttling':'Throttling','Waiting':'Waiting'}
DOWNLOAD_ACTIONS_INFO = ['Cancels the Download and removes its entry and temporary file from disk.','Pauses the current Download and let it be Resumed.','Resume the currently Paused Download.','Postpones the current Download for 2 hours by adding it to Queue List','Starts the Postponed Download.']
DOWNLOAD_PROPS = ['Done','Limbo','Throttling','Waiting']
DOWNLOAD_STATS = {}
DOWNLOAD_TEMP = {}
DOWNLOAD_FMP_EXT = '.FMPTemp'

ANIME_SEARCH = []
ANIME_KEY = '9anime'
ANIME_URL = 'https://%s.is' % ANIME_KEY
ANIME_SEARCH_URL = ANIME_URL + '/search?keyword=%s'
ES_API_URL = 'http://movies-v2.api-fetch.website'

EXT_SITE_URLS = [ANIME_URL, ES_API_URL]

# Golbal Overrides - to disable
SHOW_EXT_SRC_WHILE_LOADING = True
USE_DOWNLOAD_RESUME_GEN = True
USE_DOWNLOAD_RESUME_MEGA = True
USE_EXT_URLSERVICES = True
USE_COOKIES = True
DOWNLOAD_BACKUP_OPER = True
USE_SECOND_REQUEST = True
USE_JSFDECODER = True
USE_JSENGINE = True
USE_JSWEBHOOK = True
ALT_PLAYBACK = True
DEV_BM_CONVERSION = False
NO_MOVIE_INFO = False
USE_CUSTOM_TIMEOUT = False
SEARCH_EXT_SOURCES_FROM_SEARCH_MENU = True
CHECK_BASE_URL_REDIRECTION = False
MY_CLOUD_DISABLED = True
ENCRYPTED_URLS = False
DEV_DEBUG = False
WBH = 'aHR0cHM6Ly9ob29rLmlvL2NvZGVyLWFscGhhL3Rlc3Q='

####################################################################################################
# Get Key from a Dict using Val
@route(PREFIX + '/GetEmoji')
def GetEmoji(type, mode='vibrant', session=None):

	# modes = ['simple','vibrant'] - enforce mode to override Prefs for Search Filter

	type = str(type).strip().lower()
	
	if session == None:
		session = getSession()
	
	if mode == 'simple' and (UsingOption(DEVICE_OPTIONS[3], session=session) or UsingOption(DEVICE_OPTIONS[4], session=session)):
		if type == 'pos' or type == 'true':
			return EMOJI_TICK
		elif type =='neg' or type == 'false':
			return EMOJI_CROSS
	elif mode=='vibrant' and UsingOption(DEVICE_OPTIONS[4], session=session):
		if type == 'pos' or type == 'true':
			return EMOJI_GREEN_HEART
		elif type =='neg' or type == 'false':
			return EMOJI_BROKEN_HEART
	elif UsingOption(DEVICE_OPTIONS[3], session=session):
		if type == 'pos' or type == 'true':
			return EMOJI_TICK
		elif type =='neg' or type == 'false':
			return EMOJI_CROSS
	else:
		if type == 'pos' or type == 'true':
			return EMOJI_TXT_POS
		elif type =='neg' or type == 'false':
			return EMOJI_TXT_NEG
		else:
			return EMOJI_TXT_QUES
	
	return EMOJI_QUESTION


####################################################################################################
# Get Key from a Dict using Val
@route(PREFIX + '/getkeyfromval')
def GetKeyFromVal(list, val_look):
	for key, val in list.iteritems():
		if val == val_look:
			return key

def set_control_settings(session=None):

	keys = ['use_https_alt','control_all_uc_api_key','control_openload_api_key','use_openload_pairing','use_phantomjs','control_phantomjs_path']
	control.set_setting('ver', VERSION)
	for i in range(0,len(keys)):
		try:
			key = keys[i]
			control.set_setting(key, Prefs[key])
			
		except Exception as e:
			Log('ERROR common.py-1>set_control_settings: %s' % e)

	try:
		control.set_setting('is_uss_installed', is_uss_installed())
	except Exception as e:
		Log.Error('ERROR common.py-2>set_control_settings: %s' % e)
		
	try:
		key = DEVICE_OPTIONS[7]
		
		if key in DEVICE_OPTION_PROPOGATE_TO_CONTROL.keys() and DEVICE_OPTION_PROPOGATE_TO_CONTROL[key] != None and DEVICE_OPTION_PROPOGATE_TO_CONTROL[key] == True:
			control.set_setting('%s-%s' % (session,key), UsingOption(key, session=session))
	except Exception as e:
		Log.Error('ERROR common.py-3>set_control_settings: %s' % e)
		
	try:
		control_all_uc_api_key = Prefs['control_all_uc_api_key']
		if control_all_uc_api_key == None or len(control_all_uc_api_key) == 0:
			is_control_all_uc_api_key = False
		else:
			is_control_all_uc_api_key = True
		control.set_setting('is_control_all_uc_api_key', is_control_all_uc_api_key)
	except Exception as e:
		Log.Error('ERROR common.py-2>set_control_settings: %s' % e)
		
	try:
		control_openload_api_key = Prefs['control_openload_api_key']
		if control_openload_api_key == None or len(control_openload_api_key) == 0:
			is_control_openload_api_key = False
		else:
			is_control_openload_api_key = True
		control.set_setting('is_control_openload_api_key', is_control_openload_api_key)
	except Exception as e:
		Log.Error('ERROR common.py-2>set_control_settings: %s' % e)
			
	if Prefs["use_debug"]:
		Log("User Preferences have been set to Control")
		
def set_settings_to_control(key, val):

	try:
		control.set_setting(key, val)
	except Exception as e:
		Log.Error('ERROR common.py>set_settings_to_control: %s' % e)
	
	if Prefs["use_debug"]:
		Log("User Setting %s:%s set to Control" % (key,val))
			
####################################################################################################
# Gets a client specific identifier
@route(PREFIX + '/getsession')
def getSession():

	session = 'UnknownPlexClientSession'
	if 'X-Plex-Client-Identifier' in str(Request.Headers):
		session = str(Request.Headers['X-Plex-Client-Identifier'])
	elif 'X-Plex-Target-Client-Identifier' in str(Request.Headers):
		session = str(Request.Headers['X-Plex-Target-Client-Identifier'])
	elif 'User-Agent' in str(Request.Headers) and 'X-Plex-Token' in str(Request.Headers):
		session = 'UnknownClient-'+encode(str(Request.Headers['User-Agent']) + str(Request.Headers['X-Plex-Token'][:3]))[:10]
	
	return (session)
	
def setPlexTVUser(session):
	token = Request.Headers.get("X-Plex-Token", "")
	url = "https://plex.tv"
	plexTVUser = None
	try:
		xml = XML.ObjectFromURL(url, headers={'X-Plex-Token': token})
		plexTVUser = xml.get("myPlexUsername")
	except:
		pass
	
	try:
		control.set_setting('%s-%s' % (session, 'user'), plexTVUser)
	except Exception as e:
		Log.Error('ERROR common.py>setPlexTVUser: %s' % e)

#######################################################################################################
# base64 decode
@route(PREFIX + '/decode')
def decode(str):
	return base64.b64decode(str)
	
# base64 encode
@route(PREFIX + '/encode')
def encode(str):
	return base64.b64encode(str)
	
#######################################################################################################
@route(PREFIX + '/getHighestQualityLabel')
def getHighestQualityLabel(strr, q_label):

	try:
		i =  (q_label.lower().replace('p','').replace('hd','').strip()) # fail when q_label = TS, CAM, etc.
		i = int(i.strip())
		s = ''
		q_label = '%sp' % i
	except:
		s = ' (%s)' % q_label
	
	if '1080' in strr:
		return '1080p' + s
	elif '720' in strr:
		return '720p' + s
	elif '480' in strr:
		return '480p' + s
	elif '360' in strr:
		return '360p' + s
	else:
		return q_label
	
#######################################################################################################
def isArrayValueInString(arr, mystr, toLowercase=True):

	for a in arr:
		if toLowercase == True:
			if a.lower() in mystr.lower():
				return True
		else:
			if a in mystr:
				return True
			
	return False

#######################################################################################################
@route(PREFIX + "/setDictVal")
def setDictVal(key, val, session=None):

	if str(val).lower() == 'true':
		val = 'enabled'
	elif str(val).lower() == 'false':
		val = 'disabled'
		
	key = key.replace('Toggle','')

	if DEVICE_OPTION_CONSTRAINTS != None and key in DEVICE_OPTION_CONSTRAINTS.keys():
		for key_cons in DEVICE_OPTION_CONSTRAINTS[key]:
			if Prefs[key_cons['Pref']] and val!=key_cons['ReqValue']:
				return ObjectContainer(header='Sorry', message='Sorry %s has conflict with Pref: %s needs to be %s.' % (key, key_cons['Desc'], key_cons['ReqValue']), title1=key)
				
	if DEVICE_OPTION_CONSTRAINTS2 != None and key in DEVICE_OPTION_CONSTRAINTS2.keys():
		for key_cons in DEVICE_OPTION_CONSTRAINTS2[key]:
			if str(UsingOption(DEVICE_OPTIONS[key_cons['Option']])) != str(key_cons['ReqValue']):
				return ObjectContainer(header='Sorry', message='Sorry %s has conflict with Device Option: %s needs to be %s.' % (key, DEVICE_OPTIONS[key_cons['Option']], key_cons['ReqValue']), title1=key)
				
	if session == None:
		session = getSession()
		
	if key in DEVICE_OPTION_PROPOGATE_TO_CONTROL.keys() and DEVICE_OPTION_PROPOGATE_TO_CONTROL[key] != None and DEVICE_OPTION_PROPOGATE_TO_CONTROL[key] == True:
		control.set_setting('%s-%s' % (session,key), True if val=='enabled' else False)

	Dict['Toggle%s%s' % (key,session)] = val
	Dict.Save()
	if Prefs["use_debug"]:
		Log("%s status: %s" % (key,val))
		
	return ObjectContainer(header=key, message=key + ' has been ' + val + ' for this device.', title1=key)

@route(PREFIX + "/UsingOption")
def UsingOption(key, session=None):
	if session == None:
		session = getSession()
	if Dict['Toggle%s%s' % (key,session)] == None or Dict['Toggle%s%s' % (key,session)] == 'disabled':
		return False
	else:
		return True
		
######################################################################################
@route(PREFIX + "/isForceNoCache")
def isForceNoCache(**kwargs):
	# no_cache=isForceNoCache()
	
	if CACHE_EXPIRY == 0:
		return True
		
	return False

####################################################################################################
def OrderBasedOn(srcs, use_host=True, use_filesize=False):
	# order sources based on sequence of INTERNAL_SOURCES / quality
	#Log(INTERNAL_SOURCES)
	filter_extSources = []
	
	if use_filesize == True:
		#Log(srcs)
		filter_extSources = sorted(srcs, key=lambda k: k['fs'], reverse=True)
	else:
		if use_host == True:
			for host in INTERNAL_SOURCES: filter_extSources += [i for i in srcs if i['quality'] == '4K' and i['source'].lower() == host['name']]
			for host in INTERNAL_SOURCES: filter_extSources += [i for i in srcs if i['quality'] == '1080p' and i['source'].lower() == host['name']]
			for host in INTERNAL_SOURCES: filter_extSources += [i for i in srcs if i['quality'] == '720p' and i['source'].lower() == host['name']]
			for host in INTERNAL_SOURCES: filter_extSources += [i for i in srcs if i['quality'] == '480p' and i['source'].lower() == host['name']]
			for host in INTERNAL_SOURCES: filter_extSources += [i for i in srcs if i['quality'] == '360p' and i['source'].lower() == host['name']]
		else:
			filter_extSources += [i for i in srcs if i['quality'] == '4K']
			filter_extSources += [i for i in srcs if i['quality'] == '1080p']
			filter_extSources += [i for i in srcs if i['quality'] == '720p']
			filter_extSources += [i for i in srcs if i['quality'] == '480p']
			filter_extSources += [i for i in srcs if i['quality'] == '360p']
	
	srcs = filter_extSources
	
	# order sources based on sequence of INTERNAL_SOURCES_FILETYPE / video type
	#Log(INTERNAL_SOURCES_FILETYPE)
	filter_extSources = []
	
	
	filter_extSources += [i for i in srcs if 'Movie'.lower() in i['vidtype'].lower() or 'Show'.lower() in i['vidtype'].lower()]
	for vid_types_defined in INTERNAL_SOURCES_FILETYPE:
		#Log(vid_types_defined['label'].lower())
		filter_extSources += [i for i in srcs if vid_types_defined['label'].lower() == i['vidtype'].lower()]
	
	# filter_extSources += [i for i in srcs if 'Trailer'.lower() == i['vidtype'].lower()]
	# filter_extSources += [i for i in srcs if 'Interviews'.lower() == i['vidtype'].lower()]
	# filter_extSources += [i for i in srcs if 'Behind the scenes'.lower() == i['vidtype'].lower()]
	# filter_extSources += [i for i in srcs if 'Music Video'.lower() == i['vidtype'].lower()]
	# filter_extSources += [i for i in srcs if 'Misc.'.lower() == i['vidtype'].lower()]
	
	srcs = filter_extSources
	
	return srcs
	
####################################################################################################
def FilterBasedOn(srcs, use_quality=True, use_riptype=True, use_vidtype=True, use_provider=True, use_host=True, use_filesize=True):

	# filter sources based on host enabled in INTERNAL_SOURCES
	#Log(INTERNAL_SOURCES)
	if use_host == True:
		filter_extSources = []
		for host in INTERNAL_SOURCES: filter_extSources += [i for i in srcs if i['source'].lower() == host['name'].lower() and str(host['enabled'])=='True']
		srcs = filter_extSources
	
	# filter sources based on enabled provider in OPTIONS_PROVIDERS
	#Log(OPTIONS_PROVIDERS)
	if use_provider == True:
		filter_extSources = []
		for provider in OPTIONS_PROVIDERS: filter_extSources += [i for i in srcs if i['provider'].lower() == provider['name'].lower() and str(provider['enabled'])=='True']
		srcs = filter_extSources
		
	# filter sources based on enabled quality in INTERNAL_SOURCES_QUALS
	#Log(INTERNAL_SOURCES_QUALS)
	if use_quality == True:
		filter_extSources = []
		for qual in INTERNAL_SOURCES_QUALS: filter_extSources += [i for i in srcs if i['quality'].lower() == qual['label'].lower() and str(qual['enabled'])=='True']
		srcs = filter_extSources
		
	# filter sources based on enabled file size in INTERNAL_SOURCES_SIZES
	#Log(INTERNAL_SOURCES_SIZES)
	if use_filesize == True:
		filter_extSources = []
		for fs in INTERNAL_SOURCES_SIZES: filter_extSources += [i for i in srcs if (i['vidtype'].lower() in 'movie/show' and i['fs'] >= fs['LL'] and i['fs'] < fs['UL'] and str(fs['enabled'])=='True') or (i['vidtype'].lower() not in 'movie/show')]
		srcs = filter_extSources
	
	# filter sources based on enabled rip-type in INTERNAL_SOURCES_RIPTYPE
	#Log(INTERNAL_SOURCES_RIPTYPE)
	if use_riptype == True:
		filter_extSources = []
		for riptype in INTERNAL_SOURCES_RIPTYPE: filter_extSources += [i for i in srcs if i['rip'].lower() == riptype['label'].lower() and str(riptype['enabled'])=='True']
		srcs = filter_extSources
	
	# filter sources based on enabled rip-type in INTERNAL_SOURCES_FILETYPE
	#Log(INTERNAL_SOURCES_FILETYPE)
	if use_vidtype == True:
		filter_extSources = []
		for vidtype in INTERNAL_SOURCES_FILETYPE: filter_extSources += [i for i in srcs if i['vidtype'].lower() in vidtype['label'].lower() and str(vidtype['enabled'])=='True']
		srcs = filter_extSources
	
	return srcs
		
####################################################################################################
# Get HTTP response code (200 == good)
@route(PREFIX + '/gethttpstatus')
def GetHttpStatus(url, cookies=None):
	try:
		req = GetHttpRequest(url=url, cookies=cookies)
		if req != None:
			conn = urllib2.urlopen(req, timeout=client.GLOBAL_TIMEOUT_FOR_HTTP_REQUEST)
			resp = str(conn.getcode())
		else:
			resp = '0'
	except Exception as e:
		resp = '0'
	return resp
	
####################################################################################################
# Get HTTP request
@route(PREFIX + '/gethttprequest')
def GetHttpRequest(url, cookies=None):
	try:
		headers = {'User-Agent': client.USER_AGENT,
		   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
		   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
		   'Accept-Encoding': 'none',
		   'Accept-Language': 'en-US,en;q=0.8',
		   'Connection': 'keep-alive',
		   'Referer': url}
		   
		if cookies != None:
			headers['Cookie'] = cookies
		if '|' in url:
			url_split = url.split('|')
			url = url_split[0]
			headers['Referer'] = url
			
			for params in url_split:
				if '=' in params:
					param_split = params.split('=')
					param = param_split[0].strip()
					param_val = urllib2.quote(param_split[1].strip(), safe='/=&')
					headers[param] = param_val

		if 'http://' in url or 'https://' in url:
			req = urllib2.Request(url, headers=headers)
		else:
			req = None
	except Exception as e:
		req = None
	return req
	
######################################################################################
def ResolveFinalUrl(isTargetPlay, data, pair_required=False, params=None, host=None, **kwargs):
	# responses - true, false, unknown
	vidurl = data
	err = ''
		
	if params != None:
		params = JSON.ObjectFromString(D(params))
		headers = params['headers']		
		cookie = params['cookie']
		
	if vidurl != None:
		if isTargetPlay and 'openload' in host and pair_required == False:
			vidurl, err, sub_url = host_openload.resolve(vidurl)
		else:
			pass

	if Prefs["use_debug"]:
		Log("--- Resolved Final Url ---")
		Log("Video Url: %s : Error: %s" % (vidurl, err))
			
	return vidurl
	
######################################################################################
@route(PREFIX + "/isItemVidAvailable")
def isItemVidAvailable(isTargetPlay, data, params=None, host=None, **kwargs):
	# responses - true, false, unknown
	vidurl = None
	httpsskip = Prefs["use_https_alt"]
	use_web_proxy = Prefs["use_web_proxy"]
	
	if isTargetPlay:
		vidurl = data
	else:
		data = D(data)
		data = JSON.ObjectFromString(data)
		files = JSON.ObjectFromString(data['server'])
		sortable_list = []
		for file in files:
			furl = file['file']
			res = file['label'].replace('p','')
			if res != '1080':
				res = '0'+res
			type = file['type']
			sortable_list.append({'label': res, 'file':furl, 'type':type})
		newlist = sorted(sortable_list, key=lambda k: k['label'], reverse=True)
		for file in newlist:
			vidurl = file['file']
			break
			
	isVideoOnline = 'false'

	headers = None
	cookie = None
	if params != None:
		params = JSON.ObjectFromString(D(params))
		headers = params['headers']		
		cookie = params['cookie']
		
	if vidurl != None:
		try:
			if isTargetPlay and 'openload' in host:
				if host_openload.check(vidurl, embedpage=True, headers=headers, cookie=cookie)[0] == True:
						isVideoOnline = 'true'
			elif isTargetPlay and host in host_misc_resolvers.supported_hosts:
				resolved_url, params, udp = host_misc_resolvers.resolve(vidurl, httpsskip)
				
				if resolved_url != None:
					# params = JSON.ObjectFromString(D(params))
					# headers = params['headers']
					# hls_url = resolved_url[len(resolved_url)-1]['file']
					
					# Log(hls_url)
					# Log(headers)
					
					# if httpsskip == True:
						# http_res = request(hls_url, headers=headers, httpsskip=True)
					# else:
						# http_res = HTTP.Request(hls_url, headers=headers).content
					
					# Log(http_res)
					# if http_res == None:
						# isVideoOnline = 'unknown'
					# if http_res in client.HTTP_GOOD_RESP_CODES or http_res in client.GOOGLE_HTTP_GOOD_RESP_CODES_1 or 'EXTM3U' in http_res:
						# isVideoOnline = 'true'
					hls_url = resolved_url[len(resolved_url)-1]['file']
					isVideoOnline = 'true'
						
			elif isTargetPlay:
				isVideoOnline = 'unknown'
			else:
				if host_gvideo.check(vidurl, headers=headers, cookie=cookie, httpsskip=httpsskip)[0] == True:
					isVideoOnline = 'true'

		except Exception as e:
			Log('ERROR common.py>isItemVidAvailable %s, %s:' % (e.args,vidurl))
			Log(data)
			isVideoOnline = 'unknown'

	if Prefs["use_debug"]:
		Log("--- LinkChecker ---")
		Log("Video Url: %s : Online: %s" % (vidurl, isVideoOnline))
			
	return isVideoOnline
	
######################################################################################
@route(PREFIX + "/GetPageElements")
def GetPageElements(url, headers=None, referer=None, timeout=15):

	page_data_string = None
	page_data_elems = None
	error = ''
	try:
		if url in CACHE_META.keys():
			try:
				CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
			except:
				CACHE_EXPIRY = CACHE_EXPIRY_TIME
				
			if CACHE_META[url]['ts'] + CACHE_EXPIRY > time.time():
				page_data_string = D(CACHE_META[url]['data'])
				
		if page_data_string == None:
			page_data_string, error = GetPageAsString(url=url, headers=headers, referer=referer, timeout=timeout)
			
		if page_data_string == None:
			raise PageError('Request returned None.')

		try:
			page_data_elems = HTML.ElementFromString(page_data_string)
		except Exception as e:
			if url in CACHE_META.keys():
				del CACHE_META[url]
			raise Exception(e)
		
	except Exception as e:
		Log('ERROR common.py>GetPageElements: %s URL: %s DATA: %s' % (error,url,page_data_string))

	return page_data_elems, error
	
def make_cookie_str():
	try:
		cookie_str = ''
		p_cookie = ''
		error = ''
		if len(CACHE_COOKIE) > 0:
		
			user_defined_reqkey_cookie = Prefs['reqkey_cookie']
			reqCookie = CACHE_COOKIE[0]['reqkey']
			if user_defined_reqkey_cookie != None and user_defined_reqkey_cookie != '':
				reqCookie = user_defined_reqkey_cookie

			p_cookie = CACHE_COOKIE[0]['cookie'] + '; ' + reqCookie
			p_cookie = p_cookie.replace(';;',';')
			p_cookie_s = p_cookie.split(';')
			cookie_string_arr = []
		else:
			#setTokenCookie(serverts=serverts, use_debug=use_debug)
			error = "Cookie not set ! Please try Reset Cookies under the Options menu."
			p_cookie_s = []
		
		for ps in p_cookie_s:
			if '=' in ps:
				try:
					ps_s = ps.split('=')
					k = ps_s[0].strip()
					v = ps_s[1].strip()
					if k == 'reqkey':
						if len(v) > 5:
							cookie_string_arr.append(k+'='+v)
					else:
						cookie_string_arr.append(k+'='+v)
				except:
					pass
		try:
			cookie_str = ('; '.join(x for x in sorted(cookie_string_arr)))
		except:
			cookie_str = p_cookie
		
		return cookie_str, error
	except Exception as e:
		Log("common.py > make_cookie_str : %s" % e)
		return cookie_str, e
		
def cleanCookie(str):
	str = str.replace('\n','')
	str_s = str.split(';')
	cookie_string_arr = []
	for str in str_s:
		if 'expires' not in str and 'path' not in str and 'Date' not in str and 'undefined' not in str and 'function' not in str and '=' in str:
			ps_s= str.split('=')
			k = ps_s[0].strip()
			v = ps_s[1].strip()
			if k == 'reqkey':
				if len(v) > 3:
					cookie_string_arr.append(k + '=' + v)
			else:
				cookie_string_arr.append(k + '=' + v)
			
	cookie_string = ('; '.join(x for x in cookie_string_arr))
	return cookie_string
	
######################################################################################
@route(PREFIX + "/GetPageAsString")
def GetPageAsString(url, headers=None, timeout=15, referer=None):

	use_debug = Prefs["use_debug"]
	
	try:
		CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
	except:
		CACHE_EXPIRY = CACHE_EXPIRY_TIME

	page_data_string = None
	error = ''
	
	if headers == None:
		headers = {}
	if referer != None:
		headers['Referer'] = referer
	elif 'Referer' in headers:
		pass
	else:
		headers['Referer'] = url
	
	if USE_COOKIES and ('fmovies' in url or 'bmovies' in url):
		cookies, error = make_cookie_str()
		if error == '':
			headers['Cookie'] = cookies
			headers['User-Agent'] = CACHE_COOKIE[0]['UA']

			if use_debug:
				Log("Using Cookie retrieved at: %s" % time.ctime(CACHE_COOKIE[0]['ts']))
				Log("Using Cookie: %s" % (cookies))

	try:
		if Prefs["use_https_alt"]:
			if use_debug:
				Log("Using SSL Alternate Option")
				Log("Url: " + url)
			page_data_string = interface.request(url = url, headers=headers, timeout=str(timeout), httpsskip=True)
			if page_data_string == None:
				error, page_data_string = interface.request(url = url, headers=headers, timeout=str(timeout), error=True, httpsskip=True)
		elif Prefs["use_web_proxy"]:
			page_data_string = None
			if use_debug:
				Log("Using Web-proxy option")
				Log("Url: " + url)
			for proxy in OPTIONS_PROXY:
				if use_debug:
					Log("Using Proxy: %s - %s" % (proxy['name'], proxy['url']))
				if proxy['working']:
					page_data_string = interface.request_via_proxy(url=url, proxy_name=proxy['name'], proxy_url=proxy['url'], headers=headers, timeout=str(timeout), use_web_proxy=True)
					if page_data_string != None:
						break
		else:
			if Prefs["use_debug"]:
				Log("Headers: %s" % headers)
			try:
				page_data_string = HTTP.Request(url, headers=headers, timeout=timeout).content
			except:
				pass
			if page_data_string == None:
				error, page_data_string = interface.request(url = url, headers=headers, timeout=str(timeout), error=True)
				
		if url not in CACHE_META.keys() and page_data_string != None and error == '':
			CACHE_META[url] = {}
			CACHE_META[url]['ts'] = time.time()
			CACHE_META[url]['data'] = E(page_data_string)
				
	except Exception as e:
		Log('ERROR common.py>GetPageAsString: %s URL: %s' % (e.args,url))
		pass
		
	return page_data_string, error
	
@route(PREFIX + "/request")
def request(url, close=True, redirect=True, followredirect=False, error=False, proxy=None, post=None, headers=None, mobile=False, limit=None, referer=None, cookie=None, output='', timeout=15, httpsskip=False, use_web_proxy=False):

	page_data_string = None
	try:
		if Prefs["use_https_alt"]:
			if Prefs["use_debug"]:
				Log("Using SSL Alternate Option")
				Log("Url: " + url)
			page_data_string = interface.request(url = url, headers=headers, timeout=str(timeout))
		elif Prefs["use_web_proxy"]:
			page_data_string = None
			use_web_proxy = True
			if Prefs["use_debug"]:
				Log("Using Web-proxy option")
				Log("Url: " + url)
			for proxy in OPTIONS_PROXY:
				if proxy['working']:
					if Prefs["use_debug"]:
						Log("Using Proxy: %s - %s" % (proxy['name'], proxy['url']))
					page_data_string = interface.request_via_proxy(url=url, proxy_name=proxy['name'], proxy_url=proxy['url'], close=close, redirect=redirect, followredirect=followredirect, error=error, proxy=proxy, post=post, headers=headers, mobile=mobile, limit=limit, referer=referer, cookie=cookie, output=output, timeout=str(timeout), httpsskip=httpsskip, use_web_proxy=use_web_proxy)
					if page_data_string != None:
						break
		else:
			if headers == None:
				page_data_string = HTTP.Request(url, timeout=timeout).content
			else:
				page_data_string = HTTP.Request(url, headers=headers, timeout=timeout).content
		
	except Exception as e:
		Log('ERROR common.py>request: %s URL: %s' % (e.args,url))
		pass
		
	return page_data_string
	
####################################################################################################
def OpenLoadUnpair(**kwargs):
	msg = host_openload.unpair()
	if Prefs["use_debug"]:
		for m in msg:
			Log('OpenLoad UnPair: %s' % m)

######################################################################################

def id_generator(size=9, chars=string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))
	
def makeid(N,arr):

	r = ''
	while r == '':
		rt = ''.join(random.choice(string.ascii_uppercase) for _ in range(N))
		rt += ''.join(random.choice(string.digits) for _ in range(N))
		if rt not in arr:
			r = rt
	return r
	
def cleanJSS1(str):
	if str == None: raise ValueError("cleanJSS: Token is None type")
	
	txt = str

	for i in range(0,len(str)):
		c = str[i]
		if (ord(c) <= 127 and c != '_'):
			pass
		else:
			txt = txt.replace(c, makeid(1))

	return txt
	
def cleanJSS2(str):
	if str == None: raise ValueError("cleanJSS: Token is None type")
	
	token = str.replace(D('KCEhW10rW10pWyshIVtdXSsoW11bW11dK1tdKVshK1tdKyEhW10rISFbXV0rW11bKCFbXStbXSlbIStbXSshIVtdKyEhW11dKyhbXSt7fSlbKyEhW11dKyghIVtdK1tdKVsrISFbXV0rKCEhW10rW10pWytbXV1dWyhbXSt7fSlbIStbXSshIVtdKyEhW10rISFbXSshIVtdXSsoW10re30pWyshIVtdXSsoW11bW11dK1tdKVsrISFbXV0rKCFbXStbXSlbIStbXSshIVtdKyEhW11dKyghIVtdK1tdKVsrW11dKyghIVtdK1tdKVsrISFbXV0rKFtdW1tdXStbXSlbK1tdXSsoW10re30pWyErW10rISFbXSshIVtdKyEhW10rISFbXV0rKCEhW10rW10pWytbXV0rKFtdK3t9KVsrISFbXV0rKCEhW10rW10pWyshIVtdXV0oKCEhW10rW10pWyshIVtdXSsoW11bW11dK1tdKVshK1tdKyEhW10rISFbXV0rKCEhW10rW10pWytbXV0rKFtdW1tdXStbXSlbK1tdXSsoISFbXStbXSlbKyEhW11dKyhbXVtbXV0rW10pWyshIVtdXSsoW10re30pWyErW10rISFbXSshIVtdKyEhW10rISFbXSshIVtdKyEhW11dKyhbXVtbXV0rW10pWytbXV0rKFtdW1tdXStbXSlbKyEhW11dKyhbXVtbXV0rW10pWyErW10rISFbXSshIVtdXSsoIVtdK1tdKVshK1tdKyEhW10rISFbXV0rKFtdK3t9KVshK1tdKyEhW10rISFbXSshIVtdKyEhW11dKygre30rW10pWyshIVtdXSsoW10rW11bKCFbXStbXSlbIStbXSshIVtdKyEhW11dKyhbXSt7fSlbKyEhW11dKyghIVtdK1tdKVsrISFbXV0rKCEhW10rW10pWytbXV1dWyhbXSt7fSlbIStbXSshIVtdKyEhW10rISFbXSshIVtdXSsoW10re30pWyshIVtdXSsoW11bW11dK1tdKVsrISFbXV0rKCFbXStbXSlbIStbXSshIVtdKyEhW11dKyghIVtdK1tdKVsrW11dKyghIVtdK1tdKVsrISFbXV0rKFtdW1tdXStbXSlbK1tdXSsoW10re30pWyErW10rISFbXSshIVtdKyEhW10rISFbXV0rKCEhW10rW10pWytbXV0rKFtdK3t9KVsrISFbXV0rKCEhW10rW10pWyshIVtdXV0oKCEhW10rW10pWyshIVtdXSsoW11bW11dK1tdKVshK1tdKyEhW10rISFbXV0rKCEhW10rW10pWytbXV0rKFtdW1tdXStbXSlbK1tdXSsoISFbXStbXSlbKyEhW11dKyhbXVtbXV0rW10pWyshIVtdXSsoW10re30pWyErW10rISFbXSshIVtdKyEhW10rISFbXSshIVtdKyEhW11dKyghW10rW10pWyErW10rISFbXV0rKFtdK3t9KVsrISFbXV0rKFtdK3t9KVshK1tdKyEhW10rISFbXSshIVtdKyEhW11dKygre30rW10pWyshIVtdXSsoISFbXStbXSlbK1tdXSsoW11bW11dK1tdKVshK1tdKyEhW10rISFbXSshIVtdKyEhW11dKyhbXSt7fSlbKyEhW11dKyhbXVtbXV0rW10pWyshIVtdXSkoKSlbIStbXSshIVtdKyEhW11dKyhbXVtbXV0rW10pWyErW10rISFbXSshIVtdXSkoKShbXVsoIVtdK1tdKVshK1tdKyEhW10rISFbXV0rKFtdK3t9KVsrISFbXV0rKCEhW10rW10pWyshIVtdXSsoISFbXStbXSlbK1tdXV1bKFtdK3t9KVshK1tdKyEhW10rISFbXSshIVtdKyEhW11dKyhbXSt7fSlbKyEhW11dKyhbXVtbXV0rW10pWyshIVtdXSsoIVtdK1tdKVshK1tdKyEhW10rISFbXV0rKCEhW10rW10pWytbXV0rKCEhW10rW10pWyshIVtdXSsoW11bW11dK1tdKVsrW11dKyhbXSt7fSlbIStbXSshIVtdKyEhW10rISFbXSshIVtdXSsoISFbXStbXSlbK1tdXSsoW10re30pWyshIVtdXSsoISFbXStbXSlbKyEhW11dXSgoISFbXStbXSlbKyEhW11dKyhbXVtbXV0rW10pWyErW10rISFbXSshIVtdXSsoISFbXStbXSlbK1tdXSsoW11bW11dK1tdKVsrW11dKyghIVtdK1tdKVsrISFbXV0rKFtdW1tdXStbXSlbKyEhW11dKyhbXSt7fSlbIStbXSshIVtdKyEhW10rISFbXSshIVtdKyEhW10rISFbXV0rKFtdW1tdXStbXSlbIStbXSshIVtdKyEhW11dKyghW10rW10pWyErW10rISFbXSshIVtdXSsoW10re30pWyErW10rISFbXSshIVtdKyEhW10rISFbXV0rKCt7fStbXSlbKyEhW11dKyhbXStbXVsoIVtdK1tdKVshK1tdKyEhW10rISFbXV0rKFtdK3t9KVsrISFbXV0rKCEhW10rW10pWyshIVtdXSsoISFbXStbXSlbK1tdXV1bKFtdK3t9KVshK1tdKyEhW10rISFbXSshIVtdKyEhW11dKyhbXSt7fSlbKyEhW11dKyhbXVtbXV0rW10pWyshIVtdXSsoIVtdK1tdKVshK1tdKyEhW10rISFbXV0rKCEhW10rW10pWytbXV0rKCEhW10rW10pWyshIVtdXSsoW11bW11dK1tdKVsrW11dKyhbXSt7fSlbIStbXSshIVtdKyEhW10rISFbXSshIVtdXSsoISFbXStbXSlbK1tdXSsoW10re30pWyshIVtdXSsoISFbXStbXSlbKyEhW11dXSgoISFbXStbXSlbKyEhW11dKyhbXVtbXV0rW10pWyErW10rISFbXSshIVtdXSsoISFbXStbXSlbK1tdXSsoW11bW11dK1tdKVsrW11dKyghIVtdK1tdKVsrISFbXV0rKFtdW1tdXStbXSlbKyEhW11dKyhbXSt7fSlbIStbXSshIVtdKyEhW10rISFbXSshIVtdKyEhW10rISFbXV0rKCFbXStbXSlbIStbXSshIVtdXSsoW10re30pWyshIVtdXSsoW10re30pWyErW10rISFbXSshIVtdKyEhW10rISFbXV0rKCt7fStbXSlbKyEhW11dKyghIVtdK1tdKVsrW11dKyhbXVtbXV0rW10pWyErW10rISFbXSshIVtdKyEhW10rISFbXV0rKFtdK3t9KVsrISFbXV0rKFtdW1tdXStbXSlbKyEhW11dKSgpKVshK1tdKyEhW10rISFbXV0rKFtdW1tdXStbXSlbIStbXSshIVtdKyEhW11dKSgpKChbXSt7fSlbK1tdXSlbK1tdXSsoIStbXSshIVtdKyEhW10rISFbXSshIVtdKyEhW10rISFbXStbXSkrKCshIVtdK1tdKSkrW11bKCFbXStbXSlbIStbXSshIVtdKyEhW11dKyhbXSt7fSlbKyEhW11dKyghIVtdK1tdKVsrISFbXV0rKCEhW10rW10pWytbXV1dWyhbXSt7fSlbIStbXSshIVtdKyEhW10rISFbXSshIVtdXSsoW10re30pWyshIVtdXSsoW11bW11dK1tdKVsrISFbXV0rKCFbXStbXSlbIStbXSshIVtdKyEhW11dKyghIVtdK1tdKVsrW11dKyghIVtdK1tdKVsrISFbXV0rKFtdW1tdXStbXSlbK1tdXSsoW10re30pWyErW10rISFbXSshIVtdKyEhW10rISFbXV0rKCEhW10rW10pWytbXV0rKFtdK3t9KVsrISFbXV0rKCEhW10rW10pWyshIVtdXV0oKCEhW10rW10pWyshIVtdXSsoW11bW11dK1tdKVshK1tdKyEhW10rISFbXV0rKCEhW10rW10pWytbXV0rKFtdW1tdXStbXSlbK1tdXSsoISFbXStbXSlbKyEhW11dKyhbXVtbXV0rW10pWyshIVtdXSsoW10re30pWyErW10rISFbXSshIVtdKyEhW10rISFbXSshIVtdKyEhW11dKyhbXVtbXV0rW10pWytbXV0rKFtdW1tdXStbXSlbKyEhW11dKyhbXVtbXV0rW10pWyErW10rISFbXSshIVtdXSsoIVtdK1tdKVshK1tdKyEhW10rISFbXV0rKFtdK3t9KVshK1tdKyEhW10rISFbXSshIVtdKyEhW11dKygre30rW10pWyshIVtdXSsoW10rW11bKCFbXStbXSlbIStbXSshIVtdKyEhW11dKyhbXSt7fSlbKyEhW11dKyghIVtdK1tdKVsrISFbXV0rKCEhW10rW10pWytbXV1dWyhbXSt7fSlbIStbXSshIVtdKyEhW10rISFbXSshIVtdXSsoW10re30pWyshIVtdXSsoW11bW11dK1tdKVsrISFbXV0rKCFbXStbXSlbIStbXSshIVtdKyEhW11dKyghIVtdK1tdKVsrW11dKyghIVtdK1tdKVsrISFbXV0rKFtdW1tdXStbXSlbK1tdXSsoW10re30pWyErW10rISFbXSshIVtdKyEhW10rISFbXV0rKCEhW10rW10pWytbXV0rKFtdK3t9KVsrISFbXV0rKCEhW10rW10pWyshIVtdXV0oKCEhW10rW10pWyshIVtdXSsoW11bW11dK1tdKVshK1tdKyEhW10rISFbXV0rKCEhW10rW10pWytbXV0rKFtdW1tdXStbXSlbK1tdXSsoISFbXStbXSlbKyEhW11dKyhbXVtbXV0rW10pWyshIVtdXSsoW10re30pWyErW10rISFbXSshIVtdKyEhW10rISFbXSshIVtdKyEhW11dKyghW10rW10pWyErW10rISFbXV0rKFtdK3t9KVsrISFbXV0rKFtdK3t9KVshK1tdKyEhW10rISFbXSshIVtdKyEhW11dKygre30rW10pWyshIVtdXSsoISFbXStbXSlbK1tdXSsoW11bW11dK1tdKVshK1tdKyEhW10rISFbXSshIVtdKyEhW11dKyhbXSt7fSlbKyEhW11dKyhbXVtbXV0rW10pWyshIVtdXSkoKSlbIStbXSshIVtdKyEhW11dKyhbXVtbXV0rW10pWyErW10rISFbXSshIVtdXSkoKShbXVsoIVtdK1tdKVshK1tdKyEhW10rISFbXV0rKFtdK3t9KVsrISFbXV0rKCEhW10rW10pWyshIVtdXSsoISFbXStbXSlbK1tdXV1bKFtdK3t9KVshK1tdKyEhW10rISFbXSshIVtdKyEhW11dKyhbXSt7fSlbKyEhW11dKyhbXVtbXV0rW10pWyshIVtdXSsoIVtdK1tdKVshK1tdKyEhW10rISFbXV0rKCEhW10rW10pWytbXV0rKCEhW10rW10pWyshIVtdXSsoW11bW11dK1tdKVsrW11dKyhbXSt7fSlbIStbXSshIVtdKyEhW10rISFbXSshIVtdXSsoISFbXStbXSlbK1tdXSsoW10re30pWyshIVtdXSsoISFbXStbXSlbKyEhW11dXSgoISFbXStbXSlbKyEhW11dKyhbXVtbXV0rW10pWyErW10rISFbXSshIVtdXSsoISFbXStbXSlbK1tdXSsoW11bW11dK1tdKVsrW11dKyghIVtdK1tdKVsrISFbXV0rKFtdW1tdXStbXSlbKyEhW11dKyhbXSt7fSlbIStbXSshIVtdKyEhW10rISFbXSshIVtdKyEhW10rISFbXV0rKFtdW1tdXStbXSlbIStbXSshIVtdKyEhW11dKyghW10rW10pWyErW10rISFbXSshIVtdXSsoW10re30pWyErW10rISFbXSshIVtdKyEhW10rISFbXV0rKCt7fStbXSlbKyEhW11dKyhbXStbXVsoIVtdK1tdKVshK1tdKyEhW10rISFbXV0rKFtdK3t9KVsrISFbXV0rKCEhW10rW10pWyshIVtdXSsoISFbXStbXSlbK1tdXV1bKFtdK3t9KVshK1tdKyEhW10rISFbXSshIVtdKyEhW11dKyhbXSt7fSlbKyEhW11dKyhbXVtbXV0rW10pWyshIVtdXSsoIVtdK1tdKVshK1tdKyEhW10rISFbXV0rKCEhW10rW10pWytbXV0rKCEhW10rW10pWyshIVtdXSsoW11bW11dK1tdKVsrW11dKyhbXSt7fSlbIStbXSshIVtdKyEhW10rISFbXSshIVtdXSsoISFbXStbXSlbK1tdXSsoW10re30pWyshIVtdXSsoISFbXStbXSlbKyEhW11dXSgoISFbXStbXSlbKyEhW11dKyhbXVtbXV0rW10pWyErW10rISFbXSshIVtdXSsoISFbXStbXSlbK1tdXSsoW11bW11dK1tdKVsrW11dKyghIVtdK1tdKVsrISFbXV0rKFtdW1tdXStbXSlbKyEhW11dKyhbXSt7fSlbIStbXSshIVtdKyEhW10rISFbXSshIVtdKyEhW10rISFbXV0rKCFbXStbXSlbIStbXSshIVtdXSsoW10re30pWyshIVtdXSsoW10re30pWyErW10rISFbXSshIVtdKyEhW10rISFbXV0rKCt7fStbXSlbKyEhW11dKyghIVtdK1tdKVsrW11dKyhbXVtbXV0rW10pWyErW10rISFbXSshIVtdKyEhW10rISFbXV0rKFtdK3t9KVsrISFbXV0rKFtdW1tdXStbXSlbKyEhW11dKSgpKVshK1tdKyEhW10rISFbXV0rKFtdW1tdXStbXSlbIStbXSshIVtdKyEhW11dKSgpKChbXSt7fSlbK1tdXSlbK1tdXSsoIStbXSshIVtdKyEhW10rISFbXSshIVtdKyEhW10rW10pKyhbXSt7fSlbIStbXSshIVtdXSkrKFtdW1tdXStbXSlbIStbXSshIVtdKyEhW11dKygrKCshIVtdKyhbXVtbXV0rW10pWyErW10rISFbXSshIVtdXSsoKyEhW10rW10pKygrW10rW10pKygrW10rW10pKygrW10rW10pKStbXSlbIStbXSshIVtdKyEhW10rISFbXSshIVtdKyEhW10rISFbXV0='),'"reqkey"')
	token = token.decode('utf-8')
	use_rep = True
	txt = token
	replaced = {}
	if use_rep:
		str = txt
		safe = '[]{}><!,()=+-;/\" $_'
		notsafe = '_'
		for i in range(0,len(str)):
			c = str[i]
			if re.search('[0-9a-zA-Z]', c) or c in safe:
				pass
			else:
				new_c = makeid(3,replaced.keys())
				replaced[new_c] = c
				txt = txt.replace(c, new_c)
	code = txt
	code = code.replace('(function(', '(function xy(').replace('}(','}; xy(')
	codes = re.findall(r"if.+$", code)[0].replace('),','), jssuckit = "; " + document.cookie,')
	code = re.sub(r"if.+$", codes, code)
	fn = re.findall(r"\(function.+?\)", code)[0]
	fncode1 = re.findall(r"{.*return", code)[0]
	fncode2 = re.findall(r"return.*}", code)[0]
	fnvars = re.findall(r"; xy\(.*", code)[0]
	occurances = [m.start() for m in re.finditer('_', fn)]
	if len(occurances) >= 2:
		new_c = makeid(2,replaced.keys())
		replaced[new_c] = '_'
		fn = fn.replace('_',new_c,1)
		code = fn + fncode1 + fncode2 + fnvars
		new_c2 = makeid(3,replaced.keys())
		replaced[new_c2] = '_'
		code = code.replace('_', new_c2)
		code = code.replace('){var','){var %s=%s; var' % (new_c,new_c2))
		code = code.replace('returnreturn','return')
		code = code[1:-1]
		code = 'var R1,R2; var jssuckit="";var window = global; var document = this; location = "%s/"; %s; jssuckit = document.cookie; return jssuckit' % (BASE_URL, code)
	elif len(occurances) == 1:
		if '_=' in fncode1:
			new_c = makeid(2,replaced.keys())
			replaced[new_c] = '_'
			fn = fn.replace('_',new_c)
			new_c2 = makeid(2,replaced.keys())
			replaced[new_c2] = '_'
			fncode1 = fncode1.replace('_',new_c2)
			fncode2 = fncode2.replace('_',new_c2)
			code = fn + fncode1 + fncode2 + fnvars
			code = code.replace('){var','){var %s=%s; var' % (new_c,new_c2))
			code = code[1:-1]
			d = 'var R1,R2; var jssuckit="";var window = global; var document = this; location = "%s/"; %s; jssuckit = document.cookie; jssuckit=jssuckit.replace(R1,R2); return jssuckit' % (BASE_URL, code)
			code = d.replace('}; xy(',';R1=%s; R2=%s}; xy(')
			code = code % (new_c2,new_c)
		else:
			new_c = makeid(3,replaced.keys())
			replaced[new_c] = '_'
			code = code.replace('_', new_c)
			code = code[1:-1]
			d = 'var jssuckit="";var window = global; var document = this; location = "%s/"; %s; jssuckit = document.cookie; return jssuckit'
			code = (d % (BASE_URL,code))
	else:
		code = code[1:-1]
		d = 'var jssuckit="";var window = global; var document = this; location = "%s/"; %s; jssuckit = document.cookie; return jssuckit'
		code = (d % (BASE_URL,code))
	code = code.replace('returnreturn','return')
	code = code.encode('utf-8')
	return code, replaced
		
####################################################################################################
@route(PREFIX + "/stripDay")
def stripDay(text):
	days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
	for day in days:
		text = text.replace(day,'')
		
	return text.strip()
	
@route(PREFIX + "/convertMonthToInt")
def convertMonthToInt(text):
	months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
	m = 1
	for month in months:
		if month in text:
			m_str = '%02d' % m
			text = text.replace(month, str(m_str)+',')
			break
		m += 1
		
	return text.strip()
		
####################################################################################################
@route(PREFIX + "/removeAccents")
def removeAccents(text):
	"""
	Convert input text to id.

	:param text: The input string.
	:type text: String.

	:returns: The processed String.
	:rtype: String.
	"""
	try:
		text = strip_accents(text.lower())
		text = re.sub('[ ]+', '_', text)
		text = re.sub('[^0-9a-zA-Z]', ' ', text)
		text = text.title()
		return text
	except:
		return text

def strip_accents(text):
	"""
	Strip accents from input String.

	:param text: The input string.
	:type text: String.

	:returns: The processed String.
	:rtype: String.
	"""
	try:
		text = unicode(text, 'utf-8')
	except NameError: # unicode is a default on python 3 
		pass
	text = unicodedata.normalize('NFD', text)
	text = text.encode('ascii', 'ignore')
	text = text.decode("utf-8")
	return str(text)

def ascii_only(my_s):
	printable = set(string.printable)
	return filter(lambda x: x in printable, my_s)

####################################################################################################
@route(PREFIX + "/MakeStringLength")
def MakeStringLength(text, n=15):

	ns = n - len(text)
	text += ' ' * ns
	return text
	
####################################################################################################
# search array item's presence in string
@route(PREFIX + "/arrayitemsinstring")
def ArrayItemsInString(arr, mystr):

	for item in arr:
		if item in mystr:
			return True
			
	return False
	
####################################################################################################
class PageError(Exception):
	pass
	
####################################################################################################

# checks if USS is installed or not
def is_uss_installed():
	"""Check install state of UnSupported Services"""
	
	try:
		identifiers = list()
		plugins_list = XML.ElementFromURL('http://127.0.0.1:32400/:/plugins', cacheTime=0)

		for plugin_el in plugins_list.xpath('//Plugin'):
			identifiers.append(plugin_el.get('identifier'))

		if 'com.plexapp.system.unsupportedservices' in identifiers:
			return True
		return False
	except Exception as e:
		Log.Error("common.is_uss_installed > Error: %s" % e)
	return False
	
####################################################################################################

# author: Twoure
# source: https://github.com/Twoure/HindiMoviesOnline.bundle/blob/master/Contents/Code/messages.py
#
class NewMessageContainer(object):
	def __init__(self, prefix, title):
		self.title = title
		Route.Connect(prefix + '/message', self.message_container)

	def message_container(self, header, message):
		"""Setup MessageContainer depending on Platform"""

		if Client.Platform in ['Plex Home Theater', 'OpenPHT']:
			oc = ObjectContainer(
				title1=self.title, title2=header, no_cache=True,
				no_history=True, replace_parent=True
				)
			oc.add(PopupDirectoryObject(title=header, summary=message))
			return oc
		else:
			return MessageContainer(header, message)