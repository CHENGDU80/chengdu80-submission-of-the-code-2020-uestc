import numpy
import pandas
import openpyxl
from neo4j import GraphDatabase

def loadDataSet():  # 函数功能为打开文本文件并逐行读取
    company = []
    company2 = []
    relation = []
    effect = []
    comp = open('company_names.txt')
    for line in comp.readlines():
        company.append(line.strip('\n'))

    fr = open('triple_with_comp.txt', 'r', encoding='UTF-8')
    x = []
    for line in fr.readlines():
        x.append(line.strip('\n'))
    x = set(x)
    print(x)
    for each in x:
        curLine = each.split('|')

        company2.append(curLine[0])
        relation.append(curLine[1])
        effect.append(curLine[2].strip('\n'))

    return company, company2, effect, relation




class Example(object):

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_Company(cls, tx, Name):
        tx.run("CREATE (:Company {Name: $Name})", Name=Name)


    def create_Effect(cls, tx, Effect):
        tx.run("CREATE (:Effect {Name: $Effect})", Effect = Effect)



    def Company_Effect(cls, tx, node_name1, node_name2, relation):
        tx.run("MATCH (node1: Company {Name: $node_name1}) "
               "MATCH (node2: Effect {Name: $node_name2}) "
               "CREATE (node1)-[: " +relation+"]->(node2)",
               node_name1=node_name1, node_name2=node_name2)

    def Company_Company(cls, tx, node_name1, node_name2, relation):
        tx.run("MATCH (node1: Company {Name: $node_name1}) "
               "MATCH (node2: Company {Name: $node_name2}) "
               "CREATE (node1)-[: "+relation+"]->(node2)",
               node_name1=node_name1, node_name2=node_name2)


    def create_Company_driver(self, message):
        with self._driver.session() as session:
            session.write_transaction(self.create_Company, message)

    def create_Effect_driver(self, message):
        with self._driver.session() as session:
            session.write_transaction(self.create_Effect, message)

    def Company_Company_driver(self, message1, message2, message3):
        with self._driver.session() as session:
            session.write_transaction(self.Company_Company, message1, message2, message3)

    def Company_Effect_driver(self, message1, message2, message3):
        with self._driver.session() as session:
            session.write_transaction(self.Company_Effect, message1, message2, message3)

company, company2, effect, realtion = loadDataSet()
exam=Example("bolt://localhost:7687","neo4j","myneo4j")#密码chengdu80uestc
for each in company:
    exam.create_Company_driver(each)
effect1 = set(effect)
for each in effect1:
    if each not in company:
        exam.create_Effect_driver(each)

j = 0
for each in realtion:
    if ' ' in each:
        for i in range(0,len(each)):
            if each[i] == ' ':
                t = list(each)
                t[i] = '_'
                each = ''.join(t)
        for i in range(0, len(each)):
            if each[i] == '-':
                print(each)
                t = list(each)
                t[i] = '_'
                each = ''.join(t)
                print(each)

    realtion[j] = each
    j = j + 1

for i in range(0, len(company2)):
    if(effect[i] != company2[i]):
        if company2[i] in company:
            if effect[i] in company:
                exam.Company_Company_driver(company2[i], effect[i], realtion[i])
            else:
                exam.Company_Effect_driver(company2[i], effect[i], realtion[i])


