# Scrapes the recent updates on SEP for revision dates
# Updates revision dates in collections_update entries on the pubs sep database
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

class Scraped_Whats_New:
    def __init__(self):
        self.pubsdata = {}
        self.updates = {}
        self.additions = {}
        self.months = {'January':'01', 'February':'02', 'March':'03', 'April':'04', 'May':'05', 'June':'06', 'July':'07', 'August':'08', 'September':'09', 'October':'10', 'November':'11', 'December':'12'}
    def set_update_mode(self):
        sql = "SET SQL_SAFE_UPDATES = 0;"
        self.cursor.execute(sql)

    def get_pubs_data(self):
        sql = "SELECT collections.collection_name, collections_update.revision_date, collections.collection_id FROM pubs.collections JOIN pubs.collections_update ON collections.collection_id = collections_update.fk_collections_id WHERE collections.owner = \'sep\';"

        #Execute sql and get response
        self.cursor.execute(sql)
        results = self.cursor.fetchall()

        for entry in results:
            entry = list(entry)
            if(not entry[1] == None):
                entry[1] = str(entry[1]).replace('-', '')
            if (entry[0])[:4] == 'SEP ':
                self.pubsdata[(entry[0])[4:]] = [entry[1], entry[2]]
            else:
                self.pubsdata[entry[0]] = [entry[1], entry[2]]

    def convert_date(self, dt):
        dt = dt.strip()
        year = dt[-4:]
        month = self.months[dt[:dt.find(' ')].strip()]
        day = dt[dt.find(' ') + 1:dt.find(' ') + 3].strip()

        if len(day) == 1:
            day = '0' + day

        date = year + month + day
        return date

    def get_recent_updates(self):
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
                date = self.convert_date(date)

                self.updates[sepdir] = date.strip()

        except:
            traceback.print_exc()
            print("New updates could not be scraped")


    def compare_update_data(self):
        print()
        print("Comparing sep data to pubs database")
        print("=====================================")
        toDelete = []
        for key, val in self.updates.items():
            if key in self.pubsdata.keys():
                if int(val) <= int(self.pubsdata[key][0]):
                    print("Will not update " + key)
                    toDelete.append(key)
                else:
                    print("Update: " + key + ": " + val + ", " + self.pubsdata[key][0])
            else:
                print("New: " + key + ": " + val)
                self.additions[key] = val
                toDelete.append(key)

        for key in toDelete:
            del self.updates[key]
        print("=====================================")

    def add_to_pubs(self, sepdir, dt):
        try:
            sql = "INSERT INTO pubs.collections (collection_name, submitter, owner) VALUES (\'SEP " + sepdir + "\', \'HealyScript\', \'sep\');" 
            self.cursor.execute(sql)
            self.db.commit()

            sql = "INSERT INTO pubs.collections_update (fk_collections_id, revision_date) VALUES (LAST_INSERT_ID(), \'" + dt + "\');"
            self.cursor.execute(sql)
            self.db.commit()
        except:
            print("Failed to add " + sepdir)
            traceback.print_exc()

    def update_pubs_entry(self, sepdir, dt):
        try:
            coll_id = self.pubsdata[sepdir][1]
            sql = "UPDATE pubs.collections_update SET revision_date=" + dt + " WHERE collections_update.fk_collections_id=" + str(coll_id) + ";"

            self.cursor.execute(sql)
            self.db.commit()

        except:
            print("Failed to update " + sepdir)
            traceback.print_exc()

    def update_pubs(self):
        print()
        print("Updates")
        print("=====================================")
        for key, val in self.updates.items():
            print(key + ": " + str(val))
            self.update_pubs_entry(key, val)
        print("=====================================")

        print()
        print("Additions")
        print("=====================================")
        for key, val in self.additions.items():
            print(key + ": " + str(val))
            self.add_to_pubs(key, val)
        print("=====================================")

    def update(self):
        "Main method of Scraped_Whats_New"
        pw = str(input("Give the password for inpho@sql.inphoproject.org: "))
        self.db = mysql.connector.connect(
          host="sql.inphoproject.org",
          user="inpho",
          passwd=pw,
          database="pubs"
        )
        self.cursor = self.db.cursor()

        self.get_pubs_data()
        self.get_recent_updates()
        self.compare_update_data()
        self.set_update_mode()
        self.update_pubs()

        print()
        print("Completed.")
    
if __name__ == '__main__':
    instance = Scraped_Whats_New()
    instance.update()