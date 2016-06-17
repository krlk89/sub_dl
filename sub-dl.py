"""
This script downloads subtitles from Subscene.

"""

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
	subtitles = []
	movie_name = input("Enter movie name: ").replace(" ", "-")
	#movie_name = "10-cloverfield-lane" # For debugging
	movie_wildcard_name = movie_name.replace("-", "*")

	try:
		movie_directory = glob("{}{}*".format(download_directory, movie_wildcard_name))[0]
		movie_directory = movie_directory.split("\\")[-1]
	except IndexError: exit("Movie directory not found.")
	
	r = requests.get("https://subscene.com/subtitles/{}/english".format(movie_name))
	soup = BeautifulSoup(r.text, "html.parser")
	
	# Find all suitable subtitles
	for table_row in soup.find_all("tr"):
		if "<td class=\"a41\">" not in str(table_row):
			description = table_row.find_all("a")
			for info in description:
				if len(description) > 1 and movie_directory.lower() in str(description).lower() and "positive" in str(description):
					subtitles.append(info.get("href"))
					break

	if len(subtitles) == 0: exit("No subtitles found.")
	sub = choice(subtitles)
	
	r = requests.get("https://subscene.com{}".format(sub))
	soup = BeautifulSoup(r.text, "html.parser")
	
	# Find download link from subtitle page
	for link in soup.find_all("a"):
		if "download" in str(link):
			download_link = link.get("href")
			break
			
	r = requests.get("https://subscene.com/{}".format(download_link))
	
	download_subtitle("{}subtitle.zip".format(download_directory), r) # Downloads subtitle
	unpack_subtitle("{}subtitle.zip".format(download_directory), "{}{}".format(download_directory, movie_directory)) # Unpacks the subtitle
	remove("{}subtitle.zip".format(download_directory)) # Deletes the subtitle .zip file
	
	files = glob("{}{}\\{}*".format(download_directory, movie_directory, movie_wildcard_name)) # 
	if len(files) > 2: exit("Multiple movie files detected.")
	rename_file(files) # Unifies movie and subtitle filenames
	
	exit("Done.")

main()