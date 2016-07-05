"""
Opens VLC with a specific media file.
"""

import subprocess

def launch_vlc(media_file):
    vlc_dir = "C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe"
    subprocess.call([vlc_dir, media_file], shell = True)