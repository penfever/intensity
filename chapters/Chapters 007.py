"""Scans the network drive to determine which video files are missing chapters"""
import os
import os.path
import glob
import time
import shutil
import requests
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

def xfile():
    dest_xml = r'\\Penfever2020\Public\cdb\\'
    dest_xml = dest_xml + f'{v_title} ({v_year}).xml'
    if not os.path.isfile(dest_xml):
        r_xml = requests.post(f"{xml}")
        r_xml.raise_for_status()
        encoding = guess_encoding()
        r_xml = text_bytes.decode(encoding, errors='replace').replace('\uFFFD', '')           
        with open (dest_xml, 'w') as f:
            f.write(r_xml.text)
        return 0
    print("File exists.")
    return 1

def copyfile():
    v_path = r'\\Penfever2020\Public\Movie Storage\&*.avi'
    path_temp = glob.glob(v_path.replace('&', v_title))
    dest_temp = dest + v_title + ".avi"
    if not os.path.isfile(dest_temp):
        shutil.copy2(path_temp[0], dest_temp)
    xml_files = glob.glob(r"C:\Users\user\Downloads\*.xml")
    for file in xml_files:
        shutil.copy2(file, dest)

def scanfiles():
    m_path = r'\\Penfever2020\Public\Movie Storage\*.avi'
    return glob.glob(m_path)
    #MKVinfo needed here

def altname(alt_title, alt_year):
    if vids[vc].find('(') != -1:
        marker = vids[vc].find('(')
        alt_title = alt_title[:alt_title.find('(')-1]
        try:
            alt_year = int(vids[vc][marker + 1:marker + 5])
        except:
            pass
    elif vids[vc].find('19') or vids[vc].find('20') != -1:
        marker = vids[vc].find('19') or vids[vc].find('20')
        try:
            alt_year = int(vids[vc][marker + 2:marker + 6])
        except:
            pass
    print(alt_title, alt_year)
    return alt_title, alt_year

#Downloads the needed chapter xml files
#imports, defining globals
vids = scanfiles()
driver = webdriver.Chrome()
driver.get('http://chapterdb.plex.tv/browse')
vc = -1
dest = r"C:\Users\user\Documents\Code\Chapters\\"
for vid in tqdm(enumerate(vids)):
    #local vars
    vc += 1
    #naming
    fn_start = vids[vc].rfind('\\')
    fn_end = len(vids[vc])-4
    if vids[vc][fn_end].isspace is False:
        fn_end = fn_end - 1
    print(vids[vc][fn_start:fn_end])
    v_title = vids[vc][fn_start:fn_end]
    v_title = v_title.replace ('\\', '')
    v_title = v_title.replace (',', '') 
    v_year = 0
    #alternate naming method
    v_title, v_year = altname(v_title, v_year)
    #browse to and download the file
    chdb_search = driver.find_element_by_name('Criteria.Title')
    chdb_search.send_keys(f'{v_title}')
    chdb_search.send_keys(Keys.ENTER)
    time.sleep(3)
    xpath = r"//*[contains(@href, 'browse/')]"
    chdb_entry = driver.find_elements(By.XPATH, xpath)
    if not chdb_entry:
        print(f"{v_title} Chapter file not found.")
        driver.get('http://chapterdb.plex.tv/browse')
        continue
    chdb_entry[0].click()
    xml = driver.current_url + ".xml"
    if xfile() == 0:
        print(f"{v_title} Chapter file saved.")
    driver.get('http://chapterdb.plex.tv/browse')
