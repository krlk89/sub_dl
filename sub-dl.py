from bs4 import BeautifulSoup
import requests

"""
def parse_site():

def download_file():

"""
movie_name = "warcraft"
subs = {}

r = requests.get("https://subscene.com/subtitles/{}/english".format(movie_name))

soup = BeautifulSoup(r.text, "html.parser")

for i in soup.find_all("a"):
	y = i.find_all("span")
	if len(y) > 1 and "Warcraft.2016.TC.x264.AAC-ETRG" in str(y) and "positive" in str(y):
		subs[i.get("href")] = str(i).split()[9]
		temp = i.get("href")

print(subs)
if len(subs) == 0:		
	print("Sorry. No subtitles found.")

r = requests.get("https://subscene.com{}".format(temp))

soup = BeautifulSoup(r.text, "html.parser")

for i in soup.find_all("a"):
	print(i.get("href"))

r = requests.get("https://subscene.com/subtitle/download?mac=qWgT-rNK-e9QO0vPtafWZ7bq0ST98ACk2YdX_T5h4P1QzWgebKNvPOu0B1n1mGVg9DTdiwhuRRCfrVDEk5eyTfGqHt_Qjmn5idT_w8VXCxwq6k-sIW3Y1iEAQnGInq-h0")
local_filename = "test.zip"
with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)