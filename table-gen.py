import os 
import json

ignore = ['combined.json']
live = sorted(['HaveIBeenPwned.json','Dehashed.json','Hashmob.json','BreachDirectory.json','LeakCheck.io.json','ScatteredSecrets.json','Leak-Lookup.json'], key=str.lower)

TABLE_HEADER = """| Service Name | Breach Count | Total Records | Automatic Updates |
| ------------ | ------------ | ------------- |        :--:       |\n"""

readme_table = TABLE_HEADER

# do live datasets
for file in live:
    print(f"Loading datasets/{file}")
    data = json.loads(open(f'datasets/{file}','r').read())
    breach_count = len(data)
    total_count = 0
    for item in data:
        try:
            if "record_count" in item:
                if type(item['record_count']) == int:
                    total_count += item['record_count']
                else:
                    total_count += int(item['record_count'].replace(",",""))
        except Exception as e:
            continue
    if total_count == 0:
        readme_table += f"| {file.replace('.json','')} | {breach_count:,} | Unavailable | ✅ |\n"
    else:
        readme_table += f"| {file.replace('.json','')} | {breach_count:,} | {total_count:,} | ✅ |\n"

# do archived datasets
for file in sorted(os.listdir('datasets/'), key=str.lower):
    if file not in live and file not in ignore and file.endswith('.json'):
        print(f"Loading datasets/{file}")
        data = json.loads(open(f'datasets/{file}','r').read())
        breach_count = len(data)
        total_count = 0
        for item in data:
            try:
                if type(item['record_count']) == int:
                    total_count += item['record_count']
                else:
                    total_count += int(item['record_count'].replace(",",""))
            except:
                continue
        if total_count == 0:
            readme_table += f"| {file.replace('.json','')} | {breach_count:,} | Unavailable | ❌ |\n"
        else:
            readme_table += f"| {file.replace('.json','')} | {breach_count:,} | {total_count:,} | ❌ |\n"

# update table in readme
template = open('README.tpl').read()
with open('README.md','w') as outfile:
    outfile.write(template.replace('README_TABLE',readme_table))
