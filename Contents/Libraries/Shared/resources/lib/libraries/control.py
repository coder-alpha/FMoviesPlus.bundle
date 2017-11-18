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
all_uc_api = 'WXpFeE1qZzROV0k0WTJWall6Rm1aR1ZtWlRNNU1tVXdaR1E1WlRneVlqRT0='
openload_api = 'WW1ReU9USmxNalkzTjJZd016RTFOenBmWjNnMU5GTkROUT09'

loggertxt = []
setting_dict = {}
doPrint = False

def setting(key):
	if key in setting_dict.keys():
		return setting_dict[key]
	else:
		return None

def set_setting(key, value):
	if key == base64.b64decode('Y29udHJvbF9hbGxfdWNfYXBpX2tleQ==') and (value == None or value == '' or len(value) == 0):
		value = base64.b64decode(base64.b64decode(all_uc_api))
	elif key == base64.b64decode('Y29udHJvbF9vcGVubG9hZF9hcGlfa2V5') and (value == None or value == '' or len(value) == 0 or ':' not in value):
		value = base64.b64decode(base64.b64decode(openload_api))
	
	setting_dict[key] = value

def log(msg):
	try:
		if isinstance(msg, unicode):
			msg = msg.encode('utf-8')
			
		loggertxt.append(msg)
		print('%s' % msg)
	except Exception as e:
		pass  # just give up

# set default values for script testing - these will be updated once plugin initializes
set_setting('use_openload_pairing', True)
set_setting('is_uss_installed', False)
set_setting('use_https_alt', True)
set_setting('control_all_uc_api_key', None)
set_setting('control_openload_api_key',None)
set_setting('use_phantomjs', False)
set_setting('%s-%s' % (None,'Use-PhantomJS'), False)
