import sys
import json
from io import BytesIO
from bs4 import BeautifulSoup
import json
import pycurl

citations = []

def scrape(sepdir):
    "Scrapes the bibliography of a single entry, by url"
    url = 'https://plato.stanford.edu/entries/' + sepdir + '/'
    
    #scrape from url    
    buffer = BytesIO()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(pycurl.SSL_VERIFYPEER, 0)   
    c.setopt(pycurl.SSL_VERIFYHOST, 0)
    c.setopt(c.WRITEDATA, buffer)
    c.perform()
    c.close()
    body = buffer.getvalue()

    soup = BeautifulSoup(body.decode('iso-8859-1'),'html.parser')
    #For each citation in the bibliography
    for link in soup.find(id='bibliography').find_all('li'):
        citations.append(link)

filename = sys.argv[1]
print('Reading ', filename)
fn = open(filename)
contents = json.loads(fn.read())
scrape(sys.argv[2])

for entry,cite in contents,citations:
    print('Authors: ', entry['author'])
    print('Title: ', entry['title'])
    print()

