import MySQLdb
import codecs

pw = str(input("Give the password for inpho@sql.inphoproject.org: "))

db = MySQLdb.connect("sql.inphoproject.org","inpho",pw,"pubs")

cursor = db.cursor()

sql = "SELECT authors.firstname, authors.lastname, authors.gender, citations.raw, citations.pubtype, citations.title, collections.collection_name FROM pubs.authors JOIN pubs.author_of ON authors.author_id=author_of.author_id JOIN pubs.citations ON author_of.citation_id=citations.citation_id JOIN pubs.member_of_collection ON citations.citation_id=member_of_collection.citation_id JOIN pubs.collections ON collections.collection_id=member_of_collection.collection_id WHERE CHAR_LENGTH(citations.raw) > 0 AND SUBSTRING(collection_name, 1, 3)='SEP' AND authors.verified = 0 GROUP BY author_of.author_id;"

cursor.execute(sql)
results = cursor.fetchall()

outFile = codecs.open("pubs_authors.csv", "w", "utf-8")

outFile.write("FirstName,LastName,Gender,Citation,Pubtype,Title,Collection\n")
for entry in results:
    outFile.write("\"" + str(entry[0]).replace("\"", "\"\"") + "\",\"" + str(entry[1]).replace("\"", "\"\"") + "\",\"" + str(entry[2]).replace("\"", "\"\"") + "\",\"" + str(entry[3]).replace("\"", "\"\"") + "\",\"" + str(entry[4]).replace("\"", "\"\"") + "\",\"" + str(entry[5]).replace("\"", "\"\"") + "\",\"" + "https://plato.stanford.edu/entries/" + str(entry[6])[4:].replace("\"", "\"\"") + "/\"\n")

outFile.close()
db.close()