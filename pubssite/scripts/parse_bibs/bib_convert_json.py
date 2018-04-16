import sys
import json
from io import BytesIO
from bs4 import BeautifulSoup
import json
import pycurl

citations = []

def scrape(sepdir):
    "Scrapes the bibliography of a single entry, by sepdir, for each individual citation"
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
        citations.append(link.text.replace('\n', ' '))

if len(sys.argv) < 3:
    print("Syntax: python bib_convert_json.py <json file name> <sepdir>")
    exit()

filename = sys.argv[1]
print('Reading ', filename)
fn = open(filename, 'rb')
fn_stuff = fn.read()
fn.close()
contents = json.loads(fn_stuff)
scrape(sys.argv[2])

outFileName = '' + sys.argv[2] + '_bib.csv' 
csv = open(outFileName, 'w')
csv.write('Family Name, Given Name, Citation, Google Link\n')

for i in range(len(contents)):
    #print(citations[i])
    if 'author' in contents[i].keys():
        for author in contents[i]['author']:
            out_line = ''
            if 'family' in author.keys():
                out_line += author['family'] + ','
            else:
                out_line += ','
            if 'given' in author.keys():
                out_line += author['given'] + ',\"'
            else:
                out_line += ',\"'
            out_line += citations[i] + '\",'
            out_line += 'https://www.google.com/search?q='
            if 'given' in author.keys():
                out_line += author['given']
            if 'family' in author.keys():
                out_line += '%20' + author['family']
            if 'title' in contents[i].keys():
                out_line += '+' + (contents[i]['title']).replace(' ', '+')
            out_line += '\n'
            csv.write(out_line)
    else:
        out_line = ',,\"' + citations[i] + '\",\n'
        csv.write(out_line)
    #print('Title: ', contents[i]['title'])
    #print()

csv.close()
print('Completed')
