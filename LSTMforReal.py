# import libraries
import pandas as pd
import numpy as np
# data split

from sklearn.model_selection import train_test_split
from collections import Counter

# data preprocessing
from sklearn.preprocessing import OneHotEncoder, LabelEncoder, MinMaxScaler
import matplotlib.pyplot as plt
from keras.callbacks import ModelCheckpoint
import os


# model building
import tensorflow as tf
from tensorflow.keras import Model , Sequential,Input, backend
from tensorflow.keras.layers import LSTM , Dense , Dropout , Flatten
from tensorflow.keras.callbacks import EarlyStopping
from keras.utils.vis_utils import plot_model

import wandb
from wandb.keras import WandbCallback

gpus=tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        #currentlu, memory growth needs to be the same across GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu,True)
        logical_gpus=tf.config.experimental.list_logical_devices('GPU')
        print(len(gpus),"Phusical GPUs", len(logical_gpus),"Logical GPUS")
    except RuntimeError as e:
        #,e,pry growth must be set before GPUs have been initialized
        print(e)
def drop_d(df,features):
    list_1=list(features["col_name"][:20])
    for i in(list_1):
        df=df.drop(i,axis=1)
    return df

def get_real_data(data_path):
    df=pd.read_csv(data_path)
    df=df.loc[df["Label"]==1]
    df=df.iloc[:8000]
    df.drop("Label",axis=1)
    df["Label"]=0
    return df

def get_fake_data(data_path):
    df=pd.read_csv(data_path)
    df["Label"]=1
    return df

def get_combined_data(real_df,fake_df):
    return pd.concat([real_df, fake_df], axis=0)

def wandb_login():
    wandb.login()
    wandb.init(project="Real_Fake", config={"hyper":"paramet"})

def data_split(df):
    
    y=df.Label
    X=df.drop(columns=["Label"])
    # X=df[columns]
    
    labels=y.unique()
    classes=y.nunique()


    print(X.shape)
    print("number of Label", classes)
    print("instances per label\n", y.value_counts())
    print("label",labels)
    
    # split the dataset into 80% for training and 20% for testing
    X_train , X_test, y_train , y_test = train_test_split(X,y, random_state=42 , stratify=y, shuffle=True,test_size=0.2)


    print("after spliting the data :\n")
    print("training data length:", len(X_train))
    print("test data length:", len(X_test))

    return X_train , X_test, y_train , y_test

def pre_processing(X_train , X_test, y_train , y_test):

    scaler= MinMaxScaler()
    le = LabelEncoder()

    X_train=scaler.fit_transform(X_train)
    X_test=scaler.transform(X_test)

    # print("intances per label in training set \n",y_train.value_counts())
    y_train=le.fit_transform(y_train)

    # print("intances per label in test set \n",y_test.value_counts())
    y_test=le.fit_transform(y_test)

    print(X_train.shape)
    print(X_test.shape)

    y_train = np.asarray(y_train).astype("float32").reshape((-1,1))
    y_test = np.asarray(y_test).astype("float32").reshape((-1,1))
    

    # reshape input data to LSTM format [samples , time_steps, features]
    X_train = X_train.reshape(X_train.shape[0], 1, X_train.shape[1])
    X_test = X_test.reshape(X_test.shape[0], 1, X_test.shape[1])
   
    # print(f"shape of X_train:", X_train.shape)
    # print(f"shape of X_test:", X_test.shape)

    return X_train , X_test, y_train , y_test

def build_LSTM_model(n_features,n_classes):

    model=Sequential()

    model.add(Input(shape=(None, n_features),name="input"))

    model.add(LSTM(units=30,name="LSTM_layer"))
    model.add(Dense(256, activation = 'relu', name="Dense_Layer"))
    model.add(Dropout(0.5,name="Dropout_Layer"))
    model.add(Dense(n_classes, activation="sigmoid", name="Output"))

    model.compile(loss="sparse_categorical_crossentropy", optimizer='Adam',metrics=['accuracy'])
    print(model.summary())
    print("NUMBER OF FEATURES :",n_features)
    return model


def train_model(model, X_train , y_train ):
    
    callback = EarlyStopping(patience=20, mode='min', restore_best_weights=True)
    backend.clear_session()
    history = model.fit(X_train,y_train, 
                        epochs=30, batch_size=32, validation_split=0.2, callbacks=[callback,WandbCallback()])
    # "model.h5" is saved in wandb.run.dir & will be uploaded at the end of training
    model.save(os.path.join(wandb.run.dir, "model.h5"))

# fe=pd.read_csv("/home/infres/amustapha/DDoS/GAN/DDoS_Functional_Features.csv")
    
# fe=pd.read_csv("DDoS_Functional_Features.csv")

# data_path="combined.csv"
# real=get_real_data(data_path)
# fake=get_fake_data("Results/generatedAllclasses.csv")

# real=drop_d(real,fe)

# fake=drop_d(fake,fe)

# dataset=get_combined_data(real,fake)

# X_train , X_test, y_train , y_test = data_split(dataset)
# X_train , X_test, y_train , y_test = pre_processing(X_train , X_test, y_train , y_test)

# model = build_LSTM_model(38, 2)
# wandb_login()
# train_model(model, X_train , y_train)

    