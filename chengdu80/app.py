from flask import Flask, current_app, render_template, url_for
import tensorflow as tf
import os
import sqlite3
import datetime
import numpy as np
import json
import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Kline,Line
from sklearn.preprocessing import MinMaxScaler
from jinja2 import Markup
import graph
import utils

app = Flask(__name__)
app.instance_path = os.getcwd()


# config file of flask
config_file = 'config.py'

transaction_data = None
ticker_to_transaction_index = {}

ticker_file = 'tickers.txt'
valid_tickers = set()

company_info_file = 'company_info.json'
company_info = {}

data_dir = r'/home/ubuntu/dataset'
news_dir = r'/home/ubuntu/filtered_news'
ckpt_file = 'saved/lstm.ckpt'
look_back = 7
chengdu80_model = None

def setup(app):
    """
    Do some initial work:
    1. read the transaction data for later requests to construct K line graph
    2. connect to neo4j database
    3. load the machine learning model
    :return:
    """

    # read some data
    # config file
    try:
        app.config.from_pyfile(config_file)
    except:
        pass

    app.config.from_mapping(SECRET_KEY='dev')

    # read ticker info
    with app.open_instance_resource(ticker_file, 'r') as f:
        global valid_tickers
        valid_tickers = {line.strip() for line in f.readlines()}

    # read company info
    with app.open_instance_resource(company_info_file, 'r') as f:
        global company_info
        data = json.load(f)
        for comp in data:
            company_info[comp['ticker']] = comp


    # 1. read transaction data using pandas
    global transaction_data
    # pandas is sooooooo slow!
    # But I will let it be for now. TODO
    transaction_data = pd.read_csv(os.path.join(data_dir, 'transaction_data.tsv'), sep='\t', header=0)
    # do some pre-process to speed up later query
    ticker_column = transaction_data.values[:,1]
    for row in range(len(ticker_column)):
        # field 1 is the ticker
        ticker = ticker_column[row]
        if ticker not in ticker_to_transaction_index:
            ticker_to_transaction_index[ticker] = [row]
        else:
            ticker_to_transaction_index[ticker].append(row)
    for ticker, idx in ticker_to_transaction_index.items():
        ticker_to_transaction_index[ticker] = np.array(idx)

    # 模型建立
    model = tf.keras.models.Sequential([
        tf.keras.layers.LSTM(input_shape=(None, 6), units=50,
                             return_sequences=True),
        tf.keras.layers.LSTM(units=100, return_sequences=True),
        tf.keras.layers.LSTM(units=200, return_sequences=True),
        tf.keras.layers.LSTM(units=300, return_sequences=False),
        tf.keras.layers.Dropout(0.2),
        tf.keras.layers.Dense(100),
        tf.keras.layers.Dense(1),
        tf.keras.layers.Activation('relu')
    ])
    model.compile(loss='mean_squared_error', optimizer='Adam')
    model.load_weights(
        filepath=os.path.join(app.instance_path, ckpt_file)).expect_partial()
    model.summary()
    global chengdu80_model
    chengdu80_model = model
    print('done with setup')


@app.route('/kline/<ticker>')
def get_transactions_of_ticker(ticker):
    """
    返回某个股票的全年数据，用于前端绘制图形
    :param ticker:
    :return:
    """
    global transaction_data
    global ticker_to_transaction_index
    if ticker not in ticker_to_transaction_index:
        return utils.error_response('no such ticker')
    idx = ticker_to_transaction_index[ticker]
    data = transaction_data.values[idx]

    date, list1, list2 = data[:, 0], data[:, 3:5], data[:,5:7]
    list0 = np.concatenate([list2, list1], axis=1)
    kline = (
        Kline()
            .add_xaxis(date.tolist())
            .add_yaxis("k line chart", list0.tolist())
            .set_global_opts(
            xaxis_opts=opts.AxisOpts(is_scale=True),
            yaxis_opts=opts.AxisOpts(
                is_scale=True,
                splitarea_opts=opts.SplitAreaOpts(
                    is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
                ),
            ),
            datazoom_opts=[opts.DataZoomOpts()],
            title_opts=opts.TitleOpts(title=""),
        )
    )
    return kline.dump_options_with_quotes()

@app.route('/company/<ticker>')
def get_company_info(ticker):
    global company_info #TODO 对接数据格式
    if ticker not in company_info:
        return utils.error_response('no such company')
    return company_info[ticker]

def get_transaction_data_between(data, from_date, to_date):
    """
    :param data: numpy array
    :param from_date: inclusive
    :param to_date: exclusive
    :return: (dates, ret_data)
    dates: dates of data
    ret_data: matrix containing 6 columns
    """
    dates = data[:,0]

    # should've used binary search
    # but I am lazy and forget how to do it.
    start = 0
    end = 0
    while start < len(dates) and dates[start] < from_date:
        start += 1

    end = start

    while end < len(dates) and dates[end] < to_date:
        end += 1

    mask = list(range(start, end))

    dates = dates[mask]
    ret_data = data[mask][:,-6:]

    return dates, ret_data

def get_prediction(data, predict, pre_date):
    date, prc = data[:, 0], data[:, 6]
    prediction = np.array([None] * (len(prc) - 1))
    date=np.append(date,pre_date)
    end_data=prc[(len(prc) - 1)]
    prediction=np.append(prediction,end_data)
    prediction = np.append(prediction, predict)
    color = 'red' if end_data<predict else 'green'
    line = (
        Line()
            .add_xaxis(date.tolist())
            .add_yaxis("true value", prc.tolist(),linestyle_opts=opts.LineStyleOpts(color='blue',width=4),symbol='x')
            .add_yaxis("prediction", prediction.tolist(),linestyle_opts=opts.LineStyleOpts(color=color,width=4, type_="dashed"))
            .set_global_opts(title_opts=opts.TitleOpts(title=""),
                             yaxis_opts=opts.AxisOpts(is_scale=True))
    )
    return line

@app.route('/predict/<ticker>/<pred_date>')
def get_prediction_after_date_and_actual_data(ticker, pred_date):
    global ticker_to_transaction_index
    global transaction_data
    global chengdu80_model


    if ticker not in ticker_to_transaction_index:
        return utils.error_response('no such ticker')

    idx = ticker_to_transaction_index[ticker]
    data = transaction_data.values[idx]

    dates = data[:,0]

    # 计算出dataset
    from DATA import get_transaction_data
    X = get_transaction_data(data, look_back)

    # 找look_back个数据
    i = 0
    while i < len(dates) and dates[i] < pred_date.replace('-', '/'):
        i += 1
    predX = X[i-min(i, look_back) :i]
    predy = data[i-min(i, look_back):i,-3]
    y_scaler = MinMaxScaler(feature_range=(0, 1))
    y_scaler.fit(np.array([predy]).reshape([7,1]))
    y = chengdu80_model.predict(predX)
    # 反归一化之后的预测数据
    y = y_scaler.inverse_transform(y)[0]
    y=((int)(y*1000))/1000


    numpy_array = data[i-min(i, look_back) :i]
    line=get_prediction(numpy_array,y,pred_date)
    return line.dump_options_with_quotes()


@app.route('/search/<ticker>')
def very_important_page(ticker):
    global company_info  # TODO 对接数据格式
    if ticker not in company_info:
        return utils.error_response('no such company')

    return render_template('block_show.html', company=company_info[ticker], ticker=ticker)


@app.route('/news/<ticker>/<a_date>')
def get_news(ticker, a_date):
    path = os.path.join(app.instance_path, app.config['DATABASE_NEWS'])
    db = sqlite3.connect(path)
    cursor = db.cursor()
    result = cursor.execute('select article_date, title, neg, pos '
                   'from sentiment '
                    'where ticker = ? and '
                   'article_date '
                   'between date(?, "start of day", "-30 days")'
                   'and ?', (ticker, a_date, a_date))
    data = []
    news_data = []
    for row in result:
        title = row[1]
        path = os.path.join(news_dir, title)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf8') as f:
                news = f.read()
                news_data.append(news)
        data.append({
            'title': row[1],
            'date': row[0],
            'neg': row[2],
            'pos': row[3]
        })
    db.close()

    return {'data': data, 'news': news_data}

@app.route('/')
def hello_world():
    return render_template('block_index.html')



if __name__ == '__main__':
    setup(app)
    app.run(host='0.0.0.0', port=5003)
