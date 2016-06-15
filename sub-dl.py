"""

"""

def download_sub(local_filename, download_link):
	with open(local_filename, 'wb') as f:
		for chunk in download_link.iter_content(chunk_size = 2048): 
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)

				
def unpack_sub(file, out_dir):
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
	
	subtitles = []
	movie_name = input("Enter movie name: ").replace(" ", "-")
	movie_v = "*" + movie_name.replace("-", ".") + "*"
	try: movie_version = glob(movie_v)[0]
	except IndexError: exit("Directory not found.")
		
	r = requests.get("https://subscene.com/subtitles/{}/english".format(movie_name))
	soup = BeautifulSoup(r.text, "html.parser")

	for link in soup.find_all("a"):
		y = link.find_all("span")
		if len(y) > 1 and movie_version in str(y) and "positive" in str(y):
			subtitles.append(link.get("href"))
	
	if len(subtitles) == 0: exit("Sorry. No subtitles found.")
	
	sub = choice(subtitles)
	r = requests.get("https://subscene.com{}".format(sub))
	soup = BeautifulSoup(r.text, "html.parser")

	for link in soup.find_all("a"):
		if "download" in str(link):
			link = link.get("href")
			break
			
	r = requests.get("https://subscene.com/{}".format(link))
	
	download_sub("subtitle.zip", r) # Downloads subtitles
	unpack_sub("subtitle.zip", movie_version) # Unpacks .zip file
	remove("subtitle.zip") # Deletes .zip file
	
	files = glob(movie_version + "/" + movie_v)
	rename_file(files) # Unifies movie and subtitle filenames
	
	exit("Done.")

main()