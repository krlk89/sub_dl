"""
Downloads subtitles from Subscene.

TODO: Let user choose the subtitle?
"""

def is_tv_series(directory):
	from re import search
	
	tv = search("\.S\d{2}E\d{2}\.", directory)
	
	if tv:
		return search("S\d{2}", tv.group()).group()
	
	return False

	
def tv_seasons(key):

	seasons = {"S01": "first", "S02": "second", "S03": "third", "S04": "fourth", "S05": "fifth",
		"S06": "sixth", "S07": "seventh", "S08": "eighth", "S09": "ninth", "S10": "tenth"}
	
	return seasons[key]
	

def find_subtitles(soup, movie_directory):
	from bs4 import BeautifulSoup
	
	subtitles = []
	
	for table_row in soup.find_all("tr"):
		subtitle_info = str(table_row).lower()
		if "<td class=\"a41\">" not in subtitle_info and movie_directory.lower() in subtitle_info and "positive" in subtitle_info:
			subtitles.append(table_row.find_all("a")[0].get("href")) # Subtitle link
			
	return subtitles

	
def find_download_link(soup):
	for link in soup.find_all("a"):
		if "download" in str(link):
			return link.get("href")
	
	
def download_subtitle(local_filename, download_link):
	with open(local_filename, 'wb') as f:
		for chunk in download_link.iter_content(chunk_size = 2048): 
			if chunk:
				f.write(chunk)

				
def unpack_subtitle(file, out_dir):
	from zipfile import ZipFile
	
	with ZipFile(file, "r") as zip:
		zip.extractall(out_dir)

		
def rename_file(files):
	from os import rename

	for nr, file in enumerate(files):
		if nr == 0:
			name = file[:-4]
		else:
			extension = file[-4:]
			rename(file, name + extension)


def main():
	import requests
	from bs4 import BeautifulSoup
	from sys import exit
	from random import choice
	from glob import glob
	from os import remove
	
	download_directory = "C:\\Users\\Kaarel\\Downloads\\"
	movie_name = input("Enter movie name: ").replace(" ", "-")
	#movie_name = "10-cloverfield-lane" # For debugging
	movie_wildcard_name = movie_name.replace("-", "*")

	try:
		movie_directory = glob("{}{}*".format(download_directory, movie_wildcard_name))[0]
		movie_directory = movie_directory.split("\\")[-1]
	except IndexError: exit("Movie directory not found.")
	
	is_tv = is_tv_series(movie_directory)
	if is_tv:
		movie_name += "-{}-season".format(tv_seasons(is_tv))
	
	r = requests.get("https://subscene.com/subtitles/{}/english".format(movie_name))
	soup = BeautifulSoup(r.text, "html.parser")
	
	subtitles = find_subtitles(soup, movie_directory) # Find all suitable subtitles
	if len(subtitles) == 0: exit("No subtitles found.")
	sub = choice(subtitles) # Choose one from suitable subtitles
	
	r = requests.get("https://subscene.com{}".format(sub))
	soup = BeautifulSoup(r.text, "html.parser")
	
	download_link = find_download_link(soup) # Find download link from subtitle page
			
	r = requests.get("https://subscene.com/{}".format(download_link))
	
	destination = "{}subtitle.zip".format(download_directory)
	download_subtitle(destination, r) # Downloads subtitle
	unpack_subtitle(destination, "{}{}".format(download_directory, movie_directory)) # Unpacks the subtitle
	remove(destination) # Deletes the subtitle .zip file
	
	files = glob("{}{}\\{}*".format(download_directory, movie_directory, movie_wildcard_name)) # 
	if len(files) > 2: exit("Multiple movie files detected. Nothing renamed.")
	rename_file(files) # Unifies movie and subtitle filenames
	
	exit("Done.")

main()