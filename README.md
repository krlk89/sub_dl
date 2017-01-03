# sub-dl: Subscene subtitle downloader

This script downloads subtitle files from [Subscene](https://subscene.com).

## Requirements:
* [Python 3](https://www.python.org/)
* [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)

## Example:
1. On the first launch your input is needed for generating the configuration file.
```
user@home-pc:~/sub-dl$ ./sub-dl.py
Type your media directory: /home/user/Downloads
Type your preferred subtitle language (e.g. English): English
```
2. Choose movies/tv shows for which you want to download subtitles. You can choose a single release (*e.g.* 1) or a range of releases (*e.g.* 2-3).
```
user@home-pc:~/sub-dl$ ./sub-dl.py
Checking media directory: /home/user/Downloads
 (1)  Sherlock.The.Abominable.Bride.2016.720p.BluRay.H264.AAC-RARBG
 (2)  sherlock.4x01.repack_720p_hdtv_x264-fov.mkv
Choose a release: 1

Searching subtitles for Sherlock.The.Abominable.Bride.2016.720p.BluRay.H264.AAC-RARBG
```
3. Choose one from subtitles that are suitable for the selected release. Hearing impaired subtitles are marked with an X.
Downloaded subtitle file will be renamed after the release directory or file. Other files on your computer will not be modified in any way!
```
Nr	Rating	Votes	Hearing impaired
 (1)	9	16
 (2)	N/A	
 (3)	10	16	X
Choose a subtitle: 3
Done.
user@home-pc:~/sub-dl$
```
Note: If there's only one release and/or subtitle available then it will be chosen automatically.

./sub-dl -h for help and available command line arguments.

Enjoy!
