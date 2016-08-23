"""
Downloads subtitles from Subscene (https://subscene.com).

Usage: python sub-dl.py [-w]
-w - Launches VLC with the media file.

TODO: Show alternatives when subtitle for the exact release is not found.
"""

from bs4 import BeautifulSoup
from pathlib import Path
import requests
import sys
import zipfile
import watch

def choose_release(choice):
    if "-" in choice:
        start, end = choice.split("-")
    else:
        start, end = choice, choice
    return (int(start) - 1, int(end))

def soup(link):
    r = requests.get(link)
    return BeautifulSoup(r.text, "html.parser")

def check_release_tag(release_name):
    if str(release_name)[-1] == "]": # Possible release tag (e.g. [ettv])
        return str(release_name).split("[")[0]
    return str(release_name)

def find_subtitles(media_name):
    soup_link = soup("https://subscene.com/subtitles/release?q={}".format(media_name))
    subtitles = []
    nr = 0

    for table_row in soup_link.find_all("tr"):
        subtitle_info = str(table_row)
        if media_name in subtitle_info and "English" in subtitle_info: # Release name and language
            nr += 1
            subtitles.append(table_row.find_all("a")[0].get("href")) # Subtitle link
            if "<td class=\"a41\">" in subtitle_info:
                print("{} (Hearing impaired)".format(nr))
            else:
                print("{}".format(nr))      
    if len(subtitles) == 0:
            sys.exit("No subtitles for {} found.".format(media_name))
    return subtitles

def find_download_link(sub):
    soup_link = soup("https://subscene.com{}".format(sub))

    for link in soup_link.find_all("a"):
        if "download" in str(link):
            return link.get("href")

def download_subtitle(local_filename, download_link):
    with open(local_filename, 'wb') as f:
        for chunk in download_link.iter_content(chunk_size = 2048):
            if chunk: f.write(chunk)

def unpack_subtitle(file, out_dir, release_name):
    with zipfile.ZipFile(file, "r") as zip:
        sub_file = zip.namelist()[0]
        if Path("{}\\{}".format(out_dir, sub_file)).exists():
            print("Subtitle file overwritten.")
        zip.extractall(str(out_dir))
        Path("{}\\{}".format(out_dir, sub_file)).rename("{}\\{}.srt".format(out_dir, release_name))

def main():
    media_dir = Path("C:\\Users\\Kaarel\\Downloads\\Media\\")
    if Path("F:\\").is_dir():
        media_dir = Path("F:\\")
        
    print("Checking media directory: {}\n".format(media_dir))
    dirs = [x for x in media_dir.iterdir()] # All files and subdirs in media dir
    if len(dirs) == 0:
        sys.exit("Nothing in media directory.")
    dirs.sort()
    for nr, dir in enumerate(dirs, 1):
        print("{}  {}".format(nr, dir.name))

    choice = input("\nChoose a release: ")
    start, end = choose_release(choice)
    
    for release in range(start, end):
        download_directory, release_name = dirs[release], dirs[release].name
        search_name = check_release_tag(release_name)
        
        if not download_directory.is_dir():
            download_directory = media_dir
            release_name = ".".join(release_name.split(".")[0:-1]) # Removes extension
            search_name = check_release_tag(release_name)
        
        print("\nSearching subtitles for {}".format(search_name))
        subtitles = find_subtitles(search_name) # List of all suitable subtitles
        sub = subtitles[int(input("\nChoose a subtitle: ")) -1] # Choose one from suitable subtitles

        dl_link = find_download_link(sub)
        r = requests.get("https://subscene.com/{}".format(dl_link))
        sub_file = "{}\\subtitle.zip".format(download_directory)
        download_subtitle(sub_file, r)
        unpack_subtitle(sub_file, download_directory, release_name)
        Path(sub_file).unlink() # Deletes subtitle.zip

        if len(sys.argv) > 1 and sys.argv[1] == "-w":
            watch.launch_vlc(files[0])

    sys.exit("Done.")

main()