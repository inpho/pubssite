# Scrapes all bibliographies from SEP where revision date > updated date
# adds citation entries, author entries, and updates collections_updates 
# Runtime is very long
# Patrick Healy - pat.healy@pitt.edu
# Started 12/20/18
# Last Updated 12/20/18

if __name__ == '__main__':
    pw = str(input("Give the password for inpho@sql.inphoproject.org: "))
    db = mysql.connector.connect(
      host="sql.inphoproject.org",
      user="inpho",
      passwd=pw,
      database="pubs"
    )
    cursor = db.cursor()