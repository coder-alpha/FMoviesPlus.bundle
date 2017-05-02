#
# Coder Alpha
# https://github.com/coder-alpha
#
# Adapted from lambda's Kodi plugin
# https://github.com/lambda81
# and modified for use with Plex Media Server
#
#########################################################################################################
	
import urllib, urlparse, json, time, re, datetime, calendar
import common
from __builtin__ import ord, format

BASE_URL = "https://fmovies.to"
HASH_PATH_MENU = "/user/ajax/menu-bar"
HASH_PATH_INFO = "/ajax/episode/info"
TOKEN_PATH = "/token"
SEARCH_PATH = "/search"
FILTER_PATH = "/filter"
KEYWORD_PATH = "/tag/"
STAR_PATH = "/star/"

oldmarketgidstorage = 'MarketGidStorage=%7B%220%22%3A%7B%22svspr%22%3A%22%22%2C%22svsds%22%3A3%2C%22TejndEEDj%22%3A%22MTQ4MTM2ODE0NzM0NzQ4NTMyOTAx%22%7D%2C%22C48532%22%3A%7B%22page%22%3A1%2C%22time%22%3A1481368147359%7D%2C%22C77945%22%3A%7B%22page%22%3A1%2C%22time%22%3A1481368147998%7D%2C%22C77947%22%3A%7B%22page%22%3A1%2C%22time%22%3A1481368148109%7D%7D'
newmarketgidstorage = 'MarketGidStorage=%7B%220%22%3A%7B%22svspr%22%3A%22%22%2C%22svsds%22%3A15%2C%22TejndEEDj%22%3A%22MTQ5MzIxMTc0OTQ0NDExMDAxNDc3NDE%3D%22%7D%2C%22C110014%22%3A%7B%22page%22%3A3%2C%22time%22%3A1493215038742%7D%2C%22C110025%22%3A%7B%22page%22%3A3%2C%22time%22%3A1493216772437%7D%2C%22C110023%22%3A%7B%22page%22%3A3%2C%22time%22%3A1493216771928%7D%7D; reqkey='

USE_COOKIES = True
USE_SECOND_REQUEST = False

####################################################################################################

# Get FMovies-API
#@route(PREFIX + '/getapiurl')
def GetApiUrl(url, key, serverts=0, use_debug=True, use_https_alt=False, use_web_proxy=False, cache_expiry_time=60, reqCookie='', **kwargs):

	try:
		use_debug = Prefs["use_debug"]
		use_https_alt = Prefs["use_https_alt"]
		use_web_proxy = Prefs["use_web_proxy"]
		cache_expiry_time = int(Prefs["cache_expiry_time"])
		reqCookie = Prefs["req_cookie"]
	except:
		pass
	
	res = None
	error = ''
	myts = time.time()
	
	try:
		CACHE_EXPIRY = 60 * cache_expiry_time
	except:
		CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
		
	if reqCookie == None:
		reqCookie = ''
	
	if key in common.CACHE and 'myts' in common.CACHE[key] and (myts - int(common.CACHE[key]['myts']) < common.CACHE_EXPIRY):
		if use_debug:
			Log("Using Movie Link from Cache")
		res = common.CACHE[key]['res']
		isOpenLoad = common.CACHE[key]['isOpenLoad']
		if isOpenLoad == 'True':
			isOpenLoad = True
			#surl = common.host_openload.resolve(url=res, embedpage=True)
			surl = res
			if use_debug:
				Log("Openload Stream URL %s from %s" % (surl,res))
			res = surl
		else:
			if res == 'Unavailable':
				res = None
			isOpenLoad = False
	else:
		if use_debug:
			Log("Retrieving Fresh Movie Link")
			
		ret, isOpenLoad, error = get_sources(url=url, key=key, use_debug=use_debug, serverts=serverts, myts=myts, use_https_alt=use_https_alt, use_web_proxy=use_web_proxy, reqCookie=reqCookie)
		if use_debug:
			Log("get_sources url: %s, key: %s" % (url,key))
			Log("get_sources ret: %s" % ret)
		
		if USE_SECOND_REQUEST and ret == None: # if the request ever fails - clear CACHE right away and make 2nd attempt
			common.CACHE.clear()
			if use_debug:
				Log("CACHE cleared due to null response from API - maybe cookie issue for %s" % url)
			time.sleep(1.0)
			ret, isOpenLoad, error = get_sources(url=url, key=key, use_debug=use_debug, serverts=serverts, myts=myts, use_https_alt=use_https_alt, use_web_proxy=use_web_proxy, reqCookie=reqCookie)
			if use_debug:
				Log("API - attempt 2nd")
				Log("get_sources url: %s, key: %s" % (url,key))
				Log("get_sources ret: %s" % ret)

		if ret == None:
			if use_debug:
				Log("null response from API (possible file deleted) - for %s" % url)
			return res, isOpenLoad, error
		else:
			if isOpenLoad:
				res = ret
				common.CACHE[key] = {}
				common.CACHE[key]['res'] = res
				common.CACHE[key]['serverts'] = serverts
				common.CACHE[key]['myts'] = myts
				common.CACHE[key]['isOpenLoad'] = str(isOpenLoad)
				if use_debug:
					Log("Added " + key + " to CACHE")
				#surl = common.host_openload.resolve(url=res, embedpage=True)
				surl = ret
				if use_debug:
					Log("Openload Stream URL %s from %s" % (surl,ret))
				res = surl
			else:
				# fix api url to https
				ret = ret.replace('http://','https://')
				data = None
				headersS = {'X-Requested-With': 'XMLHttpRequest'}
				headersS['Referer'] = '%s/%s' % (url, key)
				headersS['Cookie'] = common.CACHE_COOKIE[0]['cookie']
				try:
					time.sleep(1.0)
					data = common.interface.request_via_proxy_as_backup(ret, limit='0', headers=headersS, httpsskip=use_https_alt)
					data = json.loads(data)
				except Exception as e:
					Log('ERROR fmovies.py>GetApiUrl-1: ARGS:%s, URL:%s' % (e,ret))
					pass

				if data == None:
					return None, isOpenLoad, error
				if data['error'] == None:
					res = JSON.StringFromObject(data['data'])
					common.CACHE[key] = {}
					common.CACHE[key]['res'] = res
					common.CACHE[key]['serverts'] = serverts
					common.CACHE[key]['myts'] = myts
					common.CACHE[key]['isOpenLoad'] = str(isOpenLoad)
					if use_debug:
						Log("Added " + key + " to CACHE")
						Log("Added " + res + " to " + key)
				elif data['error'] != None:
					error = data['error']
				else:
					error = 'Unknown error'

	return res, isOpenLoad, error
	
def setTokenCookie(serverts=None, use_debug=False, reset=False):
	
	if reset:
		cookie_dict_Str = None
		Dict['CACHE_COOKIE'] = None
	else:
		cookie_dict_Str = Dict['CACHE_COOKIE']
	
	cookie_dict = {'ts':0, 'cookie': '', 'UA': ''}
	
	if cookie_dict_Str != None:
		try:
			cookie_dict = JSON.ObjectFromString(D(cookie_dict_Str))
		except:
			pass
	
	if time.time() - cookie_dict['ts'] < 3 * 24 * 60 * 60:
		cookie = cookie_dict['cookie']
		if use_debug:
			Log("Retrieved Saved Cookie: %s" % cookie)
	else:
		if serverts == None:
			serverts = str(((int(time.time())/3600)*3600))
		
		UA = common.client.randomagent()
		
		headersS = {'X-Requested-With': 'XMLHttpRequest'}
		headersS['Referer'] = BASE_URL
		headersS['User-Agent'] = UA
		
		result, headers, content, cookie1 = common.interface.request_via_proxy_as_backup(BASE_URL, headers=headersS, limit='0', output='extended')
		headersS['Cookie'] = cookie1
		time.sleep(0.1)
		
		token_url = urlparse.urljoin(BASE_URL, TOKEN_PATH)
		r1 = common.interface.request_via_proxy_as_backup(token_url, headers=headersS)
		time.sleep(0.1)
		del common.TOKEN_CODE[:]
		common.TOKEN_CODE.append(common.client.b64encode(r1))
		Log("=====================TOKEN START============================")
		Log(common.TOKEN_CODE[0])
		Log("=====================TOKEN END============================")

		query = {'ts': serverts}
		tk = get_token(query)
		query.update(tk)
		hash_url = urlparse.urljoin(BASE_URL, HASH_PATH_MENU)
		hash_url = hash_url + '?' + urllib.urlencode(query)

		r1, headers, content, cookie2 = common.interface.request_via_proxy_as_backup(hash_url, headers=headersS, limit='0', output='extended')
		time.sleep(0.5)
		
		common.CACHE['cookie'] = {}
		common.CACHE['cookie']['cookie1'] = cookie1
		common.CACHE['cookie']['cookie2'] = cookie2
		common.CACHE['cookie']['myts'] = time.time()
		common.CACHE['cookie']['UA'] = UA
		
		cookie = cookie1 + '; ' + cookie2 + '; user-info=null; ' + newmarketgidstorage
		cookie_dict = {'ts':time.time(), 'cookie': cookie, 'UA': UA}
		if use_debug:
			Log("Storing Cookie: %s" % cookie)
		Dict['CACHE_COOKIE'] = E(JSON.StringFromObject(cookie_dict))
		Dict.Save()

	del common.CACHE_COOKIE[:]
	common.CACHE_COOKIE.append(cookie_dict)
	
	return cookie


def get_sources(url, key, use_debug=True, serverts=0, myts=0, use_https_alt=False, use_web_proxy=False, reqCookie='', **kwargs):

	if serverts == 0:
		#serverts = ((int(time.time())/3600)*3600)
		# 1485273600
		# 1485324000
		# 1485327600
		# 1485324000
		# 1485352800
		utc = datetime.datetime.utcnow()
		if utc.hour < 6:
			past = utc - datetime.timedelta(hours=13) 	# 1485273600
		elif utc.hour >= 6 and utc.hour < 16:
			past = utc									# 1485324000, 1485327600, 1485352800
		else:
			past = utc - datetime.timedelta(hours=12)	# 1485324000, 1485334800
		
		past_fixed = datetime.datetime(past.year, past.month, past.day, past.hour, 0, 0, 0)
		serverts = calendar.timegm(past_fixed.timetuple())
	
	try:
		error = None
		magic_url = None
		isOpenLoad = False
		if url == None: return magic_url
		referer = url
		serverts = str(serverts)
		T_BASE_URL = BASE_URL
		#T_BASE_URL = "https://fmovies.unlockpro.top"
		
		time.sleep(0.5)
		
		if USE_COOKIES:
			if len(common.CACHE_COOKIE) > 0:
				pass
			else:
				setTokenCookie(serverts=serverts, use_debug=use_debug)

			cookie = common.CACHE_COOKIE[0]['cookie'] + reqCookie
		else:
			cookie = ''

		try:
			headers = {'X-Requested-With': 'XMLHttpRequest'}
			headers['User-Agent'] = common.CACHE_COOKIE[0]['UA']
			
			hash_url = urlparse.urljoin(T_BASE_URL, HASH_PATH_INFO)
			query = {'ts': serverts, 'id': key, 'update':'0'}
			tk = get_token(query)
			query.update(tk)
			hash_url = hash_url + '?' + urllib.urlencode(query)

			headers['Referer'] = '%s/%s' % (url, key)
			
			# key0 = url.split('/')
			# key0 = key0[len(key0)-1]
			# key0 = key0.split('.')
			# key0 = key0[len(key0)-1]
			# watching_query = '{"%s":"%s"}' % (key0,key)
			# watching_query = watching_query.replace('"','%22').replace(':','%3A').replace('{','%7B').replace('}','%7D')
			
			headers['Cookie'] = cookie

			if use_debug:
				Log("Using cookies : %s" % headers['Cookie'])
			
			#print hash_url
			if use_debug:
				Log("get_sources Request-3: %s" % hash_url)
			result = common.interface.request_via_proxy_as_backup(hash_url, headers=headers, httpsskip=use_https_alt)
			Log("Request-3 result: %s" % result)
			#print result
			result = json.loads(result)

			if 'error' in result:
				grabber = None
				error = result['error']
			elif result['target'] != "":
				grabber = result['target']
				isOpenLoad = True
			else:
				query = {'id':result['params']['id'], 'token':result['params']['token']}
				grabber = result['grabber'] + '?' + urllib.urlencode(query)
				
			if grabber!=None and not grabber.startswith('http'):
				grabber = 'http:'+grabber
				
			magic_url = grabber
		except Exception as e:
			Log('ERROR fmovies.py>get_sources-1 %s, %s' % (e.args,url))
			pass

		return magic_url, isOpenLoad, error
	except Exception as e:
		error = e
		Log('ERROR fmovies.py>get_sources-2 %s, %s' % (e.args,url))
		return magic_url, isOpenLoad, error
		
def r01(t, e):
	i = 0
	n = 0
	for i in range(0, max(len(t), len(e))):
		if i < len(e):
			n += ord(e[i])
		if i < len(t):
			n += ord(t[i])
	h = format(int(hex(n),16),'x')
	return h

def a01(t):
	i = 0
	for e in range(0, len(t)): 
		i += ord(t[e])
	return i


def get_token(n, **kwargs):
	try:
		d = "b826ae04"
		s = a01(d)
		for i in n: 
			s += a01(r01(d + i, n[i]))
		return {'_': str(s)}
	except Exception as e:
		Log("fmovies.py > get_token > %s" % e)

#########################################################################################################
