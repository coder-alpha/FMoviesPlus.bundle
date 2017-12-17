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
from __builtin__ import ord, format, eval

BASE_URL = "https://bmovies.to"
HASH_PATH_MENU = "/user/ajax/menu-bar"
HASH_PATH_INFO = "/ajax/episode/info"
TOKEN_PATH = "/token"
SEARCH_PATH = "/search"
FILTER_PATH = "/filter"
KEYWORD_PATH = "/tag/"
STAR_PATH = "/star/"
SITE_MAP = "/sitemap"
GRABBER_API = "grabber-api/"
SITE_MAP_HTML_ELEMS = []
ALL_JS = "/assets/min/public/all.js"
TOKEN_KEY_PASTEBIN_URL = "https://pastebin.com/raw/VNn1454k"
TOKEN_OPER_PASTEBIN_URL = "https://pastebin.com/raw/9zFcNJuP"
DEV_NOTICE_URL = "https://pastebin.com/raw/1HDhMggt"
TOKEN_KEY = []
TOKEN_OPER = []
DEV_NOTICE = []

CACHE_IGNORELIST = ['apidata.googleusercontent.com']

newmarketgidstorage = 'MarketGidStorage=%7B%220%22%3A%7B%22svspr%22%3A%22%22%2C%22svsds%22%3A15%2C%22TejndEEDj%22%3A%22MTQ5MzIxMTc0OTQ0NDExMDAxNDc3NDE%3D%22%7D%2C%22C110014%22%3A%7B%22page%22%3A3%2C%22time%22%3A1493215038742%7D%2C%22C110025%22%3A%7B%22page%22%3A3%2C%22time%22%3A1493216772437%7D%2C%22C110023%22%3A%7B%22page%22%3A3%2C%22time%22%3A1493216771928%7D%7D'

####################################################################################################

# Get FMovies-API
#@route(PREFIX + '/getapiurl')
def GetApiUrl(url, key, serverts=0, use_debug=True, use_https_alt=False, use_web_proxy=False, cache_expiry_time=60, **kwargs):

	try:
		use_debug = Prefs["use_debug"]
		use_https_alt = Prefs["use_https_alt"]
		use_web_proxy = Prefs["use_web_proxy"]
		cache_expiry_time = int(Prefs["cache_expiry_time"])
		user_defined_reqkey_cookie = Prefs['reqkey_cookie']
	except:
		pass
		
	if key == None:
		return None, False, 'Item key is None. Item does not exist !', None, None
	
	res = None
	res_subtitle = None
	error = ''
	myts = time.time()
	
	try:
		CACHE_EXPIRY = 60 * cache_expiry_time
	except:
		CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
		
	if key in common.CACHE and 'myts' in common.CACHE[key] and (myts - int(common.CACHE[key]['myts']) < common.CACHE_EXPIRY):
		if use_debug:
			Log("Using Movie Link from Cache")
		res = common.CACHE[key]['res']
		res_subtitle = common.CACHE[key]['res_subtitle']
		isTargetPlay = common.CACHE[key]['isTargetPlay']
		host = common.CACHE[key]['host']
		if isTargetPlay == 'True':
			isTargetPlay = True
			#surl = common.host_openload.resolve(url=res, embedpage=True)
			surl = res
			if use_debug:
				Log("Target-Play Stream URL %s from %s" % (surl,res))
			res = surl
		else:
			if res == 'Unavailable':
				res = None
			isTargetPlay = False
	else:
		try:
			if use_debug:
				Log("Retrieving Fresh Movie Link")
				
			ret, isTargetPlay, error, host, res_subtitle = get_sources(url=url, key=key, use_debug=use_debug, serverts=serverts, myts=myts, use_https_alt=use_https_alt, use_web_proxy=use_web_proxy)
			if use_debug:
				Log("get_sources url: %s, key: %s" % (url,key))
				Log("get_sources ret: %s" % ret)
				Log("get_sources error: %s" % error)
			token_error = False
			if error != None and 'token' in error:
				token_error = True
			
			# if the request ever fails - clear CACHE right away and make 2nd attempt
			# if token error make 2nd attempt using modified code
			if common.USE_SECOND_REQUEST == True and (ret == None or token_error == True):
				common.CACHE.clear()
				if use_debug:
					Log("Using Second Request due to token error")
					Log("CACHE cleared due to null response from API - maybe cookie issue for %s" % url)
				time.sleep(1.0)
				ret, isTargetPlay, error, host, res_subtitle = get_sources(url=url, key=key, use_debug=use_debug, serverts=serverts, myts=myts, use_https_alt=use_https_alt, use_web_proxy=use_web_proxy, token_error=token_error)
				if use_debug:
					Log("API - attempt 2nd")
					Log("get_sources url: %s, key: %s" % (url,key))
					Log("get_sources ret: %s" % ret)

			if ret == None:
				if use_debug:
					Log("null response from API (possible file deleted) - for %s" % url)
				return res, isTargetPlay, error, host, res_subtitle
			else:
				if isTargetPlay:
					res = ret
					common.CACHE[key] = {}
					common.CACHE[key]['res'] = res
					common.CACHE[key]['res_subtitle'] = res_subtitle
					common.CACHE[key]['host'] = host
					common.CACHE[key]['serverts'] = serverts
					common.CACHE[key]['myts'] = myts
					common.CACHE[key]['isTargetPlay'] = str(isTargetPlay)
					if use_debug:
						Log("Added " + key + " to CACHE")
					#surl = common.host_openload.resolve(url=res, embedpage=True)
					surl = ret
					if use_debug:
						Log("Target-Play Stream URL %s from %s" % (surl,ret))
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
						data = common.interface.request_via_proxy_as_backup(ret, limit='0', headers=headersS, httpsskip=use_https_alt, hideurl=not use_debug)
						if 'Warning' in data or 'Notice' in data:
							Log('**Fixing requested page error responses**')
							data = re.findall(r'{.*}',data)[0]
							subdata = re.findall(r'<a.*\/a>', data)
							if len(subdata) > 0:
								data = data.replace(subdata[0],'')
						data = json.loads(data)
					except Exception as e:
						Log.Error('ERROR fmovies.py>GetApiUrl-1: ARGS:%s, URL:%s' % (e,ret))
						res = None
						raise Exception('Site returned unknown response')

					if data == None:
						return None, isTargetPlay, error, host, res_subtitle
					if data['error'] == None:
						res = JSON.StringFromObject(data['data'])
						
						add_bool = True
						try:
							for ign in CACHE_IGNORELIST:
								for res_file in data['data']:
									if ign in res_file['file']:
										add_bool = False
										break
						except Exception as e:
							Log.Error("ERROR: %s" % e)
						
						if add_bool == True:
							common.CACHE[key] = {}
							common.CACHE[key]['res'] = res
							common.CACHE[key]['res_subtitle'] = res_subtitle
							common.CACHE[key]['host'] = host
							common.CACHE[key]['serverts'] = serverts
							common.CACHE[key]['myts'] = myts
							common.CACHE[key]['isTargetPlay'] = str(isTargetPlay)
							if use_debug:
								Log("Added " + key + " to CACHE")
								Log("Added " + res + " to " + key)
						else:
							if use_debug:
								Log("*IgnoreList URL* Not Added " + key + " to CACHE")
								Log("*IgnoreList URL* Not Added " + res + " to " + key)
					elif data['error'] != None:
						error = data['error']
					else:
						error = 'Unknown error'
		except Exception as e:
			error = e

	return res, isTargetPlay, error, host, res_subtitle
		
def setTokenCookie(serverts=None, use_debug=False, reset=False, dump=False, quiet=False):

	if common.USE_COOKIES == False:
		if use_debug or dump:
			Log("Cookie Usage has been disabled from options !")

	try:
		CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
	except:
		CACHE_EXPIRY = common.CACHE_EXPIRY_TIME
	
	use_https_alt = Prefs['use_https_alt']
	use_https_alt = True
	
	if reset:
		cookie_dict_Str = None
		Dict['CACHE_COOKIE'] = None
	else:
		cookie_dict_Str = Dict['CACHE_COOKIE']
	
	cookie_dict = {'ts':0, 'cookie': '', 'UA': '', 'reqkey':''}
	
	if cookie_dict_Str != None:
		try:
			cookie_dict = JSON.ObjectFromString(D(cookie_dict_Str))
		except:
			pass
	
	if time.time() - cookie_dict['ts'] < CACHE_EXPIRY:
		try:
			cookie = cookie_dict['cookie']
			reqkey_cookie = cookie_dict['reqkey']
			token_key = cookie_dict['token_key']
			token_oper = cookie_dict['token_oper']
			del TOKEN_KEY[:]
			TOKEN_KEY.append(token_key)
			del TOKEN_OPER[:]
			TOKEN_OPER.append(token_oper)
		except:
			setTokenCookie(use_debug=use_debug, reset=True)
			
		Thread.Create(fetch_dev_notice)
		
		if dump or use_debug and quiet == False:
			Log("=====================TOKEN START============================")
			Log("USING SAVED COOKIE TOKEN - TO DUMP TOKEN PERFORM RESET COOKIE UNDER OPTIONS MENU")
			Log("Retrieved Saved Cookie: %s" % cookie)
			Log("Retrieved Saved reqkey Cookie: %s" % reqkey_cookie)
			Log("Retrieved Saved Video-Token-Key: %s" % E(token_key))
			Log("=====================TOKEN END============================")
	else:
		if serverts == None:
			serverts = str(((int(time.time())/3600)*3600))

		UA = common.client.randomagent()
		
		headersS = {'X-Requested-With': 'XMLHttpRequest'}
		headersS['Referer'] = BASE_URL
		headersS['User-Agent'] = UA
		
		result, headers, content, cookie1 = common.interface.request_via_proxy_as_backup(BASE_URL, headers=headersS, limit='0', output='extended', httpsskip=use_https_alt, hideurl=True)
		Log(cookie1)
		
		try:
			if '__cfduid' in cookie1:
				cfd = cookie1.split(';')
				for cfdd in cfd:
					if '__cfduid' in cfdd:
						cookie1 = cfdd.strip()
		except:
			pass
		
		page_data_elems = HTML.ElementFromString(result)
		ALL_JS =  page_data_elems.xpath(".//script[@src[contains(.,'all.js')]]//@src")[0]
		
		headersS['Cookie'] = cookie1
		time.sleep(0.1)
		
		try:
			token_url = urlparse.urljoin(BASE_URL, TOKEN_PATH)
			
			reqkey_cookie = ''
			del TOKEN_KEY[:]
			del TOKEN_OPER[:]
			
			counter = 0
			while reqkey_cookie == '' and counter < 5:
				r, r1 = common.interface.request_via_proxy_as_backup(token_url, headers=headersS, httpsskip=use_https_alt, output='response', hideurl=True)
				time.sleep(0.1)
				del common.TOKEN_CODE[:]
				
				if r in common.client.HTTP_GOOD_RESP_CODES and '503 Service Unavailable' not in r1 and 'NotFoundHttpException' not in r1:
					token_enc = common.client.b64encode(r1)
					common.TOKEN_CODE.append(token_enc)
					
					quiet = True
					if counter == 4:
						quiet = False
					
					try:
						reqkey_cookie = decodeAndParse(token_enc,use_debug,use_https_alt, quiet=quiet)
					except:
						reqkey_cookie = ''
						
				if '503 Service Unavailable' in r1 and counter > 2:
					break
						
				time.sleep(2.0)
				counter += 1
			
			if dump or use_debug:
				Log("=====================TOKEN START============================")
				if len(common.TOKEN_CODE) == 0:
					Log('NO COOKIE TOKEN USED/REQUIRED')
				else:
					Log(common.TOKEN_CODE[0])
				Log("=====================TOKEN END============================")
		except Exception as e:
			Log(e)
			if dump or use_debug:
				Log("=====================TOKEN START============================")
				Log("Token URL %s is not reachable !" % token_url)
				Log("If the Token URL is not reachable using a browser as well it should not affect operations of this plugin.")
				Log("=====================TOKEN END============================")

		cookie_dict = {}
		
		try:
			if len(TOKEN_KEY) == 0:
				try:
					all_js_url = urlparse.urljoin(BASE_URL, ALL_JS)
					all_js_pack_code = common.interface.request_via_proxy_as_backup(all_js_url, httpsskip=use_https_alt, hideurl=True)
					unpacked_code = common.jsunpack.unpack(all_js_pack_code)
					try:
						cch = re.findall(r'%s' % common.client.b64decode('ZnVuY3Rpb25cKHQsaSxuXCl7XCJ1c2Ugc3RyaWN0XCI7ZnVuY3Rpb24gZVwoXCl7cmV0dXJuICguKj8pfWZ1bmN0aW9uIHJcKHRcKQ=='), unpacked_code)[0]
						token_key = re.findall(r'%s=.*?\"(.*?)\"' % cch, unpacked_code)[0]
						if token_key !=None and token_key != '':
							#cookie_dict.update({'token_key':token_key})
							TOKEN_KEY.append(token_key)
					except Exception as e:
						Log('ERROR fmovies.py>Token-fetch-1.1a: %s' % e)
						
					if len(TOKEN_KEY) == 0:
						try:
							cch = re.findall(r'%s' % common.client.b64decode('ZnVuY3Rpb25cKFthLXpdLFthLXpdLFthLXpdXCl7XCJ1c2Ugc3RyaWN0XCI7ZnVuY3Rpb24gW2Etel1cKFwpe3JldHVybiAoLio/KX1mdW5jdGlvbiBbYS16XVwoW2Etel1cKQ=='), unpacked_code)[0]
							token_key = re.findall(r'%s=.*?\"(.*?)\"' % cch, unpacked_code)[0]
							if token_key !=None and token_key != '':
								#cookie_dict.update({'token_key':token_key})
								TOKEN_KEY.append(token_key)
						except Exception as e:
							Log('ERROR fmovies.py>Token-fetch-1.2a: %s' % e)
				except Exception as e:
					Log('ERROR fmovies.py>Token-fetch-1a: %s' % e)
					
				try:
					token_oper = re.findall(r'%s' % common.client.b64decode('blwrPXRcWy4qP11cKGlcKS4qPyguKj8pOw=='), unpacked_code)[0]
					if token_oper !=None and token_oper != '' and len(token_oper) < 3:
						#cookie_dict.update({'token_oper':token_oper})
						token_oper = token_oper.replace('i','e')
						TOKEN_OPER.append(token_oper)
				except Exception as e:
					Log('ERROR fmovies.py>Token-fetch-1b: %s' % e)
					if common.DEV_DEBUG:
						Log(match_exp)
						Log(unpacked_code)
		except Exception as e:
			Log('ERROR fmovies.py>Token-fetch-1: %s' % e)

		try:
			if len(TOKEN_KEY) == 0:
				token_key = common.interface.request_via_proxy_as_backup(TOKEN_KEY_PASTEBIN_URL, httpsskip=use_https_alt, hideurl=True)
				if token_key !=None and token_key != '':
					#cookie_dict.update({'token_key':token_key})
					TOKEN_KEY.append(token_key)
		except Exception as e:
			Log('ERROR fmovies.py>Token-fetch-2: %s' % e)
			
		if len(TOKEN_KEY) > 0:
			cookie_dict.update({'token_key':token_key})
			
		try:
			if len(TOKEN_OPER) == 0 or common.DOWNLOAD_BACKUP_OPER == True:
				token_oper = common.interface.request_via_proxy_as_backup(TOKEN_OPER_PASTEBIN_URL, httpsskip=use_https_alt, hideurl=True)
				if token_oper !=None and token_oper != '':
					#cookie_dict.update({'token_oper':token_oper})
					TOKEN_OPER.append(token_oper)
		except Exception as e:
			Log('ERROR fmovies.py>Token-fetch-2b: %s' % e)
			
		if len(TOKEN_OPER) > 0:
			cookie_dict.update({'token_oper':TOKEN_OPER[0]})
			
		query = {'ts': serverts}
		tk = get_token(query)
		query.update(tk)
		hash_url = urlparse.urljoin(BASE_URL, HASH_PATH_MENU)
		hash_url = hash_url + '?' + urllib.urlencode(query)

		r1, headers, content, cookie2 = common.interface.request_via_proxy_as_backup(hash_url, headers=headersS, limit='0', output='extended', httpsskip=use_https_alt, hideurl=True)
		Log(cookie2)
		try:
			if '__cfduid' in cookie2:
				cookie2w = []
				cfd = cookie2.split(';')
				skip = False
				for cfdd in cfd:
					if '__cfduid' in cfdd and not skip:
						cookie1 = cfdd
						skip = True
					else:
						cookie2w.append(cfdd)
						
				try:
					cookie2 = ('; '.join(x for x in sorted(cookie2w)))
				except:
					pass
		except:
			pass
		
		common.CACHE['cookie'] = {}
		common.CACHE['cookie']['cookie1'] = cookie1
		common.CACHE['cookie']['cookie2'] = cookie2
		common.CACHE['cookie']['myts'] = time.time()
		common.CACHE['cookie']['UA'] = UA
		common.CACHE['cookie']['reqkey'] = reqkey_cookie
		
		cookie = cookie1 + '; ' + cookie2 + '; user-info=null; ' + newmarketgidstorage
		
		cookie_dict.update({'ts':time.time(), 'cookie': cookie, 'UA': UA, 'reqkey':reqkey_cookie})
		
		if dump or use_debug:
			Log("Storing Cookie: %s" % cookie)
			Log("Storing reqkey Cookie: %s" % reqkey_cookie)
			Log("Storing Video-Token-Key: %s" % E(TOKEN_KEY[0]))
			Log("Storing Video-Token-Oper: %s" % TOKEN_OPER[0])
			if len(TOKEN_OPER) > 1:
				Log("Storing Video-Token-Oper2: %s" % TOKEN_OPER[1])
		Dict['CACHE_COOKIE'] = E(JSON.StringFromObject(cookie_dict))
		Dict.Save()

	del common.CACHE_COOKIE[:]
	common.CACHE_COOKIE.append(cookie_dict)
	
	return cookie
	
def decodeAndParse(token, use_debug=False, use_https_alt=False, quiet=True):
	# dec = common.jsfdecoder.JSFDecoder(common.client.b64decode(token)).ca_decode()
	# dec = dec.split('reqkey=')
	# dec = dec[1].split(';')
	# dec = dec[0]
	# return dec
	
	return get_reqkey_cookie(token=token,use_debug=use_debug,use_https_alt=use_https_alt, quiet=quiet)
	
# Twoure's execjs / webhook reqkey cookie routine
# https://github.com/Twoure/9anime.bundle/tree/dev
def get_reqkey_cookie(token, use_debug=False, use_https_alt=False, quiet=True):
	try:	
		success=False
		token = String.Base64Decode(token)
		
		try:
			if common.USE_JSFDECODER:
				dec = common.jsfdecoder.JSFDecoder(token).ca_decode()
				if 'function' in dec:
					raise ValueError("JSFDecoder: No JSF code or mixed-mode code")
				if 'reqkey' not in dec:
					raise ValueError("JSFDecoder: reqkey not found. No JSF code or mixed-mode code")
				cookie_string = dec
				success = True
				Log.Debug("*** Using JSFDecoder for regkey cookie ***")
			else:
				raise ValueError("JSFDecoder: Disabled via Global overide")
		except Exception as e:
			token, replaced = common.cleanJSS2(token)
			use_webhook_when_no_engine_flag = False
			
			if common.execjs == None or common.USE_JSENGINE == False:
				use_webhook_when_no_engine_flag = True
			
			try:
				if quiet == False:
					Log.Debug('JSFDecoder failed, falling back to execjs >>> {}'.format(e))
				if common.USE_JSENGINE:
					ctx = common.execjs.compile(token)
					cookie_string = ctx.exec_('return jssuckit')
					for k in replaced.keys():
						cookie_string = cookie_string.replace(k, replaced[k])
					if 'reqkey=' in cookie_string:
						success = True
						Log.Debug("*** Using JS-Engine for regkey cookie ***")
					else:
						if quiet == False:
							Log.Debug('execjs output >>> %s' % (cookie_string))
				else:
					raise ValueError("JSEngine: Disabled via Global overide")
			except Exception as e:
				try:
					if quiet == False:
						Log.Debug('execjs failed, falling back to webhook if available >>> {}'.format(e))
					if common.USE_JSWEBHOOK and use_webhook_when_no_engine_flag:
						webhook_url = Prefs["webhook_url"]
						freeapi = True
						usage = 0
						if webhook_url != None and webhook_url != "" and "http" in webhook_url:
							if webhook_url == String.Base64Decode(common.WBH):
								usage = Dict[common.WBH]
								if usage != None and int(usage) > 10:
									freeapi = False
							if freeapi == True:
								token = re.sub(r"new(.*?|$\[\?\])\(\)", "new Date()", token)
								data = common.client.encodePostData({"jssuck": (token.replace('return jssuckit','jssuckit').replace('global','this'))})
								cookie_string, headers, content, cookie = common.interface.request(webhook_url, post=data, output='extended', httpsskip=use_https_alt, hideurl=True)
								if webhook_url == String.Base64Decode(common.WBH) and quiet == False:
									usage = Dict[common.WBH]
									if usage == None:
										usage = 0
									usage = int(usage)+1
									Dict[common.WBH] = usage
									Log.Debug('You have used %s requests out of 10 so far. Please fork your own WebHook (from https://hook.io/coder-alpha/test/fork) to use this method unrestricted ! Refer forum thread.' % usage)
								if quiet == False:
									Log.Debug('webhook X-RateLimit-Remaining this month >>> %s' % (content['X-RateLimit-Remaining']))
								for k in replaced.keys():
									cookie_string = cookie_string.replace(k, replaced[k])
								if 'reqkey=' in cookie_string:
									success = True
									Log.Debug("*** Using WebHook for regkey cookie ***")
								else:
									if quiet == False:
										Log.Debug('webhook output >>> %s' % (cookie_string))
							else:
								if quiet == False:
									Log.Debug('You have used your free %s requests. Please fork your own WebHook (from https://hook.io/coder-alpha/test/fork) to use this method ! Refer forum thread.' % usage)
						else:
							if quiet == False:
								Log.Debug('webhook url not defined in Channel Settings/Prefs.')
					else:
						raise ValueError("JSWebHook: Disabled via Global overide")
				except Exception as e:
					if quiet == False:
						Log.Debug('webhook failed, >>> {}'.format(e))

		if success == False:
			if quiet == False:
				Log.Debug("No method available to decode JSF code - use manual method".upper())
			return ''
		else:
			return common.cleanCookie(cookie_string)
	except Exception as e:
		if quiet == False:
			Log.Exception("fmovies.py >> : Cannot handle token cookie >>> {}".format(e))
			Log.Debug("No method available to decode JSF code - use manual method")
	return ''
	
def fetch_dev_notice():
	try:
		dev_notice = common.interface.request_via_proxy_as_backup(DEV_NOTICE_URL, httpsskip=True, hideurl=True)
		if dev_notice !=None and dev_notice != '':
			del DEV_NOTICE[:]
			DEV_NOTICE.append(dev_notice)
	except Exception as e:
		Log('ERROR fmovies.py>fetch_dev_notice: %s' % e)

def get_sources(url, key, use_debug=True, serverts=0, myts=0, use_https_alt=False, use_web_proxy=False, token_error=False, **kwargs):

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
		host_type = None
		magic_url = None
		subtitle = None
		isTargetPlay = False
		if url == None:
			error = 'No url'
			return magic_url, isTargetPlay, error, host_type, subtitle
		referer = url
		serverts = str(serverts)
		
		try:
			myts1 = serverts
			serverts = str(int(myts1))
		except:
			if use_debug:
				Log("Server-TS is encoded !")
			try:
				b, resp = decode_ts(myts1)
				if b == False:
					raise Exception('Could not decode ts')
				else:
					serverts = str(int(resp))
					if use_debug:
						Log("Server-TS decoded !")
			except:
				Log("Server-TS could not be decoded !")
				if common.control.setting('9animeserverts') != None:
					serverts = str(common.control.setting('9animeserverts'))
					if use_debug:
						Log("Server-TS from provider plugin !")
		
		T_BASE_URL = BASE_URL
		T_BASE_URL = 'https://%s' % common.client.geturlhost(url)
		is9Anime = True if common.ANIME_KEY in url else False
		
		time.sleep(0.5)
		
		if common.USE_COOKIES == True:
			cookie, error = common.make_cookie_str()
		else:
			cookie = ''

		try:
			headers = {'X-Requested-With': 'XMLHttpRequest'}
			
			if common.USE_COOKIES == True:
				headers['User-Agent'] = common.CACHE_COOKIE[0]['UA']
			else:
				headers['User-Agent'] = common.client.randomagent()
			
			hash_url = urlparse.urljoin(T_BASE_URL, HASH_PATH_INFO)
			query = {'ts': serverts, 'id': key, 'update':'0', 'server':'36'}
			tk = get_token(query, token_error, is9Anime)
			if tk == None:
				raise ValueError('video token algo')
			
			query.update(tk)
			hash_url = hash_url + '?' + urllib.urlencode(query)

			headers['Referer'] = '%s/%s' % (url, key)
			
			headers['Cookie'] = cookie

			if use_debug:
				Log("Using cookies : %s" % headers['Cookie'])
			
			#print hash_url
			if use_debug:
				Log("get_sources Request-3: %s" % hash_url)
				
			result = common.interface.request_via_proxy_as_backup(hash_url, headers=headers, httpsskip=use_https_alt, hideurl=not use_debug)
			
			if use_debug:
				Log("Request-3 result: %s" % result)
			#print result
			result = json.loads(result)

			if is9Anime == True:
				if 'error' in result:
					grabber = None
					error = result['error']
				elif result['target'] == "-":
					grabber = result['grabber']
					grab_data = grabber
					grabber_url = urlparse.urljoin(T_BASE_URL, GRABBER_API)
					
					if '?' in grabber:
						grab_data = grab_data.split('?')
						grabber_url = grab_data[0]
						grab_data = grab_data[1]
						
					print grab_data
					grab_server = str(urlparse.parse_qs(grab_data)['server'][0])
					
					b, resp = decode_t(result['params']['token'], -18, is9Anime)
					if b == False:
						raise Exception(resp)
					token = resp
					b, resp = decode_t(result['params']['options'], -18, is9Anime)
					if b == False:
						raise Exception(resp)
					options = resp
					
					grab_query = {'ts':serverts, grabber_url:'','id':result['params']['id'],'server':grab_server,'mobile':'0','token':token,'options':options}
					tk = get_token(grab_query, token_error, is9Anime)

					if tk == None:
						raise Exception('video token algo')
					grab_info = {'token':token,'options':options}
					del query['server']
					query.update(grab_info)
					query.update(tk)
					
					subtitle = result['subtitle']
					if subtitle==None or len(subtitle) == 0:
						subtitle = None
					
					if '?' in grabber:
						grabber += '&' + urllib.urlencode(query)
					else:
						grabber += '?' + urllib.urlencode(query)
				
					if grabber!=None and not grabber.startswith('http'):
						grabber = 'http:'+grabber
				else:
					grabber = result['target']
					b, resp = decode_t(grabber, -18, is9Anime)
					if b == False:
						raise ValueError(resp)
					grabber = resp
					isTargetPlay = True
					subtitle = result['subtitle']
			else:
				if 'error' in result:
					grabber = None
					error = result['error']
				elif result['target'] != "":
					grabber = result['target']
					b, resp = decode_t(grabber, -18, is9Anime)
					if b == False:
						raise ValueError(resp)
					grabber = resp
					isTargetPlay = True
					subtitle = result['subtitle']
				else:
					grabber = result['grabber']
					grab_data = grabber
					grabber_url = urlparse.urljoin(T_BASE_URL, GRABBER_API)
					
					if '?' in grabber:
						grab_data = grab_data.split('?')
						grabber_url = grab_data[0]
						grab_data = grab_data[1]
						
					grab_server = str(urlparse.parse_qs(grab_data)['server'][0])
					
					b, resp = decode_t(result['params']['token'], -18, is9Anime)
					if b == False:
						raise ValueError(resp)
					token = resp
					b, resp = decode_t(result['params']['options'], -18, is9Anime)
					if b == False:
						raise ValueError(resp)
					options = resp
					
					grab_query = {'ts':serverts, grabber_url:'','id':result['params']['id'],'server':grab_server,'mobile':'0','token':token,'options':options}
					tk = get_token(grab_query, token_error, is9Anime)

					if tk == None:
						raise ValueError('video token algo')
					grab_info = {'token':token,'options':options}
					del query['server']
					query.update(grab_info)
					query.update(tk)
					
					subtitle = result['subtitle']
					if '?' in grabber:
						grabber += '&' + urllib.urlencode(query)
					else:
						grabber += '?' + urllib.urlencode(query)
						
			if subtitle == None or len(subtitle) == 0:
				subtitle = None
				
			if grabber!=None and not grabber.startswith('http'):
				grabber = 'http:'+grabber
				
			if grabber != None:
				host_type = common.client.geturlhost(grabber)
				
			magic_url = grabber
		except Exception as e:
			error = e
			Log('ERROR fmovies.py>get_sources-1 %s, %s' % (e.args,url))
			pass

		return magic_url, isTargetPlay, error, host_type, subtitle
	except Exception as e:
		error = e
		Log('ERROR fmovies.py>get_sources-2 %s, %s' % (e.args,url))
		return magic_url, isTargetPlay, error, host_type, subtitle
		
def r01(t, e, token_error=False):
	i = 0
	n = 0
	for i in range(0, max(len(t), len(e))):
		if i < len(e):
			n += ord(e[i])
		if i < len(t):
			n += ord(t[i])
	h = format(int(hex(n),16),'x')
	return h

def a01(t, token_error=False, is9Anime=False):
	i = 0
	for e in range(0, len(t)):
		if token_error == False:
			if is9Anime == False:
				i += ord(t[e]) + e
			else:
				i += ord(t[e]) * e
		else:
			try:
				i += eval('ord(t[%s]) %s' % (e, TOKEN_OPER[0]))
			except:
				i += eval('ord(t[%s]) %s' % (e, TOKEN_OPER[1]))
	return i
	
#6856
def decode_t(t, i, is9Anime=False, **kwargs):
	n = [] 
	e = []
	r = ''
	
	if common.ENCRYPTED_URLS == False:
		return True, t

	try:
		if is9Anime == True:
			return decode_t2(t)
		for n in range(0, len(t)):
			if n==0 and t[n] == '.':
				pass
			else:
				c = ord(t[n])
				if c >= 97 and c <= 122:
					e.append((c - 71 + i) % 26 + 97)
				elif c >= 65 and c <= 90:
					e.append((c - 39 + i) % 26 + 65)
				else:
					e.append(c)
		for ee in e:
			r += chr(ee)
			
		return True, r
	except Exception as e:
		Log("fmovies.py > decode_t > %s" % e)
	return False, 'Error in decoding val'
	
def decode_t2(t):
	r = ""
	e_s = 'abcdefghijklmnopqrstuvwxyz'
	r_s = 'acegikmoqsuwybdfhjlnprtvxz'
	try:
		if t[0] == '-' and len(t) > 1:
			t = t[1:]
			for n in range(0, len(t)):
				if n == 0 and t[n] == '-':
					pass
				else:
					s = False
					for ix in range(0, len(r_s)):
						if t[n] == r_s[ix]:
							r += e_s[ix]
							s = True
							break
					if s == False:
						r += t[n]
						
			missing_padding = len(r) % 4
			if missing_padding != 0:
				r += b'='* (4 - missing_padding)
			r = common.client.b64decode(r)
		return True, r
	except Exception as e:
		False, 'Error in decoding'
		
def decode_ts(t):
	r = ""
	e_s = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
	r_s = 'ACEGIKMOQSUWYBDFHJLNPRTVXZ'
	try:
		if len(t) > 1:
			for n in range(0, len(t)):
				s = False
				for ix in range(0, len(r_s)):
					if t[n] == r_s[ix]:
						r += e_s[ix]
						s = True
						break
				if s == False:
					r += t[n]
						
			missing_padding = len(r) % 4
			if missing_padding != 0:
				r += b'='* (4 - missing_padding)
			r = common.client.b64decode(r)
		return True, r
	except Exception as e:
		False, 'Error in decoding'

def get_token(n, token_error=False, is9Anime=False, **kwargs):
	try:
		if is9Anime == False:
			d = TOKEN_KEY[0]
		else:
			d = common.control.setting('9animeVidToken')
		
		s = a01(d, token_error, is9Anime)
		for i in n: 
			s += a01(r01(d + i, n[i]), token_error, is9Anime)
		return {'_': str(s)}
	except Exception as e:
		Log("fmovies.py > get_token > %s" % e)

#########################################################################################################
