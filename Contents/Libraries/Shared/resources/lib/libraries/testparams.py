# -*- coding: utf-8 -*-

import json, re
import client

test_movies = []
test_movies_c = [{'title':'Ready Player One', 'year':'2018', 'imdb':'tt1677720'},{'title':'Peter Rabbit','year':'2018','imdb':'tt5117670'},{'title':'Passengers','year':'2016','imdb':'tt1355644'},{'title':'The Great Wall','year':'2016','imdb':'tt2034800'},{'title':'Gifted','year':'2017','imdb':'tt4481414'}]

test_shows = [{'title':'Sakura Quest','year':'2017', 'season':'1', 'episode':'1'}]

test_documentaries = [{'title':'Our Universe','year':'2013', 'imdb':'tt3263598'}]

p_options = [{'name':'MyAddr','url':'https://ssl-proxy.my-addr.org','working':True}]

e_url = 'YUhSMGNITTZMeTloY0drdWRHaGxiVzkyYVdWa1lpNXZjbWN2TXk5a2FYTmpiM1psY2k5dGIzWnBaVDl6YjNKMFgySjVQWEJ2Y0hWc1lYSnBkSGt1WkdWell5WmhjR2xmYTJWNVBUYzRaR0l3TWpBNE5XTXhPR0pqTmpFeVlXVTVaVGMxTWpZM1lqUTVNVEky'

def getLatest():

	test_movies_x = []
	
	for r in test_movies_c:
		test_movies_x.append({'title':r['title'], 'year':r['year'], 'imdb':r['imdb']})
			
	try:
		res = client.request(client.b64ddecode(e_url))
		js = json.loads(res)
		results = js['results']
		
		for r in results:
			try:
				title = r['title']
				yr = r['release_date']
				year = re.findall(r'\d{4}',yr)[0]
				imdb = None
				test_movies_x.append({'title':title, 'year':year, 'imdb':imdb})
			except:
				pass
	except:
		pass
		
	for i in test_movies_x:
		test_movies.append(i)
		if len(test_movies) >= 7:
			break

getLatest()