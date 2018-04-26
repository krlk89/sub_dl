#!/usr/bin/env python3

"""Download subtitles from Subscene (https://subscene.com).
   Author: https://github.com/krlk89/sub_dl
"""

import argparse
import difflib
import operator
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile

try:
    from fake_useragent import UserAgent
    from bs4 import BeautifulSoup, SoupStrainer
    import requests
except ImportError:
    sys.exit("Missing dependencies. Type 'pip install -r requirements.txt' to install them.")

import config
#import logger # TODO


def parse_arguments():
    """Parse command line arguments. All are optional."""
    parser = argparse.ArgumentParser(description = "sub_dl: Subscene subtitle downloader.")
    parser.add_argument("-c", "--config", action = "store_true", help = "configure your media directory")
    parser.add_argument("-l", "--language", type = str, default = "english", help = "specify desired subtitles language (overrules default which is English)")
    parser.add_argument("-a", "--auto", action = "store_true", help = "automatically choose best-rated non hearing-impaired subtitles")
    parser.add_argument("-w", "--watch", action = "store_true", help = "launch VLC after downloading subtitles")

    return parser.parse_args()


def tv_series_or_movie(release_name):
    """Check if release is a tv show. If yes then fallback search shows only subtitles for the right episode.
    Return empty string for movies so that comparison works in find_subs function."""
    match = re.search("\.S\d+E\d+\.", release_name, re.IGNORECASE)
    if match:
        return match.group().lower()

    return ""


def check_media_dir(media_dir):
    """Return a list of releases inside the media directory."""
    sub_extensions = (".sub", ".idx", ".srt")

    print("Checking media directory: {}".format(media_dir))
    # Files and release dirs in media dir
    dirs = [x for x in media_dir.iterdir() if x.suffix not in sub_extensions]
    if not dirs:
        sys.exit("No releases in {}.".format(media_dir))

    dirs.sort()
    for nr, release in enumerate(dirs, 1):
        print(" ({})  {}".format(nr, release.name))

    return dirs


def choose_release(dirs):
    """Choose release(s) for which you want to download subtitles."""
    choice = input("Choose a release: ")
    dir_count = len(dirs)

    try:
        if "-" in choice:
            start, end = map(int, choice.split("-"))
        elif "," in choice:
            choices = (int(i) - 1 for i in choice.split(",") if int(i) <= dir_count)
            return [dirs[i] for i in choices]
        else:
            start, end = map(int, [choice, choice])
    except ValueError:
        return choose_release(dirs)

    if start == 0 or start > dir_count:
        return choose_release(dirs)
    if end > dir_count:
        end = dir_count

    return dirs[start - 1:end]


def check_release_tag(release_name):
    """Check for a release tag (e.g. [ettv]) and remove it (for searching) if it exists."""
    if release_name[-1] == "]":
        return release_name.split("[")[0]

    return release_name


def get_sub_info(sub_link, session):
    """Return subtitle download link, rating, vote count and tag for hearing impaired."""
    r = session.get("https://subscene.com{}".format(sub_link), timeout = 10)
    soup = BeautifulSoup(r.text, "lxml", parse_only = SoupStrainer("li", class_ = "clearfix"))
    dl_link = soup.find(id = "downloadButton").get("href")
    rating = soup.find("div", class_ = "rating")
    hi = soup.find("span", class_ = "hearing-impaired")

    hi_tag = "Y"
    if hi:
        hi_tag = "X"

    if rating:
        vote_count = rating.attrs["data-hint"].split()[1]
        return dl_link, int(rating.span.text), int(vote_count), hi_tag

    return dl_link, -1, -1, hi_tag


def find_subs(search_name, language, session):
    """Return list of lists for subtitle info.
       0 - Download link
       1 - Rating
       2 - Vote count
       3 - Hearing-impaired tag (H-i = "X", Non H-i = "Y" [for correct sorting])
       4 - Release name (for fallback search results)
    """
    fallback = True
    sub_list = []
    fallback_sub_list = []
    search_name = search_name.replace(" ", ".").lower()  # Local file/dir name
    tv_or_movie = tv_series_or_movie(search_name)

    r = session.get("https://subscene.com/subtitles/release?", params = {"q": search_name}, timeout = 10)
    soup = BeautifulSoup(r.text, "lxml", parse_only = SoupStrainer("td", class_ = "a1"))
    soup_data = soup.find_all("td")

    for subtitle in soup_data:
        sub_language, release = subtitle.find_all("span")
        sub_language, release = map(str.strip, [sub_language.text, release.text])
        is_close_match = difflib.SequenceMatcher(None, search_name, release.lower()).ratio() > 0.9

        if language == sub_language.lower() and (search_name in release.lower() or (fallback and is_close_match)) and tv_or_movie in release.lower():
            subtitle_link = subtitle.a.get("href")
            download_link, rating, vote_count, hi_tag = get_sub_info(subtitle_link, session)

            if fallback and search_name not in release.lower() and is_close_match:
                fallback_sub_list.append([download_link, rating, vote_count, hi_tag, release])
            else:
                fallback = False
                sub_list.append([download_link, rating, vote_count, hi_tag, release])

    if not sub_list:
        return fallback_sub_list, True

    return sub_list, False


def show_available_subtitles(subtitles, args_auto, fallback):
    """Print all available subtitles and choose one from them."""
    subtitles = sorted(subtitles, key = operator.itemgetter(3, 1, 2), reverse = True)

    if fallback:
        print("\nNo exact matches found, showing fallback results.\n Nr\tRating\tVotes\tH-i\tRelease")
    else:
        print("\n Nr\tRating\tVotes\tH-i")

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
        while True:
            try:
                choice = int(input("Choose a subtitle: ")) - 1
                return subtitles[choice][0]
            except (IndexError, ValueError):
                print("You chose a non-existing subtitle. Choose again.")


def download_sub(sub_zip, sub_link):
    """Download subtitle .zip file."""
    with open(sub_zip, 'wb') as f:
        for chunk in sub_link.iter_content(chunk_size = 1024):
            if chunk:
                f.write(chunk)


def unpack_sub(sub_zip, sub_file, download_dir):
    """Unpack compressed subtitle file."""
    with zipfile.ZipFile(sub_zip, "r") as zip:
        if len(zip.namelist()) > 1:
            print("Multiple files in the archive. First file will be chosen.")
        new_sub_file = zip.namelist()[0]

        if Path(sub_file).exists():
            print("Previous subtitle file will be overwritten.")
            Path(sub_file).unlink()

        zip.extractall(str(download_dir))

        return new_sub_file


def handle_sub(sub_zip, download_dir, release_name):
    """Handle downloaded subtitle file."""
    sub_file = "{}/{}".format(download_dir, release_name)

    if zipfile.is_zipfile(sub_zip):
        new_sub_file = unpack_sub(sub_zip, sub_file, download_dir)
    else:
        new_sub_file = sub_zip

    Path("{}/{}".format(download_dir, new_sub_file)).rename(sub_file)


def main(arguments, media_dir):
    """Main function."""
    releases = check_media_dir(Path(media_dir))
    if not releases:
        sys.exit("Media dir is empty. Exited")
    elif len(releases) == 1:
        dirs = releases
    else:
        dirs = choose_release(releases)

    user_agent = UserAgent(fallback = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0").random
    with requests.Session() as session:
        session.headers.update({"user-agent": user_agent})

        for release in dirs:
            if release.is_dir():
                download_dir, release_name = release, release.name
            else:
                download_dir, release_name = media_dir, release.stem  # Removes extension (for searching)

            search_name = check_release_tag(release_name)
            print("\nSearching {} subtitles for {}".format(arguments.language.capitalize(), search_name))
            subtitles, fallback = find_subs(search_name, arguments.language.lower(), session)

            if not subtitles:
                if release == dirs[-1]:
                    sys.exit("No subtitles found. Exited.")

                print("No subtitles found. Continuing search.")
                continue

            chosen_sub = show_available_subtitles(subtitles, arguments.auto, fallback)

            sub_link = session.get("https://subscene.com/{}".format(chosen_sub))
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
    settings_file = Path(__file__).parent.joinpath("settings.ini")

    if not settings_file.is_file() or args.config:
        config.create_config(settings_file)

    media_dir = config.read_config(settings_file)
    main(args, media_dir)

