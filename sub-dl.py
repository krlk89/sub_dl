"""
Downloads subtitles from Subscene.
Usage: python sub-dl.py <name>

TODO: Prettify module imports.
	  Rename the subtitle file not the movie file.
"""

import requests
from bs4 import BeautifulSoup
from sys import argv, exit
from glob import glob
from os import remove, rename, path
from re import search
from requests import get
from zipfile import ZipFile	

def is_tv_series(directory):
	tv = search("\.S\d{2}E\d{2}\.", directory)
	if tv:
		return search("S\d{2}", tv.group()).group()
	
	return False


def tv_seasons(key):
	seasons = {"S01": "first", "S02": "second", "S03": "third", "S04": "fourth", "S05": "fifth",
		"S06": "sixth", "S07": "seventh", "S08": "eighth", "S09": "ninth", "S10": "tenth",
		"S11": "eleventh", "S12": "twelfth", "S13": "thirteenth", "S14": "fourteenth", "S15": "fifteenth",
		"S16": "sixteenth", "S17": "seventeenth", "S18": "eighteenth", "S19": "nineteenth", "S20": "twentieth",}
	
	return seasons[key]


def find_subtitle_page(soup, movie_name):
	for list in soup.find_all("li"):
		if all(word in str(list).lower() for word in movie_name.split("-")):
		
			return list.find_all("a")[0].get("href")
	
	exit("Subtitle page not found.")


def soup(link):
	r = get(link)
	
	return BeautifulSoup(r.text, "html.parser")


def find_subtitles(soup, movie_directory):
	subtitles = []
	nr = 0
	
	for table_row in soup.find_all("tr"):
		subtitle_info = str(table_row).lower()
		if movie_directory.lower() in subtitle_info and "positive" in subtitle_info:
			nr += 1
			subtitles.append(table_row.find_all("a")[0].get("href")) # Subtitle link
			if "<td class=\"a41\">" in subtitle_info:
				print(nr, "(Hearing impaired)")
			else:
				print(nr)

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
	with ZipFile(file, "r") as zip:
		if path.exists("{}\\{}".format(out_dir, zip.namelist()[0])):
			print("Subtitle file overwritten.")
			
		zip.extractall(out_dir)


def handle_multiple_subtitle_files(files):
	for nr, file in enumerate(files, 1):
		print(nr, file.split("\\")[-1])
		
	user_choice = input("Multiple subtitle files detected. Do you wish to delete one? (i\\n): ")
	if user_choice == "n":
		exit("Subtitle downloaded. Nothing renamed or deleted.")
	else:
		remove(files[int(user_choice) -1]) # Deletes file
		files.pop(int(user_choice) -1) # Removes file from the list


def rename_file(files):
	for nr, file in enumerate(files):
		if nr == 0:
			name = file[:-4]
		else:
			extension = file[-4:]
			rename(file, name + extension)


def main():
	download_directory = "C:\\Users\\Kaarel\\Downloads\\"
	movie_name = "-".join(argv[1:])
	movie_wildcard_name = movie_name.replace("-", "*")
	
	try:
		movie_directory = glob("{}{}*".format(download_directory, movie_wildcard_name))
		if len(movie_directory) > 1: # Multiple directories for the same tv series/movie
			for nr, directory in enumerate(movie_directory, 1):
				print(nr, directory.split("\\")[-1])
			user_choice = int(input("Multiple directories detected. Which to choose? (i): ")) - 1
			movie_directory = movie_directory[user_choice].split("\\")[-1]
		else:
			movie_directory = movie_directory[0].split("\\")[-1]
			
		if movie_directory[-1] == "]": # Possible release tag
			movie_directory, tag = movie_directory.split("[")
			tag = "[{}".format(tag)
		else: tag = ""
	except IndexError: exit("Movie directory not found.")
	
	is_tv = is_tv_series(movie_directory)
	if is_tv:
		movie_name += "-{}-season".format(tv_seasons(is_tv))
	
	movie_name = find_subtitle_page(soup("https://subscene.com/subtitles/title?q={}&l=".format(movie_name.replace("-", "+"))), movie_name) # Find correct subtitle page
	
	subtitles = find_subtitles(soup("https://subscene.com{}/english".format(movie_name)), movie_directory) # Find all suitable subtitles
	if len(subtitles) == 0: exit("No subtitles found.")
	sub = subtitles[int(input("Choose a subtitle: ")) -1] # Choose one from suitable subtitles
	
	download_link = find_download_link(soup("https://subscene.com{}".format(sub))) # Find download link from the subtitle page
	r = requests.get("https://subscene.com/{}".format(download_link))
	
	destination = "{}subtitle.zip".format(download_directory)
	download_subtitle(destination, r) # Downloads subtitle
	unpack_subtitle(destination, "{}{}{}".format(download_directory, movie_directory, tag)) # Unpacks the subtitle
	remove(destination) # Deletes the subtitle .zip file
	
	files = glob("{}{}*\\{}*".format(download_directory, movie_directory, movie_wildcard_name)) # Find all the files in movie directory
	files.sort(key=path.getmtime)
	if len(files) > 2:
		handle_multiple_subtitle_files(files) # Option to delete unnecessary file
		
	rename_file(files) # Unifies movie and subtitle filenames
	
	exit("Done.")

main()