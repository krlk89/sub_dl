"""
Opens VLC with a specific media file.
"""

import subprocess

def launch_vlc(media_file):
    subprocess.call(["vlc", media_file])