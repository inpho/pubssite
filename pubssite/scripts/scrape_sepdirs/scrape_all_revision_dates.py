# This script pulls from all individual SEP articles and updates their revision date in the SEP pubs database
# This should only be run once, covering new entries in the database
# Must run scrape_recent_revision_dates for subsequent updates
# Pat Healy - pat.healy@pitt.edu
# Started: 12/20/18
# Last Updated: 12/20/18
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
months = {'Jan':'01', 'Feb':'02', 'Mar':'03', 'Apr':'04', 'May':'05', 'Jun':'06', 'Jul':'07', 'Aug':'08', 'Sep':'09', 'Oct':'10', 'Nov':'11', 'Dec':'12'}

def set_update_mode():
    sql = "SET SQL_SAFE_UPDATES = 0;"
    cursor.execute(sql)

def get_pubs_data():
    sql = "SELECT collections.collection_name, collections_update.revision_date, collections.collection_id, collections_update.fk_parent_id, collections_update.is_retired_document FROM pubs.collections JOIN pubs.collections_update ON collections.collection_id = collections_update.fk_collections_id WHERE collections.owner = \'sep\';"
    
    #Execute sql and get response
    cursor.execute(sql)
    results = cursor.fetchall()
    
    for entry in results:
        entry = list(entry)
        if(not entry[1] == None):
            entry[1] = str(entry[1]).replace('-', '')
        if (entry[0])[:4] == 'SEP ':
            pubsdata[(entry[0])[4:]] = [entry[1], entry[2], entry[3], entry[4]]
        else:
            pubsdata[entry[0]] = [entry[1], entry[2], entry[3], entry[4]]

def update_rev_date(sep, update_id):
    print("Update " + sep)
    url = 'https://plato.stanford.edu/entries/' + sep + '/'
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

        pubInfo = soup.find(id='pubinfo').text
        date = pubInfo[-12:].strip()

        year = date[-4:]
        
        day = date[-8:-6].strip()
        if len(day) == 1:
            day = '0' + day
         
        month = months[date[:3]]
        
        fullDate = year + month + day

        print("date: " + date)
        #print("year: " + year)
        #print("month: " + month)
        #print("day: " + day)
        print("formatted date: " + fullDate)
        
        sql = "UPDATE collections_update SET revision_date=\'" + str(fullDate) + "\' WHERE fk_collections_id=" + str(update_id) + ";"
    
        #Execute sql and get response
        cursor.execute(sql)
        db.commit()
        
    except:
        #traceback.print_exc()
        print(sep + " could not be updated")
    
    
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
    
    #count = 0
    
    set_update_mode()
    
    for key, val in pubsdata.items():
        #print(key + " : " + str(val))
        if val[0] is None and val[2] is None and val[3] == 0:
            print()
            update_rev_date(key, val[1])
            #count = count + 1
            #if count > 5:
            #    break
    
    print()
    print("Completed.")
            