// Usage: phantomjs fmovies.js <video_url>
// if that doesn't work try: phantomjs --ssl-protocol=any fmovies.js <video_page_url>
// Author: Coder Alpha
//

var separator = ' | ';
var page = require('webpage').create(),
  system = require('system'),
  id, match;

if(system.args.length < 2) {
  console.error('No URL provided');
  phantom.exit(1);
}

function extractHostname(url) {
    var hostname;
    //find & remove protocol (http, ftp, etc.) and get hostname

    if (url.indexOf("//") > -1) {
        hostname = url.split('/')[2];
    }
    else {
        hostname = url.split('/')[0];
    }

    //find & remove port number
    hostname = hostname.split(':')[0];
    //find & remove "?"
    hostname = hostname.split('?')[0];

    return hostname;
}

var page_url = system.args[1];
var hostname = "."+extractHostname(page_url);

if(system.args.length >= 2) {
	if (system.args[2].indexOf(";") > -1) {
		var cookies = system.args[2].split(";");

		for (i=0; i < cookies.length; i++) {
			if (cookies[i].indexOf("=") > -1) {
				var cook = cookies[i].split("=");
				var c_name = cook[0].trim();
				var c_val = cook[1].trim();
				phantom.addCookie({
				  'name'     : c_name,   /* required property */
				  'value'    : c_val,    /* required property */
				  'domain'   : hostname, /* required property */
				  'path'     : '/'       /* required property */
				});
			}
		}
	}
}

page.settings.userAgent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36";
if(system.args.length >= 3) {
	if (system.args[3].indexOf("Mozilla") > -1) {
		var ua = system.args[3];
		page.settings.userAgent = ua;
	}
}

// thanks @Mello-Yello :)
page.onInitialized = function() {
  page.evaluate(function() {
    delete window._phantom;
    delete window.callPhantom;
	window.outerHeight = 1200;
	window.outerWidth = 1600;
  });
  var MAXIMUM_EXECUTION_TIME = 2 * 60 * 1000; // 1 min. thanks @Zablon :)
  setTimeout(function() {
	phantom.exit();
  }, MAXIMUM_EXECUTION_TIME);
};

// thanks @skidank (https://forums.plex.tv/discussion/comment/1582115/#Comment_1582115)
page.onError = function(msg, trace) {
	console.log(msg);
	var info = page.evaluate(function() {
		function GetIframeLink() {
			try {
				var txt = document.documentElement.innerHTML;
				if (txt != null && txt.length > 0) {
					return txt;
				}
				return null;
			} catch(err) {
				return 'Exception: ' + err.message + ', DocTitle:' + document.title;
			}
		};
		
		var spanID = GetIframeLink();
		
		if (spanID == null || spanID.length == 0 || spanID.indexOf('Exception') > -1) {
			return {
				decoded_id: spanID
			};
		}
		return {
			decoded_id: spanID
		};
	  });

	var myInfo = info.decoded_id;
	if (myInfo == null || myInfo.length == 0 || myInfo.indexOf('Exception') > -1) {
		console.log('ERROR: not found. ' + myInfo);
	} else {
		var url = info.decoded_id;
		console.log(url);
	}
	phantom.exit();
}

page.open(page_url, function(status) {

	//page.includeJs('https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js', function() {
		var info = page.evaluate(function() {
			function GetIframeLink() {
				try {
					var txt = document.documentElement.innerHTML;
					if (txt != null && txt.length > 0) {
						return txt;
					}
					return null;
				} catch(err) {
					return 'Exception: ' + err.message;
				}
			};
			
			var spanID = GetIframeLink();
			
			if (spanID == null || spanID.length == 0 || spanID.indexOf('Exception') > -1) {
				return {
					decoded_id: spanID
				};
			}
			return {
				decoded_id: spanID
			};
		  });

		var myInfo = info.decoded_id;
		if (myInfo == null || myInfo.length == 0 || myInfo.indexOf('Exception') > -1) {
			console.log('ERROR: not found. ' + myInfo);
		} else {
			var url = info.decoded_id;
			console.log(url);
		}
	//});
});

page.onLoadFinished = function(status) {
	//console.log('Status: ' + status);
	phantom.exit();
};