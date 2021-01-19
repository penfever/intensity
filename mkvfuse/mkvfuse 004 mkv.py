import os
import glob
from pymkv import MKVFile

v_path = r'\\Penfever2020\Public\Movie Storage\mkvn\$.mkv'
v_path_q = r'\\Penfever2020\Public\Movie Storage\$.mkv'
xml_files = glob.glob(r'\\Penfever2020\Public\mtch\*.xml')
for xml in xml_files:
    v_title = xml[27:len(xml)-4]
    path_temp = v_path_q.replace('$', v_title)
    print(path_temp)
    dest_temp = v_path.replace('$', v_title)
    print(dest_temp)
    for line in path_temp:
        if v_title in line:
            if not os.path.isfile(path_temp):
                print("No video found. Check filetype.")
                continue
            mkv = MKVFile()
            mkv.add_track(line)
            mkv.chapters(xml)
            mkv.mux(dest_temp)
            if not os.path.isfile(dest_temp):
                print("MKVToolnix error: new MKV not saved.")
                continue
            v_path_x = '\\\Penfever2020\Public\mtch\\' + v_title + ".xml"
            cmd = f"del \"{v_path_q}\""
            print(cmd)
            os.system("" + cmd + "")
            cmd = f"del \"{v_path_x}\""
            print(cmd)
            os.system("" + cmd + "")