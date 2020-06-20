"""This script measures the average intensity level of a video file and saves it to a database."""

import time
import statistics
import os
import sqlite3
import glob
import numpy as np
import matplotlib.pyplot as plt
from imdb import IMDb
import cv2

def imscan(title):
    """IMDb tagging"""
    imsearch = im.search_movie(title)
    found = 0
    for imtitle in imsearch:
        if found == 0 and title == imtitle['title']:
            try:
                im.update(imtitle, info=['year'])
                if intdb[vc]['year'] == int(imtitle['year']):
                    print("matched " + imtitle.movieID)
                    return int(imtitle.movieID)
            except:
                pass
    return

def checkdb(i_v):
    """check for duplicates in local DB"""
    for row in enumerate(moviesdb):
        for item in row:
            if i_v == item:
                return 1
    return

def vidtest(clip):
    """checks if video is playable, and if so, returns the capture link"""
    try:
        capc = cv2.VideoCapture(clip)
        return capc
    except:
        print("CV2 error")
        return

#define globals, retrieve local DB, IMDb
NFDB = sqlite3.connect('NFDB.db')
c = NFDB.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS movies (id INT, imdbid BIGINT, title VARCHAR[255], year YEAR, length TIME, filmintensity FLOAT(5))''')
vids = glob.glob('.\*.avi') + glob.glob('.\*.mkv') + glob.glob('.\*.mp4') + glob.glob('.\*.m4v')
intdb = {}
im = IMDb()
c.execute('''SELECT * FROM movies''')
moviesdb = c.fetchall()
moviecount = len(moviesdb)
vc = -1
for vid in enumerate(vids):
    vc = vc + 1
    #define local variables
    iid = moviecount + vc + 1
    strid = "{}".format(iid)
    intdb[vc] = {}
    intdb[vc]['intensity'] = []
    intdb[vc]['year'] = 0
    end = len(vids[vc])-4
    intdb[vc]['title'] = vids[vc][2:end]
    #alternate naming method
    if vids[vc].find('(') != -1:
        marker = vids[vc].find('(')
        intdb[vc]['title'] = vids[vc][2:marker - 1]
        intdb[vc]['year'] = int(vids[vc][marker + 1:marker + 5])
    elif vids[vc].find('19') or vids[vc].find('20') != -1:
        marker = vids[vc].find('19') or vids[vc].find('20')
        if isinstance(vids[vc][marker:marker+4], int):
            intdb[vc]['title'] = vids[vc][2:marker - 1]
            intdb[vc]['year'] = int(vids[vc][marker:marker + 4])        
    imid = imscan(intdb[vc]['title'])
    if imid == 0:
        pass
    elif checkdb(imid) == 1:
        print("Match exists in local DB.")
        continue
    cap = vidtest(vids[vc])
    if cap is None:
        print("CV2 error")
        continue
    stryear = "{}".format(intdb[vc]['year'])
    ##begin scanning the video
    starttime = time.perf_counter()
    fc = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    statstr = "Video {} of {} is called {} and has a frame count of {}.".format(vc + 1, len(vids), intdb[vc]['title'], fc)
    print(statstr)
    fps = cap.get(cv2.CAP_PROP_FPS)
    intdb[vc]['length'] = time.strftime('%H:%M:%S', time.gmtime(fc/fps))
    idstr = 'CREATE TABLE IF NOT EXISTS "' + strid + 'intensity" (intensity FLOAT(5))'
    c.execute(idstr)
    idstr = 'INSERT INTO "' + strid + 'intensity" '
    args = 'Intensity-' + intdb[vc]['title'] + '-' + stryear
    for i in range(fc):
        ret, frame = cap.read()
        frame = np.ma.masked_equal(frame, 0)
        try:
            framemean = (np.mean(frame)/255)*100
        except:
            framemean = np.arange(1)
        pyf = framemean.item()
        intdb[vc]['intensity'].append(pyf)
        c.execute(idstr + 'VALUES (?)', (pyf, ))
    intdb[vc]['filmintensity'] = statistics.mean(intdb[vc]['intensity'])
    cap.release()
    cv2.destroyAllWindows()
    c.execute('INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?)', (strid, imid, intdb[vc]['title'], intdb[vc]['year'], intdb[vc]['length'], intdb[vc]['filmintensity']))
    #verify the db entry
    c.execute('''SELECT * FROM movies''')
    moviesdb = c.fetchall()
    pop = moviesdb.pop()
    print(pop)
    #save the chart
    plt.plot(intdb[vc]['intensity'])
    plt.title(intdb[vc]['title'] + '-' + intdb[vc]['length'] + '-Intensity')
    plt.ylabel('Intensity/Brightness')
    plt.ylim(0, 100)
    plt.xlabel('Frames')
    if not os.path.exists('results'):
        os.makedirs('results')
    plt.savefig(os.path.join('results', args + '.png'), dpi=300)
    plt.clf()
    print(vc)
    runtime = time.perf_counter() - starttime
    print(runtime)
c.close()
NFDB.commit()
NFDB.close()
