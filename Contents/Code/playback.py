import common

# ToDo
####################################################################################################
@route(common.PREFIX+'/videoplayback')
def CreateVideoObject(title, summary, thumb, params, duration, genres, videoUrl, videoRes, include_container=False, **kwargs):

	video = MovieObject(
	key = Callback(CreateVideoObject, title=title, summary=summary, thumb=thumb, params=params, duration=duration, genres=genres, videoUrl=videoUrl, videoRes=videoRes, include_container=True),
		rating_key = videoUrl,
		title = title,
		summary = summary,
		thumb = thumb,
		items = [
			MediaObject(
					container = Container.MP4,     # MP4, MKV, MOV, AVI
					video_codec = VideoCodec.H264, # H264
					audio_codec = AudioCodec.AAC,  # ACC, MP3
					audio_channels = 2,            # 2, 6
					parts = [PartObject(key=Callback(PlayVideo, videoUrl=videoUrl, params=params))]
				)
			]
	)
  
	if include_container:
		return ObjectContainer(objects=[video])
	else:
		return video

####################################################################################################
@route(common.PREFIX+'/PlayVideo')
def PlayVideo(videoUrl, params, **kwargs):

	http_headers = {'User-Agent': common.client.USER_AGENT}
	http_cookies = None
	
	if params != None:
		params = JSON.ObjectFromString(D(params))
		headers = params['headers']
		if headers != None and headers != '':
			for key in headers.keys():
				http_headers[key] = headers[key]
				
		cookie = params['cookie']
		if cookie != None and cookie != '':
			headers['Cookie'] = cookie
			http_cookies = cookie
			http_headers['Cookie'] = cookie
			HTTP.Headers['Cookie'] = cookie

	return IndirectResponse(VideoClipObject, key=videoUrl, http_headers=http_headers)