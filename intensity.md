intensity.py
============

https://github.com/penfever/intensity

As a filmmaker and film historian, I found myself wondering about certain
questions that lacked (to my knowledge) satisfying answers. For instance:

*Are “Films Noir”, ‘black’ films, visibly darker than other film genres of their
era?*

*Are films shot on Technicolor actually brighter than films captured with later
color film technologies?*

In order to answer these and other related questions, I wrote intensity.py.

The program is very simple -- when it runs, it searches its local folder for any
video files, including .avi, .mkv and .mp4 formats. It collects some essential
information about the films by inputting their (properly formatted) filenames,
places that information in a SQL database for later retrieval, along with the
intensity, or average brightness, of each frame in the video, and the ‘overall’
intensity level of the film.

The script ignores completely black portions of the film (EG: letterboxing,
title cards) when computing its average.

Finally, the script uses matplotlib to produce a simple chart of the video’s
brightness over time.

In order for the script to work, you must name your movie files according to the
following convention --

movietitle (year).extension

EG: The Last Drop of Water (1911).avi

I plan to use this script to store the intensity values of over 4000 films, and
use the data to provide helpful insights for my fellow film buffs.
