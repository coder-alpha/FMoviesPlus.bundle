#
# Coder Alpha
# https://github.com/coder-alpha
#
# Adapted from lambda's Kodi plugin
# https://github.com/lambda81
# and modified for use with Plex Media Server
#
#########################################################################################################
	
import urllib, urlparse, json, time, re, datetime, calendar, base64
import common
from __builtin__ import ord

BASE_URL = "https://fmovies.to"
HASH_PATH_MENU = "/user/ajax/menu-bar"
HASH_PATH_INFO = "/ajax/episode/info"
SEARCH_PATH = "/search"
FILTER_PATH = "/filter"
KEYWORD_PATH = "/tag/"
STAR_PATH = "/star/"

USE_COOKIES = False

####################################################################################################

# Get FMovies-API
#@route(PREFIX + '/getapiurl')
def GetApiUrl(url, key, serverts=0, use_debug=True, use_https_alt=False, use_web_proxy=False, cache_expiry_time=60, **kwargs):

	try:
		use_debug = Prefs["use_debug"]
		use_https_alt = Prefs["use_https_alt"]
		use_web_proxy = Prefs["use_web_proxy"]
		cache_expiry_time = int(Prefs["cache_expiry_time"])
	except:
		pass
	
	res = None
	myts = time.time()
	
	try:
		CACHE_EXPIRY = 60 * cache_expiry_time
	except:
		CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
	
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
			
		ret, isOpenLoad = get_sources(url=url, key=key, use_debug=use_debug, serverts=serverts, myts=myts, use_https_alt=use_https_alt, use_web_proxy=use_web_proxy)
		if use_debug:
			Log("get_sources url: %s, key: %s" % (url,key))
			Log("get_sources ret: %s" % ret)
		
		if ret == None: # if the request ever fails - clear CACHE right away and make 2nd attempt
			common.CACHE.clear()
			if use_debug:
				Log("CACHE cleared due to null response from API - maybe cookie issue for %s" % url)
			ret, isOpenLoad = get_sources(url=url, key=key, use_debug=use_debug, serverts=serverts, myts=myts, use_https_alt=use_https_alt, use_web_proxy=use_web_proxy)
			if use_debug:
				Log("API - attempt 2nd")
				Log("get_sources url: %s, key: %s" % (url,key))
				Log("get_sources ret: %s" % ret)
			
		if ret == None:
			if use_debug:
				Log("null response from API (possible file deleted) - for %s" % url)
			return res, isOpenLoad
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
				if use_web_proxy:
					json_data_string = common.request(url=ret, limit='0')
					try:
						data = JSON.ObjectFromString(json_data_string)
					except Exception as e:
						Log('ERROR fmovies.py>GetApiUrl-1: ARGS:%s, URL: %s, DATA: %s' % (e.args,ret,json_data_string))
						pass
				else:
					try:
						data = common.request(ret)
						data = json.loads(data)
					except Exception as e:
						Log('ERROR fmovies.py>GetApiUrl-2: ARGS:%s, URL:%s' % (e.args,ret))
						pass

				if data == None:
					return None, isOpenLoad
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
				else:
					if use_debug:
						Log("%s : %s : File has been deleted !" % (url,key))

	return res, isOpenLoad

def get_sources(url, key, use_debug=True, serverts=0, myts=0, use_https_alt=False, use_web_proxy=False, **kwargs):

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
		magic_url = None
		isOpenLoad = False
		if url == None: return magic_url
		referer = url
		serverts = str(serverts)
		
		if USE_COOKIES:
			if 'cookie' in common.CACHE and 'myts' in common.CACHE['cookie'] and (myts - int(common.CACHE['cookie']['myts'])) < common.CACHE_EXPIRY:
				# use cache to minimize requests
				if use_debug:
					try:
						Log('Using Cookies from Cache')
					except:
						print 'Using Cookies from Cache'
				cookie1 = common.CACHE['cookie']['cookie1']
				cookie2 = common.CACHE['cookie']['cookie2']
			else:
				if use_debug:
					try:
						Log('NOT Using Cookies from Cache')
					except:
						print 'NOT Using Cookies from Cache'
				common.CACHE['cookie'] = {}
				time.sleep(0.2)
				if use_debug:
					Log("get_sources Request-1: %s" % url)
				result, headers, content, cookie1 = common.interface.request(url, limit='0', output='extended', httpsskip=use_https_alt, use_web_proxy=use_web_proxy)
				#print result
				hash_url = urlparse.urljoin(BASE_URL, HASH_PATH_MENU)
				query = {'ts': serverts, 'update':'0'}
				tk = get_token(query)
				query.update(tk)
				hash_url = hash_url + '?' + urllib.urlencode(query)
				time.sleep(0.2)
				if use_debug:
					Log("get_sources Request-2: %s" % hash_url)
				r1, headers, content, cookie2 = common.interface.request(hash_url, limit='0', output='extended', cookie=cookie1, httpsskip=use_https_alt, use_web_proxy=use_web_proxy)
				#print r1
				common.CACHE['cookie']['cookie1'] = cookie1
				common.CACHE['cookie']['cookie2'] = cookie2
				common.CACHE['cookie']['myts'] = myts

		try:
			headers = {'X-Requested-With': 'XMLHttpRequest'}
			hash_url = urlparse.urljoin(BASE_URL, HASH_PATH_INFO)
			query = {'ts': serverts, 'id': key, 'update':'0'}
			tk = get_token(query)
			query.update(tk)
			hash_url = hash_url + '?' + urllib.urlencode(query)

			headers['Referer'] = urlparse.urljoin(url, key)
			oldmarketgidstorage = 'MarketGidStorage=%7B%220%22%3A%7B%22svspr%22%3A%22%22%2C%22svsds%22%3A3%2C%22TejndEEDj%22%3A%22MTQ4MTM2ODE0NzM0NzQ4NTMyOTAx%22%7D%2C%22C48532%22%3A%7B%22page%22%3A1%2C%22time%22%3A1481368147359%7D%2C%22C77945%22%3A%7B%22page%22%3A1%2C%22time%22%3A1481368147998%7D%2C%22C77947%22%3A%7B%22page%22%3A1%2C%22time%22%3A1481368148109%7D%7D'
			newmarketgidstorage = 'MarketGidStorage=%7B%220%22%3A%7B%22svspr%22%3A%22%22%2C%22svsds%22%3A75%2C%22TejndEEDj%22%3A%22MTQ4NDc3MzczNzkzOTc3OTQ0NjgwMQ%3D%3D%22%7D%2C%22C77944%22%3A%7B%22page%22%3A1%2C%22time%22%3A1485149595898%7D%2C%22C77946%22%3A%7B%22page%22%3A1%2C%22time%22%3A1485149600480%7D%2C%22C77948%22%3A%7B%22page%22%3A1%2C%22time%22%3A1485149600326%7D%7D'
			
			if USE_COOKIES:
				headers['Cookie'] = cookie1 + ';' + cookie2 + ';user-info=null; ' + newmarketgidstorage
			else:
				headers['Cookie'] = 'user-info=null; ' + newmarketgidstorage
			
			time.sleep(0.4)
			#print hash_url
			if use_debug:
				Log("get_sources Request-3: %s" % hash_url)
			result = common.interface.request(hash_url, headers=headers, limit='0', use_web_proxy=use_web_proxy)
			#print result
			
			result = json.loads(result)

			if 'error' in result:
				grabber = None
			elif result['target'] != "":
				grabber = result['target']
				isOpenLoad = True
			else:
				query = {'id': key}
				tk = get_token(query)
				query.update(tk)
				url = url + '?' + urllib.urlencode(query)
				query = {'id':result['params']['id']}
				tk = get_token(query)
				query.update(tk)
				query = {'id':result['params']['id'], 'token':result['params']['token']}
				grabber = result['grabber'] + '?' + urllib.urlencode(query)
				
			if grabber!=None and not grabber.startswith('http'):
				grabber = 'http:'+grabber
				
			magic_url = grabber
		except Exception as e:
			Log('ERROR fmovies.py>get_sources-1 %s, %s' % (e.args,url))
			pass

		return magic_url, isOpenLoad
	except Exception as e:
		Log('ERROR fmovies.py>get_sources-2 %s, %s' % (e.args,url))
		return magic_url, isOpenLoad

def get_token_(data, **kwargs):

	try:
		index1 = 0
		sn = 256
		for index2 in data:
			i = list(range(0, sn))
			if not index2.startswith('_'):
				n = 0
				index4 = 0
				for s in range(0, sn):
					n = (n + i[s] +
						 ord(index2[s % len(index2)])) % sn
					r = i[s]
					i[s] = i[n]
					i[n] = r
				n = 0
				for index8 in range(0, len(data[index2])):
					s = index8 + 1  # line:15
					n = (n + i[s]) % (sn)
					r = i[s]
					i[s] = i[n]
					i[n] = r
					index4 += ord(data[index2][index8]) ^ (i[(i[s] +i[n]) % sn]) * index8 + index8
				index1 += index4
		return {'_': str(index1)}
	except Exception as e:
		Log("fmovies.py > get_token_ > %s" % e)
		
		
def r01(e, n):
	v = t01(e, n);
	return v

def t01(t, e):
		T = ""
		sn = 256
		o = list(range(0, sn))
		for r in range(0, sn):
			o[r] = r
		i = 0
		for r in range(0,sn):
			i = (i + o[r] + ord(t[(r % len(t))])) % sn
			n = o[r]
			o[r] = o[i]
			o[i] = n
		r = 0
		i = 0
		a = T
		for s in range(0, len(e)):
			r = (r + 1) % sn
			i = (i + o[r]) % sn 
			n = o[r]
			o[r] = o[i] 
			o[i] = n
			a += chr(ord(e[s]) ^ o[(o[r] + o[i]) % sn])
		return T + a

def a01(t):
	i = 0
	for e in range(0, len(t)): 
		i += ord(t[e])
	return i


def get_token(n, **kwargs):
	try:
		d = base64.b64decode(base64.b64decode("UWxFMFFYZENaMVJTZW5CQ1lsTkxURUk9"))
		s = a01(d)
		for i in n: 
			s += a01(r01(d + i, n[i]))
		return {'_': str(s)}
	except Exception as e:
		Log("fmovies.py > get_token > %s" % e)

#########################################################################################################
