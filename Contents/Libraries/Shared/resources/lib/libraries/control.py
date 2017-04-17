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


import os, base64, jsunpack

tmdb_key = jsunpack.jsunpack_keys()
tvdb_key = base64.urlsafe_b64decode('MUQ2MkYyRjkwMDMwQzQ0NA==')
fanarttv_key = base64.urlsafe_b64decode('YTc4YzhmZWRjN2U3NTE1MjRkMzkyNmNhMmQyOTU3OTg=')
trakt_key = base64.urlsafe_b64decode('NDFjYzI1NjY5Y2Y2OTc0NTg4ZjA0MTMxYjcyZjc4MjEwMzdjY2I1ZTdlMjMzNDVjN2MxZTk3NGI4MGI5ZjI1NQ==')
trakt_secret = base64.urlsafe_b64decode('Y2I4OWExYTViN2ZlYmJiMDM2NmQ3Y2EyNzJjZDc4YTU5MWQ1ODI2Y2UyMTQ1NWVmYzE1ZDliYzQ1ZWNjY2QyZQ==')


def log(msg):

	try:
		if isinstance(msg, unicode):
			msg = msg.encode('utf-8')
		print('[FMovies]: %s' % (msg))
	except Exception as e:
		pass  # just give up