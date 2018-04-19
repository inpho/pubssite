from stannford_bib_single import Scraped_Bib

json_file = open('stanford_data')
entries = json.loads(json_file.read())
json_file.close()


for sepdir in entries.keys():
    bib = Scraped_Bib(sepdir)
    bib.save()

print('Completed')