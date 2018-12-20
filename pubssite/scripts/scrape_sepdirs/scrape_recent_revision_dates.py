# Scrapes the recent updates on SEP for revision dates
# Updates revision dates in collections_update entries on the pubs sep database
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