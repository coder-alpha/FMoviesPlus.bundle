import re, urllib, urllib2, json, sys, time, random, urlparse
import common, updater, fmovies, tools, download
from DumbTools import DumbKeyboard
import AuthTools
from __builtin__ import eval

TITLE = common.TITLE
PREFIX = common.PREFIX

MC = common.NewMessageContainer(common.PREFIX, common.TITLE)

####################################################################################################
@route(PREFIX+'/videoplayback')
def CreateVideoObject(url, title, summary, thumb, params, duration, genres, videoUrl, videoRes, watch_title, include_container=False, playDirect=False, **kwargs):

	videoUrl = videoUrl.decode('unicode_escape')
	url = url if url != None else videoUrl
	
	if include_container:
		video = MovieObject(
			key = Callback(CreateVideoObject, url=url, title=title, summary=summary, thumb=thumb, params=params, duration=duration, genres=genres, videoUrl=videoUrl, videoRes=videoRes, watch_title=watch_title, include_container=True, playDirect=playDirect),
			rating_key = url + title,
			title = title,
			summary = summary,
			thumb = thumb,
			items = [
				MediaObject(
						container = Container.MP4,	 # MP4, MKV, MOV, AVI
						video_codec = VideoCodec.H264, # H264
						audio_codec = AudioCodec.AAC,  # ACC, MP3
						audio_channels = 2,			# 2, 6
						video_resolution = int(videoRes.replace('p','')),
						parts = [PartObject(key=Callback(PlayVideo,videoUrl=videoUrl, params=params, retResponse=include_container, url=url, title=title, summary=summary, thumb=thumb, watch_title=watch_title, playDirect=playDirect))],
						optimized_for_streaming = True
				)
			]
		)
	else:
		video = VideoClipObject(
			key = Callback(CreateVideoObject, url=url, title=title, summary=summary, thumb=thumb, params=params, duration=duration, genres=genres, videoUrl=videoUrl, videoRes=videoRes, watch_title=watch_title, include_container=True, playDirect=playDirect),
			rating_key = url + title,
			title = title,
			summary = summary,
			thumb = thumb,
			items = [
				MediaObject(
						container = Container.MP4,	 # MP4, MKV, MOV, AVI
						video_codec = VideoCodec.H264, # H264
						audio_codec = AudioCodec.AAC,  # ACC, MP3
						audio_channels = 2,			# 2, 6
						video_resolution = int(videoRes.replace('p','')),
						parts = [PartObject(key=Callback(PlayVideo,videoUrl=videoUrl, params=params, retResponse=include_container, url=url, title=title, summary=summary, thumb=thumb, watch_title=watch_title, playDirect=playDirect))],
						optimized_for_streaming = True
				)
			]
		)
  
	if include_container:
		return ObjectContainer(objects=[video])
	else:
		return video

####################################################################################################
@route(PREFIX+'/PlayVideo.mp4')
@indirect
def PlayVideo(videoUrl, params, retResponse, url, title, summary, thumb, watch_title, playDirect=False, **kwargs):

	playDirect = True if str(playDirect).lower() == 'true' else False
	Log('%s : %s : %s' % (url, videoUrl, playDirect))
	
	if 'googleusercontent.com' in videoUrl or playDirect == True:
		if Prefs['use_debug']:
			Log('PlayVideo > Using Direct Play')
		pass
	elif '3donlinefilms.com' in url:
		videoUrl, params_enc, err = common.host_direct.resolve(url)
		#params = JSON.ObjectFromString(D(params_enc))
		params = params_enc
	elif common.client.geturlhost(videoUrl) in common.host_misc_resolvers.supported_hosts:
		videoUrl, params_enc, b = common.host_misc_resolvers.resolve(videoUrl, Prefs["use_https_alt"])
		#params = JSON.ObjectFromString(D(params_enc))
		params = params_enc
		if videoUrl != None:
			videoUrl = videoUrl[len(videoUrl)-1]['file']
	elif '.mp4' not in videoUrl and 'mime=video/mp4' not in videoUrl:
		page_data, error = common.GetPageAsString(url=videoUrl)
		reg_exs = [[r'\[{.*mp4.*}]',0],[r'{.*mp4.*}',0],[r'\({.*mp4.*?}\)',0]]
		for regex in reg_exs:	
			try:
				p = re.findall(regex[0], page_data)[regex[1]]
				if p[0:1] == '(' and p[-1:] == ')':
					p = p[1:-1]
				if '[' not in p[0:2]:
					st = "[" + p + "]"
				else:
					st = p
				st = st.replace('\'','"')
				Log("json1: %s" % st)
				try:
					links = json.loads(st)
					if 'sources' in p:
						links = links['sources']
				except:
					sta = []
					for parts in p.split(','):
						p1 = re.findall(r'[a-z].*?:', parts)[0][0:-1]
						sta.append(parts.replace(p1, "\""+p1+"\""))
					st = ','.join(str(x) for x in sta)
					st = st.replace('""','"')
					if '[' not in st[0:2]:
						st = "[" + st + "]"
					Log("json2: %s" % st)
					links = json.loads(st)
					if 'sources' in p:
						links = links['sources']
				Log("links: %s" % links)
				for link in links:
					if 'mp4' in link:
						Log("link: %s" % link)
						break
				if 'file:' in p:
					link = link['file']
				elif 'src:' in p:
					link = link['src']
				else:
					link = re.findall(r'http.*mp4', p)[0]
				pre = 'https://'
				if 'http://' in link:
					pre = 'http://'
				link = link.replace('https://','').replace('http://','').replace('https:','').replace('http:','').replace('//','')
				if 'http' not in link:
					link = pre + link
				videoUrl = link
				break
			except Exception as e:
				Log(e)
				pass

	http_headers = {'User-Agent': common.client.USER_AGENT}
	http_cookies = None
	
	if params != None:
		params = JSON.ObjectFromString(D(params))
		
		if params != '':
			if 'headers' in params.keys():
				headers = params['headers']
				if headers != None and headers != '':
					for key in headers.keys():
						http_headers[key] = headers[key]
						
			if 'cookie' in params.keys():
				cookie = params['cookie']
				if cookie != None and cookie != '':
					headers['Cookie'] = cookie
					http_cookies = cookie
					http_headers['Cookie'] = cookie

	if Prefs['use_debug']:
		Log("Playback via Generic for URL: %s" % videoUrl)
		#Log("http_headers : %s" % http_headers)
		#Log("http_cookies : %s" % http_cookies)
		#Log(common.client.request(videoUrl, headers=http_headers, output='chunk')[0:20])
	
	if '.m3u8' in videoUrl:
		return IndirectResponse(VideoClipObject, key=HTTPLiveStreamURL(url=PlayAndAdd(url=url, title=title, summary=summary, thumb=thumb, videoUrl=videoUrl, watch_title=watch_title)), http_headers=http_headers, post_headers=http_headers, http_cookies=http_cookies)
	else:
		return IndirectResponse(VideoClipObject, key=PlayAndAdd(url=url, title=title, summary=summary, thumb=thumb, videoUrl=videoUrl, watch_title=watch_title), http_headers=http_headers, post_headers=http_headers, http_cookies=http_cookies)
	
####################################################################################################
@route(common.PREFIX+'/PlayAndAdd')
def PlayAndAdd(url, title, summary, thumb, videoUrl, watch_title, **kwargs):

	addfile = AddRecentWatchList(title=watch_title, url=url, summary=summary, thumb=thumb)
	
	return videoUrl
	
######################################################################################
# Adds a movie to the RecentWatchList list using the (title + 'R4S') as a key for the url
@route(PREFIX + "/addRecentWatchList")
def AddRecentWatchList(title, url, summary, thumb, **kwargs):

	#Log("%s %s" % (title, url))
	if url == None:
		return
	#append the time string to title so we can sort old to new items
	try:
		timestr = str(int(time.time()))
		Dict[timestr+'RR44SS'+title+'RR44SS'] = title + 'RR44SS' + url +'RR44SS'+ summary + 'RR44SS' + thumb + 'RR44SS' + timestr 
		Dict.Save()
	except:
		pass
		
	return None