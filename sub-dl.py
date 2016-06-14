from bs4 import BeautifulSoup
import requests

# TODO
# 
# 
# 

#def parse_site():


def download_sub(local_filename, download_link):
	with open(local_filename, 'wb') as f:
		for chunk in download_link.iter_content(chunk_size = 2048): 
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)

def main():
	movie_name = "warcraft"
	subs = {}

	r = requests.get("https://subscene.com/subtitles/{}/english".format(movie_name))

	soup = BeautifulSoup(r.text, "html.parser")

	for i in soup.find_all("a"):
		y = i.find_all("span")
		if len(y) > 1 and "Warcraft.2016.TC.x264.AAC-ETRG" in str(y) and "positive" in str(y):
			subs[i.get("href")] = str(i).split()[9]
			temp = i.get("href")

	#print(subs)
	if len(subs) == 0:		
		print("Sorry. No subtitles found.")

	r = requests.get("https://subscene.com{}".format(temp))

	soup = BeautifulSoup(r.text, "html.parser")

	for i in soup.find_all("a"):
		if "download" in str(i):
			link = i.get("href")

	r = requests.get("https://subscene.com/{}".format(link))
	download_sub("test.zip", r)

	print("Done.")

main()