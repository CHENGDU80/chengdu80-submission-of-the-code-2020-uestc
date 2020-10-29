import ticker


def get_relations(relation_file):
    """
    return (company name, ticker, primary industry)
    """
    comname = []
    ticker = []
    industry = []
    with open(relation_file, 'r', encoding='gbk') as f:
        for line in f.readlines():
            splited = line.split('\t')
            comname.append(splited[0].strip())
            ticker.append(splited[1].strip())
            industry.append(splited[2].strip())
    return (comname, ticker, industry)


def generate_keywords(relation_file='dataset/industrial_relation.tsv'):
    keywords = set()

    # 一些常用词
    common = set(['of','The', 'IT'])

    common.update(list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'))

    comname, ticker, industry = get_relations(relation_file)
    keywords.update(comname)
    # 由于新闻中可能不会出现完整的公司名比如Microsoft Cop.
    # 切分一下，再加入到集合中
    #for name in comname:
        #splited = list(map(lambda w: w.replace(',','').strip(), name.split(' ')))
        #keywords.update(splited)
    simple_company = []
    with open('company_names.txt', 'r', encoding='gbk') as f:
        for line in f.readlines():
            line = line.strip()
            if len(line) != 0:
                simple_company.append(line)
    keywords.update(simple_company)
    #keywords.update(ticker)
    #keywords.update(industry)

    #return keywords - common
    return keywords - common


def save_keywords(filename='keywords.json'):
    words = generate_keywords()
    print(len(words))
    import json
    with open(filename, 'w') as f:
        json.dump(list(words), f)


def is_qualified_news(news, keywords):
    """
    用于判断一条news是否有效，看它内容是否出现了keywords中的词
    """
    import re
    one_line = news.replace(r'\n', ' ')
    one_line = re.sub(r'[\t\n,.]', ' ', one_line)
    one_line = re.sub(' +', ' ', one_line)
    news = set(one_line.split(' ')) - set([''])
    join = (news & keywords)
    if len(join) > 0:
        return True, join
    return False, None


import os
keywords = generate_keywords()
qcnt = 0
cnt = 0
for root, dirs, files in os.walk('dataset/2012_financial_news'):
    for fi in files:
        with open(os.path.join(root, fi), 'r', encoding='utf8') as f:
            d = f.read()
            q,_ = is_qualified_news(d, keywords)
            if q:
                qcnt += 1
            cnt += 1
            if cnt % 10000 == 0:
                print(f'qcnt: {qcnt}')
                print(f'cnt: {cnt}')


exit(0)
with open('common.pkl', 'wb') as f:
    import pickle
    pickle.dump(c.most_common(100), f)

with open('common_words.json', 'w') as f:
    json.dump(list(d), f)
print(c.most_common(100))

