import re
import glob
from imdb import IMDb

def makename(full_str):
    vid_title = full_str[full_str.rfind('\\') + 1:len(full_str)-4]
    y_mark = re.search(r"\([12][90]\d\d\)", vid_title)
    if y_mark is not None:
        vid_year = int(vid_title[y_mark.start() + 1: y_mark.start() + 5])
        vid_title = vid_title[:y_mark.start() - 1]
        return vid_title, vid_year, 0
    elif y_mark is None:
        y_mark = re.findall(r"[12][90]\d\d", vid_title)
        if y_mark == 1:
            vid_year = int(y_mark[0])
            vid_title = vid_title[:len(vid_title) - 4]
            return vid_title, vid_year, 1
    vid_title = vid_title.replace ('\\', '')
    vid_year = 0
    return vid_title, vid_year, 2

def get_vids(get_where):
    v_types = ['.avi', '.mp4', '.mkv', '.m4v']
    videos = []
    if get_where is 'local':
        directory_string = r'.\*'
    elif get_where is 'global':
        directory_string = r'\\Penfever2020\Public\Movie Storage\*'
        for _ in v_types:
            videos.extend(glob.glob(f'{directory_string}{_}'))
        directory_string = r'\\Penfever2020\Public\Movie Storage\**\*'
        for _ in v_types:
            videos.extend(glob.glob(f'{directory_string}{_}', recursive=True))
        return videos
    elif get_where is 'sample':
        directory_string = r'\\Penfever2020\\10TB-Main\test_set\*'
    else:
        return False
    for _ in v_types:
        videos.extend(glob.glob(f'{directory_string}{_}'))
    return videos

def imscan(title, year, vidc, v_code, v_length):
    """IMDb tagging"""
    if v_code != 2:
        im = IMDb()
        imsearch = im.search_movie(title)
        for imtitle in imsearch:
            if title == imtitle['title']:
                try:
                    im.update(imtitle, info=['year'])
                    if year == int(imtitle['year']):
                        return int(imtitle.movieID), 0
                except:
                    return 0, 0
    else:
        v_length = str(v_length)
        im = IMDb()
        imsearch = im.search_movie(title)
        for imtitle in imsearch:
            im.update(imtitle, info=['technical', 'year'])
            try:
                if v_length in str(imtitle['technical']['runtime']):
                    return int(imtitle.movieID), str(imtitle['year'])
            except:
                return 0, 0
    return 0, 0
