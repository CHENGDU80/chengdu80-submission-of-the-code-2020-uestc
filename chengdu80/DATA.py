import pandas as pd
import numpy as np

from sklearn.preprocessing import MinMaxScaler


def create_dataset(data_x, look_back):
    dataX = []
    for i in range(len(data_x)-look_back-1):
        a = data_x[i: (i+look_back), :]
        dataX.append(a)
    return np.array(dataX)


def get_trainX(X, look_back):
    """
    X is returned from get_transaction_data
    :param X:
    :return:
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_x = scaler.fit_transform(X)
    dataX = []
    for i in range(len(data_x)-look_back-1):
        a = data_x[i: (i+look_back), :]
        dataX.append(a)
    return np.array(dataX)



def get_transaction_data(transaction_data, look_back):
    X = transaction_data[:, [3, 4, 5, 8, 7, 6]]
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_x = scaler.fit_transform(X)
    dataX = []
    for i in range(len(data_x)-look_back-1):
        a = data_x[i: (i+look_back), :]
        dataX.append(a)
    return np.array(dataX)





def Data():
    data = pd.read_csv("transaction_data.tsv", sep='\t',header=None)
    # ticker = data[1]
    # print(ticker.shape)
    # del(data[8])
    for i in range(0,3):
        del(data[i])
    # print(data)
    t=data[6].copy()
    # print(t)
    data[6]=data[8]
    data[8]=t
    x=data.iloc[0:100000,0:6].values
    y=data.iloc[0:100000,5].values
    data =np.array(data)

    return data,x,y
#Data()

if __name__ == '__main__':
    pass








