import json

import os
cnt = 0
for root, dirs, files in os.walk(r'C:\Users\Administrator\Desktop\dataset\2012_financial_news'):
    cnt += len(files)
print(cnt)
exit(0)

e_f = open('company_names.txt', 'r', encoding='gbk')

with open('companies.json', 'r') as f:
    companies = json.load(f)

def add_to_companies(e_name, ticker):
    for c in companies:
        if c['ticker'] == ticker:
            c['entity_name'] = e_name

ticker2entity = {}

with open('dataset/industrial_relation.tsv', 'r', encoding='gbk') as f:
    for line in f.readlines():
        fields = line.split('\t')
        ticker = fields[1].strip()
        e_name = e_f.readline().strip()
        ticker2entity[ticker] = e_name

for c in companies:
    e_name = ticker2entity[c['ticker']]
    c['entity_name'] = e_name

with open('companies.json', 'w') as f:
    json.dump(companies, f, indent=2)
