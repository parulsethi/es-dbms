from urllib.request import urlopen

def scrape_txt(url):
	raw = urlopen(url).read()
	raw = raw.decode('utf-8')
	x = raw.find("CHAPTER I")
	y = raw.find("THE END.")
	raw = raw[x:y]

	return raw

def text_blocks(url):
	groups = []
	init,end = 0,1000
	txt_to_div = scrape_txt(url)
	for i in txt_to_div:
		groups.append(txt_to_div[init:end])
		init = end+1
		end = init+1000
	es_block = []
	for x in groups:
		txt = {"text":x}
		es_block.append(txt)

	return es_block




