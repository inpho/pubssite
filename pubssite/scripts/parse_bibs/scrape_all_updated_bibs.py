# Scrapes all bibliographies from SEP where revision date > updated date
# adds citation entries, author entries, and updates collections_updates 
# Runtime is very long
# Patrick Healy - pat.healy@pitt.edu
# Started 12/20/18
# Last Updated 1/3/18
import pycurl
from io import BytesIO
from bs4 import BeautifulSoup
import pickle
import json
import mysql.connector
import codecs
import datetime
import traceback

class Bib_Updater:
    def __init__(self):
        self.pubsdata = {}
        
    def set_update_mode(self):
        sql = "SET SQL_SAFE_UPDATES = 0;"
        self.cursor.execute(sql)

    def get_pubs_data(self):
        sql = "SELECT collections.collection_name, collections_update.revision_date, collections_update.update_date collections.collection_id FROM pubs.collections JOIN pubs.collections_update ON collections.collection_id = collections_update.fk_collections_id WHERE collections.owner = \'sep\';"

        #Execute sql and get response
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        for entry in results:
            entry = list(entry)
            if(not entry[1] == None):
                entry[1] = str(entry[1]).replace('-', '')
            if (entry[0])[:4] == 'SEP ':
                self.pubsdata[(entry[0])[4:]] = [entry[1], entry[2], entry[3]]
            else:
                self.pubsdata[entry[0]] = [entry[1], entry[2], entry[3]]
        
    def update(self):
        pw = str(input("Give the password for inpho@sql.inphoproject.org: "))
        self.db = mysql.connector.connect(
          host="sql.inphoproject.org",
          user="inpho",
          passwd=pw,
          database="pubs"
        )
        self.cursor = self.db.cursor()

        self.get_pubs_data()
        self.determine_updates()
        #self.set_update_mode()

if __name__ == '__main__':
    updater = Bib_Updater()
    updater.update()
    