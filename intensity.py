"""This script measures the average intensity level of a video file and saves it to a database."""

import time
import statistics
import os
import sqlite3
import glob
import multiprocessing
import numpy as np
import matplotlib.pyplot as plt
from imdb import IMDb
import cv2

def imscan(title, viddc):
    """IMDb tagging"""
    imsearch = im.search_movie(title)
    found = 0
    for imtitle in imsearch:
        if found == 0 and title == imtitle['title']:
            try:
                im.update(imtitle, info=['year'])
                if intdb[viddc]['year'] == int(imtitle['year']):
                    print("matched " + imtitle.movieID)
                    return int(imtitle.movieID)
            except:
                pass
    return

def checkdb(i_v, viddc):
    check_id = 0
    count_id = str(moviecount + viddc + 1)
    if i_v != 0:
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
            print("Entry exists in db.")
            return 1
    except:
        pass
    try:
        with lock:
            c.execute('SELECT * FROM "' + check_id +'intensity"')
        if len(c.fetchall) > 100:
            print("Entry exists in db.")
            return 1
    except:
        pass

    try:
        with lock:
            c.execute('SELECT * FROM "' + count_id +'rgbintensity"')
        if len(c.fetchall) > 100:
            print("Entry exists in db.")
            return 1
    except:
        pass
    return strid_d

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
    if not os.path.exists('results'):
        os.makedirs('results')
    count = 0
    while os.path.exists(f'./results/{ndir}.png'):
        count += 1
        ndir = ndir + str(count)
    try:
        plt.savefig(os.path.join('results', ndir + '.png'), dpi=300)
    except:
        pass
    plt.clf()

def altname(alt_title, alt_year, viddc):
    if vids[viddc].find('(') != -1:
        marker = vids[viddc].find('(')
        alt_title = alt_title[1:alt_title.find('(')-1]
        try:
            alt_year = int(vids[viddc][marker + 1:marker + 5])
        except:
            pass
    elif vids[viddc].find('19') or vids[viddc].find('20') != -1:
        marker = vids[viddc].find('19') or vids[viddc].find('20')
        try:
            alt_year = int(vids[viddc][marker + 2:marker + 6])
        except:
            pass
    print(alt_title, alt_year)
    return alt_title, alt_year

def intensity(id_count):
    #initialize variables
    global counter
    with counter.get_lock():
        counter.value += 1
        vidc = counter.value
    id_count_str = str(id_count + vidc)
    intdb[vidc] = {}
    intdb[vidc]['intensity'] = []
    intdb[vidc]['year'] = 0
    fn_start = vids[vidc].rfind('\\')
    fn_end = len(vids[vidc])-4
    intdb[vidc]['title'] = vids[vidc][fn_start:fn_end]
    intdb[vidc]['title'] = intdb[vidc]['title'].replace ('\\', '') 
    #labeling for DB and checking for duplicates
    intdb[vidc]['title'], intdb[vidc]['year'] = altname(intdb[vidc]['title'], intdb[vidc]['year'], vidc)     
    imid = imscan(intdb[vidc]['title'], vidc)
    if checkdb(imid, vidc) == 1:
        return
    else:
        strid = checkdb(imid, vidc)
    stryear = "{}".format(intdb[vidc]['year'])
    #testing video playback
    cap = vidtest(vids[vidc])
    if cap is None:
        print("CV2 error")
        return
    ##begin scanning the video
    starttime = time.perf_counter()
    fc = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if fc == 0:
        return
    print(f"Video {vidc + 1} of {len(vids)} is called {intdb[vidc]['title']} and has a frame count of {fc}.")
    fps = cap.get(cv2.CAP_PROP_FPS)
    intdb[vidc]['length'] = time.strftime('%H:%M:%S', time.gmtime(fc/fps))    
    idstr = 'CREATE TABLE IF NOT EXISTS "' + strid + 'intensity" (intensity FLOAT(5))'
    with lock:
        c.execute(idstr)
    idstr = 'INSERT INTO "' + strid + 'intensity" '
    savepath = intdb[vidc]['title'] + '-' + strid + '-Intensity'
    for _ in range(fc):
        ret, frame = cap.read()
        frame = np.ma.masked_equal(frame, 0)
        try:
            framemean = (np.mean(frame)/255)*100
        except:
            framemean = np.arange(1)
        pyf = framemean.item()
        intdb[vidc]['intensity'].append(pyf)
        with lock:
            c.execute(idstr + 'VALUES (?)', (pyf, ))
    intdb[vidc]['filmintensity'] = statistics.mean(intdb[vidc]['intensity'])
    cap.release()
    cv2.destroyAllWindows()
    with lock:
        c.execute('INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?)', (id_count_str, imid, intdb[vidc]['title'], intdb[vidc]['year'], intdb[vidc]['length'], intdb[vidc]['filmintensity']))
    ityplot(savepath, vidc)
    print(f"{intdb[vidc]['title']} completed. Runtime was {time.perf_counter() - starttime} seconds.")
    return

if __name__ == '__main__':
    #define globals, retrieve local DB, IMDb
    NFDB = sqlite3.connect('NFDB.db')
    c = NFDB.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS movies (id INT, imdbid BIGINT, title VARCHAR[255], year YEAR, length TIME, filmintensity FLOAT(5))''')
    vids = glob.glob(r'C:\Code\Intensity\*.avi') + glob.glob(r'C:\Code\Intensity\*.mkv') + glob.glob(r'C:\Code\Intensity\*.mp4') + glob.glob(r'C:\Code\Intensity\*.m4v')
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
        for _ in range(len(vids)):
            p.map_async(intensity(idcount), vids[_], )
    print("Batch complete.")
    c.close()
    NFDB.commit()
    NFDB.close()
    