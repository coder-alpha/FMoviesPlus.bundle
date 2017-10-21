FMoviesPlus.bundle
===================
[![GitHub issues](https://img.shields.io/github/issues/coder-alpha/FMoviesPlus.bundle.svg?style=flat)](https://github.com/coder-alpha/FMoviesPlus.bundle/issues) 
[![](https://img.shields.io/github/release/coder-alpha/FMoviesPlus.bundle.svg?style=flat)](https://github.com/coder-alpha/FMoviesPlus.bundle/releases)
[![Plex Forums](https://img.shields.io/badge/Plex%20Forums-FMoviesPlus-E5A00D.svg?style=flat-square)](https://forums.plex.tv/discussion/255348/rel-fmoviesplus-channel/p1)

This is a plugin that creates a new channel in Plex Media Server to view content indexed by the website FMovies(.se|.to|.is), G2G, FMovies.io, YesMovies, Primewire

[Please read the first post for most up to date info](https://forums.plex.tv/discussion/255348/rel-fmoviesplus-channel/p1)

System Requirements
===================

- **Plex Media Server: ver. 1.3.3.3148 and above**
	- Tested Working:
		- Windows
		- Linux (Due to PMS issue - requires SSL option enabled under Channel Prefs.)
		- MacOS (Due to PMS issue - requires SSL option enabled under Channel Prefs.)
- **Plex Clients:**
	- Tested Working:
		- Plex Home Theater
		- Plex/Web
		- Samsung Plex App
		- Android M (Samsung Galaxy S6)
		- iOS (Apple iPhone6)
		- Chromecast

How To Install
==============

- Download the latest version of the plugin.
- Unzip and rename folder to "FMoviesPlus.bundle"
- Delete any previous versions of this bundle
- Copy FMoviesPlus.bundle into the PMS plugins directory under your user account:
	- Windows 7, Vista, or Server 2008:
		- C:\Users[Your Username]\AppData\Local\Plex Media Server\Plug-ins
	- Windows XP, Server 2003, or Home Server:
		- C:\Documents and Settings[Your Username]\Local Settings\Application Data\Plex Media Server\Plug-ins
	- Mac/Linux:
        - ~/Library/Application Support/Plex Media Server/Plug-ins
- Restart PMS
- OR via WbTools

Features & Issues
=================
Please visit the [Plex Support Thread](http://forums.plex.tv/discussion/255348/) for additional information.

Acknowledgements
================
- [mrknow](https://github.com/mrknow) for work on FMovies movie sources routine & Specto plugin for Kodi
- [lambda](https://github.com/lambda81) for HTTP Request routine for SSL/Alternate lambdalib for Kodi
- [youtube-dl](https://github.com/rg3/youtube-dl) / [Tithen-Firion](https://github.com/Tithen-Firion) for their work on OpenLoad scraper
- [coryo123](https://forums.plex.tv/discussion/194503) for DumbTools-for-Plex
- [Twoure](https://github.com/Twoure) for [AuthTools](https://github.com/Twoure/KissNetwork.bundle) and valuable techinical insights and suggestions for JS routines, etc.
- [mikew](https://github.com/mikew) for SS-Plex the inspiration for the Downloader