
from argparse import ArgumentParser
from multiprocessing import Pool
from sys import exit
from urllib.request import urlopen

from bs4 import BeautifulSoup

__desc__ = """Download all links from http://allrecipes.com/"""

def download(links):
	recipes = []
	for link in links:
		with urlopen(link) as f:
			txt = f.read()
			soup = BeautifulSoup(txt)

			for div in soup.find_all('div'):
				if div.get('class') == None: continue
			
				if div['class'] == ['recipe-info']:
					for p in div.find_all('p'):
						for a in p.find_all('a'):
							recipes.append(a['href'])
	return recipes

def get_link(pages, startPage = 1, packageSize = 1):
	page, package = startPage, []
	while page < startPage + pages:
		link = "http://allrecipes.com/recipes/main.aspx?Page={}#recipes".format(page)
		package.append(link)
		if len(package) == packageSize:
			yield package
			package = []
		page += 1
	if len(package) > 0: yield package

parser = ArgumentParser(description = __desc__)
parser.add_argument("amount",
		type = int,
		metavar = "AMOUNT",
		help = "number of subsequent pages to download links from"
	)
parser.add_argument("-s", "--start",
		type = int,
		default = 1,
		metavar = "N",
		dest = "startPage",
		help = "specify starting page"
	)

def flatten(list):
	return [item for sublist in list for item in sublist]

if __name__ == "__main__":
	args = parser.parse_args()
	for url in flatten(Pool().map(download, get_link(args.amount, args.startPage))): print(url)
	exit(0)

