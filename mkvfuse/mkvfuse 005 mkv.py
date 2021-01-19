import os
import glob
from pymkv import MKVFile

v_path = r'\\Penfever2020\Public\Movie Storage\mkvn\$.mkv'
v_path_q = r'\\Penfever2020\Public\Movie Storage\$.mkv'
xml_files = glob.glob(r'\\Penfever2020\Public\mtch\*.xml')
for xml in xml_files:
    print(xml)
    if '(0)' in xml:
        v_title = xml[26:len(xml)-4]
        v_title = v_title.replace( "\\", "" )
    else:
        v_title = xml[27:len(xml)-4] 
    path_temp = v_path_q.replace('$', v_title)
    dest_temp = v_path.replace('$', v_title)
    if not os.path.isfile(path_temp):
        print(f"{path_temp} no video found. Check filetype.")
        continue
    mkv = MKVFile()
    mkv.add_track(path_temp)
    mkv.chapters(xml)
    mkv.mux(dest_temp)
    if not os.path.isfile(dest_temp) or not os.path.getsize(dest_temp) > 256_000_000:
        print("MKVToolnix error: new MKV not saved or may be corrupt.")
        continue
    v_path_x = '\\\Penfever2020\Public\mtch\\' + v_title + ".xml"
    cmd = f"del \"{path_temp}\""
    print(cmd)
    os.system("" + cmd + "")
    cmd = f"del \"{v_path_x}\""
    print(cmd)
    os.system("" + cmd + "")