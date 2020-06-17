import glob
import cv2
import time
import statistics
import numpy as np
import sqlite3
import matplotlib.pyplot as plt
import os
NFDB = sqlite3.connect('NFDB.db')
c = NFDB.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS movies (id INT, imdbid TEXT, title VARCHAR[255], year YEAR, length TIME, filmintensity FLOAT(5))''')
vids = glob.glob('.\*.avi') + glob.glob('.\*.mkv') + glob.glob('.\*.mp4') + glob.glob('.\*.m4v')
moviecount = 0
intdb = {}
moviesdb = c.execute('''SELECT * FROM movies''')
for row in moviesdb:
    moviecount += 1
for vid in range(len(vids)):
    intdb[vid] = {}
    intdb[vid]['year'] = 0
    end = len(vids[vid])-4
    intdb[vid]['title'] = vids[vid][2:end]
    m1=vids[vid].find('(')
    m2=vids[vid].find('19') or vids[vid].find('20')
    if m1 != -1:
        marker = m1
        intdb[vid]['title'] = vids[vid][2:marker - 1]
        intdb[vid]['year'] = int(vids[vid][marker + 1:marker + 5])
    elif m2 != -1 and isinstance(vids[vid][m2:m2+4], int):     
        marker = m2
        intdb[vid]['title'] = vids[vid][2:marker - 1]
        intdb[vid]['year'] = int(vids[vid][marker:marker + 4])
    ##check if the video has already been scanned
    flag = 1
    if intdb[vid]['title'] in moviesdb:
        if moviesdb['year'] == intdb[vid]['year']:
            print("match in db")
            flag = 0;
            break
    if flag == 0:
        break
    ##continue setting variables
    intdb[vid]['intensity'] = []
    id = moviecount + vid + 1
    strid = "{}".format(id)
    stryear = "{}".format(intdb[vid]['year'])
    ##begin scanning the video
    flag = 1
    try:
        cap = cv2.VideoCapture(vids[vid])
    except:
        flag = 0
    if flag == 0:
        print("CV2 error")
        break
    fc = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(fc)
    fps = cap.get(cv2.CAP_PROP_FPS)
    intdb[vid]['length'] = time.strftime('%H:%M:%S', time.gmtime(fc/fps))
    idstr = 'CREATE TABLE IF NOT EXISTS "' + strid + 'intensity" (intensity FLOAT(5))'
    c.execute(idstr)
    idstr = 'INSERT INTO "' + strid + 'intensity" '
    args = 'Intensity-' + intdb[vid]['title'] + '-' + stryear
    for i in range(fc):
        ret, frame = cap.read()
        frame = np.ma.masked_equal(frame,0)
        try:
            framemean = (np.mean(frame)/255)*100
        except:
            framemean = np.arange(1)
        pyf = framemean.item()
        intdb[vid]['intensity'].append(pyf)
        c.execute(idstr + 'VALUES (?)',(pyf,))
    intdb[vid]['filmintensity'] = statistics.mean(intdb[vid]['intensity'])
    cap.release()
    cv2.destroyAllWindows()
    c.execute('INSERT INTO movies VALUES (?, ?, ?, ?, ?, ?)',(strid, None, intdb[vid]['title'], intdb[vid]['year'], intdb[vid]['length'], intdb[vid]['filmintensity']))
    #save the chart
    plt.plot(intdb[vid]['intensity'])
    plt.title(intdb[vid]['title'] + '-' + intdb[vid]['length'] + '-Intensity')
    plt.ylabel('Intensity/Brightness')
    plt.ylim(0,100)
    plt.xlabel('Frames')
    if not os.path.exists('results'):
        os.makedirs('results')
    plt.savefig(os.path.join('results', args + '.png'), dpi=300)
    plt.clf()
    print(intdb[vid]['title'])
NFDB.commit()
NFDB.close()