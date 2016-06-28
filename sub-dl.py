"""
Downloads subtitles from Subscene.
Usage: python sub-dl.py

TODO: Fix renaming.
"""

from bs4 import BeautifulSoup
import sys
import glob
import os
import re
import requests
import zipfile


def soup(link):
    r = requests.get(link)
    
    return BeautifulSoup(r.text, "html.parser")


def find_subtitles(media_name):
    soup_link = soup("https://subscene.com/subtitles/release?q={}/english".format(media_name))
    subtitles = []
    nr = 0
    
    for table_row in soup_link.find_all("tr"):
        subtitle_info = str(table_row)
        if media_name in subtitle_info:
            nr += 1
            subtitles.append(table_row.find_all("a")[0].get("href")) # Subtitle link
            if "<td class=\"a41\">" in subtitle_info:
                print(nr, "(Hearing impaired)")
            else:
                print(nr)

    return subtitles


def find_download_link(sub):
    soup_link = soup("https://subscene.com{}".format(sub))
    
    for link in soup_link.find_all("a"):
        if "download" in str(link): return link.get("href")


def download_subtitle(local_filename, download_link):
    with open(local_filename, 'wb') as f:
        for chunk in download_link.iter_content(chunk_size = 2048): 
            if chunk: f.write(chunk)

            
def unpack_subtitle(file, out_dir):
    with zipfile.ZipFile(file, "r") as zip:
        if os.path.exists("{}\\{}".format(out_dir, zip.namelist()[0])):
            print("Subtitle file overwritten.")
            
        zip.extractall(out_dir)


def handle_multiple_subtitle_files(files):
    for nr, file in enumerate(files, 1):
        if file == files[-1]:
            print("{} {} - NEW".format(nr, file.split("\\")[-1]))
        else:
            print(nr, file.split("\\")[-1])
        
    user_choice = input("Multiple subtitle files detected. Do you wish to delete one? (i\\n): ")
    if user_choice == "n":
        sys.exit("Subtitle downloaded. Nothing renamed or deleted.")
    else:
        os.remove(files[int(user_choice) -1]) # Deletes file
        files.pop(int(user_choice) -1) # Removes file from the list


def rename_file(files):
    for nr, file in enumerate(files):
        if nr == 0:
            name = file[:-4]
        else:
            extension = file[-4:]
            os.rename(file, name + extension)


def main():
    download_directory = "C:\\Users\\Kaarel\\Downloads\\Movies_and_TV\\"
    dirs = [dir for dir in os.listdir(download_directory) if os.path.isdir(download_directory + dir)] # All directories in download directory
    for nr, dir in enumerate(dirs, 1):
        print(nr, dir)
    
    release_name = dirs[int(input("Choose: ")) - 1]
    if release_name[-1] == "]": # Possible release tag
            release_name, tag = release_name.split("[")
            tag = "[{}".format(tag)
    else: tag = ""
    
    subtitles = find_subtitles(release_name) # Find all suitable subtitles
    if len(subtitles) == 0: sys.exit("No subtitles found.")
    sub = subtitles[int(input("Choose a subtitle: ")) -1] # Choose one from suitable subtitles
    
    r = requests.get("https://subscene.com/{}".format(find_download_link(sub)))
    
    destination = "{}subtitle.zip".format(download_directory)
    download_subtitle(destination, r) # Downloads subtitle
    unpack_subtitle(destination, "{}{}{}".format(download_directory, release_name, tag)) # Unpacks the subtitle
    os.remove(destination) # Deletes the subtitle .zip file
    
    files = glob.glob("{}{}{}*\\*".format(download_directory, release_name, tag)) # Find all the files in movie directory
    files.sort(key = os.path.getmtime)
    if len(files) > 2: handle_multiple_subtitle_files(files) # Option to delete unnecessary file
    if len(files) <= 2: rename_file(files) # Unifies movie and subtitle filenames
    
    sys.exit("Done.")

main()