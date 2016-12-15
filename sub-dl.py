#!/usr/bin/env python3

"""
Downloads subtitles from Subscene (https://subscene.com).

Usage:
    ./sub-dl.py [-w]
    -w - Launches VLC with the media file.
"""

from bs4 import BeautifulSoup
from pathlib import Path
import operator
import requests
import sys
import zipfile
import subprocess

def check_media_dir():
    media_dir = Path("/home/kaarel/Downloads/")
    if Path("/media/kaarel/64/").is_dir():
        media_dir = Path("/media/kaarel/64/Media/")
    elif Path("/media/kaarel/32/").is_dir():
        media_dir = Path("/media/kaarel/32/Media/")
    
    sub_extensions = (".sub", ".idx", ".srt")
    
    print("Checking media directory: {}".format(media_dir))
    # Files and subdirs in media dir
    dirs = [x for x in media_dir.iterdir()
            if x.name.count(".") > 2
            and x.name[-4:] not in sub_extensions]
    if not dirs:
        sys.exit("No releases in {}.".format(media_dir))
    
    for nr, dir in enumerate(dirs, 1):
        print("  ({})  {}".format(nr, dir.name))
        
    return dirs, media_dir

def choose_release(dirs, choice):
    if "-" in choice:
        start, end = map(int, choice.split("-"))
    else:
        start, end = int(choice), int(choice)
    
    if start <= 0 or end <= 0 or start > len(dirs):
        sys.exit("You chose a non-existing release. Quit.")
    if end > len(dirs):
        end = len(dirs)    
        
    return dirs[start - 1: end]

def get_soup(link):
    r = requests.get(link)
    
    return BeautifulSoup(r.text, "html.parser")

def check_release_tag(release_name):
    if release_name[-1] == "]": # Possible release tag (e.g. [ettv])
        return release_name.split("[")[0]
        
    return release_name
    
def get_sub_rating(sub_link):
    soup_link = get_soup("https://subscene.com{}".format(sub_link))
    rating = soup_link.find("div", class_ = "rating")
    if rating:
        vote_count = rating.attrs["data-hint"].split()[1]
        return rating.span.text, vote_count
        
    return -1, -1

def find_subs(search_name):
    soup_link = get_soup("https://subscene.com/subtitles/release?q={}".format(search_name))
    subtitles = []
    
    for table_row in soup_link.find_all("tr")[1:]: # Skip first
        sub_info = table_row.find_all("td", ["a1", "a41"]) # a41 == Hearing impaired
        language, release = sub_info[0].find_all("span")

        if language.text.strip() == "English" and release.text.strip() == search_name:
            subtitle_link = sub_info[0].a.get("href")
            
            rating, vote_count = get_sub_rating(subtitle_link)
            if len(sub_info) == 2:
                subtitles.append([subtitle_link, int(rating), int(vote_count), 0])
            else:
                subtitles.append([subtitle_link, int(rating), int(vote_count), 1])

    if not subtitles:
        sys.exit("No subtitles for {} found.".format(search_name))

    return subtitles

def show_available_subtitles(subtitles):
    subtitles = sorted(subtitles, key = operator.itemgetter(3, 1, 2), reverse = True)
    print(" Nr\tRating\tVotes\tHearing impaired")
    for nr, sub in enumerate(subtitles, start = 1):
        if sub[1] == -1:
            sub[1], sub[2] = "N/A", ""
        if sub[3] == 1:
            print(" ({})\t{}\t{}".format(nr, sub[1], sub[2]))
        else:
            print(" ({})\t{}\t{}\tX".format(nr, sub[1], sub[2]))
            
    choice = int(input("Choose a subtitle: ")) - 1
    
    return subtitles[choice][0]

def get_download_link(sub_link):
    soup_link = get_soup("https://subscene.com{}".format(sub_link))
    
    return soup_link.find(id="downloadButton").get("href")

def download_sub(sub_zip, sub_link):
    with open(sub_zip, 'wb') as f:
        for chunk in sub_link.iter_content(chunk_size = 1024):
            if chunk:
                f.write(chunk)

def unpack_sub(sub_zip, download_dir, release_name):
    with zipfile.ZipFile(sub_zip, "r") as zip:
        sub_file = zip.namelist()[0]
        if Path("{}/{}".format(download_dir, release_name)).exists():
            print("Previous subtitle file will be overwritten.")
        zip.extractall(str(download_dir))
        Path("{}/{}".format(download_dir, sub_file)).rename("{}/{}".format(download_dir, release_name))

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-auto": # TODO
        pass
    releases, media_dir = check_media_dir()
    if len(releases) == 1:
        dirs = releases
    else:
        choice = input("Choose a release: ")
        dirs = choose_release(releases, choice)
    
    for release in dirs:
        if release.is_dir():
            download_dir, release_name = release, release.name
        else:
            download_dir, release_name = media_dir, release.stem # Removes extension
              
        search_name = check_release_tag(release_name)
        print("\nSearching subtitles for {}".format(search_name))
        subtitles = find_subs(search_name) # List of tuples
        chosen_sub = show_available_subtitles(subtitles)
        dl_link = get_download_link(chosen_sub)
        sub_link = requests.get("https://subscene.com/{}".format(dl_link))
        sub_zip = "{}/subtitle.zip".format(download_dir)
        download_sub(sub_zip, sub_link)
        unpack_sub(sub_zip, download_dir, release_name + ".srt")
        Path(sub_zip).unlink() # Deletes subtitle.zip

        if len(sys.argv) > 1 and sys.argv[1] == "-w" and release.is_file():
            subprocess.call(["vlc", str(release)])

    sys.exit("Done.")

if __name__ == "__main__":
    main()