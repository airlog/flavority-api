
from argparse import ArgumentParser
from json import dumps
from multiprocessing import Pool
from sys import exit, stdin, stderr
from urllib.request import urlopen

from bs4 import BeautifulSoup	

__author__	= "Joanna Cisło"
__desc__	= """Download recipes' data from given URL (from http://allrecipes.com)."""

def parsePage(links):
	if not isinstance(links, list): links = [links]
	
	recipes = []
	for address in links:
		recipe = {}
		ingredients = []
		directions = []
	
		link = "http://allrecipes.com{}".format(address)
#		print("link = {}".format(link), file = stderr)
		f = urlopen(link)
		txt = f.read()
		soup = BeautifulSoup(txt)

		for h1 in soup.find_all('h1'):
			if h1.get('id') == 'itemTitle':
				recipe['name'] = h1.string
				break

		for div in soup.find_all('div'):
			if div.get('id') == 'pnlReadyInTime':
				for span in div.find_all('span'):
					if span.get('class') == ['time']:
						recipe['time'] = span.get_text()
			
		for li in soup.find_all('li'):
			for p in li.find_all('p'):
				if p.get('class') == ['fl-ing']:
					ingredient = {}
					ingredient['name'] = ""
					ingredient['amount'] = "1"
					for span in p.find_all('span'):
						if span.get('class') == ['ingredient-amount']:
							ingredient['amount'] = span.string
						elif span.get('class') == ['ingredient-name']:
							ingredient['name'] = span.string.strip()
					if ingredient['name']:
						ingredients.append(ingredient)
	
		for div in soup.find_all('div'):
			if div.get('class') == ['directions']:
				for ol in div.find_all('ol'):
					for span in ol.find_all('span'):
						directions.append(span.string)		

		recipe['ingredients'] = ingredients
		recipe['directions'] = "\n".join(directions)
		f.close()
	
		recipes.append(recipe)
	return recipes

def download(links):
	return [recipe for link in links for recipe in parsePage(link)]

def get_package(text, packageSize = 1, skip = 0, limit = None):
	counter, parsed, package = 0, 0, []
	for line in text.splitlines():
		counter += 1
		if skip is not None and counter <= skip: continue
		elif limit is not None and parsed >= limit: break
		
		package.append(line)
		if packageSize is not None and len(package) == packageSize:
			yield package
			package = []
		parsed += 1
	if len(package) > 0: yield package

def flatten(list):
	return [item for sublist in list for item in sublist]

parser = ArgumentParser(description = __desc__)
parser.add_argument("-s", "--skip",
		type = int,
		metavar = "N",
		dest = "skip",
		help = "skip first N links"
	)
parser.add_argument("-n", "--number",
		type = int,
		metavar = "N",
		dest = "number",
		help = "download recipes for N subsequent links"
	)
parser.add_argument("-i", "--input",
		type = str,
		dest = "file",
		help = "specify input file, by default application reads from STDIN"
	)

if __name__ == "__main__":
	args = parser.parse_args()
	
	text = None
	try:
		if args.file:
			with open(args.file, "r") as file: text = file.read()
	except IOError as e:
		print(e)
		exit(1)

	if text is None:
		file = stdin
		text = file.read()

#	FIXME
#	urównoleglanie (multiprocessing.Pool.map) nie działa z dziwnego powodu związanego z serlializacją 
#	(pickle) podczas przetwarzania wyników poszczególnych procesów przez funkcję map
#	res = flatten(Pool().map(download, get_package(text, 1)))
	res = download(get_package(text, packageSize = None, skip = args.skip, limit = args.number))	# jeden wątek
	print(dumps(res, indent = 4))
	exit(0)

