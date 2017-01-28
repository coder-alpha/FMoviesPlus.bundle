import time, fmovies, base64

################################################################################
TITLE = "FMoviesPlus"
VERSION = '0.05' # Release notation (x.y - where x is major and y is minor)
GITHUB_REPOSITORY = 'coder-alpha/FMoviesPlus.bundle'
PREFIX = "/video/fmoviesplus"
################################################################################

# Vibrant Emoji's (might not be supported on all clients)
EMOJI_LINK = u'\U0001F517'
EMOJI_GREEN_HEART = u'\U0001F49A'
EMOJI_BROKEN_HEART = u'\U0001F494'

# Simple Emoji's
EMOJI_HEART = u'\u2665'
EMOJI_TICK = u'\u2713'
EMOJI_CROSS = u'\u2717'
EMOJI_QUESTION = u'\u2753'


####################################################################################################
# Get Key from a Dict using Val
@route(PREFIX + '/GetEmoji')
def GetEmoji(type, mode='vibrant'):

	# modes = ['simple','vibrant'] - enforce mode to override Prefs for Search Filter

	if mode == 'simple' or Prefs["use_vibrant_emoji"] == False:
		if type == 'pos' or type == 'true':
			return EMOJI_TICK
		elif type =='neg' or type == 'false':
			return EMOJI_CROSS
	else:
		if type == 'pos' or type == 'true':
			return EMOJI_GREEN_HEART
		elif type =='neg' or type == 'false':
			return EMOJI_BROKEN_HEART
	
	return EMOJI_QUESTION


####################################################################################################
# Get Key from a Dict using Val
@route(PREFIX + '/getkeyfromval')
def GetKeyFromVal(list, val_look):
	for key, val in list.iteritems():
		if val == val_look:
			return key
			
####################################################################################################
# Gets a client specific identifier
@route(PREFIX + '/getsession')
def getSession():
	if 'X-Plex-Client-Identifier' in str(Request.Headers):
		return str(Request.Headers['X-Plex-Client-Identifier'])
	elif 'X-Plex-Target-Client-Identifier' in str(Request.Headers):
		return str(Request.Headers['X-Plex-Target-Client-Identifier'])
	elif 'User-Agent' in str(Request.Headers) and 'X-Plex-Token' in str(Request.Headers):
		return 'UnknownClient-'+encode(str(Request.Headers['User-Agent']) + str(Request.Headers['X-Plex-Token'][:3]))[:10]
	else:
		return 'UnknownPlexClientSession'
		
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
@route(PREFIX + "/UseDumbKeyboard")
def UseDumbKeyboard():
	session = getSession()
	if Dict['ToggleDumbKeyboard'+session] == None or Dict['ToggleDumbKeyboard'+session] == 'disabled':
		return False
	else:
		return True

@route(PREFIX + "/ToggleDumbKeyboard")
def ToggleDumbKeyboard(session):
	
	if Dict['ToggleDumbKeyboard'+session] == None or Dict['ToggleDumbKeyboard'+session] == 'disabled':
		Dict['ToggleDumbKeyboard'+session] = 'enabled'
	else:
		Dict['ToggleDumbKeyboard'+session] = 'disabled'

	Dict.Save()
	return ObjectContainer(header='DumbKeyboard', message='DumbKeyboard has been ' + Dict['ToggleDumbKeyboard'+session] + ' for this device.', title1='DumbKeyboard')

####################################################################################################
# Get HTTP response code (200 == good)
@route(PREFIX + '/gethttpstatus')
def GetHttpStatus(url):
	try:
		req = GetHttpRequest(url=url)
		if req != None:
			conn = urllib2.urlopen(req, timeout=fmovies.GLOBAL_TIMEOUT_FOR_HTTP_REQUEST)
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
		headers = {'User-Agent': fmovies.USER_AGENT,
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