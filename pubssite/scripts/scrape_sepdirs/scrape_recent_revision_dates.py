# Scrapes the recent updates on SEP for revision dates
# Updates revision dates in collections_update entries on the pubs sep database
# Patrick Healy - pat.healy@pitt.edu
# Started 12/20/18
# Last Updated 12/20/18
import pycurl
from io import BytesIO
from bs4 import BeautifulSoup
import pickle
import json
import mysql.connector
import codecs
import datetime
import traceback

pubsdata = {}
updates = {}
additions = {}
months = {'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12'}

def set_update_mode():
    sql = "SET SQL_SAFE_UPDATES = 0;"
    cursor.execute(sql)

def get_pubs_data():
    sql = "SELECT collections.collection_name, collections_update.revision_date, collections.collection_id FROM pubs.collections JOIN pubs.collections_update ON collections.collection_id = collections_update.fk_collections_id WHERE collections.owner = \'sep\';"
    
    #Execute sql and get response
    cursor.execute(sql)
    results = cursor.fetchall()
    
    for entry in results:
        entry = list(entry)
        if(not entry[1] == None):
            entry[1] = str(entry[1]).replace('-', '')
        if (entry[0])[:4] == 'SEP ':
            pubsdata[(entry[0])[4:]] = [entry[1], entry[2]]
        else:
            pubsdata[entry[0]] = [entry[1], entry[2]]

def convert_date(dt):
    dt = dt.strip()
    year = dt[-4:]
    month = months[dt[:dt.find(' ')].strip()]
    day = dt[dt.find(' ') + 1:dt.find(' ') + 3].strip()
        
    if len(day) == 1:
        day = '0' + day
    
    date = year + month + day
    return date
    
def get_recent_updates():
    print("Scraping new updates")
    url = 'https://plato.stanford.edu/new.html'
    try:
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
            sepdir = (link.a.get('href'))[(link.a.get('href')).find('/')+1:-1]
            date_block = text[text.find(')'):]
            date_block = date_block[date_block.find('[')+1:date_block.find(']')]
            date = (date_block[date_block.find(':')+1:]).replace(',', '')
            date = convert_date(date)
            
            updates[sepdir] = date.strip()
            
    except:
        traceback.print_exc()
        print("New updates could not be scraped")
    
    
def compare_update_data():
    print()
    print("Comparing sep data to pubs database")
    print("=====================================")
    toDelete = []
    for key, val in updates.items():
        if key in pubsdata.keys():
            if int(val) <= int(pubsdata[key][0]):
                print("Will not update " + key)
                toDelete.append(key)
            else:
                print("Update: " + key + ": " + val + ", " + pubsdata[key][0])
        else:
            print("New: " + key + ": " + val)
            additions[key] = val
            toDelete.append(key)
    
    for key in toDelete:
        del updates[key]
    print("=====================================")
    
def add_to_pubs(sepdir, dt):
    try:
        sql = "INSERT INTO pubs.collections (collection_name, submitter, owner) VALUES (\'SEP " + sepdir + "\', \'HealyScript\', \'sep\');" 
        cursor.execute(sql)
        db.commit()

        sql = "INSERT INTO pubs.collections_update (fk_collections_id, revision_date) VALUES (LAST_INSERT_ID(), \'" + dt + "\');"
        cursor.execute(sql)
        db.commit()
    except:
        print("Failed to add " + sepdir)
        traceback.print_exc()
    
def update_pubs_entry(sepdir, dt):
    try:
        coll_id = pubsdata[sepdir][1]
        sql = "UPDATE pubs.collections_update SET revision_date=" + dt + " WHERE collections_update.fk_collections_id=" + str(coll_id) + ";"
        
        cursor.execute(sql)
        db.commit()
        
    except:
        print("Failed to update " + sepdir)
        traceback.print_exc()
    
def update_pubs():
    print()
    print("Updates")
    print("=====================================")
    for key, val in updates.items():
        print(key + ": " + str(val))
        update_pubs_entry(key, val)
    print("=====================================")
    
    print()
    print("Additions")
    print("=====================================")
    for key, val in additions.items():
        print(key + ": " + str(val))
        add_to_pubs(key, val)
    print("=====================================")
    
if __name__ == '__main__':
    pw = str(input("Give the password for inpho@sql.inphoproject.org: "))
    db = mysql.connector.connect(
      host="sql.inphoproject.org",
      user="inpho",
      passwd=pw,
      database="pubs"
    )
    cursor = db.cursor()
    
    get_pubs_data()
    get_recent_updates()
    compare_update_data()
    set_update_mode()
    update_pubs()
    
    print()
    print("Completed.")