import MySQLdb

pw = str(raw_input("Give the password for inpho@sql.inphoproject.org: "))

db = MySQLdb.connect("sql.inphoproject.org","inpho",pw,"pubs")

cursor = db.cursor()

sql = "SELECT gender.firstname, gender.gender FROM pubs.gender;"

cursor.execute(sql)
results = cursor.fetchall()

outFile = open("pubs_genders.csv", "w")

outFile.write("FirstName,Gender\n")
for entry in results:
    outFile.write("\"" + str(entry[0]) + "\",\"" + str(entry[1]) + "\"\n")

outFile.close()
db.close()