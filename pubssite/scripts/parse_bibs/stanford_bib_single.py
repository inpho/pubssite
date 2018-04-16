# goal to scrape a bibliography from plato.stanford.edu

import pycurl
import re
import random
from io import BytesIO
from bs4 import BeautifulSoup
import json
import rython

def getStyleBibliography(biblioList):
    ctx = rython.RubyContext(requires=["rubygems", "anystyle/parser"])
    ctx("Encoding.default_internal = 'UTF-8'")
    ctx("Encoding.default_external = 'UTF-8'")
    anystyle = ctx("Anystyle.parser")
    anyStyleList = []
    h =  HTMLParser.HTMLParser()
    for biblio in biblioList:
        parsed = anystyle.parse((h.unescape(biblio).encode('utf-8')))
        anyStyleList.append(parsed)
    return anyStyleList

def getNames(allNames):
    ctx = rython.RubyContext(requires=["rubygems", "namae"])
    ctx("Encoding.default_internal = 'UTF-8'")
    ctx("Encoding.default_external = 'UTF-8'")
    namae = ctx("Namae")
    parsed = namae.parse(allNames)
    return parsed

def scrape(sepdir):
    "Scrapes the bibliography of a single entry, by url"
    url = 'https://plato.stanford.edu/entries/' + sepdir + '/'
    entries = []
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
    
    components = getStyleBibliography(soup.find(id='bibliography').find_all('li'))
    
    i = 0
    #For each citation in the bibliography
    for citation in soup.find(id='bibliography').find_all('li'):
        if 'author' in components[i].keys():
            names = getNames(components[i]['author'])
            for nm in names:
                entry = {}
                entry['full_citation'] = (citation.text).replace('\n', ' ')
                
                if 'family' in nm:
                    entry['family_name'] = nm['family']
                else:
                    entry['family_name'] = ''
                    
                if 'given' in nm.keys():
                    entry['given_name'] = nm['given']
                else:
                    entry['given_name'] = ''
                
                entry['title'] = components[i]['title']
                entries.append(entry)
                
        else:
            entry = {}
            entry['full_citation'] = (citation.text).replace('\n', ' ')
            entry['family_name'] = ''
            entry['given_name'] = ''
            entry['title'] = components[i]['title']
            entries.append(entry)
        i = i + 1
    return entries

#scapes a single entry, based on sepdir
#THIS CAN BE CHANGED TO SCRAPE ALL PAGES
scrape('social-ontology')

outFile = open('all_bibs_json', 'w')
outFile.write(json.dumps(entries))
outFile.close()

print('Complete')
        