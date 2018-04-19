# scrapes a bibliography from plato.stanford.edu; if run directly, runs 
import pycurl
import re
import random
from io import BytesIO
from bs4 import BeautifulSoup
import json
import rython
import HTMLParser
import sys
import string

#Object of a scraped bibliography with names, titles, full citations parsed
class Scraped_Bib:
    def __init__(self, sepdir):
        "On init, scrape this sepdir"
        self.ctx = rython.RubyContext(requires=["rubygems", "anystyle/parser", "namae"])
        self.ctx("Encoding.default_internal = 'UTF-8'")
        self.ctx("Encoding.default_external = 'UTF-8'")
        self.sepdir = sepdir
        self.entries = self.scrape(sepdir)

    def getStyleBibliography(self, biblioList):
        "Uses AnyStyle to parse a bibliography"
        anystyle = self.ctx("Anystyle.parser")
        anyStyleList = []
        h =  HTMLParser.HTMLParser()
        for biblio in biblioList:
            text = biblio.text.replace('\n','').encode('utf-8')
            printable = set(string.printable)
            text = ''.join(filter(lambda x: x in printable, text))
            parsed = anystyle.parse(text)[0]
            anyStyleList.append(parsed)
        return anyStyleList

    def getNames(self, allNames):
        "Uses Namae to parse a set of names"
        namae = self.ctx("Namae")
        parsed = []
        try:
            parsed = namae.parse(allNames.encode('utf-8'))
        except Exception:
            print('Fault parsing names')
            parsed = [{'family':allNames}]
        return parsed
    
    def scrape(self, sepdir):
        "Scrapes a bibliography by sepdir from plato.stanford.edu"
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

        components = self.getStyleBibliography(soup.find(id='bibliography').find_all('li'))

        i = 0
        #For each citation in the bibliography
        for citation in soup.find(id='bibliography').find_all('li'):
            if 'author' in components[i].keys():
                names = self.getNames(components[i]['author'])
                for nm in names:
                    entry = {}
                    entry['full_citation'] = (citation.text).replace('\n', ' ').encode('utf-8')
                    printable = set(string.printable)
                    entry['full_citation'] = ''.join(filter(lambda x: x in printable, entry['full_citation']))
                    

                    if 'family' in nm:
                        entry['family_name'] = nm['family']
                    else:
                        entry['family_name'] = ''

                    if 'given' in nm.keys():
                        entry['given_name'] = nm['given']
                    else:
                        entry['given_name'] = ''

                    if 'title' in components[i]:
                        entry['title'] = components[i]['title']
                    else:
                        entry['title'] = ''

                    entries.append(entry)

            else:
                entry = {}
                entry['full_citation'] = (citation.text).replace('\n', ' ')
                entry['family_name'] = ''
                entry['given_name'] = ''
                if 'title' in components[i]:
                    entry['title'] = components[i]['title']
                else:
                    entry['title'] = ''
                entries.append(entry)
            i = i + 1
        return entries
    
    def save_json(self):
        "Saves a JSON representation of the entries"
        json_file_name = self.sepdir + '_bib_json'
        outFile = open(json_file_name, 'w')
        outFile.write(json.dumps(self.entries))
        outFile.close()
        print('Saved JSON to ' + json_file_name)
    
    def save_csv(self):
        "Saves a CSV of the entries"
        csv_file_name = self.sepdir + '_bib.csv'
        csv = open(csv_file_name, 'w')
        
        first_line = 'Family Name, Given Name, Gender,  Title, Full Citation, Google Link\n'
        csv.write(first_line)
        
        for entry in self.entries:
            for key in entry.keys():
                if entry[key] == None:
                    entry[key] = ''
            
            line = ''
            line = line + entry['family_name'] + ','
            line = line + entry['given_name'] + ',,\"'
            line = line + entry['title'] + '\",\"'
            line = line + entry['full_citation'] + '\",\"'
            google_line = 'https://www.google.com/search?q='
            google_line = google_line + entry['given_name'] + '+'
            google_line = google_line + entry['family_name'] + '+'
            google_line = google_line + ((entry['title']).replace(' ', '+')) + '+'
            line = line + google_line + '\"\n'
            csv.write(line)
        
        print('Saved csv to ' + csv_file_name)
        csv.close() 

    def save(self):
        "Saves both a JSON and CSV"
        self.save_json()
        self.save_csv()
        


#scapes a single entry, based on sepdir
#THIS CAN BE CHANGED TO SCRAPE ALL PAGES

    def get_entries(self):
        "Returns the entries list from this object"
        return self.entries
    
    def get_sepdir(self):
        "Returns this object's sepdir"
        return self.sepdir

if __name__ == '__main__':
    if len(sys.argv) == 2:
        sepdir = sys.argv[1]
        print('Scraping ' + sepdir + '...')
        sb = Scraped_Bib(sepdir)
        sb.save()
        print('Complete')
    else:
        print('Syntax: python stanford_bib_single.py <sepdir>')
        