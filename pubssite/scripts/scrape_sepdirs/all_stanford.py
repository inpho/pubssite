# goal to scrape https://plato.stanford.edu/new.html

import pycurl
from io import BytesIO
from bs4 import BeautifulSoup
import pickle
import json

#url we are scraping from
url = "https://plato.stanford.edu/published.html"

#earliest year of entries we care about
start_year = 1980

#A dictionary of entries, will eventually be a dictionary of dictionaries
entries = {}

def add_entry(key, value):
    "Adds an entry to the dictionary, if published after start_year"
    if int(value[1][-4:]) >= start_year:
        entries[key] = {}
        entries[key]['link'] = value[0]
        entries[key]['publish_date'] = convert_date(value[1].replace(',', ''))
        
        #slices link to find sepdir
        sepdir = value[0]
        sepdir = sepdir[:-1]
        sepdir = sepdir[sepdir.rfind('/')+1:]
        entries[key]['sepdir'] = sepdir
        
        #calls compare_to_pubsdata to see if we already have this entry
        entries[key]['in_database'] = compare_to_pubsdata(sepdir)
        
        entries[key]['revised_date'] = ''
        entries[key]['revised_or_new'] = ''
        entries[key]['authors'] = ''
        
        #Confirms to console that this entry was added
        #print('Added: ', key)

def compare_to_pubsdata(key):
    "Returns true if we have this entry in pubsdata"
    for entry in pubsdata:
        if entry == key:
            return True
    return False

#The following lines scrape the html from url
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


buffer = BytesIO()
c = pycurl.Curl()
c.setopt(c.URL, url)
#included for SSL stuff
c.setopt(pycurl.SSL_VERIFYPEER, 0)   
c.setopt(pycurl.SSL_VERIFYHOST, 0)
c.setopt(c.WRITEDATA, buffer)
c.perform()
c.close()
body = buffer.getvalue()

#soup contains the html from url
soup = (BeautifulSoup(body.decode('iso-8859-1'),'html.parser'))

#A dictionary of basic link data
main_page_links = {}

#Parses through the page source for entries
for link in soup.find(id='content').find_all('li'):
    main_page_links[link.a.text] = (link.a.get('href'), link.text[link.text.rfind('[') + 1:-1])

#Loads pubsdata into RAM
pubs = open('pubsdata')
pubsdata = []
for line in pubs:
    pubsdata.append(line.strip())
pubs.close()
    
#Calls 'add_entry' for every basic link
for keys, values in main_page_links.items():
    add_entry(keys,values)

#open csv, a csv file, for writing  
csv = open('stanford_data.csv', "w", encoding='utf-8') 

#title row
columnTitleRow = "title, sepdir, publish_date, in_database, link\n"
csv.write(columnTitleRow)

#write out all entries
for key, values in entries.items():
    #print('Name: ', key)
    #for k, v in values.items():
        #print('\t', k, ': ', v)
    row = key.replace(',', ':') + ',' + values['sepdir'] + ',' + values['publish_date'] + ',' + str(values['in_database']) + ',' + values['link'] + '\n'
    csv.write(row)
csv.close()
    
#pyc_file = open('stanford_data', 'wb')
#pickle.dump(entries, pyc_file)
#pyc_file.close()

json_file = open('stanford_data', 'w')
json_file.write(json.dumps(entries))
json_file.close()

print('Complete')