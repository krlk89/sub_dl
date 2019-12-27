#!/usr/bin/env python3

"""Script for downloading subtitles from SubDB (http://thesubdb.com/).
   Author: https://github.com/krlk89/sub_dl
"""

import argparse
from pathlib import Path
import subprocess
import sys

try:
    import requests
except ImportError:
    sys.exit("Missing dependencies. Type 'pip install -r requirements.txt' to install them.")

import sub_dl_config
import sub_dl_subdb


def parse_arguments():
    """Parse command line arguments. All are optional."""
    parser = argparse.ArgumentParser(description = "sub_dl: SubDB subtitle downloader.")
    parser.add_argument("-c", "--config", action = "store_true", help = "configure your media directory")
    parser.add_argument("-l", "--language", type = str, default = "en", choices = ["en","es","fr","it","nl","pl","pt","ro","sv","tr"], help = "specify desired subtitles language (overrules default which is en (English)")
    parser.add_argument("-d", "--directory", nargs = "+", help = "specify media directory (overrules default temporarily)")
    parser.add_argument("-w", "--watch", action = "store_true", help = "launch VLC after downloading subtitles")

    return parser.parse_args()


def check_media_dir(media_dir):
    """Return a list of releases inside the media directory."""
    sub_extensions = (".sub", ".idx", ".srt")

    print("Checking media directory: {}".format(media_dir))
    # Files in media dir
    releases = [release for release in media_dir.iterdir() if release.is_file() and release.suffix not in sub_extensions]
    if not releases:
        sys.exit("No releases in {}.".format(media_dir))

    releases.sort()
    for nr, release in enumerate(releases, 1):
        print(" ({})  {}".format(nr, release.name))

    return releases


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


def download_sub(hash, target, session):
    """Download subtitle file."""
    resp = session.get("http://api.thesubdb.com/?action=download&hash={}&language={}".format(hash, args.language))
    with open("{}.srt".format(target), "w") as f:
        f.write(resp.text)


def main(arguments, media_dir):
    """Main function."""
    releases = check_media_dir(Path(media_dir))
    if not releases:
        sys.exit("Media dir is empty. Exited")
    elif len(releases) == 1:
        dirs = releases
    else:
        dirs = choose_release(releases)

    user_agent = "SubDB/1.0 (sub_dl/0.1; https://github.com/krlk89/sub_dl)"
    with requests.Session() as session:
        session.headers.update({"user-agent": user_agent})

        for release in dirs:
            hash = sub_dl_subdb.get_hash(release)
            resp = session.get("http://api.thesubdb.com/?action=search&hash={}".format(hash))

            if args.language not in resp.text:
                print("No subtitles found for {}".format(release), end=". ")
                if release == dirs[-1]:
                    sys.exit("Exited.")

                print("Continuing search.")
                continue

            download_sub(hash, release.parent / release.stem, session)
            print("Subtitles ({}) downloaded for {}".format(args.language, release.stem))

            if arguments.watch and release.is_file() and len(dirs) == 1:
                try:
                    subprocess.call(["vlc", str(release)])
                except FileNotFoundError:
                    sys.exit("VLC is not installed or you are not using a Linux based system.")


if __name__ == "__main__":
    args = parse_arguments()

    print("For information about available command line arguments launch the script with -h (--help) argument.\n")

    settings_file = Path(__file__).parent.joinpath("settings.ini")

    if not settings_file.is_file() or args.config:
        sub_dl_config.create_config(settings_file)

    media_dir = sub_dl_config.read_config(settings_file)

    dir = args.directory
    if dir:
        dir = " ".join(args.directory)
        temp_dir = Path(media_dir).joinpath(dir)

        if Path(temp_dir).is_dir():
            # dir inside media dir
            media_dir = temp_dir
        elif Path(dir).is_dir():
            media_dir = dir
        else:
            print("Non-existing directory given as an argument. Using media directory from the settings file instead.")

    main(args, media_dir)
