#!/usr/bin/env python3

"""
Downloads subtitles from Subscene (https://subscene.com).

Usage:
    ./sub-dl.py [-w]
    -w - Launches VLC with the media file.
"""

from bs4 import BeautifulSoup
from pathlib import Path
import requests
import sys
import zipfile
import watch

def check_media_dir():
    media_dir = Path("/home/kaarel/Downloads/")
    if Path("/media/kaarel/64/").is_dir():
        media_dir = Path("/media/kaarel/64/")
    elif Path("/media/kaarel/32/").is_dir():
        media_dir = Path("/media/kaarel/32/")
    
    print("Checking media directory: {}".format(media_dir))
    dirs = [x for x in media_dir.iterdir() if str(x).count(".") > 2] # Files and subdirs in media dir
    if len(dirs) == 0:
        sys.exit("No releases in {}.".format(media_dir))
    dirs.sort()
    
    for nr, dir in enumerate(dirs, 1):
        print("  {}  {}".format(nr, dir.name))
        
    return dirs, media_dir

def choose_release(dirs, choice):
    if "-" in choice:
        start, end = choice.split("-")
    else:
        start, end = choice, choice
        
    return dirs[int(start) - 1: int(end)]

def soup(link):
    r = requests.get(link)
    
    return BeautifulSoup(r.text, "html.parser")

def check_release_tag(release_name):
    if release_name[-1] == "]": # Possible release tag (e.g. [ettv])
        return release_name.split("[")[0]
        
    return release_name

def find_subtitles(media_name):
    soup_link = soup("https://subscene.com/subtitles/release?q={}".format(media_name))
    subtitles = {}
    nr = 0

    for table_row in soup_link.find_all("tr"):
        subtitle_info = str(table_row)
        if media_name in subtitle_info and "English" in subtitle_info: # Release name and language
            nr += 1
            subtitles[nr] = table_row.find_all("a")[0].get("href") # Subtitle link
            if "<td class=\"a41\">" in subtitle_info:
                print(" {} (Hearing impaired)".format(nr))
            else:
                print(" {}".format(nr))
    if len(subtitles) == 0:
        sys.exit("No subtitles for {} found.".format(media_name))
        
    return subtitles

def find_download_link(sub):
    soup_link = soup("https://subscene.com{}".format(sub))

    for link in soup_link.find_all("a"):
        if "download" in str(link):
            return link.get("href")

def download_subtitle(subtitle_zip, download_link):
    with open(subtitle_zip, 'wb') as f:
        for chunk in download_link.iter_content(chunk_size = 1024):
            if chunk:
                f.write(chunk)

def unpack_subtitle(sub_file, out_dir, release_name):
    release_name += ".srt"
    with zipfile.ZipFile(sub_file, "r") as zip:
        sub_file = zip.namelist()[0]
        if Path("{}/{}".format(out_dir, release_name)).exists():
            print("Previous subtitle file will be overwritten.")
        zip.extractall(str(out_dir))
        Path("{}/{}".format(out_dir, sub_file)).rename("{}/{}".format(out_dir, release_name))

def main():
    releases, media_dir = check_media_dir()
    choice = input("Choose a release: ")
    dirs = choose_release(releases, choice)
    
    for release in dirs:
        if release.is_dir():
            download_directory, release_name = release, release.name
        else:
            download_directory = media_dir
            release_name = ".".join(release.name.split(".")[0:-1]) # Removes extension
              
        search_name = check_release_tag(release_name)
        print("\nSearching subtitles for {}".format(search_name))
        subtitles = find_subtitles(search_name) # Dict of all suitable subtitles
        choice = int(input("Choose a subtitle: "))
        dl_link = find_download_link(subtitles[choice])
        r = requests.get("https://subscene.com/{}".format(dl_link))
        sub_file = "{}/subtitle.zip".format(download_directory)
        download_subtitle(sub_file, r)
        unpack_subtitle(sub_file, download_directory, release_name)
        Path(sub_file).unlink() # Deletes subtitle.zip

        if len(sys.argv) > 1 and sys.argv[1] == "-w":
            watch.launch_vlc(str(release))

    sys.exit("Done.")

main()