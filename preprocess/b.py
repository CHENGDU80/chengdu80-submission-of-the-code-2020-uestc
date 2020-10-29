
import json
import sqlite3

def create_database():
    a = sqlite3.connect('sentiment.sqlite')

    a = sqlite3.connect('sentiment.sqlite')
    a.execute('create table sentiment(ticker varchar(100), article_date date ,  title varchar(200),neg decimal ,neu decimal,pos decimal ,compound decimal )')
    a.commit()
    a.close()

def open_database():
    return sqlite3.connect('sentiment.sqlite')

def show_content():
    db = open_database()
    cursor = db.cursor()
    
    for r in cursor.execute('select count(*) from sentiment'):
        size = r
    for row in cursor.execute('select count(*) from sentiment where neg > pos'):
        neg = row
    print(size)
    print(neg)

show_content()
exit(0)

create_database()
db = open_database()
cursor = db.cursor()

with open('companies.json', 'r', encoding='utf8') as f:
    companies = json.load(f)
company2ticker = {}
for comp in companies:
    try:
        company2ticker[comp['entity_name']] = comp['ticker']
    except:
        pass




data_dir = r'C:\Users\Administrator\Desktop\company_news'
import os

sentences = {}

for root, dirs, files in os.walk(data_dir):
    for f in files:
        company_name = os.path.basename(root)
        date = f[:10]
        with open(os.path.join(root, f), 'r') as in_f:
            for line in in_f.readlines():
                if len(line.strip()) == 0:
                    continue
                d = json.loads(line.strip())
                if company_name not in company2ticker:
                    continue
                ticker = company2ticker[company_name]
                cursor.execute('insert into sentiment values("{}", "{}", "{}", {}, {}, {}, {})'.format(
                    ticker, date, d['title'], d['neg'], d['neu'], d['pos'], d['compound']
                ))
        if company_name not in sentences:
            sentences[company_name] = []
        sentences[company_name].append([date, d])
db.commit()
db.close()
