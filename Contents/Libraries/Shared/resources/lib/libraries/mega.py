#! /usr/bin/python
# -*- coding: utf-8 -*-

#########################################################################################################
#
# Mega scrapper
# by pts@fazekas.hu at Tue Oct 11 13:12:47 CEST 2016
# Modified by 
# Coder Alpha
# https://github.com/coder-alpha
#
'''
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
#########################################################################################################


""":" #megapubdl: Download public files from MEGA (mega.nz).

type python2.7 >/dev/null 2>&1 && exec python2.7 -- "$0" ${1+"$@"}
type python2.6 >/dev/null 2>&1 && exec python2.6 -- "$0" ${1+"$@"}
type python2.5 >/dev/null 2>&1 && exec python2.5 -- "$0" ${1+"$@"}
type python2.4 >/dev/null 2>&1 && exec python2.4 -- "$0" ${1+"$@"}
exec python -- ${1+"$@"}; exit 1

megapubdl is command-line tool for Unix implemented as a Python script to
download public files (with a public URL) from MEGA (mega.nz, mega.co.nz).
It works with Python 2.6 and 2.7, and needs only the `openssl' external tool or
PyCryptodome (https://github.com/Legrandin/pycryptodome) installed.

megapubdl doesn't work with Python 3.x. It works with Python 2.4
and 2.5 if the ssl module (https://pypi.python.org/pypi/ssl) is installed.

Usage:

  megapubdl.py "https://mega.nz/#!..."
"""

#
# TODO(pts): Improve error handling (especially socket errors and parse errors).
#

import base64
import urllib  # For urlencode.
import httplib
import os
import random
import re
import select
import socket
import stat
import struct
import subprocess
import sys
import traceback
import json
import ast
import urllib2,HTMLParser,urlparse
import time, cookielib

import control

from __builtin__ import eval

def import_get(module, name, default):
	try:
		__import__(module)
	except ImportError:
		return default
	return getattr(__import__('sys').modules[module], name, default)

###########################
	
# Tis a bit more permissive (in the number syntax) than the grammar on
# http://json.org/ . This also merges multiple operator tokens (without a
# space) to one.
JSON_TOKEN_RE = re.compile(
		r'(\s+)|'	# Whitespace.
		r'("([^\\"]+|\\(?:["\\/bfnrt]|u[0-9a-f]{4}))*")|'	# String literal.
		r'(true|false|null)|'	# Named values.
		r'[{}\[\],:]+|'	# Operators.
		r'[-+]?(?:\d+(?:[.]\d*)?|[.]\d+)(?:[eE][-+]?\d+)?')	# Number literal.
JSON_NAMED_VALUES = {'true': 'True', 'false': 'False', 'null': 'None'}
JSON_STRING_PART_RE = re.compile(r'[^\\]+|\\(?:["\\/bfnrt]|u[0-9a-f]{4})')
JSON_STRING_ESCAPE_RE = re.compile(
		r'[\xC0-\xDF][\x80-\xBF]|[\xE0-\xEF][\x80-\xBF]{2}|'
		r'[\x00-\x1F"\\\x7F-\xFF]')
URL_RE = re.compile(r'([a-z0-9]+)://([^/:@?#]+)(?::(\d+))?')
MEGA_ERRORS = {
		0: 'API_OK',	# Success
		-1: 'API_EINTERNAL',	# An internal error has occurred. Please submit a bug report, detailing the exact circumstances in which this error occurred.
		-2: 'API_EARGS',	# You have passed invalid arguments to this command.
		-3: 'API_EAGAIN',	# (always at the request level): A temporary congestion or server malfunction prevented your request from being processed. No data was altered. Retry. Retries must be spaced with exponential backoff.
		-4: 'API_ERATELIMIT',	# You have exceeded your command weight per time quota. Please wait a few seconds, then try again (this should never happen in sane real-life applications).
		-5: 'API_EFAILED',	# The upload failed. Please restart it from scratch.
		-6: 'API_ETOOMANY',	# Too many concurrent IP addresses are accessing this upload target URL.
		-7: 'API_ERANGE',	# The upload file packet is out of range or not starting and ending on a chunk boundary.
		-8: 'API_EEXPIRED',	# The upload target URL you are trying to access has expired. Please request a fresh one.
		-9: 'API_EOENT',	# Object (typically, node or user) not found
		-10: 'API_ECIRCULAR',	# Circular linkage attempted
		-11: 'API_EACCESS',	# Access violation (e.g., trying to write to a read-only share)
		-12: 'API_EEXIST',	# Trying to create an object that already exists
		-13: 'API_EINCOMPLETE',	# Trying to access an incomplete resource
		-14: 'API_EKEY',	# A decryption operation failed (never returned by the API)
		-15: 'API_ESID',	# Invalid or expired user session, please relogin
		-16: 'API_EBLOCKED',	# User blocked
		-17: 'API_EOVERQUOTA',	# Request over quota
		-18: 'API_ETEMPUNAVAIL',	# Resource temporarily not available, please try again later
		-19: 'API_ETOOMANYCONNECTIONS',	# Too many connections on this resource
		-20: 'API_EWRITE',	# Write failed
		-21: 'API_EREAD',	# Read failed
		-22: 'API_EAPPKEY',	# Invalid application key; request not processed
}

def parse_json(data):
	"""Combination of json.loads and unicode_to_str. Works in Python >=2.4."""

	if not isinstance(data, str):
		raise TypeError

	def unicode_to_str(obj, encoding='utf-8'):
		if isinstance(obj, (list, tuple)):
			return type(obj)(unicode_to_str(v, encoding) for v in obj)
		elif isinstance(obj, dict):
			return type(obj)((unicode_to_str(k, encoding), unicode_to_str(v, encoding))
											 for k, v in obj.iteritems())
		elif isinstance(obj, unicode):
			return obj.encode(encoding)
		else:
			return obj

	# Verified manually that custom_parse_json is the same as json.loads (from
	# Python 2.6).
	def custom_parse_json(data):
		output = []
		i = 0
		while i < len(data):
			match = JSON_TOKEN_RE.match(data, i)
			if not match:
				raise ValueError('JSON syntax error: %r' % (data[i : i + 16]))
			i = match.end()
			if match.group(1):	# Whitespace.
				pass
			elif match.group(2):	# String literal.
				output.append('u')
				if '\\/' not in match.group(2):
					output.append(match.group(2))	# Fortunately same as Python syntax.
				else:
					for match2 in JSON_STRING_PART_RE.finditer(match.group(2)):
						if match2.group() == '\\/':
							output.append('/')
						else:
							output.append(match2.group())
			elif match.group(3):
				output.append(JSON_NAMED_VALUES[match.group(3)])
			else:
				# Fortunately punctuation and number literals are also the same as
				# Python syntax.
				output.append(match.group())
		data = ''.join(output)
		if ast:
			return ast.literal_eval(data)
		else:
			# This is still safe because of the regexp scanning above.
			return eval(data, {})

	if json:
		try:
			return unicode_to_str(json.loads(data))	# Faster.
		except Exception, e:	# Not KeyboardInterrupt.
			raise ValueError('Error parsing JSON.')
	else:
		return unicode_to_str(custom_parse_json(data))


def dump_json(obj):
	if json:
		return json.dumps(obj)

	output = []
	emit = output.append

	def escape_utf8(data):
		if len(data) > 1:
			try:
				data = ord(data.decode('utf-8'))
				if data > 0xffff:
					data = '?'	# TODO(pts): Support surrogates.
				else:
					data = '\\u%04x' % data
			except UnicdodDecodeError:
				data = '?'
		else:
			data = '\\u%04x' % ord(data)
		# TODO(pts): Generate short \" \\ \/ \b \f \n \r \t .
		return data

	def add(obj):
		if obj is None:
			emit('null')
		elif obj is True:
			emit('true')
		elif obj is False:
			emit('false')
		elif isinstance(obj, (int, long)):
			emit(str(obj))
		elif isinstance(obj, float):
			emit(repr(obj))	# TODO(pts): Does JSON support NaN etc.?
		elif isinstance(obj, (str, unicode)):
			if isinstance(obj, unicode):
				obj = obj.encode('UTF-8')
			emit('"')
			emit(JSON_STRING_ESCAPE_RE.sub(
					lambda match: escape_utf8(match.group()), obj))
			emit('"')
		elif isinstance(obj, (list, tuple)):
			emit('[')
			sep = ''
			for item in obj:
				if sep:
					emit(sep)
				sep = ','
				add(item)
			emit(']')
		elif isinstance(obj, dict):
			emit('{')
			sep = ''
			for key, value in sorted(obj.iteritems()):
				if sep:
					emit(sep)
				sep = ','
				add(str(key))
				emit(':')
				add(value)
			emit('}')

	add(obj)
	return ''.join(output)


assert dump_json([7, 77L, -6.5, True, False, None, "foo\"\\bar", unichr(0x15a) + '\0', [], {}, {33: [44]}]) in (
		'[7, 77, -6.5, true, false, null, "foo\\"\\\\bar", "\\u015a\\u0000", [], {}, {"33": [44]}]',
		'[7,77,-6.5,true,false,null,"foo\\u0022\\u005cbar","\\u015a\\u0000",[],{},{"33":[44]}]')

# --- SSL fixes.
def fix_ssl():
	# This solves the HTTP connection problem on Ubuntu Lucid (10.04):
	#	 SSLError: [Errno 1] _ssl.c:480: error:140770FC:SSL routines:SSL23_GET_SERVER_HELLO:unknown protocol
	# It also fixes the following problem with StaticPython ob some systems:
	#	 SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:590)
	#
	# This fix works with Python version 2.4--2.7, with the bundled and the new
	# (1.16) ssl module.
	class fake_ssl:
		import ssl	# Needed, the MEGA API is https:// only.
		def partial(func, *args, **kwds):	# Emulate functools.partial for 2.4.
			return lambda *fargs, **fkwds: func(*(args+fargs), **dict(kwds, **fkwds))
		wrap_socket = staticmethod(partial(
				ssl.wrap_socket, ssl_version=ssl.PROTOCOL_TLSv1))
		# Prevent staticpython from trying to load /usr/local/ssl/cert.pem .
		# `export PYTHONHTTPSVERIFY=1' would also work from the shell.
		if getattr(ssl, '_create_unverified_context', None):
			_create_default_https_context = staticmethod(
					ssl._create_unverified_context)
		del ssl, partial
	httplib.ssl = fake_ssl



openssl_prog = False

# --- Cryptodome ---
# Don't use this, alo-aes doesn't have AES-CTR, so we'd have to use openssl
# anyway.
if 0:
	def aes_cbc(is_encrypt, data, key, iv='\0' * 16):
		#print "aes_cbc-1"
		if len(key) != 16:
			raise ValueError
		if len(iv) != 16:
			raise ValueError
		# https://pypi.python.org/pypi/alo-aes/0.3 , implemented in C.
		import aes
		aes_obj = aes.Keysetup(key)
		if is_encrypt:
			return aes_obj.cbcencrypt(iv, data)[1]
		else:
			return aes_obj.cbcdecrypt(iv, data)[1]
elif import_get('Cryptodome.Cipher.AES', 'MODE_CBC', None) is not None:
	# PyCrypto, implemented in C (no Python implementation). Tested and found
	# working with pycrypto-2.3.
	def aes_cbc(is_encrypt, data, key, iv='\0' * 16):
		#print "aes_cbc-2"
		if len(key) != 16:
			raise ValueError
		if len(iv) != 16:
			raise ValueError
		from Cryptodome.Cipher import AES
		aes_obj = AES.new(key, AES.MODE_CBC, iv)
		if is_encrypt:
			return aes_obj.encrypt(data)
		else:
			return aes_obj.decrypt(data)
else:
	openssl_prog = True
	def aes_cbc(is_encrypt, data, key, iv='\0' * 16):
		try:
			#print "aes_cbc-3"
			print key
			if len(key) != 16:
				print 'error - key'
				raise ValueError
			if len(iv) != 16:
				print 'error - iv'
				raise ValueError
			encdec = ('-d', '-e')[bool(is_encrypt)]
			print encdec
			p = subprocess.Popen(
					(openssl_prog, 'enc', encdec, '-aes-128-cbc', '-nopad',
					 '-K', key.encode('hex'), '-iv', iv.encode('hex')),
					stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			try:
				got, _ = p.communicate(data)
			finally:
				p.stdin.close()
				exitcode = p.wait()
				
			print exitcode
			if exitcode:
				raise ValueError('Error running openssl enc.')
			if len(got) != len(data):
				raise ValueError('openssl enc output size mismatch.')
			assert len(got) == len(data)
			return got
		except Exception as e:
			print e


def test_crypto_aes_cbc():
	key = 'k' * 16
	plaintext = 'a' * 64
	ciphertext = 'c8a97171fe2841736c27863f5da199d199bd3d757aacf7da7dd1805dcf2bb652e638f58d25420ab367966acdde3c8a1a9994b7e7fd32ed91bf0ea646fdd874a3'.decode('hex')
	assert aes_cbc(True,	plaintext, key) == ciphertext
	assert aes_cbc(False, ciphertext, key) == plaintext


if import_get('Cryptodome.Cipher.AES', 'MODE_CTR', None) is not None:
	# PyCrypto, implemented in C (no Python implementation). Tested and found
	# working with pycrypto-2.3.
	def yield_aes_ctr(data_iter, key, iv='\0' * 16, bufsize=None):
		if len(key) != 16:
			raise ValueError
		if len(iv) != 16:
			raise ValueError
		if isinstance(data_iter, str):
			data_iter = (data_iter,)
		data_iter = iter(data_iter)
		# PyCrypto, implemented in C (no Python implementation).
		from Cryptodome.Cipher import AES
		from Cryptodome.Util import Counter
		counter = Counter.new(8 * len(key), initial_value=int(iv.encode('hex'), 16))
		aes_obj = AES.new(key, AES.MODE_CTR, counter=counter)
		yield ''	# This is important, it signifies that decryption has started.
		encrypt = aes_obj.encrypt	# .encrypt and .decrypt do the same.
		for data in data_iter:
			yield encrypt(data)
else:
	openssl_prog = True
	def yield_aes_ctr(data_iter, key, iv='\0' * 16, bufsize=65536):
		if len(key) != 16:
			raise ValueError
		if len(iv) != 16:
			raise ValueError
		if isinstance(data_iter, str):
			data_iter = (data_iter,)
		data_iter = iter(data_iter)
		# Ubuntu Lucid has openssl-0.9.8k (2009-03-15) and openssl-0.9.8zh (2016)
		# don't have -aes-128-ctr.
		p = subprocess.Popen(
				(openssl_prog, 'enc', '-d', '-aes-128-ctr', '-nopad',
				 '-K', key.encode('hex'), '-iv', iv.encode('hex')),
				stdin=subprocess.PIPE, stdout=subprocess.PIPE)
		wfd = p.stdin.fileno()
		rfd = p.stdout.fileno()
		file_size = read_size = write_size = 0
		go = True
		# We don't do MAC verification on the downloaded data, that would
		# need additional crypto operations.
		try:
			yield ''	# This is important, it signifies that decryption has started.
			assert wfd >= 0
			while go:
				data = ''
				for data in data_iter:
					file_size += len(data)
					break	# Just get one (next) string.
				if not data:
					p.stdin.close()	# os.close(wfd)
					wfd = -1
					while 1:
						pdata = os.read(rfd, bufsize)
						if not pdata:
							go = False
							break
						read_size += len(pdata)
						yield pdata
					break
				i = 0
				while i < len(data):
					rfds, wfds, _ = select.select((rfd,), (wfd,), (), None)
					if rfds:
						pdata = os.read(rfd, bufsize)
						if not pdata:
							go = False
							break
						read_size += len(pdata)
						yield pdata
					if wfds:
						got = os.write(wfd, buffer(data, i, i + bufsize))
						i += got
						write_size += got
			exitcode = p.wait()
		except:
			p.wait()
			raise
		if exitcode:
			raise ValueError('Error running openssl enc.')
		if read_size != write_size:
			raise ValueError('openssl enc output size mismatch: read_size=%d write_size=%d' % (read_size, write_size))
		if read_size != file_size:
			raise ValueError('File size mismatch.')


def test_crypto_aes_ctr():
	key = 'k' * 16
	plaintext = 'a' * 63	# Not divisible by 16.
	# With default iv: ciphertext = 'f442c33f3a194b34800aa6c6a1387a1e51a61c628a5d9cf4dfc404a5853bbdb2a35e5ffa6454a3f994189ecba05b4d106c80c5976b9b0d5825988eff547d15'.decode('hex')
	ciphertext = '98ebbfa0932e0c3cf867b2ab5a7cd191a4d207475ec0340b49782d2e1083955c5838cf0b84ee87cf4b95a9b94b7e8f29de835be1ad0d7d078d505fb9bec167'.decode('hex')
	iv = '\0\1\2\3' * 4
	#assert aes_ctr(plaintext, key, iv) == ciphertext
	#assert aes_ctr(ciphertext, key, iv) == plaintext
	assert ''.join(yield_aes_ctr(plaintext, key, iv)) == ciphertext
	assert ''.join(yield_aes_ctr(ciphertext, key, iv)) == plaintext
	assert ''.join(yield_aes_ctr('foo\n', '\0' * 16)) == '\x00\x86\x24\xde'
	# Does the encryption 1 byte at a time.
	assert ''.join(yield_aes_ctr(iter('foo\n'), '\0' * 16)) == '\x00\x86\x24\xde'


def check_aes_128_ctr():
	# Ubuntu Lucid has openssl-0.9.8k (2009-03-15), which doesn't have
	# -aes-128-ctr.
	try:
		data = ''.join(yield_aes_ctr('foo\n', '\0' * 16))
	except (OSError, IOError, ValueError):
		raise ValueError(
				'Error starting crypto -- '
				'you may need to upgrade your openssl command or install pycrypto.')
	if data != '\x00\x86\x24\xde':
		raise ValueError(
				'Incorrect result from crypto -- '
				'you may need to reinstall your openssl command or install pycrypto.')


def find_custom_openssl():
	global openssl_prog
	if openssl_prog is not True:
		return
	import os
	import os.path
	prog = __file__
	try:
		target = os.readlink(prog)
	except (OSError, AttributeError):
		target = None
	if target is not None:
		if not target.startswith('/'):
			prog = os.path.join(os.path.dirname(prog), target)
	progdir = os.path.dirname(prog)
	if not progdir:
		progdir = '.'
	for name in ('openssl-megapubdl',
							 'openssl-core2.static', 'openssl.static', 'openssl'):
		pathname = os.path.join(progdir, name)
		if os.path.isfile(pathname):
			openssl_prog = pathname
			break
	else:
		openssl_prog = 'openssl'


# ---


def aes_cbc_encrypt_a32(data, key):
	return str_to_a32(aes_cbc(True, a32_to_str(data), a32_to_str(key)))


def aes_cbc_decrypt_a32(data, key):
	return str_to_a32(aes_cbc(False, a32_to_str(data), a32_to_str(key)))


def stringhash(str, aeskey):
	s32 = str_to_a32(str)
	h32 = [0, 0, 0, 0]
	for i in xrange(len(s32)):
		h32[i % 4] ^= s32[i]
	for r in xrange(0x4000):
		h32 = aes_cbc_encrypt_a32(h32, aeskey)
	return a32_to_base64((h32[0], h32[2]))


def encrypt_key(a, key):
	return sum(
		(aes_cbc_encrypt_a32(a[i:i + 4], key)
			for i in xrange(0, len(a), 4)), ())


def decrypt_key(a, key):
	return sum(
		(aes_cbc_decrypt_a32(a[i:i + 4], key)
			for i in xrange(0, len(a), 4)), ())


def decrypt_attr(attr, key):
	attr = aes_cbc(False, attr, a32_to_str(key)).rstrip('\0')
	return attr.startswith('MEGA{"') and parse_json(attr[4:])


def a32_to_str(a):
	return struct.pack('>%dI' % len(a), *a)


def str_to_a32(b):
	if len(b) % 4:
		# pad to multiple of 4
		b += '\0' * (4 - len(b) % 4)
	return struct.unpack('>%dI' % (len(b) / 4), b)


def base64_url_decode(data):
	data += '=='[(2 - len(data) * 3) % 4:]
	for search, replace in (('-', '+'), ('_', '/'), (',', '')):
		data = data.replace(search, replace)
	return base64.b64decode(data)


def base64_to_a32(s):
	return str_to_a32(base64_url_decode(s))


def base64_url_encode(data):
	data = base64.b64encode(data)
	for search, replace in (('+', '-'), ('/', '_'), ('=', '')):
		data = data.replace(search, replace)
	return data


def a32_to_base64(a):
	return base64_url_encode(a32_to_str(a))


# more general functions
def make_id(length):
	possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
	return ''.join(random.choice(possible) for _ in xrange(length))


def send_http_request(url, data=None, timeout=None):
	"""Return a httplib.HTTPResponse object."""
	#print url
	#print data
	match = URL_RE.match(url)
	if not match:
		raise ValueError('Bad URL: %s' % url)
	schema = match.group(1)
	if schema not in ('http', 'https'):
		raise ValueError('Unknown schema: %s' % schema)
	host = match.group(2)
	if match.group(3):
		port = int(match.group(3))
	else:
		port = (80, 443)[schema == 'https']
	path = url[match.end():] or '/'

	#print host
	ipaddr = socket.gethostbyname(host)	# Force IPv4. Needed by Mega.
	#print ipaddr
	hc_cls = (httplib.HTTPConnection, httplib.HTTPSConnection)[schema == 'https']
	# TODO(pts): Cleanup: Call hc.close() eventually.
	if sys.version_info < (2, 6):	# Python 2.5 doesn't support timeout.
		hc = hc_cls(ipaddr, port)
	else:
		hc = hc_cls(ipaddr, port, timeout=timeout)
	if data is None:
		hc.request('GET', path)
	else:
		hc.request('POST', path, data)
	return hc.getresponse()	# HTTPResponse.


class RequestError(ValueError):
	"""Error in API request."""


class Mega(object):
	def __init__(self, options=None):
		self.bufsize = 65536
		self.schema = 'https'
		self.domain = 'mega.co.nz'
		self.timeout = 160	# max time (secs) to wait for resp from api requests
		self.sid = None
		self.sequence_num = random.randint(0, 0xFFFFFFFF)
		self.request_id = make_id(10)

		if options is None:
			options = {}
		self.options = options
		
	def setBufferSize(self, buffer):
		self.bufsize = buffer

	def _login(self):
		master_key = [random.randint(0, 0xFFFFFFFF)] * 4
		password_key = [random.randint(0, 0xFFFFFFFF)] * 4
		session_self_challenge = [random.randint(0, 0xFFFFFFFF)] * 4

		user = self._api_request({
			'a': 'up',
			'k': a32_to_base64(encrypt_key(master_key, password_key)),
			'ts': base64_url_encode(a32_to_str(session_self_challenge) +
									a32_to_str(encrypt_key(session_self_challenge, master_key)))
		})

		resp = self._api_request({'a': 'us', 'user': user})
		#if numeric error code response
		if isinstance(resp, int):
			raise RequestError(resp)
		encrypted_master_key = base64_to_a32(resp['k'])
		self.master_key = decrypt_key(encrypted_master_key, password_key)
		if 'tsid' not in resp:
			raise RequestError('Missing tsid.')
		tsid = base64_url_decode(resp['tsid'])
		key_encrypted = a32_to_str(
			encrypt_key(str_to_a32(tsid[:16]), self.master_key))
		if key_encrypted == tsid[-16:]:
			self.sid = resp['tsid']

	def _api_request(self, data):
		params = {'id': self.sequence_num}
		self.sequence_num += 1

		if self.sid:
			params.update({'sid': self.sid})

		#ensure input data is a list
		if not isinstance(data, list):
			data = [data]

		url = '%s://g.api.%s/cs?%s' % (self.schema, self.domain, urllib.urlencode(params))
	
		if 'use_client_lib' in self.options.keys() and self.options['use_client_lib']:
			hr = client.request(url, post=dump_json(data), timeout=self.timeout, httpsskip=False)
			json_resp = parse_json(hr)
		else:
			hr = send_http_request(url, data=dump_json(data), timeout=self.timeout)
			
			if hr.status != 200:
				raise RequestError('HTTP not OK: %s %s' % (hr.status, hr.reason))
			json_resp = parse_json(hr.read())
			
	
		if isinstance(json_resp, int):
			raise RequestError('%s (%s)' % (MEGA_ERRORS.get(json_resp), json_resp))
		if isinstance(json_resp[0], int):
			raise RequestError('%s (%s)' % (MEGA_ERRORS.get(json_resp[0]), json_resp[0]))
		return json_resp[0]

	@classmethod
	def _parse_url(self, url):
		"""Returns (file_id, file_key."""
		i = url.find('/#!')
		if i < 0:
			raise RequestError('Key missing from URL.')
		path = url[i + 3:].split('!')
		return path[:2]

	@classmethod
	def get_file_id(self, url):
		return self._parse_url(url)[0]

	def download_url(self, url):
		"""Starts downloading a file from Mega, based on URL.

		Example usage:

			mega = Mega()
			dl = mega.download_url('https://mega.nz/#!gbYXQQ4I!PFUmL5I2xWgtbFhwFZjzwAMklsTPmG8y2bpOjYVMZc0')
			dl_info = dl.next()
			print (dl_info['name'], dl_info['size'])
			dl.next()	# Start the download.
			f = open(dl_info['name'], 'wb')
			try:
				for data in dl:
					f.write(data)
			finally:
				f.close()
		"""
		if self.sid is None:
			self._login()
		file_id, file_key = self._parse_url(url)
		file_key = base64_to_a32(file_key)	# if is_public:
		file_data = self._api_request({'a': 'g', 'g': 1, 'p': file_id})
		k = (file_key[0] ^ file_key[4], file_key[1] ^ file_key[5],
			 file_key[2] ^ file_key[6], file_key[3] ^ file_key[7])
		iv = file_key[4:6] + (0, 0)
		meta_mac = file_key[6:8]

		# Seems to happens sometime... When	this occurs, files are
		# inaccessible also in the official also in the official web app.
		# Strangely, files can come back later.
		if 'g' not in file_data:
			raise RequestError('File not accessible now.')
		file_url = file_data['g']	# Can be non-ASCII UTF-8.
		file_size = int(file_data['s'])	# Was already an int.
		attribs = base64_url_decode(file_data['at'])
		attribs = decrypt_attr(attribs, k)
		file_name = attribs['n']	# Can be non-ASCII UTF-8.
		key_str = a32_to_str(k)
		assert len(key_str) == 16
		iv_str = struct.pack('>LLLL', iv[0], iv[1], 0, 0)
		assert len(iv_str) == 16

		yield {'name': file_name, 'size': file_size, 'url': file_url, 'key': key_str, 'iv': iv_str, 'id': file_id}

		hr = send_http_request(file_url, timeout=self.timeout)
		if hr.status != 200:
			raise RequestError('HTTP download link not OK: %s %s' % (hr.status, hr.reason))
		ct = hr.getheader('content-type', '').lower()
		if ct.startswith('text/'):	# Typically 'application/octet-stream'.
			raise RequestError('Unexpected content-type: %s' % ct)
		yield_size = 0
		for pdata in yield_aes_ctr(
				iter(lambda bufsize=self.bufsize: hr.read(bufsize), ''),
				key_str, iv_str, self.bufsize):
			yield pdata
			yield_size += len(pdata)
		if yield_size != file_size:
			raise RequestError('File size mismatch: got=%d expected=%d' %
												 (yield_size, file_size))
												 
	def file_info(self, url):
		file_id, file_key = self._parse_url(url)
		file_key = base64_to_a32(file_key)	# if is_public:
		file_data = self._api_request({'a': 'g', 'g': 1, 'p': file_id})
		k = (file_key[0] ^ file_key[4], file_key[1] ^ file_key[5],
			 file_key[2] ^ file_key[6], file_key[3] ^ file_key[7])
		iv = file_key[4:6] + (0, 0)
		meta_mac = file_key[6:8]

		# Seems to happens sometime... When	this occurs, files are
		# inaccessible also in the official also in the official web app.
		# Strangely, files can come back later.
		if 'g' not in file_data:
			raise RequestError('File not accessible now.')
		file_url = file_data['g']	# Can be non-ASCII UTF-8.
		file_size = int(file_data['s'])	# Was already an int.
		attribs = base64_url_decode(file_data['at'])
		attribs = decrypt_attr(attribs, k)
		file_name = attribs['n']	# Can be non-ASCII UTF-8.
		key_str = a32_to_str(k)
		#assert len(key_str) == 16
		iv_str = struct.pack('>LLLL', iv[0], iv[1], 0, 0)
		#assert len(iv_str) == 16

		return {'name': file_name, 'size': file_size, 'url': file_url, 'key': key_str, 'iv': iv_str, 'id': file_id}
	
	def directDecode(self, chunk, key_str, iv_str):
		yield_size = 0
		for pdata in yield_aes_ctr(chunk, key_str, iv_str, self.bufsize):
			yield(pdata)
			yield_size += len(pdata)

def next(dl):
	for d in dl:
		return d
	return
	
			
def get_module_docstring():
	return __doc__


def get_doc(doc=None):
	if doc is None:
		doc = get_module_docstring()
	doc = doc.rstrip()
	doc = re.sub(r'\A:"\s*#', '', doc, 1)
	doc = re.sub(r'\n(\ntype python.*)+\nexec python -- .*', '', doc, 1)
	return doc


def fix_ext(filename):
	a, b = os.path.splitext(filename)
	return a + b.lower()


def download_mega_url(url, mega):
	print >>sys.stderr, 'info: Downloading URL: %s' % url
	file_id = mega.get_file_id(url)
	prefix = 'mega_%s_' % file_id
	entries = [e for e in os.listdir('.') if e.startswith(prefix) and not e.endswith('.tmpdl')]
	if entries:
		for entry in entries:
			print >>sys.stderr, 'info: Already present, keeping %s bytes in file: %s' % (
					os.stat(entry).st_size, entry)
		return
	dl = mega.download_url(url)
	try:
		dl_info = dl.next()
	except RequestError, e:
		if str(e).startswith('API_EOENT ('):	# File not found on MEGA.
			open(prefix + 'not_found.err', 'wb').close()
		raise
	filename = prefix + fix_ext('_'.join(dl_info['name'].split()))
	try:
		st = os.stat(filename)
	except OSError, e:
		st = None
	if st and stat.S_ISREG(st.st_mode) and st.st_size == dl_info['size']:
		print >>sys.stderr, 'info: Already downloaded, keeping %s bytes in file: %s' % (
				dl_info['size'], filename)
		return
	print >>sys.stderr, 'info: Saving file of %s bytes to file: %s' % (dl_info['size'], filename)
	marker = dl.next()	# Start the download.
	assert marker == ''
	filename_tmpdl = filename + '.tmpdl'
	try:
		f = open(filename_tmpdl, 'wb')
		try:
			for data in dl:
				f.write(data)
		finally:
			f.close()
		os.rename(filename_tmpdl, filename)
		filename_tmpdl = ''	# Don't attempt to remove it.
	finally:
		if filename_tmpdl:
			try:
				os.remove(filename_tmpdl)
			except OSError:
				pass

# def main(argv):
	# if len(argv) < 2 or argv[1] == '--help':
		# print get_doc()
		# sys.exit(0)
	# find_custom_openssl()
	# fix_ssl()
	# check_aes_128_ctr()
	# if len(argv) > 1 and argv[1] == '--test-crypto':
		# test_crypto_aes_cbc()
		# test_crypto_aes_ctr()
		# print '%s --test-crypto OK.' % argv[0]
		# return
	# mega = Mega()
	# had_error = False
	# for url in argv[1:]:
		# try:
			# download_mega_url(url, mega)
		# except (socket.error, IOError, OSError, ValueError):
			# traceback.print_exc()
			# had_error = True
	# sys.exit(2 * bool(had_error))
	
def get_mega_dl_link(mega_url):
	#fix_ssl()
	mega = Mega()
	log(type='INFO',method='get_mega_dl_link',err='created Mega service')
	login = mega._login()
	log(type='INFO',method='get_mega_dl_link',err='anon login')
	dl_info = mega.file_info(mega_url)
	log(type='INFO',method='get_mega_dl_link',err='created Mega downloader')
	
	file_url = "%s/%s" % (dl_info['url'],dl_info['name'])
	file_ext = dl_info['name'].split('.')
	file_ext = '.%s' % file_ext[1]
	
	file_size = dl_info['size']
	
	return file_url, file_size, file_ext

def test():
	fix_ssl()
	mega = Mega()
	dl = mega.download_url('https://mega.nz/#!R6xyBBpY!JmZlf7cn7w2scbWaPYESoppAY8UDbrkXKFz0e2FZASs')
	dl_info = dl.next()
	#print dl_info
	file_url = "%s/%s" % (dl_info['url'],dl_info['name'])
	print file_url
	
	#print (dl_info['name'], dl_info['size'])
	#return

	dl.next()	# Start the download.
	f = open(dl_info['name'], 'wb')
	try:
		for data in dl:
			f.write(data)
			print len(data)
	finally:
		f.close()
	print '* DONE *'
	
def test2():
	fix_ssl()
	print get_mega_dl_link('https://mega.nz/#!R6xyBBpY!JmZlf7cn7w2scbWaPYESoppAY8UDbrkXKFz0e2FZASs')

def log(type='INFO', method='undefined', err='', logToControl=False, doPrint=True):
	try:
		msg = '%s: %s > %s > %s : %s' % (time.ctime(time.time()), type, 'mega.py', method, err)
		if logToControl == True:
			control.log(msg)
		if control.doPrint == True and doPrint == True:
			print msg
	except Exception as e:
		control.log('Error in Logging: %s >>> %s' % (msg, e))
	
#test()
