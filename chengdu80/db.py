from flask import current_app
from neo4j import GraphDatabase

"""
some operations with Neo4j
"""


def get_db(url):
    """
    获取数据库的实例
    :param url:
    :return:
    """
    app = current_app()
    user = app.config['DATABASE_USER']
    password = app.config['DATABASE_PASSWORD']
    driver = GraphDatabase.driver(url, auth=(user, password))
    return driver


def get_factor_db():
    """
    获取影响因子的database
    :return:
    """
    url = current_app().config['DATABASE_FACTORS_URL']
    return get_db(url)


def get_relation_db():
    """
    获取公司关系的database
    :return:
    """
    url = current_app().config['DATABASE_RELATIONS_URL']
    return get_db(url)


def close_db(db):
    """
    关闭连接
    :return:
    """
    db.close()