"""
Downloads subtitles from Subscene.

TODO: Rename the subtitle file not the movie file.
	  Let user choose the subtitle?
"""

def is_tv_series(directory):
	from re import search
	
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


#def soup():
	

	
def find_subtitles(soup, movie_directory):
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
	from sys import argv, exit
	from random import choice
	from glob import glob
	from os import remove
	
	download_directory = "C:\\Users\\Kaarel\\Downloads\\"
	movie_name = input("Enter movie name: ").replace(" ", "-")
	movie_wildcard_name = movie_name.replace("-", "*")
	
	try: movie_directory = glob("{}{}*".format(download_directory, movie_wildcard_name))[0].split("\\")[-1]
	except IndexError: exit("Movie directory not found.")
	
	is_tv = is_tv_series(movie_directory)
	if is_tv:
		movie_name += "-{}-season".format(tv_seasons(is_tv))
	
	sub_search = requests.get("https://subscene.com/subtitles/title?q={}&l=".format(movie_name.replace("-", "+")))
	soup = BeautifulSoup(sub_search.text, "html.parser")
	
	movie_name = find_subtitle_page(soup, movie_name) # Find correct subtitle page
	
	r = requests.get("https://subscene.com{}/english".format(movie_name))
	soup = BeautifulSoup(r.text, "html.parser")
	
	subtitles = find_subtitles(soup, movie_directory) # Find all suitable subtitles
	if len(subtitles) == 0: exit("No subtitles found.")
	sub = choice(subtitles) # Choose one from suitable subtitles
	
	r = requests.get("https://subscene.com{}".format(sub))
	soup = BeautifulSoup(r.text, "html.parser")
	download_link = find_download_link(soup) # Find download link from the subtitle page
	r = requests.get("https://subscene.com/{}".format(download_link))
	
	destination = "{}subtitle.zip".format(download_directory)
	download_subtitle(destination, r) # Downloads subtitle
	unpack_subtitle(destination, "{}{}".format(download_directory, movie_directory)) # Unpacks the subtitle
	remove(destination) # Deletes the subtitle .zip file
	
	files = glob("{}{}\\{}*".format(download_directory, movie_directory, movie_wildcard_name)) # Find all the files in movie directory
	if len(files) > 2: exit("Multiple movie files detected. Subtitle downloaded, but nothing renamed.")
	rename_file(files) # Unifies movie and subtitle filenames
	
	exit("Done.")

main()