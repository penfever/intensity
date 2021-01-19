import os
import glob
from pymkv import MKVFile

v_path = r'\\Penfever2020\Public\Movie Storage\$.avi'
xml_files = glob.glob(r'\\Penfever2020\Public\mtch\*.xml')
for xml in xml_files:
    v_title = xml[27:len(xml)-4]
    path_temp = glob.glob(v_path.replace('$', v_title))
    dest_temp = v_path.replace('$.avi', v_title + ".mkv")
    for line in path_temp:
        if v_title in line:
            mkv = MKVFile()
            mkv.add_track(line)
            mkv.chapters(xml)
            mkv.mux(dest_temp)
            if not os.path.isfile(dest_temp) or not os.path.getsize(dest_temp) > 128_000_000:
                print("MKVToolnix error: new MKV not saved or may be corrupt.")
                continue
            v_path_q = '\\\Penfever2020\Public\Movie Storage\\' + v_title + ".avi"
            v_path_x = '\\\Penfever2020\Public\mtch\\' + v_title + ".xml"
            cmd = f"del \"{v_path_q}\""
            print(cmd)
            os.system("" + cmd + "")
            cmd = f"del \"{v_path_x}\""
            print(cmd)
            os.system("" + cmd + "")