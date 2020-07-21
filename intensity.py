"""This script measures the average intensity level of a video file and saves it to a database."""

import time
import statistics
import os
import sqlite3
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
    while len(intdb[viddc]['intensity']) < len(intdb[viddc]['contrast']):
        intdb[viddc]['contrast'].append(0)
    while len(intdb[viddc]['contrast']) < len(intdb[viddc]['intensity']):
        intdb[viddc]['intensity'].append(0)
    plt.plot(intdb[viddc]['contrast'], color='Brown', label = "Contrast", linewidth=.25)
    plt.plot(intdb[viddc]['intensity'], label = "Intensity", linewidth=.25)
    plt.title(intdb[viddc]['title'] + '-' + intdb[viddc]['length'] + '-Intensity')
    plt.ylabel('Intensity/Contrast')
    plt.ylim(0, 100)
    plt.xlabel('Frames')
    _ = 0
    if os.path.exists(ndir):
        print("Old chart deleted.")
        os.remove(ndir)
    plt.savefig(ndir, dpi=300)
    print("New chart saved.")
    # except:
    #    print("Chart could not be saved.")
    plt.clf()

def checkcolor(vidc, cappy):
    ret_sm, frame_sm = cappy.read(cv2.IMREAD_UNCHANGED)
    if frame_sm is None:
        return False
    if len(frame_sm.shape) < 3:
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

    if abs(statistics.mean(r_framemean_sm_tot) - statistics.mean(g_framemean_sm_tot)) < .5 and abs(statistics.mean(g_framemean_sm_tot) - statistics.mean(b_framemean_sm_tot)) < .5:
        return False
    return True

def intensity():
    #initialize variables
    global counter
    with counter.get_lock():
        counter.value += 1
        vc = counter.value
    countid = moviecount + vc + 1
    intdb[vc] = {}
    intdb[vc]['intensity'] = []
    intdb[vc]['contrast'] = []
    #labeling for DB and checking for duplicates
    intdb[vc]['title'], intdb[vc]['year'], code = nfdbhelp.makename(vids[n])
    if code != 2:
        imid, _ = nfdbhelp.imscan(intdb[vc]['title'], intdb[vc]['year'], vc, 0, 0)
    else:
        print("No IMDb match found. Using local count.")
        imid = 0
        strid = str(countid)
    if checkdb(imid, vc) == 'False':
        print("Table already exists. Skipping.")
        return
    #testing video playback
    cap = vidtest(vids[vc])
    if cap is None:
        print("CV2 error. Skipping title.")
        return
    #check for color
    bwflag = False
    if checkcolor(vc, cap) is False:
        print(f"{intdb[vc]['title']} is not in color.")
        bwflag = True
    elif checkcolor(vc, cap) is True:
        print(f"{intdb[vc]['title']} is in color.")
        intdb[vc]['r_intensity'] = []
        intdb[vc]['g_intensity'] = []
        intdb[vc]['b_intensity'] = []
        try:
            with lock:
                c.execute('SELECT * FROM "' + str(imid) +'rgbintensity"')
            if len(c.fetchall) > 100:
                print("Color table exists in DB. Skipping color processing.")
                bwflag = True
        except:
            pass
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
    with lock:
        if bwflag is False:
            c.execute('CREATE TABLE IF NOT EXISTS "' + strid + 'rgbintensity" (r_intensity FLOAT(5), g_intensity FLOAT(5), b_intensity FLOAT(5))')
            c.execute('CREATE TABLE IF NOT EXISTS "' + strid + 'rgbfilmintensity" (imdbid TEXT, r_filmintensity FLOAT(5), g_filmintensity FLOAT(5), b_filmintensity FLOAT(5))')
        c.execute('CREATE TABLE IF NOT EXISTS "' + strid + 'intensity" (intensity FLOAT(5), contrast FLOAT(10), cont_max INT, cont_min INT)')
    savepath = r'C:\\Code\\Other\\intensity_charts\\'
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    savepath = savepath + intdb[vc]['title'] + '-' + str(imid) + '-Intensity.png'
    for _ in range(fc):
        ret, frame = cap.read()
        if frame is None:
            continue
        if bwflag is True:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if np.ndim(frame) == 3:
            rev_fr = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            rev_fr = frame
        rev_fr = np.reshape(rev_fr, rev_fr.size)
        diff_fr = float(np.mean(np.diff(rev_fr))/2.56)
        con_max = len(np.where(rev_fr < 50)) / rev_fr.size
        con_min = len(np.where(rev_fr > 205)) / rev_fr.size
        intdb[vc]['contrast'].append(diff_fr)
        frame = np.ma.masked_less_equal(frame, 3)
        if bwflag is False:
            try:
                r_framemean = (np.mean(frame[:, :, 0])/2.56)
                g_framemean = (np.mean(frame[:, :, 1])/2.56)
                b_framemean = (np.mean(frame[:, :, 2])/2.56)
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
            else:
                intdb[vc]['r_intensity'].append(0)
                intdb[vc]['g_intensity'].append(0)
                intdb[vc]['b_intensity'].append(0)
                with lock:
                    c.execute('INSERT INTO "' + strid + 'rgbintensity" VALUES (?, ?, ?)', (r_pyf, g_pyf, b_pyf))
        try:
            framemean = (np.mean(frame)/2.56)
        except:
            framemean = np.arange(1)
        if framemean > 1:
            pyf = framemean.item()
            intdb[vc]['intensity'].append(pyf)
            with lock:
                c.execute('INSERT INTO "' + strid + 'intensity" VALUES (?, ?, ?, ?)', (pyf, diff_fr, con_max, con_min))
        else:
            intdb[vc]['intensity'].append(0)
    intdb[vc]['filmintensity'] = statistics.mean(intdb[vc]['intensity'])
    intdb[vc]['filmaverage'] = statistics.mean(intdb[vc]['contrast'])
    print("Film average contrast was {} percent, average intensity was {} percent.".format(intdb[vc]['filmaverage'], intdb[vc]['filmintensity']))
    if bwflag is False:
        intdb[vc]['r_filmintensity'] = statistics.mean(intdb[vc]['r_intensity'])
        intdb[vc]['g_filmintensity'] = statistics.mean(intdb[vc]['g_intensity'])
        intdb[vc]['b_filmintensity'] = statistics.mean(intdb[vc]['b_intensity'])
        print("RGB intensity calculated.")
        with lock:
            c.execute('INSERT INTO "' + strid + 'rgbfilmintensity" ' + 'VALUES (?, ?, ?, ?)', (str(imid), intdb[vc]['r_filmintensity'], intdb[vc]['g_filmintensity'], intdb[vc]['b_filmintensity']))
    cap.release()
    cv2.destroyAllWindows()
    with lock:
        c.execute('INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?, ?)', (countid, imid, intdb[vc]['title'], intdb[vc]['year'], intdb[vc]['length'], intdb[vc]['filmintensity'], intdb[vc]['filmaverage']))
    ityplot(savepath, vc)
    print(f"{intdb[vc]['title']} completed. Runtime was {time.perf_counter() - starttime} seconds.")
    return

if __name__ == '__main__':
    #define globals, retrieve local DB, IMDb
    dbdir = r'C:\\Code\\Other\\NFDB.db'
    if not os.path.isfile(dbdir):
        with open(f'{dbdir}', 'w+'): pass
    NFDB = sqlite3.connect(dbdir)
    c = NFDB.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS movies (id INT, imdbid BIGINT, title VARCHAR[255], year YEAR, length TIME, filmintensity FLOAT(5), filmcontrast FLOAT(5))''')
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
            p.map_async(intensity(), vids[n], )
    print("Batch complete.")
    c.close()
    NFDB.commit()
    NFDB.close()