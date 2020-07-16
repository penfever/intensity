#This script measures the average RGB intensity level of a video file and saves it to a database.

import time
import statistics
import os
import glob
import sqlite3
import multiprocessing
from imdb import IMDb
import nfdbhelp
import numpy as np
import matplotlib.pyplot as plt
import cv2

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

def ityplot(ndir, vidc, imid_b):
    """Draws and saves the chart"""
    plt.plot(intdb[vidc]['g_intensity'], color="Green", linewidth=.25, label = "Green Intensity")
    plt.plot(intdb[vidc]['r_intensity'], color="Red", linewidth=.25, label = "Red Intensity")
    plt.plot(intdb[vidc]['b_intensity'], color="Blue", linewidth=.25, label = "Blue Intensity")
    plt.title(intdb[vidc]['title'] + '-' + str(imid_b) + '-RGBIntensity')
    plt.ylabel('Intensity/Brightness')
    plt.ylim(0, 100)
    plt.xlabel('Frames')
    if not os.path.exists('results'):
        os.makedirs('results')
    count = 0
    while os.path.exists(f'./results/{ndir}.png'):
        count += 1
        ndir = ndir + '-' + str(count)
    try:
        plt.savefig(os.path.join('results', ndir + '.png'), dpi=300)
    except:
        pass
    plt.clf()

def checkcolor(vidc, cappy):
    ret_sm, frame_sm = cappy.read(cv2.IMREAD_UNCHANGED)
    if frame_sm is None:
        return False
    if(len(frame_sm.shape)<3):
        return False
    total_frames = cappy.get(7)
    cappy.set(1, 5000)
    r_framemean_sm_tot, g_framemean_sm_tot, b_framemean_sm_tot = [], [], []
    for _ in range(250):
        ret_sm, frame_sm = cappy.read(cv2.IMREAD_UNCHANGED)
        r_framemean_sm = (np.mean(frame_sm[:, :, 0])/255)*100
        r_framemean_sm_tot.append(r_framemean_sm)
        g_framemean_sm = (np.mean(frame_sm[:, :, 1])/255)*100
        g_framemean_sm_tot.append(g_framemean_sm)
        b_framemean_sm = (np.mean(frame_sm[:, :, 2])/255)*100
        b_framemean_sm_tot.append(r_framemean_sm)
    cappy.set(1, 8000)
    for _ in range(250):
        ret_sm, frame_sm = cappy.read(cv2.IMREAD_UNCHANGED)
        r_framemean_sm = (np.mean(frame_sm[:, :, 0])/255)*100
        r_framemean_sm_tot.append(r_framemean_sm)
        g_framemean_sm = (np.mean(frame_sm[:, :, 1])/255)*100
        g_framemean_sm_tot.append(g_framemean_sm)
        b_framemean_sm = (np.mean(frame_sm[:, :, 2])/255)*100
        b_framemean_sm_tot.append(r_framemean_sm)

    print(r_framemean_sm, g_framemean_sm, b_framemean_sm)
    if abs(statistics.mean(r_framemean_sm_tot) - statistics.mean(g_framemean_sm_tot)) < .5 and abs(statistics.mean(g_framemean_sm_tot) - statistics.mean(b_framemean_sm_tot)) < .5:
        return False
    return True

def rgbintensity():

    #define global vars
    global counter
    with counter.get_lock():
        counter.value += 1
        vc = counter.value

    #define local vars
    intdb[vc] = {}
    intdb[vc]['r_intensity'] = []
    intdb[vc]['g_intensity'] = []
    intdb[vc]['b_intensity'] = []

    #name the video
    intdb[vc]['title'], intdb[vc]['year'], code = nfdbhelp.makename(vids[n])

    #check video stream
    cap = vidtest(vids[vc])
    if checkcolor(vc, cap) is False:
        print(f"{intdb[vc]['title']} is not in color or video stream cannot be read. Skipping.")
        return
    fc = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if fc == 0:
        return
    fps = cap.get(cv2.CAP_PROP_FPS)
    intdb[vc]['length'] = time.strftime('%H:%M:%S', time.gmtime(fc/fps))

    #IMDb checks
    imid = 0
    if code != 2:
        imid, vac = nfdbhelp.imscan(intdb[vc]['title'], intdb[vc]['year'], vc, 0, 0)
    if code == 2:
        frame_time = int(((fc/fps)/60))
        imid, intdb[vc]['year'] = nfdbhelp.imscan(intdb[vc]['title'], intdb[vc]['year'], vc, 2, frame_time)
    if imid == 0:
        imid = moviecount + vc + 1
        print("No IMDb match found.")

    #check for DB match
    strid = "{}".format(imid)
    try:
        with lock:
            c.execute('SELECT * FROM "' + strid +'rgbintensity"')
        if len(c.fetchall) > 100:
            print("Table exists. Skipping.")
            return False
    except:
        pass

    #begin main function
    print(f"Video {vc + 1} of {len(vids)} is called {intdb[vc]['title']} and has a frame count of {fc}.")
    print(f"IMDb ID is {imid}.\n")
    starttime = time.perf_counter()
    idstr = 'CREATE TABLE IF NOT EXISTS "' + strid + 'rgbintensity" (r_intensity FLOAT(5), g_intensity FLOAT(5), b_intensity FLOAT(5))'
    with lock:
        c.execute(idstr)
    idstr = 'INSERT INTO "' + strid + 'rgbintensity" '
    savepath = intdb[vc]['title'] + '-' + str(imid) + '-rgbintensity'
    for _ in range(fc):
        ret, frame = cap.read()
        if frame is None:
            frame = np.arange(1)
        frame = np.ma.masked_less_equal(frame, 4)
        try:
            r_framemean = (np.mean(frame[:, :, 0])/255)*100
            g_framemean = (np.mean(frame[:, :, 1])/255)*100
            b_framemean = (np.mean(frame[:, :, 2])/255)*100
        except:
            r_framemean = np.arange(1)
            g_framemean = np.arange(1)
            b_framemean = np.arange(1)
        if r_framemean > 1 and g_framemean > 1 and b_framemean > 1:
            r_pyf = r_framemean.item()
            intdb[vc]['r_intensity'].append(r_pyf)
            g_pyf = g_framemean.item()
            intdb[vc]['g_intensity'].append(g_pyf)
            b_pyf = b_framemean.item()
            intdb[vc]['b_intensity'].append(b_pyf)
            with lock:
                c.execute(idstr + 'VALUES (?, ?, ?)', (r_pyf, g_pyf, b_pyf))
    intdb[vc]['r_filmintensity'] = statistics.mean(intdb[vc]['r_intensity'])
    intdb[vc]['g_filmintensity'] = statistics.mean(intdb[vc]['g_intensity'])
    intdb[vc]['b_filmintensity'] = statistics.mean(intdb[vc]['b_intensity'])
    idstr = 'CREATE TABLE IF NOT EXISTS "' + strid + 'rgbfilmintensity" (imdbid TEXT, r_filmintensity FLOAT(5), g_filmintensity FLOAT(5), b_filmintensity FLOAT(5))'
    with lock:
        c.execute(idstr)
        c.execute('INSERT INTO "' + strid + 'rgbfilmintensity" ' + 'VALUES (?, ?, ?, ?)', (str(imid), intdb[vc]['r_filmintensity'], intdb[vc]['g_filmintensity'], intdb[vc]['b_filmintensity']))
    cap.release()
    cv2.destroyAllWindows()
    ityplot(savepath, vc, imid)
    print(f"{intdb[vc]['title']} completed. Runtime was {time.perf_counter() - starttime} seconds.")
    return

if __name__ == '__main__':
    #multiprocessing, counter, local database
    counter = multiprocessing.Value('i', -1)
    NFDB = sqlite3.connect('NFDB.db')
    c = NFDB.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS movies (id INT, imdbid BIGINT, title VARCHAR[255], year YEAR, length TIME, filmintensity FLOAT(5))''')
    vids = nfdbhelp.get_vids('sample')
    if vids is False:
        print("That is not a valid directory.")
        exit(code=1)
    intdb = {}
    c.execute('''SELECT * FROM movies''')
    moviesdb = c.fetchall()
    moviecount = len(moviesdb)
    p_count = multiprocessing.cpu_count()-1 or 1
    lock = multiprocessing.Lock()
    with multiprocessing.Pool(p_count, initargs=(lock,)) as p:
        for n in range(len(vids)):
            p.map_async(rgbintensity(), vids[n], )
    print("Batch complete.")
    c.close()
    NFDB.commit()
    NFDB.close()
    