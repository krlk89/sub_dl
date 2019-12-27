# sub_dl: SubDB subtitle downloader

sub_dl is a command-line tool that searches and downloads subtitles via [SubDB](http://thesubdb.com/) API.

[Python 3](https://www.python.org/) is required.

## Dependencies:
* [Requests](http://docs.python-requests.org/en/master/)

Easiest way to install all the dependencies:

    pip install -r requirements.txt
    
## How to use:
1. On the first launch your input is needed for generating the configuration file. You can later change this preference by launching the script as ./sub_dl.py -c.
    ```
    ./sub_dl.py
    For information about available command line arguments launch the script with -h (--help) argument.
    
    Type your media directory: /home/user/Downloads
    ```

2. Choose movies/tv shows for which you want to download subtitles. You can choose a single release (*e.g.* 1), multiple releases (*e.g.* 1,3) or a range of releases (*e.g.* 1-4).
    ```
    Checking media directory: /home/user/Downloads
     (1)  No.avi
     (2)  The Great Dictator.avi
     (3)  The.Dawn.Wall.2017.1080p.BluRay.H264.AAC-RARBG.mp4
     (4)  sherlock.4x01.repack_720p_hdtv_x264-fov.mkv
    Choose a release: 3
    Subtitles downloaded for for The.Dawn.Wall.2017.1080p.BluRay.H264.AAC-RARBG
    ```

4. For help and available command line arguments:
    ```
    ./sub_dl.py -h
    usage: sub_dl.py [-h] [-c] [-l {en,es,fr,it,nl,pl,pt,ro,sv,tr}]
                 [-d DIRECTORY [DIRECTORY ...]] [-w]

    sub_dl: SubDB subtitle downloader.

    optional arguments:
      -h, --help            show this help message and exit
      -c, --config          configure your media directory
      -l {en,es,fr,it,nl,pl,pt,ro,sv,tr}, --language {en,es,fr,it,nl,pl,pt,ro,sv,tr}
                            specify desired subtitles language (overrules default
                            which is en (English)
      -d DIRECTORY [DIRECTORY ...], --directory DIRECTORY [DIRECTORY ...]
                            specify media directory (overrules default
                            temporarily)
      -w, --watch           launch VLC after downloading subtitles
    ```

Enjoy!
