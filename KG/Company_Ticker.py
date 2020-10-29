import numpy
import pandas
import openpyxl
from neo4j import GraphDatabase

def loadDataSet():  # 函数功能为打开文本文件并逐行读取
    Company_name = []
    Ticker = []
    Primary_Industry = []
    fr = open('sharp.txt')
    for line in fr.readlines():
        #取Inter_name
        a = ''
        x = 0
        for i in range(0,len(line)):
            if line[i] == '#':
                x = x + 1
                if(x == 1):
                    Company_name.append(a)
                    a = ''
                else:
                    Ticker.append(a)
                    a = ''
            else:
                if(line[i] != '\n'):
                    a = a + line[i]

        Primary_Industry.append(a)

    print("公司名称：", Company_name)
    print("股票", Ticker)
    print("主要行业", Primary_Industry)

    return Company_name, Ticker, Primary_Industry


class Example(object):

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_Company(cls, tx, Name):
        tx.run("CREATE (:Company {Name: $Name})", Name=Name)


    def create_Ticker(cls, tx, Ticker):
        tx.run("CREATE (:Ticker {Name: $Ticker})", Ticker = Ticker)

    def create_Industry(cls, tx, Industry):
        tx.run("CREATE (:Industry {Name: $Industry})", Industry = Industry)

    def Company_Ticker(cls, tx, node_name1, node_name2):
        tx.run("MATCH (node1: Company {Name: $node_name1}) "
               "MATCH (node2: Ticker {Name: $node_name2}) "
               "CREATE (node1)-[:发行]->(node2)",
               node_name1=node_name1, node_name2=node_name2)

    def Company_Industry(cls, tx, node_name1, node_name2):
        print(node_name1, node_name2)
        tx.run("MATCH (node1: Company {Name: $node_name1}) "
               "MATCH (node2: Industry {Name: $node_name2}) "
               "CREATE (node1)-[:主营]->(node2)",
               node_name1=node_name1, node_name2=node_name2)



    def create_Company_driver(self, message):
        with self._driver.session() as session:
            session.write_transaction(self.create_Company, message)

    def create_Ticker_driver(self, message):
        with self._driver.session() as session:
            session.write_transaction(self.create_Ticker, message)


    def create_Industry_driver(self, message):
        with self._driver.session() as session:
            session.write_transaction(self.create_Industry, message)

    def create_Company_Ticker_driver(self, message1, message2):
        with self._driver.session() as session:
            session.write_transaction(self.Company_Ticker, message1, message2)

    def create_Company_Industry_driver(self, message1, message2):
        print("1111111")
        with self._driver.session() as session:
            session.write_transaction(self.Company_Industry, message1, message2)

exam=Example("bolt://localhost:7687","neo4j","myneo4j")

Company, Ticker, Primary_Industry = loadDataSet()


Company1 = set(Company)
Ticker1 = set(Ticker)
Primary_Industry1 = set(Primary_Industry)


for each in Company1:
    exam.create_Company_driver(each)
for each in Ticker1:
    exam.create_Ticker_driver(each)
for each in Primary_Industry1:
    exam.create_Industry_driver(each)

#导入公司和股票的关系
for i in range(0, len(Company)):
    exam.create_Company_Ticker_driver(Company[i], Ticker[i])

#导入公司和行业的关系
exam.create_Company_Industry_driver(Company[0], Primary_Industry[0])
for i in range(1, len(Company)):
    if(Company[i] != Company[i-1]):
        exam.create_Company_Industry_driver(Company[i], Primary_Industry[i])


