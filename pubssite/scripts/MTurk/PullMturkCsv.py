import MySQLdb

pw = str(raw_input("Give the password for inpho@sql.inphoproject.org: "))

db = MySQLdb.connect("sql.inphoproject.org","inpho",pw,"pubs")

cursor = db.cursor()

sql = "SELECT authors.firstname, authors.lastname, authors.gender, citations.raw FROM pubs.authors JOIN pubs.author_of ON authors.author_id=author_of.author_id JOIN pubs.citations ON author_of.citation_id=citations.citation_id WHERE CHAR_LENGTH(citations.raw) > 0 GROUP BY author_of.author_id;"

cursor.execute(sql)
results = cursor.fetchall()

outFile = open("pubs_authors.csv", "w")

outFile.write("FirstName,LastName,Gender,Citation\n")
for entry in results:
    outFile.write("\"" + str(entry[0]) + "\",\"" + str(entry[1]) + "\",\"" + str(entry[2]) + "\",\"" + str(entry[3]).replace("\"", "") + "\"\n")

outFile.close()
db.close()