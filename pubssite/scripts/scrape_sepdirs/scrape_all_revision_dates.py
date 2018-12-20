# This script pulls from all individual SEP articles and updates their revision date in the SEP pubs database
# This should only be run once, covering new entries in the database
# Must run scrape_recent_revision_dates for subsequent updates
# Pat Healy - pat.healy@pitt.edu
# Started: 12/20/18
# Last Updated: 12/20/18

if __name__ == '__main__':
    pw = str(input("Give the password for inpho@sql.inphoproject.org: "))
    db = mysql.connector.connect(
      host="sql.inphoproject.org",
      user="inpho",
      passwd=pw,
      database="pubs"
    )
    cursor = db.cursor()