#!/usr/bin/env python3

"""Download subtitles from Subscene (https://subscene.com).
   Author: https://github.com/krlk89/sub_dl
"""

import time
import config
import logger  # TODO
import argparse
import os
import sys
from pathlib import Path
import re
import operator
import zipfile
import subprocess
try:
    from fake_useragent import UserAgent
    from bs4 import BeautifulSoup
    import requests
except ImportError:
    sys.exit("Missing dependencies. Type 'pip install -r requirements.txt' to install them.")


def parse_arguments():
    """Parse command line arguments. All are optional."""
    parser = argparse.ArgumentParser(description = "sub_dl: Subscene subtitle downloader.")
    parser.add_argument("-c", "--config", action = "store_true", help = "configure your media directory and subtitle language")
    parser.add_argument("-l", "--language", help = "specify desired subtitle language (overrules default which is English)", type = str, default = "English")
    parser.add_argument("-a", "--auto", action = "store_true", help = "automatically choose best-rated non hearing-impaired subtitle")
    parser.add_argument("-w", "--watch", action = "store_true", help = "launch VLC after downloading subtitles")

    return parser.parse_args()


def is_tv_series(release_name):
    """Check if release is a tv show. If yes then fallback search shows only subtitles for the right episode."""
    match = re.search("\.S\d{2}E\d{2}\.", release_name, re.IGNORECASE)
    if match:
        return match.group().lower()
    
    return ""


def check_media_dir(media_dir):
    """Return a list of releases inside the media directory."""
    sub_extensions = (".sub", ".idx", ".srt")

    print("Checking media directory: {}".format(media_dir))
    # Files and release dirs in media dir
    dirs = [x for x in media_dir.iterdir()
            if x.suffix not in sub_extensions]
    if not dirs:
        sys.exit("No releases in {}.".format(media_dir))
    
    dirs.sort()
    for nr, release in enumerate(dirs, 1):
        print(" ({})  {}".format(nr, release.name))

    return dirs


#TODO: comma separated choosing (e.g. 1,3,5,10)
def choose_release(dirs):
    """Choose release(s) for which you want to download subtitles."""
    choice = input("Choose a release: ")
    dir_count = len(dirs)
    
    if "-" in choice:
        start, end = map(int, choice.split("-"))
    else:
        start, end = map(int, [choice, choice])

    if start == 0 or start > dir_count:
        sys.exit("You chose a non-existing release. Exited.")
    if end > dir_count:
        end = dir_count

    return dirs[start - 1:end]


def get_soup(link):
    """Return BeautifulSoup object."""
    r = requests.get(link, user_agent)

    return BeautifulSoup(r.text, "html.parser")


def check_release_tag(release_name):
    """Check for a release tag and remove it if it exists."""
    if release_name[-1] == "]":  # Possible release tag (e.g. [ettv])
        return release_name.split("[")[0]

    return release_name


def get_sub_rating(sub_link):
    """Return subtitle rating and vote count."""
    soup_link = get_soup("https://subscene.com{}".format(sub_link))
    rating = soup_link.find("div", class_ = "rating")
    if rating:
        vote_count = rating.attrs["data-hint"].split()[1]
        return int(rating.span.text), int(vote_count)

    return -1, -1


def find_subs(search_name, lang, fallback):
    """Return list of lists for subtitle link and info.
       0 - Subtitle page link
       1 - Rating
       2 - Vote count
       3 - H-i = "X", Non H-i = "Y" (for correct sorting)
       4 - Release name (for fallback search results)
    """
    search_name = search_name.replace(" ", ".")  # 
    is_tv = is_tv_series(search_name)
    soup_link = get_soup("https://subscene.com/subtitles/release?q={}".format(search_name))
    
    for table_row in soup_link.find_all("tr")[1:]:  # First entry is not a subtitle
        
        sub_info = table_row.find_all("td", ["a1", "a41"])  # a41 == Hearing impaired
        language, release = sub_info[0].find_all("span")
        language, release = map(str.strip, [language.text, release.text])
        
        if language.lower() == lang.lower() and (release.lower() == search_name.lower() or fallback) and is_tv in release.lower():
            subtitle_link = sub_info[0].a.get("href")

            rating, vote_count = get_sub_rating(subtitle_link)
            if len(sub_info) == 2:
                yield [subtitle_link, rating, vote_count, "X", release]  # H-i sub
            else:
                yield [subtitle_link, rating, vote_count, "Y", release]  # Non H-i sub


def show_available_subtitles(subtitles, args_auto, fallback):
    """Print all available subtitles and choose one from them."""
    subtitles = sorted(subtitles, key = operator.itemgetter(3, 1, 2), reverse = True)
    if not subtitles:
        return None

    if fallback:
        print(" Nr\tRating\tVotes\tH-i\tRelease")
    else:
        print(" Nr\tRating\tVotes\tH-i")

    for nr, sub in enumerate(subtitles, start = 1):
        if not fallback:
            sub[4] = ""
        if sub[1] == -1:
            sub[1], sub[2] = "N/A", ""
        if sub[3] == "Y":
            sub[3] = ""
            
        print(" ({})\t{}\t{}\t{}\t{}".format(nr, sub[1], sub[2], sub[3], sub[4]))

    if args_auto or len(subtitles) == 1:
        print("Subtitle nr 1 chosen automatically.")
        return subtitles[0][0]
    else:
        try:
            choice = int(input("Choose a subtitle: ")) - 1
            return subtitles[choice][0]
        except (IndexError, ValueError):
            print("You chose a non-existing subtitle. Subtitle nr 1 chosen instead.")
            return subtitles[0][0]


def get_download_link(sub_link):
    """Return subtitle download link for the chosen subtitle."""
    soup_link = get_soup("https://subscene.com{}".format(sub_link))

    return soup_link.find(id = "downloadButton").get("href")


def download_sub(sub_zip, sub_link):
    """Download subtitle .zip file."""
    with open(sub_zip, 'wb') as f:
        for chunk in sub_link.iter_content(chunk_size = 1024):
            if chunk:
                f.write(chunk)


def unpack_sub(sub_zip, sub_file, download_dir):
    """Unpack compressed subtitle file."""
    with zipfile.ZipFile(sub_zip, "r") as zip:
        new_sub_file = zip.namelist()[0]
        
        if Path(sub_file).exists():
            print("Previous subtitle file will be overwritten.")
            Path(sub_file).unlink()
            
        zip.extractall(str(download_dir))
        
        return new_sub_file
        

# TODO: Check if there's multiple files in the .zip
# handle other possible extensions
def handle_sub(sub_zip, download_dir, release_name):
    """Handle downloaded subtitle file."""
    sub_file = "{}/{}".format(download_dir, release_name)
    
    if zipfile.is_zipfile(sub_zip):
        new_sub_file = unpack_sub(sub_zip, sub_file, download_dir) 
    else:
        new_sub_file = sub_zip
                
    Path("{}/{}".format(download_dir, new_sub_file)).rename(sub_file)


def main(arguments, media_dir):
    global user_agent
    user_agent = UserAgent().random

    releases = check_media_dir(Path(media_dir))
    if len(releases) == 1:
        dirs = releases
    else:
        dirs = choose_release(releases)

    for release in dirs:
        if release.is_dir():
            download_dir, release_name = release, release.name
        else:
            download_dir, release_name = media_dir, release.stem  # Removes extension

        search_name = check_release_tag(release_name)
        print("\nSearching {} subtitles for {}".format(arguments.language, search_name))
        subtitles = find_subs(search_name, arguments.language, False)
        chosen_sub = show_available_subtitles(subtitles, arguments.auto, False)

        if not chosen_sub:  # Fallback (list all available releases/subs)
            print("No subtitles for {} found. Showing all subtitles.".format(search_name))
            time.sleep(1)  # 
            subtitles = find_subs(search_name, arguments.language, True)
            chosen_sub = show_available_subtitles(subtitles, arguments.auto, True)

            if not chosen_sub and release == dirs[-1]:
                sys.exit("No subtitles found. Exited.")
            elif not chosen_sub:
                print("No subtitles found. Continuing search.")
                continue

        dl_link = get_download_link(chosen_sub)
        sub_link = requests.get("https://subscene.com/{}".format(dl_link), user_agent)
        sub_zip = "{}/subtitle.zip".format(download_dir)
        download_sub(sub_zip, sub_link)
        handle_sub(sub_zip, download_dir, "{}.srt".format(release_name))
        Path(sub_zip).unlink()  # Deletes subtitle.zip

        if arguments.watch and release.is_file() and len(dirs) == 1:
            try:
                subprocess.call(["vlc", str(release)])
            except FileNotFoundError:
                sys.exit("VLC is not installed or you are not using a Linux based system.")

    sys.exit("Done.")


if __name__ == "__main__":
    print("For information about available command line arguments launch the script with -h (--help) argument.\n")
    
    args = parse_arguments()
    settings = "settings.ini"
    script_dir = Path(__file__).parent
    settings_file = script_dir.joinpath(settings)

    if not settings_file.is_file() or args.config:
        config.create_config(settings_file)

    media_dir = config.read_config(settings_file)
    main(args, media_dir)

