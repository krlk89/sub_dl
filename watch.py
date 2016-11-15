"""
Opens VLC with a media file.
"""

def launch_vlc(media_file = ""):
    import subprocess
    
    subprocess.call(["vlc", media_file])

if __name__ == "__main__":
    #launch_vlc()