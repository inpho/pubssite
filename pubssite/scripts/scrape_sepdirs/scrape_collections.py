# Patrick Healy - pat.healy@pitt.edu
# Last Updated 12/20/18
# goal to scrape https://plato.stanford.edu/published.html
# adds all new SEP articles to the pubs database
# adds empty collections_update entries for every new collection, too

import pycurl
from io import BytesIO
from bs4 import BeautifulSoup
import pickle
import json
import mysql.connector
import codecs
import datetime

#url we are scraping from
url = "https://plato.stanford.edu/published.html"

#earliest year of entries we care about
start_year = 1980

#A dictionary of entries, will eventually be a dictionary of dictionaries
entries = {}
pubsdata = {}
toAdd = []
toUpdate = []

def add_entry(key, value):
    "Adds an entry to the dictionary"
    entries[key] = {}
    entries[key]['link'] = value[0]
    entries[key]['publish_date'] = convert_date(value[1].replace(',', ''))

    #slices link to find sepdir
    sepdir = value[0]
    sepdir = sepdir[:-1]
    sepdir = sepdir[sepdir.rfind('/')+1:]
    entries[key]['sepdir'] = "SEP " + sepdir

    #calls compare_to_pubsdata to see if we already have this entry
    entries[key]['in_database'] = compare_to_pubsdata(sepdir)
    
    entries[key]['collection_id'] = None
    
    if entries[key]['in_database']:
        entries[key]['last_revised'] = pubsdata[entries[key]['sepdir']][0]
        entries[key]['collection_id'] = pubsdata[entries[key]['sepdir']][1]
    else:
        entries[key]['last_revised'] = None

    #Confirms to console that this entry was added
    #print('Added: ', key)

def compare_to_pubsdata(key):
    "Returns true if we have this entry in pubsdata"
    for sepdir in pubsdata.keys():
        if key == sepdir[4:]:
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



#Loads pubsdata into RAM, taking from database
def scrape_sep():
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

    #Calls 'add_entry' for every basic link
    for keys, values in main_page_links.items():
        add_entry(keys,values)


def save_data():
    #open csv, a csv file, for writing  
    toAddCsv = codecs.open('added_' + str(datetime.datetime.now()) + '.csv', "w", "utf-8")
    toUpdateCsv = codecs.open('updated_' + str(datetime.datetime.now()) + '.csv', "w", "utf-8")

    #title row
    columnTitleRow = "sepdir, publish_date\n"
    toAddCsv.write(columnTitleRow)

    columnTitleRow = "sepdir, publish_date, collection_id\n"
    toUpdateCsv.write(columnTitleRow)


    #write out all entries
    for key, values in entries.items():
        if not values['in_database']:
            row = values['sepdir'] + ',' + values['publish_date'] + '\n'
            val = (values['sepdir'], values['publish_date'])
            toAdd.append(val)
            toAddCsv.write(row)
        else:
            row = values['sepdir'] + ',' + values['publish_date'] + ',' + str(values['collection_id']) + '\n'
            val = (values['publish_date'], str(values['collection_id']))
            toUpdate.append(val)
            toUpdateCsv.write(row)

    toAddCsv.close()
    toUpdateCsv.close()

def pull_pubs():
    sql = "SELECT collections.collection_name, collections_update.revision_date, collections.collection_id FROM pubs.collections JOIN pubs.collections_update ON collections.collection_id = collections_update.fk_collections_id WHERE collections.owner = \'sep\';"
    
    #Execute sql and get response
    cursor.execute(sql)
    results = cursor.fetchall()

    for entry in results:
        if(not entry[1] == None):
            entry[1] = str(entry[1]).replace('-', '')
        if (entry[0])[:4] == 'SEP ':
            pubsdata[entry[0]] = [entry[1], entry[2]]
        else:
            pubsdata[("SEP " + entry[0])] = [entry[1], entry[2]]
    
def set_unsafe():
    sql = "SET SQL_SAFE_UPDATES = 0;"
    cursor.execute(sql)
    
def add_new_collections():
    for addition in toAdd:
        sql = "INSERT INTO pubs.collections (collection_name, submitter, owner) VALUES (\'" + addition[0] + "\', \'HealyScript\', \'sep\');" 
        cursor.execute(sql)
        db.commit()
        
        sql = "INSERT INTO pubs.collections_update (fk_collections_id) VALUES (LAST_INSERT_ID());"
        cursor.execute(sql)
        db.commit()
        print("Added: " + addition[0])

def update_collections():
    sql = "UPDATE pubs.collections_update SET revision_date=%s WHERE collections_update.fk_collections_id = %s;"
    
    #print(toUpdate)
    cursor.executemany(sql, toUpdate)
    db.commit()

if __name__ == '__main__':
    pw = str(input("Give the password for inpho@sql.inphoproject.org: "))
    db = mysql.connector.connect(
      host="sql.inphoproject.org",
      user="inpho",
      passwd=pw,
      database="pubs"
    )
    cursor = db.cursor()

    pull_pubs()
    scrape_sep()
    save_data()
    set_unsafe()
    add_new_collections();
    #update_collections();
    
    print("\n====================================================================\n")
    #print("All other entries updated\n")
    print('Complete')