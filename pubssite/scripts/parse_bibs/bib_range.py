from stanford_bib_single import Scraped_Bib
import json

json_file = open('stanford_data')
entry_dictionary = json.loads(json_file.read())
json_file.close()
print(entries)

for entry in entry_dictionary.values():
    bib = Scraped_Bib(entry['sepdir'])
    bib.save()

print('Completed')