from stanford_bib_single import Scraped_Bib
import json

json_file = open('stanford_data')
entries = json.loads(json_file.read())
json_file.close()


for sepdir in entries.keys():
    print(sepdir)
    bib = Scraped_Bib(sepdir)
    bib.save()

print('Completed')