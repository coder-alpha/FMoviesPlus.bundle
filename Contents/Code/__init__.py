######################################################################################
#
#	FMovies.se by Coder Alpha
# 	https://github.com/coder-alpha/FMoviesPlus.bundle
#
######################################################################################

import re, urllib, urllib2, json, base64, sys
import common, updater, fmovies
from DumbTools import DumbKeyboard

TITLE = common.TITLE
PREFIX = common.PREFIX
ART = "art-default.jpg"
ICON = "icon-fmovies.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_SEARCH_QUE = "icon-search-queue.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_FILTER = "icon-filter.png"
ICON_GENRE = "icon-genre.png"
ICON_LATEST = "icon-latest.png"
ICON_HOT = "icon-hot.png"
ICON_COUNTRIES = "icon-countries.png"
ICON_QUEUE = "icon-bookmark.png"
ICON_UNAV = "MoviePosterUnavailable.jpg"
ICON_PREFS = "icon-prefs.png"
ICON_UPDATE = "icon-update.png"
ICON_UPDATE_NEW = "icon-update-new.png"
ICON_DK_ENABLE = "icon-dumbKeyboardE.png"
ICON_DK_DISABLE = "icon-dumbKeyboardD.png"

MC = common.NewMessageContainer(common.PREFIX, common.TITLE)

######################################################################################
# Set global variables

CAT_WHATS_HOT = ['Sizzlers','Most Favourited','Recommended','Most Watched This Week','Most Watched This Month','Latest Movies','Latest TV-Series','Requested Movies']
CAT_REGULAR = ['Movies','TV-Series','Most Watched']
CAT_FILTERS = ['Release','Genre','Country','Filter Setup >>>']
CAT_GROUPS = ['What\'s Hot ?', 'Movies & TV-Series', 'Sort using...']

Filter = {}
Filter_Search = {}

######################################################################################

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_LIST)
	DirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_UNAV)
	VideoClipObject.art = R(ART)
	
	fmovies.CACHE.clear()
	HTTP.ClearCache()
	
	if Prefs["use_debug"]:
		HTTP.CacheTime = 0
		Log(common.TITLE + ' v.' + common.VERSION)
		Log("OS: " + sys.platform)
	else:
		try:
			CACHE_EXPIRY = 60 * int(Prefs["cache_expiry_time"])
		except:
			CACHE_EXPIRY = fmovies.CACHE_EXPIRY_TIME
		HTTP.CacheTime = CACHE_EXPIRY
	
	HTTP.Headers['User-Agent'] = fmovies.USER_AGENT
	HTTP.Headers['Referer'] = fmovies.BASE_URL

######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer(title2=TITLE)
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[0]), title = CAT_GROUPS[0], thumb = R(ICON_HOT)))
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[1]), title = CAT_GROUPS[1], thumb = R(ICON_MOVIES)))
	oc.add(DirectoryObject(key = Callback(ShowMenu, title = CAT_GROUPS[2]), title = CAT_GROUPS[2], thumb = R(ICON_FILTER)))
	
	oc.add(DirectoryObject(key = Callback(Bookmarks, title="Bookmarks"), title = "Bookmarks", thumb = R(ICON_QUEUE)))
	oc.add(DirectoryObject(key = Callback(SearchQueueMenu, title = 'Search Queue'), title = 'Search Queue', summary='Search using saved search terms', thumb = R(ICON_SEARCH_QUE)))
	
	session = common.getSession()
	if Dict['ToggleDumbKeyboard'+session] == None or Dict['ToggleDumbKeyboard'+session] == 'disabled':
		oc.add(DirectoryObject(key = Callback(common.ToggleDumbKeyboard, session=session), title = 'Enable DumbKeyboard', summary='Click here to Enable DumbKeyboard for this Device', thumb = R(ICON_DK_ENABLE)))
	else:
		oc.add(DirectoryObject(key = Callback(common.ToggleDumbKeyboard, session=session), title = 'Disable DumbKeyboard', summary='Click here to Disable DumbKeyboard for this Device', thumb = R(ICON_DK_DISABLE)))
	
	if common.UseDumbKeyboard():
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
	
	oc.add(PrefsObject(title = 'Preferences', thumb = R(ICON_PREFS)))
	try:
		if updater.update_available()[0]:
			oc.add(DirectoryObject(key = Callback(updater.menu, title='Update Plugin'), title = 'Update (New Available)', thumb = R(ICON_UPDATE_NEW)))
		else:
			oc.add(DirectoryObject(key = Callback(updater.menu, title='Update Plugin'), title = 'Update (Running Latest)', thumb = R(ICON_UPDATE)))
	except:
		pass
		
	return oc

######################################################################################
@route(PREFIX + "/showMenu")
def ShowMenu(title):

	oc = ObjectContainer(title2 = title)
	
	if title == CAT_GROUPS[0]:
		elems = CAT_WHATS_HOT
	elif title == CAT_GROUPS[1]:
		elems = CAT_REGULAR
	elif title == CAT_GROUPS[2]:
		elems = CAT_FILTERS
		
	if title == CAT_GROUPS[1]:
		for title in elems:
			oc.add(DirectoryObject(
				key = Callback(ShowCategory, title = title),
				title = title
				)
			)
	else:
		for title in elems:
			if title == CAT_FILTERS[3]:
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title),
					title = title
					)
				)
			else:
				oc.add(DirectoryObject(
					key = Callback(SortMenu, title = title),
					title = title
					)
				)
			
	if common.UseDumbKeyboard():
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
	return oc

######################################################################################
@route(PREFIX + "/sortMenu")
def SortMenu(title):

	url = fmovies.BASE_URL
	oc = ObjectContainer(title2 = title)
	
	# Test for the site url initially to report a logical error
	page_data = GetPageElements(url = url)
	if page_data == None:
		try:
			resp = '0'
			cookies = None
			req = common.GetHttpRequest(url=url, cookies=cookies)
			if req != None:
				response = urllib2.urlopen(req, timeout=fmovies.GLOBAL_TIMEOUT_FOR_HTTP_REQUEST)
				resp = str(response.getcode())
			
			if resp in fmovies.HTTP_GOOD_RESP_CODES:
				page_data = HTML.ElementFromString(response.read())
			else:
				msg = ("HTTP Code %s for %s. Enable SSL option in Channel Prefs." % (resp, url))
				Log("HTTP Error: %s", msg)
				return MC.message_container("HTTP Error", msg)
		except urllib2.HTTPError, err:
			msg = ("%s for %s" % (err.code, url))
			Log(msg)
			return MC.message_container("HTTP Error %s" % (err.code), "Error: Try Enabling SSL option in Channel Prefs.")
		except urllib2.URLError, err:
			msg = ("%s for %s" % (err.args, url))
			Log(msg)
			return MC.message_container("HTTP Error %s" % (err.args), "Error: Try Enabling SSL option in Channel Prefs.")

	if title in CAT_FILTERS:
		if title == CAT_FILTERS[0]:
			elems = page_data.xpath(".//*[@id='menu']//li[@class='has-children'][3]//li//a")
		elif title == CAT_FILTERS[1]:
			elems = page_data.xpath(".//*[@id='menu']//li[@class='has-children'][1]//li//a")
		elif title == CAT_FILTERS[2]:
			elems = page_data.xpath(".//*[@id='menu']//li[@class='has-children'][2]//li//a")

		for elem in elems:
			key = elem.xpath(".//text()")[0]
			urlpath = elem.xpath(".//@href")[0]
			if 'http' not in urlpath:
				urlpath = fmovies.BASE_URL + urlpath
			skey=key
			key=key.replace(' ','-')
				
			oc.add(DirectoryObject(
				key = Callback(ShowCategory, title = title, urlpath = urlpath, key = key),
				title = skey
				)
			)
	elif title in CAT_WHATS_HOT:
		if title == CAT_WHATS_HOT[0]:
			elems = page_data.xpath(".//*[@id='header-wrapper']//div[@class='swiper-wrapper']//div[contains(@class, 'item swiper-slide')]")
			for elem in elems:
				name = elem.xpath(".//a[@class='name']//text()")[0]
				loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
				
				thumbstr = elem.xpath(".//@style")[0]
				matches = re.findall(ur"url=([^\"]*)\)", thumbstr)
				thumb = matches[0]
				quality = elem.xpath(".//div[@class='meta']//span[@class='quality']//text()")[0]
				summary = elem.xpath(".//p[@class='desc']//text()")[0]
				try:
					more_info_link = elem.xpath(".//@data-tip")[0]
				except:
					more_info_link = None

				oc.add(DirectoryObject(
					key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
					title = name + " (" + quality + ")",
					summary = GetMovieInfo(summary=summary, urlPath=more_info_link),
					thumb = Resource.ContentsOfURLWithFallback(url = thumb)
					)
				)
		else:
			if title == CAT_WHATS_HOT[1]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@data-name='most-favorited']//div[@class='item']")
			elif title == CAT_WHATS_HOT[2]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@data-name='recommend']//div[@class='item']")
			elif title == CAT_WHATS_HOT[3]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@data-name='views-week']//div[@class='item']")
			elif title == CAT_WHATS_HOT[4]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@data-name='views-month']//div[@class='item']")
			elif title == CAT_WHATS_HOT[5]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='widget latest-movies']//div[@data-name='all']//div[@class='item']")
			elif title == CAT_WHATS_HOT[6]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='widget latest-series']//div[@class='item']")
			elif title == CAT_WHATS_HOT[7]:
				elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='widget requested']//div[@class='item']")
			
			for elem in elems:
				name = elem.xpath(".//a[@class='name']//text()")[0]
				loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
				thumb = elem.xpath(".//a[@class='poster']//@src")[0].split('url=')[1]
				summary = 'Plot Summary on Item Page'
				try:
					more_info_link = elem.xpath(".//@data-tip")[0]
				except:
					more_info_link = None

				oc.add(DirectoryObject(
					key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
					title = name,
					summary = GetMovieInfo(summary=summary, urlPath=more_info_link),
					thumb = Resource.ContentsOfURLWithFallback(url = thumb)
					)
				)
	
	if common.UseDumbKeyboard():
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))
	if len(oc) == 1:
		return ObjectContainer(header=title, message='No Videos Available')
	return oc
	
######################################################################################
@route(PREFIX + "/showcategory")
def ShowCategory(title, key=' ', urlpath=None, page_count='1'):
	
	if urlpath != None:
		newurl = urlpath + '?page=%s' % page_count
	else:
		if title == CAT_FILTERS[0]:
			newurl = (fmovies.BASE_URL + '/release-' + key.lower() + '?page=%s' % page_count)
		elif title == CAT_FILTERS[1]:
			newurl = (fmovies.BASE_URL + '/genre/' + key.lower() + '?page=%s' % page_count)
		elif title == CAT_FILTERS[2]:
			newurl = (fmovies.BASE_URL + '/country/' + key.lower() + '?page=%s' % page_count)
		elif title == CAT_REGULAR[0]:
			newurl = (fmovies.BASE_URL + '/movies' + '?page=%s' % page_count)
		elif title == CAT_REGULAR[1]:
			newurl = (fmovies.BASE_URL + '/tv-series' + '?page=%s' % page_count)
		elif title == CAT_REGULAR[2]:
			newurl = (fmovies.BASE_URL + '/most-watched' + '?page=%s' % page_count)
		
	page_data = GetPageElements(url=newurl)
	
	elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row movie-list']//div[@class='item']")
	last_page_no = int(page_count)
	try:
		last_page_no = int(page_data.xpath(".//*[@id='body-wrapper']//ul[@class='pagination'][1]//li[last()-1]//text()")[0])
	except:
		pass
		
	if key != ' ':
		oc = ObjectContainer(title2 = title + '|' + key.title() + '|Page ' + str(page_count) + ' of ' + str(last_page_no))
	else:
		oc = ObjectContainer(title2 = title + '|Page ' + str(page_count) + ' of ' + str(last_page_no))
		
	for elem in elems:
		name = elem.xpath(".//a[@class='name']//text()")[0]
		loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
		thumb = elem.xpath(".//a[@class='poster']//@src")[0].split('url=')[1]
		summary = 'Plot Summary on Item Page'
		try:
			more_info_link = elem.xpath(".//@data-tip")[0]
		except:
			more_info_link = None

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
			title = name,
			summary = GetMovieInfo(summary=summary, urlPath=more_info_link),
			thumb = Resource.ContentsOfURLWithFallback(url = thumb)
			)
		)
		
	if int(page_count) < last_page_no:
		oc.add(NextPageObject(
			key = Callback(ShowCategory, title = title, key = key, urlpath = urlpath, page_count = str(int(page_count) + 1)),
			title = "Next Page (" + str(int(page_count) + 1) +'/'+ str(last_page_no) + ") >>",
			thumb = R(ICON_NEXT)
			)
		)
		
	if common.UseDumbKeyboard():
		DumbKeyboard(PREFIX, oc, Search,
				dktitle = 'Search',
				dkthumb = R(ICON_SEARCH)
		)
	else:
		oc.add(InputDirectoryObject(key = Callback(Search), thumb = R(ICON_SEARCH), title='Search', summary='Search Channel', prompt='Search for...'))

	if len(oc) == 1:
		return ObjectContainer(header=title, message='No More Videos Available')
	return oc

######################################################################################
@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url, thumb):

	title = unicode(title)
	page_data = GetPageElements(url=url)
	if page_data == None:
		return MC.message_container("Unknown Error", "Error: The page was not received.")
	
	try:
		art = page_data.xpath(".//meta[@property='og:image'][1]//@content")[0]
	except:
		art = 'https://cdn.rawgit.com/coder-alpha/FMoviesPlus.bundle/master/Contents/Resources/art-default.jpg'
	oc = ObjectContainer(title2 = title, art = art)
	
	try:
		summary = page_data.xpath(".//*[@id='info']//div[@class='info col-md-19']//div[@class='desc']//text()")[0]
		#summary = re.sub(r'[^0-9a-zA-Z \-/.,\':+&!()]', '', summary)
	except:
		summary = 'Not Available'
	
	try:
		trailer = page_data.xpath(".//*[@id='control']//div['item mbtb watch-trailer hidden-xs']//@data-url")[0]
	except:
		trailer = None
	
	try:
		year = str(page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][2]//dd[2]//text()")[0][0:4])
	except:
		year = 'Not Available'
		
	try:
		rating = str(page_data.xpath(".//*[@id='info']//div[@class='info col-md-19']//span[1]//b//text()")[0])
	except:
		rating = 'Not Available'
		
	try:
		duration = int(page_data.xpath(".//*[@id='info']//div[@class='info col-md-19']//span[2]//b//text()")[0].strip('/episode').strip(' min'))
	except:
		duration = 'Not Available'

	try:
		genre0 = page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][1]//dd[1]//a//text()")
		genre = (','.join(str(x) for x in genre0))
		if genre == '':
			genre = 'Not Available'
	except:
		genre = 'Not Available'
	
	try:
		directors0 = page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][1]//dd[3]//text()")
		directors = (','.join(str(x) for x in directors0))
		if directors == '...':
			directors = 'Not Available'
	except:
		directors = 'Not Available'
	
	try:
		roles0 = page_data.xpath(".//*[@id='info']//dl[@class='meta col-sm-12'][1]//dd[2]//a//text()")
		roles = (','.join(str(x) for x in roles0))
		if roles == '':
			roles = 'Not Available'
	except:
		roles = 'Not Available'
	
	try:
		servers = page_data.xpath(".//*[@id='servers']//div[@class='server row']")
	except:
		servers = []
	
	summary += '\n '
	summary += 'Actors: ' + roles + '\n '
	summary += 'Directors: ' + directors + '\n '
	
	if str(duration) == 'Not Available':
		summary += 'Runtime: ' + str(duration) + '\n '
	else:
		summary += 'Runtime: ' + str(duration) + ' min.' + '\n '
	
	summary += 'Year: ' + year + '\n '
	summary += 'Genre: ' + genre + '\n '
	summary += 'IMDB rating: ' + rating + '\n '
	
	summary = unicode(summary)
	
	episodes = []
	servers_list = {}
	episodes_list = []
	server_lab = []
	isTvSeries = False
	
	try:
		episodes = page_data.xpath(".//*[@id='movie']//div[@class='widget boxed episode-summary']//div[@class='item']")
	except:
		pass
	
	for server in servers:
		label = server.xpath(".//label[@class='name col-md-4 col-sm-5']//text()[2]")[0].strip()
		if 'Server F' in label:
			label = label.replace('Server F','Google ')
		
		server_lab.append(label)
		items = server.xpath(".//ul[@class='episodes range active']//li")
		if len(items) > 1:
			isTvSeries = True
			
		servers_list[label] = []
		c=0
		for item in items:
			servers_list[label].append([])
			servers_list[label][c]={}
			label_qual = item.xpath(".//a//text()")[0].strip()
			label_val = item.xpath(".//a//@data-id")[0]
			servers_list[label][c]['quality'] = label_qual
			servers_list[label][c]['loc'] = label_val
			c += 1

	# label array of servers available - sort them so that presentation order is consistent
	server_lab = sorted(server_lab)
	
	# remap server list - this way its easier to iterate for tv-show episodes
	servers_list_new = []
	c=0
	
	if len(servers_list) > 0:
		for k in servers_list:
			break
		for no in servers_list[k]:
			servers_list_new.append([])
			servers_list_new[c] = {}
			for label in servers_list:

				servers_list_new[c][label] = {}
				servers_list_new[c][label] = {'quality':servers_list[label][c]['quality'], 'loc':servers_list[label][c]['loc']}
			c += 1
		
	# trailer
	if trailer != None:
		oc.add(VideoClipObject(
			url = trailer,
			title = title + ' (Trailer)',
			thumb = thumb,
			art = art,
			summary = summary)
		)
	
	if len(episodes) > 0:
		# case for presenting tv-series with synopsis
		det_Season = title.split(' ')
		try:
			SeasonN = int(det_Season[len(det_Season)-1])
			oc = ObjectContainer(title2 = title.replace(str(SeasonN), '(Season ' + str(SeasonN) + ')'), art = art)
		except:
			oc = ObjectContainer(title2 = title, art = art)
			
		for episode in episodes:
			no = episode.xpath(".//div[@class='ep']//i//text()")[0].strip()
			try:
				name = episode.xpath(".//span[@class='name']//text()")[0]
			except:
				name = 'Episode Name Not Available'
				
			air_date = episode.xpath(".//div[@class='date']//text()")[0]
			try:
				desc = episode.xpath(".//div[@class='desc']//text()")[0]
			except:
				desc = 'Episode Summary Not Available'

			episodes_list.append({"name":name,"air_date":air_date,"desc":desc})
			
		for eps in servers_list_new:
			qual_i = (int(eps[server_lab[0]]['quality'])-1)
			title_s = 'Ep:' + eps[server_lab[0]]['quality'] + ' - ' + episodes_list[qual_i]['name']
			desc = episodes_list[qual_i]['air_date'] + " : " + episodes_list[qual_i]['desc']
			
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail1, title=title_s, url=url, servers_list_new=servers_list_new[qual_i], server_lab=(','.join(str(x) for x in server_lab)), ep_idx=qual_i, summary=desc+'\n'+summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles),
				title = title_s,
				summary = desc,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb)
				)
			)
	elif isTvSeries:
		# case for presenting tv-series without synopsis
		det_Season = title.split(' ')
		try:
			SeasonN = int(det_Season[len(det_Season)-1])
			oc = ObjectContainer(title2 = title.replace(str(SeasonN), '(Season ' + str(SeasonN) + ')'), art = art)
		except:
			oc = ObjectContainer(title2 = title, art = art)
			
		for eps in servers_list_new:
			title_s = 'Ep:' + eps[server_lab[0]]['quality']
			qual_i = (int(eps[server_lab[0]]['quality'])-1)
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail1, title=title_s, url=url, servers_list_new=servers_list_new[qual_i], server_lab=(','.join(str(x) for x in server_lab)), ep_idx=qual_i, summary=summary, thumb=thumb, art=art, year=year, rating=rating, duration=duration, genre=genre, directors=directors, roles=roles),
				title = title_s,
				summary = summary,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb)
				)
			)
	else:
		# case for presenting movies
		for label in server_lab:
			for label_i in servers_list[label]:
				title_s = label + ' - ' + label_i['quality']
				url_s = label_i['loc']
				server_info, isOpenLoad = fmovies.GetApiUrl(url=url, key=url_s)
				if server_info != None:
					durl = "fmovies://" + E(JSON.StringFromObject({"url":url, "server":server_info, "title":title, "summary":base64.b64encode(summary), "thumb":thumb, "art":art, "year":year, "rating":rating, "duration":str(duration), "genre":genre, "roles":roles, "directors":directors, "roles":roles, "isOpenLoad":str(isOpenLoad), "useSSL":str(Prefs["use_https_alt"])}))
					try:
						oc.add(VideoClipObject(
							url = durl,
							title = title + ' - ' + title_s,
							thumb = thumb,
							art = art,
							summary = summary
							)
						)
					except:
						pass
	
		
	if Check(title=title,url=url):
		oc.add(DirectoryObject(
			key = Callback(RemoveBookmark, title = title, url = url),
			title = "Remove Bookmark",
			summary = 'Removes the current item from the Boomark que',
			art = art,
			thumb = R(ICON_QUEUE)
		)
	)
	else:
		oc.add(DirectoryObject(
			key = Callback(AddBookmark, title = title, url = url, summary=summary, thumb=thumb),
			title = "Add Bookmark",
			summary = 'Adds the current item to the Boomark que',
			art = art,
			thumb = R(ICON_QUEUE)
		)
	)

	return oc

@route(PREFIX + "/episodedetail1")
def EpisodeDetail1(title, url, servers_list_new, server_lab, ep_idx, summary, thumb, art, year, rating, duration, genre, directors, roles):

	oc = ObjectContainer(title2 = title, art = art)

	servers_list_new = servers_list_new.replace("'", "\"")
	servers_list_new = json.loads(servers_list_new)
	
	server_lab = server_lab.split(',')
	
	for label in server_lab:
		url_s = servers_list_new[label]['loc']
		server_info,isOpenLoad = fmovies.GetApiUrl(url=url, key=url_s)
		if server_info != None:
			durl = "fmovies://" + E(JSON.StringFromObject({"url":url, "server":server_info, "title":title, "summary":base64.b64encode(summary), "thumb":thumb, "art":art, "year":year, "rating":rating, "duration":str(duration), "genre":genre, "directors":directors, "roles":roles, "isOpenLoad":str(isOpenLoad), "useSSL":str(Prefs["use_https_alt"])}))
			try:
				oc.add(VideoClipObject(
					url = durl,
					title = title + ' (' + label + ')',
					thumb = thumb,
					art = art,
					summary = summary
					)
				)
			except:
				pass

	return oc
	
####################################################################################################
@route(PREFIX + "/getmovieinfo")
def GetMovieInfo(summary, urlPath):

	if urlPath == None and (summary == None or summary == ''):
		return 'Plot Summary on Item Page'
	elif urlPath == None:
		return summary
		
	if Prefs["dont_fetch_more_info"]:
		return summary

	try:
		url = fmovies.BASE_URL + '/' + urlPath
		page_data = GetPageElements(url=url)
		
		summary = ''
		
		try:
			summary_n = page_data.xpath(".//div[@class='inner']//p[@class='desc']//text()")[0]
			summary = summary_n + ' |\n '
		except:
			pass
		
		try:
			quality = page_data.xpath(".//div[@class='inner']//span[@class='quality']//text()")[0]
			year = page_data.xpath(".//div[@class='inner']//div[@class='title']//span//text()")[0]
			rating = (page_data.xpath(".//div[@class='inner']//span[@class='imdb']//text()"))[1].strip()
			summary += 'IMDb: ' + rating + ' | ' + 'Year: ' + year + ' | ' + 'Quality: ' + quality + ' |\n '
		except:
			pass
		
		try:
			country = page_data.xpath(".//div[@class='inner']//div[@class='meta'][1]//a//text()")[0]
			genre = page_data.xpath(".//div[@class='inner']//div[@class='meta'][2]//a//text()")[0]
			summary += 'Country: ' + country + ' | ' + 'Genre: ' + genre + ' |\n '
		except:
			pass
		
		try:
			actors = (page_data.xpath(".//div[@class='inner']//div[@class='meta'][3]//text()"))[2].strip()
			summary += 'Actors: ' + actors + '\n '
		except:
			pass
			
		if summary == '':
			summary = 'Plot Summary on Item Page'

	except:
		summary = 'Plot Summary on Item Page'
		
	return summary

######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.
@route(PREFIX + "/bookmarks")
def Bookmarks(title):

	oc = ObjectContainer(title1=title)
	for each in Dict:
		longstring = Dict[each]
		
		if 'https:' in longstring and 'Key4Split' in longstring:	
			stitle = longstring.split('Key4Split')[0]
			url = longstring.split('Key4Split')[1]
			summary = longstring.split('Key4Split')[2]
			thumb = longstring.split('Key4Split')[3]

			oc.add(DirectoryObject(
				key=Callback(EpisodeDetail, title=stitle, url=url, thumb=thumb),
				title=stitle,
				thumb=thumb,
				summary=summary
				)
			)
				
	#add a way to clear bookmarks list
	oc.add(DirectoryObject(
		key = Callback(ClearBookmarks),
		title = "Clear Bookmarks",
		thumb = R(ICON_QUEUE),
		summary = "CAUTION! This will clear your entire bookmark list!"
		)
	)

	if len(oc) == 0:
		return ObjectContainer(header=title, message='No Bookmarked Videos Available')
	return oc

######################################################################################
# Checks a show to the bookmarks list using the title as a key for the url
@route(PREFIX + "/checkbookmark")
def Check(title, url):
	longstring = Dict[title]
	#Log("url-----------" + url)
	if longstring != None and (longstring.lower()).find('fmovies.'.lower()) != -1:
		return True
	return False

######################################################################################
# Adds a movie to the bookmarks list using the title as a key for the url
@route(PREFIX + "/addbookmark")
def AddBookmark(title, url, summary, thumb):
	Dict[title] = title + 'Key4Split' + url +'Key4Split'+ summary + 'Key4Split' + thumb
	Dict.Save()
	return ObjectContainer(header=title, message='This item has been added to your bookmarks.')

######################################################################################
# Removes a movie to the bookmarks list using the title as a key for the url
@route(PREFIX + "/removebookmark")
def RemoveBookmark(title, url):
	del Dict[title]
	Dict.Save()
	return ObjectContainer(header=title, message='This item has been removed from your bookmarks.', no_cache=True)

######################################################################################
# Clears the Dict that stores the bookmarks list
@route(PREFIX + "/clearbookmarks")
def ClearBookmarks():

	remove_list = []
	for each in Dict:
		try:
			url = Dict[each]
			if url.find(TITLE.lower()) != -1 and 'http' in url:
				remove_list.append(each)
		except:
			continue

	for bookmark in remove_list:
		try:
			del Dict[bookmark]
		except Exception as e:
			Log.Error('Error Clearing Bookmarks: %s' %str(e))
			continue

	Dict.Save()
	return ObjectContainer(header="My Bookmarks", message='Your bookmark list will be cleared soon.', no_cache=True)

######################################################################################
# Clears the Dict that stores the search list
@route(PREFIX + "/clearsearches")
def ClearSearches():

	remove_list = []
	for each in Dict:
		try:
			if each.find(TITLE.lower()) != -1 and 'MyCustomSearch' in each:
				remove_list.append(each)
		except:
			continue

	for search_term in remove_list:
		try:
			del Dict[search_term]
		except Exception as e:
			Log.Error('Error Clearing Searches: %s' %str(e))
			continue

	Dict.Save()
	return ObjectContainer(header="Search Queue", message='Your Search Queue list will be cleared soon.', no_cache=True)

####################################################################################################
@route(PREFIX + "/search")
def Search(query=None, surl=None, page_count='1'):
	
	last_page_no = page_count
	
	if surl != None:
		url = surl + '&page=%s' % (str(page_count))
		page_data = GetPageElements(url=url)
	else:
		Dict[TITLE.lower() +'MyCustomSearch'+query] = query
		Dict.Save()
		url = fmovies.BASE_URL + fmovies.SEARCH_PATH + '?page=%s&keyword=%s' % (str(page_count), String.Quote(query, usePlus=True))
		page_data = GetPageElements(url=url)
		
	elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row movie-list']//div[@class='item']")
	
	last_page_no = int(page_count)
	try:
		last_page_no = int(page_data.xpath(".//*[@id='body-wrapper']//ul[@class='pagination'][1]//li[last()-1]//text()")[0])
	except:
		pass
		
	oc = ObjectContainer(title2 = 'Search Results|Page ' + str(page_count) + ' of ' + str(last_page_no))
	
	for elem in elems:
		name = elem.xpath(".//a[@class='name']//text()")[0]
		loc = fmovies.BASE_URL + elem.xpath(".//a[@class='name']//@href")[0]
		thumb = elem.xpath(".//a[@class='poster']//@src")[0].split('url=')[1]
		summary = 'Plot Summary on Item Page'
		try:
			more_info_link = elem.xpath(".//@data-tip")[0]
		except:
			more_info_link = None

		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = name, url = loc, thumb = thumb),
			title = name,
			summary = GetMovieInfo(summary=summary, urlPath=more_info_link),
			thumb = Resource.ContentsOfURLWithFallback(url = thumb)
			)
		)
		
	if int(page_count) < last_page_no:
		oc.add(NextPageObject(
			key = Callback(Search, query = query, surl = surl, page_count = str(int(page_count) + 1)),
			title = "Next Page (" + str(int(page_count) + 1) +'/'+ str(last_page_no) + ") >>",
			thumb = R(ICON_NEXT)
			)
		)
		
	if len(oc) == 0:
		return ObjectContainer(header='Search Results', message='No More Videos Available')

	return oc

####################################################################################################
@route(PREFIX + "/searchQueueMenu")
def SearchQueueMenu(title):
	oc = ObjectContainer(title2='Search Using Term')
	oc.add(DirectoryObject(
		key = Callback(ClearSearches),
		title = "Clear Search Queue",
		thumb = R(ICON_SEARCH),
		summary = "CAUTION! This will clear your entire search queue list!"
		)
	)
	for each in Dict:
		query = Dict[each]
		try:
			if each.find(TITLE.lower()) != -1 and 'MyCustomSearch' in each and query != 'removed':
				oc.add(DirectoryObject(key = Callback(Search, query = query, page_count='1'), title = query, thumb = R(ICON_SEARCH)))
		except:
			pass

	return oc
	
######################################################################################
@route(PREFIX + "/filtersetup")
def FilterSetup(title, key1 = None, key2val = None, mode='add', update=True):

	oc = ObjectContainer(title2 = title)
	
	if len(Filter) == 0:
		# Initialize Filter Data
		FilterSetupData()
		
	if len(Filter) == 0:
		return MC.message_container("Filter Setup Error", "Sorry but the Filter could not be created !")
	
	#Log(Filter)
		
	if len(Filter_Search) == 0:
		# Set defaults for 'Sort' & 'Order'
		Filter_Search['sort'] = 'post_date'
		Filter_Search['order'] = 'desc'
	
	if key1 == None:
		for f_key in sorted(Filter):
			oc.add(DirectoryObject(
				key = Callback(FilterSetup, title = title, key1 = f_key),
				title = f_key.title()
				)
			)
	else:
		oc = ObjectContainer(title2 = title + ' (' + key1.title() + ')')
		
		for f2_key in sorted(Filter[key1]):

			selected = ''
			# This indicates selected item
	
			if (key2val != None and key2val == Filter[key1][f2_key]):
				if (mode == 'add' or key1 == 'sort' or key1 == 'order'):
					selected = ' ' + u'\u2713'
			
			elif (key1 != 'sort' and key1 != 'order' and key1 in Filter_Search and Filter[key1][f2_key] in Filter_Search[key1]):
				selected = ' ' + u'\u2713'
			
			elif (key2val == None and key1 in Filter_Search and Filter[key1][f2_key] in Filter_Search[key1]):
				selected = ' ' + u'\u2713'
				
				
			key_title = f2_key.title() + selected
			if key1 == 'quality' or 'mode: and' in f2_key.lower(): # dont Camelcase quality values and Mode in Genre
				key_title = f2_key + selected
			
			if mode == 'rem' and selected != '':
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title, key1 = key1, key2val = Filter[key1][f2_key], update = MakeSelections(key1=key1, key2val=key2val, mode='rem', k2v= Filter[key1][f2_key]), mode='rem'),
					title = key_title
					)
				)
			elif selected != '':
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title, key1 = key1, key2val = Filter[key1][f2_key], update = MakeSelections(key1=key1, key2val=key2val, mode='rem', k2v= Filter[key1][f2_key]), mode='rem'),
					title = key_title
					)
				)
			else:
				oc.add(DirectoryObject(
					key = Callback(FilterSetup, title = title, key1 = key1, key2val = Filter[key1][f2_key], update = MakeSelections(key1=key1, key2val=key2val, mode=mode, k2v=Filter[key1][f2_key])),
					title = key_title
					)
				)
		
		oc.add(DirectoryObject(
			key = Callback(FilterSetup, title = title, key1 = None, key2val = None, update = MakeSelections(key1=key1, key2val=key2val, mode=mode, k2v=key2val)),
			title = 'Continue Filter Setup >>'
			)
		)
		
	# Build search string
	searchString = ''
	searchStringDesc = 'Sorting using ' + common.GetKeyFromVal(Filter['sort'],Filter_Search['sort']) + ' in ' + common.GetKeyFromVal(Filter['order'],Filter_Search['order']) + ' order.'
	
	for k1 in Filter_Search:
		if k1 != 'sort' and k1 != 'order':
			searchStringDesc += ' Filter ' + k1.title() + ' has '
			c=0
			for k2v in Filter_Search[k1]:
				searchString += k1 + '[]=' + k2v + '&'
				if c == len(Filter_Search[k1])-1:
					searchStringDesc += common.GetKeyFromVal(Filter[k1],k2v) + '.'
				else:
					searchStringDesc += common.GetKeyFromVal(Filter[k1],k2v) + ', '
				c += 1

	searchString += Filter_Search['sort'] + ':' + Filter_Search['order']
	searchString = searchString.replace(' ','+')

	
	# Build Search Url
	#https://fmovies.se/filter?sort=post_date%3Adesc&genre%5B%5D=25&genre_mode=and&country%5B%5D=2&type%5B%5D=movie&quality%5B%5D=HD+1080p&release%5B%5D=2017
	searchUrl = fmovies.BASE_URL + fmovies.FILTER_PATH + '?' + urllib2.quote(searchString, safe='_+=&')
	
	oc.add(DirectoryObject(
		key = Callback(Search, surl=searchUrl),
		title = '<<< Submit Search >>>',
		summary = searchStringDesc
		)
	)
	
	oc.add(DirectoryObject(
		key = Callback(ClearFilter),
		title = 'Reset Search Filter'
		)
	)
	oc.add(DirectoryObject(
		key = Callback(MainMenu),
		title = '<< Main Menu'
		)
	)
	
	return oc
	
######################################################################################
@route(PREFIX + "/makeselections")
def MakeSelections(key1, key2val, mode, k2v):
	
	if k2v != key2val or key1 == None or key2val == None:
		return False
	
	# Update Filter_Search based on previous selection
	# ToDo: This will deselect
	if (key1 != 'sort' and key1 != 'order' and key1 != None and key2val != None and key1 in Filter_Search and key2val in Filter_Search[key1] and mode == 'rem'):
		Filter_Search[key1].remove(key2val)
		if len(Filter_Search[key1]) == 0:
			del Filter_Search[key1]
	
	# This indicates selected item
	elif (key1 != None and key2val != None and (key1 not in Filter_Search or key2val not in Filter_Search[key1]) and mode == 'add'):
		if key1 != None and key2val != None:
			if key1 == 'sort' or key1 == 'order':
				Filter_Search[key1] = key2val
			else:
				if key1 not in Filter_Search:
					Filter_Search[key1] = []
				if key2val not in Filter_Search[key1]:
					Filter_Search[key1].append(key2val)
		
	return True

######################################################################################
@route(PREFIX + "/clearfilter")
def ClearFilter():
	Filter_Search.clear()
	
	oc = ObjectContainer(title2 = "Filter Reset")
	oc.add(DirectoryObject(
		key = Callback(FilterSetup, title=CAT_FILTERS[3]),
		title = CAT_FILTERS[3]
		)
	)
	return oc

######################################################################################
@route(PREFIX + "/filtersetupdata")
def FilterSetupData():

	try:
		url = (fmovies.BASE_URL + fmovies.SEARCH_PATH + '?keyword=fmovies')
		page_data = GetPageElements(url=url)
		
		Filter['sort']={}
		Filter['order']={'Ascending':'asc', 'Descending':'desc'}
		Filter['genre']={}
		Filter['country']={}
		Filter['type']={}
		Filter['quality']={}
		Filter['release']={}
		
		# Get Sort by info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter']//li")
		for elem in elems:
			key = elem.xpath(".//text()")[0].strip()
			val = elem.xpath(".//@data-value")[0].split(':')[0].strip()
			Filter['sort'][key] = val
			
		# Get Genre info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter genre']//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			if key == 'Mode: AND':
				key = 'Mode: AND (unchecked is OR)'
			Filter['genre'][key] = val
			
		# Get Country info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter country']//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			Filter['country'][key] = val
			
		# Get Type info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter type']//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			Filter['type'][key] = val
		
		# Get Quality info - page has wrong div classification using div[6] instead
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='row']//div[6]//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			Filter['quality'][key] = val
			
		# Get Release info
		elems = page_data.xpath(".//*[@id='body-wrapper']//div[@class='filter quality']//li")
		for elem in elems:
			key = elem.xpath(".//label//text()")[0].strip()
			val = elem.xpath(".//@value")[0].strip()
			Filter['release'][key] = val
	
	except:
		# Empty partial Filter if failed - error will be reported when using Filter
		Filter.clear()

######################################################################################
@route(PREFIX + "/GetPageElements")
def GetPageElements(url):

	page_data_elems = None
	try:
		if Prefs["use_https_alt"]:
			if Prefs["use_debug"]:
				Log("Using SSL Alternate Option")
				Log("Url: " + url)
			page_data = fmovies.request(url = url)
			page_data_elems = HTML.ElementFromString(page_data)
		else:
			page_data_elems = HTML.ElementFromURL(url)
	except:
		pass
		
	return page_data_elems
	
######################################################################################
@route(PREFIX + "/GetPageString")
def GetPageString(url):

	page_data_string = None
	try:
		if Prefs["use_https_alt"]:
			if Prefs["use_debug"]:
				Log("Using SSL Alternate Option")
				Log("Url: " + url)
			page_data_string = fmovies.request(url = url)
		else:
			page_data_string = HTTP.Request(url)
	except:
		pass
		
	return page_data_string
	
	######################################################################################