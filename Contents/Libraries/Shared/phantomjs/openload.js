// Usage: phantomjs openload.js <video_url>
// if that doesn't work try: phantomjs --ssl-protocol=any openload.js <video_url>
// Author: Tithen-Firion
// https://gist.github.com/Tithen-Firion/8b3921d745131837519d5c5b95b86440
//
// Modded by CA
// https://github.com/coder-alpha/FMoviesPlus.bundle/blob/master/Contents/Libraries/Shared/phantomjs/openload.js
//

var separator = ' | ';
var page = require('webpage').create(),
  system = require('system'),
  id, match;

if(system.args.length < 2) {
  console.error('No URL provided');
  phantom.exit(1);
}
match = system.args[1].match(/https?:\/\/(?:www\.)?(?:openload\.(?:co|io|link)|oload|openloed\.(?:tv|stream|site|xyz))\/(?:f|embed)\/([\w\-]+)/);
// https?://(?:www\.)?(?:openload\.(?:co|io|link)|oload\.(?:tv|stream|site|xyz))/(?:f|embed)/(?P<id>[a-zA-Z0-9-_]+)
if(match === null) {
  console.error('Could not find video ID in provided URL');
  phantom.exit(2);
}
id = match[1];

// thanks @Mello-Yello :)
page.onInitialized = function() {
  page.evaluate(function() {
    delete window._phantom;
    delete window.callPhantom;
	delete window.__phantomas;
	delete window.webdriver;
	delete window.domAutomation;
	window.outerHeight = 1200;
	window.outerWidth = 1600;
  });
  var MAXIMUM_EXECUTION_TIME = 1 * 60 * 1000; // 1 min. thanks @Zablon :)
  setTimeout(function() {
	phantom.exit();
  }, MAXIMUM_EXECUTION_TIME);
};
page.settings.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36";
page.settings.resourceTimeout = 1 * 60 * 1000; // 1 min.

// thanks @skidank (https://forums.plex.tv/discussion/comment/1582115/#Comment_1582115)
page.onError = function(msg, trace) {
	//console.log(msg);
}

page.open('https://openload.co/embed/' + id + '/', function(status) {

	//page.includeJs('https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js', function() {
		var info = page.evaluate(function() {

			function GetMySpanID(el) {
				try {
					var elm = null;
					var oid = null;
					oid = window.shouldreport;
					if (oid == null) {
						oid = window.fileid;
					}
					if (oid == null) {
						oid = document.querySelector('meta[name="og:url"]').content;
						if (oid != null) {
							oid = oid.split('/');
							oid = oid[oid.length-1];
<<<<<<< HEAD
						}
					}
					if (oid == null) {
						return 'Exception: OID could not be found from window.';
					}
					var elms = document.getElementsByTagName(el);
					for (var j = 0; j < elms.length; j++) {
						if (elms[j].id.length > 0) {
							var txt = elms[j].innerHTML;
							if (txt.indexOf(oid+'~') > -1) {
								return elms[j].id;
							} else if (j == elms.length-1) {
								return elms[j].id;
							}
						}
					}
=======
						}
					}
					if (oid == null) {
						return 'Exception: OID could not be found from window.';
					}
					var elms = document.getElementsByTagName(el);
					for (var j = 0; j < elms.length; j++) {
						if (elms[j].id.length > 0) {
							var txt = elms[j].innerHTML;
							if (txt.indexOf(oid+'~') > -1) {
								return elms[j].id;
							} else if (j == elms.length-1) {
								return elms[j].id;
							}
						}
					}
>>>>>>> origin/master
					return elm;
				} catch(e) {
					return 'Exception: Error occurred.';
				}
				
			};
			
			var spanID = GetMySpanID("p");
			var spanID2 = GetMySpanID("span");
			
			if ((spanID == null || spanID.length == 0 || spanID.indexOf('Exception') > -1) && (spanID2 == null || spanID2.length == 0 || spanID2.indexOf('Exception') > -1)) {
				return {
					decoded_id: '',
					decoded_id2: ''
				};
			}
			if (spanID == null || spanID.length == 0 || spanID.indexOf('Exception') > -1) {
				return {
					decoded_id: document.getElementById(spanID2).innerHTML,
					decoded_id2: ''
				};
			}
			if (spanID2 == null || spanID2.length == 0 || spanID2.indexOf('Exception') > -1) {
				return {
					decoded_id: document.getElementById(spanID).innerHTML,
					decoded_id2: ''
				};
			}
			return {
				decoded_id: document.getElementById(spanID).innerHTML,
				decoded_id2: document.getElementById(spanID2).innerHTML
			};
		  });

		var myInfo = info.decoded_id;
		if (myInfo == null || myInfo.length == 0 || myInfo.indexOf('Exception') > -1) {
			console.log('ERROR: ID not found. ' + myInfo);
		} else {
			var url = 'https://openload.co/stream/' + info.decoded_id + '?mime=true';
			var url2 = 'https://openload.co/stream/' + info.decoded_id2 + '?mime=true';
			var url_search = page.content.match(/\w+~\d+~[\d\.]+~\w+/);
<<<<<<< HEAD
			
=======
			var url_search2 = page.content.match(/\w+~\d+~[\d\.]+~\w+/);

>>>>>>> origin/master
			if (info.decoded_id.indexOf(id+'~') > -1) {
				//console.log('1');
				console.log(url);
			} else {
				if (info.decoded_id2.indexOf(id+'~') > -1) {
					//console.log('2');
					console.log(url2);
				} else {
					var url = 'https://openload.co/stream/' + url_search[0] + '?mime=true';
					//console.log('3');
					console.log(url);
				}
			}
		}
	//});
});

page.onLoadFinished = function(status) {
	//console.log('Status: ' + status);
	phantom.exit();
};
