Drop your PhantomJS http://phantomjs.org/download.html binary file here.

Currently only tested on Windows & Linux. You might need to use 32bit Linux binary of PhantomJS.

Note: The PhantomJS response time to retrieve the final url can be more than 20 sec. So any Plex client like Plex-web that has a time-out of 20 sec. or less may throw a generic Channel error.

To use PhantomJS in the Channel for External Sources it needs to be enabled under the Channel settings. To use it also for the FMovies site interface each client needs to enable it via Channel menu > Options > Device Options > Use-PhantomJS.

If you would like to place the PhantomJS binary file outside the FMoviesPlus.bundle (FMoviesPlus.bundle\Contents\Libraries\Shared\phantomjs) folder so that it does not get deleted due to updating the Channel code, you may place it elsewhere and define the folder path under the Channel Settings.