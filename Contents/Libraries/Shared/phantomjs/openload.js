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
match = system.args[1].match(
  /https?:\/\/(?:openload\.(?:co|io)|oload\.tv)\/(?:f|embed)\/([\w\-]+)/);
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
  });
};
page.settings.userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36";

// thanks @skidank (https://forums.plex.tv/discussion/comment/1582115/#Comment_1582115)
page.onError = function(msg, trace) {
	//console.log(msg);
}

page.open('https://openload.co/embed/' + id + '/', function(status) {

	//page.includeJs('https://ajax.googleapis.com/ajax/libs/jquery/3.2.1/jquery.min.js', function() {
		var info = page.evaluate(function() {

			function GetMySpanID() {
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
					}
				}
				if (oid == null) {
					return 'Exception: OID could not be found from window.';
				}
				var elms = document.getElementsByTagName("span");
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
				return elm;
			};
			
			var spanID = GetMySpanID();
			
			if (spanID == null || spanID.length == 0 || spanID.indexOf('Exception') > -1) {
				return {
					decoded_id: spanID
				};
			}
			return {
				decoded_id: document.getElementById(spanID).innerHTML
			};
		  });
		var myInfo = info.decoded_id;
		if (myInfo == null || myInfo.length == 0 || myInfo.indexOf('Exception') > -1) {
			console.log('ERROR: ID not found. ' + myInfo);
		} else {
			var url = 'https://openload.co/stream/' + info.decoded_id + '?mime=true';
			console.log(url);
		}
	//});
});

page.onLoadFinished = function(status) {
	//console.log('Status: ' + status);
	phantom.exit();
};