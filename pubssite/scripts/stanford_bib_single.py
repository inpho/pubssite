# goal to scrape a bibliography from plato.stanford.edu

import pycurl
import re
import random
from io import BytesIO
from bs4 import BeautifulSoup
import json
#import rython

entries = {}
#def getStyleBibliography(biblioList):
#    ctx = rython.RubyContext(requires=["rubygems", "anystyle/parser"])
#    ctx("Encoding.default_internal = 'UTF-8'")
#    ctx("Encoding.default_external = 'UTF-8'")
#    anystyle = ctx("Anystyle.parser")
#    anyStyleList = []
#    h =  HTMLParser.HTMLParser()
#    for biblio in biblioList:
#        parsed = anystyle.parse((h.unescape(biblio).encode('utf-8')))
#        anyStyleList.append(parsed)
#    return anyStyleList


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
    cites = []
    #For each citation in the bibliography
    for link in soup.find(id='bibliography').find_all('li'):
        cites.append((link.text).replace('\n', ' '))
    #Add this list of citations to the dictionary            
    entries[sepdir] = cites

#scapes a single entry, based on sepdir
#THIS CAN BE CHANGED TO SCRAPE ALL PAGES
scrape('social-ontology')

outFile = open('all_bibs_json', 'w')
outFile.write(json.dumps(entries))
outFile.close()

print('Complete')
        