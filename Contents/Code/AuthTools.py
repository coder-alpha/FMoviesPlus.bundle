#!/usr/bin/env python
#
# AuthTools
# https://github.com/Twoure/KissNetwork.bundle
#
# Author: Twoure 
# https://github.com/Twoure
#

import urllib2

def CheckAdmin():
	"""
	For Plex Home   : Only the main users token is accepted at http://127.0.0.1:32400/myplex/account
	For All Else	: Only the main users token is accepted at https://plex.tv/users/account
	"""

	url = 'https://plex.tv/users/account' if Prefs['plextv'] else 'http://127.0.0.1:32400/myplex/account'

	if Prefs['use_debug']:
		Log.Debug('*' * 80)
		Log('* Checking if user is Admin')
		Log.Debug('* Auth URL   = {}'.format(url))

	ptoken = Request.Headers.get('X-Plex-Token', '')
	if not ptoken:
		if Prefs['use_debug']:
			Log.Error('* NO Plex Token available for validation')
			Log('* Assuming current user is Admin')
			Log.Debug('*' * 80)
		return True
	else:
		if Prefs['use_debug']:
			Log.Debug('* Plex Token is available for validation')
		try:
			result = ""
			req = urllib2.Request(url, headers={'X-Plex-Token': ptoken})
			res = urllib2.urlopen(req, timeout=10)
			result = res.read()
			if result:
				Log('* Current User is Admin')
				Log.Debug('*' * 80)
				return True
		except Exception as e:
			if Prefs['use_debug']:
				Log('* Current User is NOT Admin')
				Log.Error('* CheckAdmin: User denied access: {}'.format(e))
				Log.Debug('*' * 80)
			pass
	return False