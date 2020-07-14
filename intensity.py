"""This script measures the average intensity level of a video file and saves it to a database."""

import time
import statistics
import os
import shutil
import sqlite3
import glob
import multiprocessing
import nfdbhelp
import numpy as np
import matplotlib.pyplot as plt
from imdb import IMDb
import cv2

def checkdb(i_v, viddc):
    check_id = 0
    count_id = str(moviecount + viddc + 1)
    if i_v is False:
        try:
            with lock:
                c.execute(f'''SELECT id FROM movies WHERE imdbid is {str(i_v)}''')
        except:
            pass
        iid = c.fetchall()
        check_id = str(c.fetchall())
        if iid == []:
            iid = i_v
    else:
        iid = count_id
    strid_d = "{}".format(iid)
    try:
        with lock:
            c.execute('SELECT * FROM "' + strid_d +'intensity"')
        if len(c.fetchall) > 100:
            return 'False'
    except:
        pass
    try:
        with lock:
            c.execute('SELECT * FROM "' + check_id +'intensity"')
        if len(c.fetchall) > 100:
            return 'False'
    except:
        pass

    try:
        with lock:
            c.execute('SELECT * FROM "' + count_id +'rgbintensity"')
        if len(c.fetchall) > 100:
            return 'False'
    except:
        pass
    return strid_d, iid

def vidtest(clip):
    """checks if video is playable, and if so, returns the capture link"""
    try:
        capc = cv2.VideoCapture(clip)
        return capc
    except:
        print("CV2 error")
        return

def ityplot(ndir, viddc):
    """Draws and saves the chart"""
    plt.plot(intdb[viddc]['intensity'], linewidth=.25)
    plt.title(intdb[viddc]['title'] + '-' + intdb[viddc]['length'] + '-Intensity')
    plt.ylabel('Intensity/Brightness')
    plt.ylim(0, 100)
    plt.xlabel('Frames')
    _ = 0
    while os.path.exists(ndir):
        _ += 1
        ndir = ndir + str(_)
    try:
        plt.savefig(ndir, dpi=300)
    except:
        print("Chart could not be saved.")
        pass
    plt.clf()

def intensity(database_dir):
    #initialize variables
    global counter
    with counter.get_lock():
        counter.value += 1
        vc = counter.value
    countid = moviecount + vc + 1
    intdb[vc] = {}
    intdb[vc]['intensity'] = []
    #labeling for DB and checking for duplicates
    intdb[vc]['title'], intdb[vc]['year'], code = nfdbhelp.makename(vids[n])
    if code != 2:
        imid, _ = nfdbhelp.imscan(intdb[vc]['title'], intdb[vc]['year'], vc, 0, 0)
    else:
        imid = 0
    if checkdb(imid, vc) == 'False':
        print("Table already exists. Skipping.")
        return
    #testing video playback
    cap = vidtest(vids[vc])
    if cap is None:
        print("CV2 error")
        return
    #begin scanning the video
    starttime = time.perf_counter()
    fc = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if fc == 0:
        return
    fps = cap.get(cv2.CAP_PROP_FPS)
    intdb[vc]['length'] = time.strftime('%H:%M:%S', time.gmtime(fc/fps))
    if code == 2:
        frame_time = int(((fc/fps)/60))
        imid, intdb[vc]['year'] = nfdbhelp.imscan(intdb[vc]['title'], intdb[vc]['year'], vc, 2, frame_time)
    if imid == 0:
        print("No IMDb match found. Using local count.")
        strid = str(countid)
    else:
        print(f"Video {vc + 1} of {len(vids)} is called {intdb[vc]['title']} and has a frame count of {fc}.")
        print(f"IMDb ID is {imid}.\n")
        strid = str(imid)
    idstr = 'CREATE TABLE IF NOT EXISTS "' + strid + 'intensity" (intensity FLOAT(5))'
    with lock:
        c.execute(idstr)
    idstr = 'INSERT INTO "' + strid + 'intensity" '
    savepath = r'C:\\Code\\Other\\intensity_charts\\'
    if not os.path.exists(savepath):
        os.makedirs(savepath)   
    savepath = savepath + intdb[vc]['title'] + '-' + strid + '-Intensity.png'
    for _ in range(fc):
        ret, frame = cap.read()
        if frame is None:
            continue
        frame = np.ma.masked_less_equal(frame, 4)
        try:
            framemean = (np.mean(frame)/255)*100
        except:
            framemean = np.arange(1)
        if framemean > 1:
            pyf = framemean.item()
            intdb[vc]['intensity'].append(pyf)
            with lock:
                c.execute(idstr + 'VALUES (?)', (pyf, ))
    intdb[vc]['filmintensity'] = statistics.mean(intdb[vc]['intensity'])
    cap.release()
    cv2.destroyAllWindows()
    with lock:
        c.execute('INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?)', (countid, imid, intdb[vc]['title'], intdb[vc]['year'], intdb[vc]['length'], intdb[vc]['filmintensity']))
    ityplot(savepath, vc)
    print(f"{intdb[vc]['title']} completed. Runtime was {time.perf_counter() - starttime} seconds.")
    return

if __name__ == '__main__':
    #define globals, retrieve local DB, IMDb
    dbdir = r'C:\\Code\\Other\\NFDB.db'
    NFDB = sqlite3.connect(dbdir)
    c = NFDB.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS movies (id INT, imdbid BIGINT, title VARCHAR[255], year YEAR, length TIME, filmintensity FLOAT(5))''')
    vids = nfdbhelp.get_vids('sample')
    intdb = {}
    im = IMDb()
    c.execute('''SELECT * FROM movies''')
    moviesdb = c.fetchall()
    moviecount = len(moviesdb)
    #multiprocessing setup
    counter = multiprocessing.Value('i', -1)
    p_count = multiprocessing.cpu_count()-1 or 1
    lock = multiprocessing.Lock()
    idcount = len(moviesdb) + 1
    with multiprocessing.Pool(p_count) as p:
        for n in range(len(vids)):
            p.map_async(intensity(dbdir), vids[n], )
    print("Batch complete.")
    c.close()
    NFDB.commit()
    NFDB.close()