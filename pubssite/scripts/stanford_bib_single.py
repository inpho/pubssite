# goal to scrape a bibliography from plato.stanford.edu

import pycurl
import re
import random
from io import BytesIO
from bs4 import BeautifulSoup
import json

entries = {}
   
def get_fn(auth):
    "Gets the first name, based on an author name string"
    fn_segment = auth[auth.find(',') + 1:]
    names = fn_segment.split(' ')
    for nm in names:
        if len(nm) > 2:
            return nm
    return ''

def get_ln(auth):
    "Gets the last name, based on an author name string"
    ln = auth[:auth.find(',')]
    return ln

def get_initials(auth):
    "Gets the initials, based on an author name string"
    initials = ''
    
    names = auth.split(' ')
    for nm in names:
        if len(nm) == 2:
            initials = initials + nm
    
    return initials

def scrape(sepdir):
    "Scrapes the bibliography of a single entry, by url"
    url = 'https://plato.stanford.edu/entries/' + sepdir + '/'
    citations = []
    
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
        #Text of the full citation
        link_str = (link.text).replace('\n', ' ')
        
        #Finds year with regex as checkpoint to find authors names
        year = (re.search('\d\d\d\d',link_str)).group(0)
        
        #Gets a list of authors names
        authors = link_str[:link_str.find(year)-2]
        authors_list = authors.split(' and ')
        
        #Checks if there is more than two authors, or some other special case
        special_case = False
        for auth in authors_list:
            if auth.count(',') > 1:
                special_case = True
        
        #If special case, don't worry about it
        if special_case:
            citation = {}
            citation['full_citation'] = link_str.strip()
            citation['last_name'] = ''
            citation['first_name'] = ''
            citation['initial'] = ''
            citation['gender'] = ''
            citations.append(citation)
            continue
        
        #For each author in this citation
        for auth in authors_list:
            #If there's a comma, this is a plain LastName, FirstName Initial.
            if auth.count(',') > 0:
                citation = {}
                citation['full_citation'] = link_str.strip()
                citation['last_name'] = get_ln(auth).strip()
                citation['first_name'] = get_fn(auth).strip()
                citation['initial'] = get_initials(auth).strip()
                citation['gender'] = ''
                citations.append(citation)
            #Otherwise, check a few cases
            else:
                citation = {}
                citation['full_citation'] = link_str.strip()
                citation['initial'] = ''
                citation['gender'] = ''
                #If this is the second name in a list of two without initials provided
                if len(auth.split(' ')) == 2:
                    nms = auth.split(' ')
                    citation['last_name'] = nms[1]
                    citation['first_name'] = nms[0]
                #If this is the second name in a list of two with initials provided
                elif len(auth.split(' ')) == 3:
                    nms = auth.split(' ')
                    citation['initial'] = nms[1]
                    citation['last_name'] = nms[2]
                    citation['first_name'] = nms[0]
                #Otherwise, just plop it all in last_name
                else:
                    citation['last_name'] = auth.strip()
                    citation['first_name'] = ''
                #Add this citation to the list of citations
                citations.append(citation)
    #Add this list of citations to the dictionary            
    entries[sepdir] = citations

#scapes a single entry, based on sepdir
#THIS CAN BE CHANGED TO SCRAPE ALL PAGES
scrape('social-ontology')

#Loops through every entry (by sepdir) and creates a csv file for each
for sep, values in entries.items():
    #print(sep)
    file_n = '' + sep + '_bib.csv'
    csv = open(file_n, 'w')
    line = 'Last,Initial,First,Gender,Full Citation\n'
    csv.write(line)
    for dicts in values:
        line = ''
        line = line + dicts['last_name'] + ','
        line = line + dicts['initial'] + ','
        line = line + dicts['first_name'] + ','
        line = line + dicts['gender'] + ','
        line = line + '\"' + dicts['full_citation'] + '\"' + '\n'
        csv.write(line)
        #for key, value in dicts.items():
        #    print(key, ': ', value)
        #print()
    csv.close()
    print('Created: ', file_n)
    
print('Complete')
        
        
        
        
        
        