import numpy
import pandas
import openpyxl
from neo4j import GraphDatabase


class Example(object):

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    # 查询所有公司和股票
    def Quary_issue(cls, tx):
        result = tx.run("MATCH (a)-[:issue]->(b) RETURN a.Name, b.Name")
        print(result)
        a = []
        b = []
        for record in result:
            # print("{} issue {}".format(record["a.Name"], record["b.Name"]))
            a.append(record["a.Name"])
            b.append(record["b.Name"])
        return a, b

    def Quary_issue_driver(self):
        aa = []
        bb = []
        with self._driver.session() as session:
            aa, bb = session.write_transaction(self.Quary_issue)
        return aa, bb

    # 查询所有公司
    def Quary_all_Company(cls, tx):
        result = tx.run("MATCH (n:Company) RETURN n.Name")
        company = []
        for record in result:
            company.append(record["n.Name"])
        return company

    def Quary_all_Company_driver(self):
        with self._driver.session() as session:
            company = session.write_transaction(self.Quary_all_Company)
        return company

    # 查询所有股票
    def Quary_all_Ticker(cls, tx):
        result = tx.run("MATCH (n:Ticker) RETURN n.Name")
        Ticker = []
        for record in result:
            Ticker.append(record["n.Name"])
        return Ticker

    def Quary_all_Ticker_driver(self):
        with self._driver.session() as session:
            Ticker = session.write_transaction(self.Quary_all_Ticker)
        return Ticker

# 查询所有Primary Industry
    def Quary_all_Primary_Industry(cls, tx):
        result = tx.run("MATCH (n:Primary_Industry) RETURN n.Name")
        PI = []
        for record in result:
            PI.append(record["n.Name"])
        return PI

    def Quary_all_Primary_Industry_driver(self):
        with self._driver.session() as session:
            PI = session.write_transaction(self.Quary_all_Primary_Industry)
        return PI

# 查询所有Industry Category
    def Quary_all_Industry_Category(cls, tx):
        result = tx.run("MATCH (n:Industry_Category) RETURN n.Name")
        IC = []
        for record in result:
            IC.append(record["n.Name"])
        return IC

    def Quary_all_Industry_Category_driver(self):
        with self._driver.session() as session:
            IC = session.write_transaction(self.Quary_all_Industry_Category)
        return IC

    # 查询所有公司
    def Quary_Company(cls, tx):
        result = tx.run("MATCH (n:Company) RETURN n.Name")
        company = []
        for record in result:
            company.append(record["n.Name"])
        return company

    def Quary_Company_driver(self):
        with self._driver.session() as session:
            company = session.write_transaction(self.Quary_all_Company)
        return company

# 查询公司返回股票和行业
    def Quary_Company1(cls, tx, Name):
        result = tx.run("MATCH (a:Company { Name: '"+Name+"' })-[r]->(b) RETURN a.Name,b.Name")
        ticker = []
        industry = []
        a = industry.append(result["b.Name"])
        ticker = a[1]
        industry = a[0]

        return ticker, industry

    def Quary_Company1_driver(self, Name):
        with self._driver.session() as session:
            ticker, industry = session.write_transaction(self.Quary_Company1, Name)
        return ticker, industry

exam = Example("bolt://18.162.205.162:5002", "neo4j", "chengdu80uestc")  # 密码chengdu80uestc

# 查询所有issue关系，返回所有Company（aa)和所有Ticker(bb)
aa = []
bb = []
aa, bb = exam.Quary_issue_driver()
print("Company", aa)
print("Ticker", bb)

# 查询所有Company
company = exam.Quary_all_Company_driver()
print("Company", company)

# 查询所有股票
ticker = exam.Quary_all_Ticker_driver()
print("Ticker", ticker)

# 查询所有Primary Industry
PI = exam.Quary_all_Primary_Industry_driver()
print("Primary Industry", PI)

# 查询所有Industry Category
IC = exam.Quary_all_Industry_Category_driver()
print("Industry Category", IC)

# 查询某个Company
Name = 'Edwards Lifesciences Corporation'
ticker, industry = exam.Quary_Company1_driver(Name)
print("ticker", ticker)
print("industry", industry)

