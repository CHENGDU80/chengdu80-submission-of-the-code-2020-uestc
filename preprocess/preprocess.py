import string
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


def generate_keywords(relation_file='industrial_relation.tsv'):
    keywords = set()

    # 一些常用词
    common = set()

    common.update(list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'))

    comname, ticker, industry = get_relations(relation_file)
    keywords.update(comname)
    # 由于新闻中可能不会出现完整的公司名比如Microsoft Cop.
    # 切分一下，再加入到集合中
    #for name in comname:
        #splited = list(map(lambda w: w.replace(',','').strip(), name.split(' ')))
        #keywords.update(splited)
    simple_company = []
    keywords.update(simple_company)
    # add entity name
    with open('company_names.txt', 'r') as f:
        e_names = []
        for line in f.readlines():
            line = line.strip()
            if len(line) != 0:
                e_names.append(line)
    keywords.update(e_names)
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

    for w in keywords:
        if w in news:
            return True
    return False


def filter_news(output_dir='filtered_news', input_dir='2012_financial_news'):
    import os
    keywords = generate_keywords()
    try:
        os.mkdir(output_dir)
    except:
        pass
    cnt = 0
    qcnt = 0

    for root, dirs, files in os.walk(input_dir):
        if len(files) != 0:
            date = os.path.basename(root)
        for fi in files:
            new_filename = str(date) + '_' + str(fi)
            with open(os.path.join(root, fi), 'r', encoding='utf8') as f:
                d = f.read()
                if is_qualified_news(d, keywords):
                    qcnt += 1
                    with open(os.path.join(output_dir, new_filename), 'w', encoding='utf8') as of:
                        of.write(d)
                cnt += 1
                if cnt % 10000 == 0:
                    print(f'qcnt: {qcnt}')
                    print(f'cnt : {cnt}')


keywords = generate_keywords()
keywords.update(['stackholder', 'deficit', 'default', 'consolidation', 'bankrupt'])

key_verbs = set(['control', 'merge'])

# 出现此类verb就扔掉
black_verb = set(list(r'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'+string.punctuation))
black_verb.update(['is', 'was', 'does', 'had', 'didnt', 'said', 'are', 'be', 'have',
    'were', 'says', 'has', 'make', 'made', 'makes', 'say', 'ask', 'asked', 'asks',
    'based', 'told', 'tell'])

def verb_filter(word):
    if len(word) == 0:
        return False
    if word in black_verb:
        return False
    if not word[0].isalpha():
        return False
    for w in black_verb:
        if w in word.split(' '):
            return False


    return True

def subject_filter(word):
    if word in keywords:
        return True
    return False
triple_filtered = open('triple_with_comp.txt', 'w', encoding='utf8')

with open('relation.txt', 'r', encoding='utf8') as f:
    import json
    from collections import Counter
    c = Counter()
    i = 0
    for line in f.readlines():
        keep = False
        subject, verb, object, _ = json.loads(line)
        # 下面多个过滤器, 白名单规则，只要一条满足就保留
        def get_str(tagged):
            # tagged是列表的列表
            return ' '.join(list(map(lambda x:x[0], tagged)))

        verb_string = get_str(verb)
        subject_string = get_str(subject)
        object_string = get_str(object)

        
        
        if len(subject_string) == 0 or len(object_string) == 0:
            continue
        
        if verb_filter(verb_string) == False:
            continue
        if subject_filter(subject_string):
            triple_filtered.write('|'.join([subject_string, verb_string, object_string]) + '\n')
            c[verb_string]+=1
        

print(len(c))
with open('counter.txt', 'w', encoding='utf8') as f:
    import json
    json.dump(list(c.most_common(300)), f, indent=2)
#filter_news()

exit(0)

