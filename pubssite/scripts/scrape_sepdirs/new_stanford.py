# DEPRECATED! - all functionality offered by this is now offered by scrape_collections.py
# By Pat Healy
# goal to scrape https://plato.stanford.edu/new.html

import pycurl
import re
import random
from io import BytesIO
from bs4 import BeautifulSoup
import json

url = "https://plato.stanford.edu/new.html"

def add_entry(title, sepdir, revised_or_new, date, authors):
    "Adds entry to entries dictionary"
    
    if in_db(sepdir):
        entries[title]['revised_or_new'] = revised_or_new
        entries[title]['authors'] = '\"' + authors + '\"'
        if revised_or_new == 'REVISED':
            entries[title]['revised_date'] = date
            if entries[title]['publish_date'] == None:
                entries[title]['publish_date'] = ''
        else:
            entries[title]['publish_date'] = date
            entries[title]['revised_date'] = ''
    else:
        entries[title] = {}
        entries[title]['sepdir'] = sepdir
        entries[title]['publish_date'] = date
        entries[title]['revised_or_new'] = revised_or_new
        entries[title]['authors'] = '\"' + authors + '\"'
        entries[title]['in_database'] = compare_to_pubsdata(sepdir)
    
def compare_to_pubsdata(key):
    "Returns true if we have this entry in pubsdata"
    for entry in pubsdata:
        if entry == key:
            return True
    return False

def in_db(key):
    "Returns true if we have this entry in stanford_data"
    for entry in entries.values():
        if entry['sepdir'] == key:
            return True
    return False

#Loads pubdata into RAM
def convert_date(date):
    "Convert date to typical format"
    #remove ending spaces
    date = date.strip()
    
    #split string into separate components
    parts = date.split(' ')
    
    #handle month
    if parts[0] == 'January':
        parts[0] = '01'
    elif parts[0] == 'February':
        parts[0] = '02'
    elif parts[0] == 'March':
        parts[0] = '03'
    elif parts[0] == 'April':
        parts[0] = '04'
    elif parts[0] == 'May':
        parts[0] = '05'
    elif parts[0] == 'June':
        parts[0] = '06'
    elif parts[0] == 'July':
        parts[0] = '07'
    elif parts[0] == 'August':
        parts[0] = '08'
    elif parts[0] == 'September':
        parts[0] = '09'
    elif parts[0] == 'October':
        parts[0] = '10'
    elif parts[0] == 'November':
        parts[0] = '11'
    elif parts[0] == 'December':
        parts[0] = '12'
    else:
        return ''
    
    #handle day
    if len(parts[1]) < 2:
        parts[1] = '0' + parts[1]
    
    #assumes only 4 digit years
    
    return parts[2] + parts[0] + parts[1]
    
    

pubs = open('pubsdata')
pubsdata = []
for line in pubs:
    pubsdata.append(line.strip())
pubs.close()

#load entries into ram
prev_data = open('stanford_data')
entries = json.loads(prev_data.read())
prev_data.close()

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
for link in soup.find(id='content').find_all('li'):
    text = link.text
    title = link.a.text
    sepdir = (link.a.get('href'))[(link.a.get('href')).find('/')+1:-1]
    date_block = text[text.find(')'):]
    date_block = date_block[date_block.find('[')+1:date_block.find(']')]
    revised_or_new = date_block[:date_block.find(':')]
    date = (date_block[date_block.find(':')+1:]).replace(',', '')
    date = convert_date(date)
    
    authors = (text[text.find('(')+1:text.find(')')]).replace(',', '\,')
    add_entry(title, sepdir, revised_or_new, date, authors)
    
#open csv, a csv file, for writing  
csv = open('stanford_data.csv', "w", encoding='utf-8') 

#title row
columnTitleRow = "title, sepdir, authors, publish_date, revised_date, in_database, link, revised_or_new\n"
csv.write(columnTitleRow)

#write out all entries
for key, values in entries.items():
    #print('Name: ', key)
    #for k, v in values.items():
        #print('\t', k, ': ', v)
    if 'revised_date' not in values.keys():
        values['revised_date'] = ''
    if 'link' not in values.keys():
        values['link'] = ''
    if 'authors' not in values.keys():
        values['authors'] = ''
    if 'publish_date' not in values.keys():
        values['publish_date'] = ''
    if 'revised_or_new' not in values.keys():
        values['revised_or_new'] = ''
    if 'in_database' not in values.keys():
        values['in_database'] = ''
        
        
    row = key.replace(',', ':') + ',' +values['sepdir'] + ',' + values['authors'] + ',' + values['publish_date'] + ',' + values['revised_date'] + ',' + str(values['in_database']) + ',' + values['link'] + ',' + values['revised_or_new'] + '\n'
    csv.write(row)
csv.close()
        
json_file = open('stanford_data', 'w')
json_file.write(json.dumps(entries))
json_file.close()

print('Complete')
    
