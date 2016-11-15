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
    # Files and subdirs in media dir
    dirs = [x for x in media_dir.iterdir() if x.name.count(".") > 2 and x.name[-4:] != ".srt"]
    if not dirs:
        sys.exit("No releases in {}.".format(media_dir))
    
    for nr, dir in enumerate(dirs, 1):
        print("  ({})  {}".format(nr, dir.name))
        
    return dirs, media_dir

def choose_release(dirs, choice):
    if "-" in choice:
        start, end = choice.split("-")
    else:
        start, end = choice, choice
   
    start, end = map(int, (start, end))

    if end > len(dirs):
        end = len(dirs)
    if start > len(dirs):
        sys.exit("You chose a non-existing release. Quit.")
        
    return dirs[start - 1: end]

def soup(link):
    r = requests.get(link)
    
    return BeautifulSoup(r.text, "html.parser") # Try "lxml"

def check_release_tag(release_name):
    if release_name[-1] == "]": # Possible release tag (e.g. [ettv])
        return release_name.split("[")[0]
        
    return release_name
    
def get_sub_rating(sub_link):
    soup_link = soup("https://subscene.com{}".format(sub_link))
    rating = soup_link.find("div", class_ = "rating")
    if rating:
        return rating.span.text
        
    return "N/A"

def find_subtitles(media_name):
    soup_link = soup("https://subscene.com/subtitles/release?q={}".format(media_name))
    subtitles = {}
    nr = 0

    for table_row in soup_link.find_all("tr")[1:]: # Skip first
        sub_info = table_row.find_all("td", ["a1", "a41"]) # a41 == Hearing impaired
        language, release = sub_info[0].find_all("span")

        if language.text.strip() == "English" and release.text.strip() == media_name:
            nr += 1
            subtitle_link = sub_info[0].a.get("href")
            subtitles[nr] = subtitle_link
            rating = get_sub_rating(subtitle_link)
            if len(sub_info) == 2:
                print(" ({})  Rating: {:>3}  (Hearing impaired)".format(nr, rating))
            else:
                print(" ({})  Rating: {:>3}".format(nr, rating))
                
    if not subtitles:
        sys.exit("No subtitles for {} found.".format(media_name))
        
    return subtitles

def find_download_link(sub_link):
    soup_link = soup("https://subscene.com{}".format(sub_link))
    
    return soup_link.find(id="downloadButton").get("href")

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
            download_dir, release_name = release, release.name
        else:
            download_dir = media_dir
            release_name = ".".join(release.name.split(".")[0:-1]) # Removes extension
              
        search_name = check_release_tag(release_name)
        print("\nSearching subtitles for {}".format(search_name))
        subtitles = find_subtitles(search_name) # Dict of all suitable subtitles
        choice = int(input("Choose a subtitle: "))
        try:
            dl_link = find_download_link(subtitles[choice])
        except KeyError:
            sys.exit("You chose a non-existing subtitle. Quit.")
        r = requests.get("https://subscene.com/{}".format(dl_link))
        sub_file = "{}/subtitle.zip".format(download_directory)
        download_subtitle(sub_file, r)
        unpack_subtitle(sub_file, download_dir, release_name)
        Path(sub_file).unlink() # Deletes subtitle.zip

        if len(sys.argv) > 1 and sys.argv[1] == "-w":
            watch.launch_vlc(release.name)

    sys.exit("Done.")

if __name__ == "__main__":
    main()