# -*- coding: utf-8 -*-
"""lise-ort-multi-output.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/18EgQIhNO0WEchoa0NZIBBreW3H89H0y_
"""

from sklearn.linear_model import LinearRegression
from sklearn.multioutput import RegressorChain
import math
import numpy as np
from sklearn.datasets import make_regression
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error
from xgboost import XGBRegressor
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn import svm
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import plot_confusion_matrix
from mlxtend.feature_selection import SequentialFeatureSelector as SFS
from sklearn.linear_model import LinearRegression
import statsmodels.api as sm
from sklearn import model_selection, preprocessing, feature_selection, ensemble, linear_model, metrics, decomposition
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVR

os.chdir("/content/drive/MyDrive/Works/Bitirme")

data_file = "Data/Veriseti_Anadolu_Liseleri.xlsx"
data_original = pd.read_excel(data_file)
df = data_original.copy()
df = df.drop(columns=["okuladi", "okulno"])
df.head()

df.dtypes

df.iloc[:, -7:] = df.iloc[:, -7:].astype("int64")

df.dtypes

"""Hayır=1 Evet=0 değerlerini Hayır=0 Evet=1 olarak değiştirelim;"""

def sifir_bir_duzelt(degisken):
  for i in df[degisken].index:
    if df[degisken][i] ==0:
      df[degisken][i] = 1
    elif df[degisken][i]==1:
      df[degisken][i]=0

sifir_bir_duzelt("Asag")
sifir_bir_duzelt("Bsag")
sifir_bir_duzelt("Aoz")
sifir_bir_duzelt("Boz")
sifir_bir_duzelt("ABayri")
sifir_bir_duzelt("Abirlikte")
sifir_bir_duzelt("Acalisma")
sifir_bir_duzelt("Bcalisma")
sifir_bir_duzelt("oda")
sifir_bir_duzelt("hastalik")
sifir_bir_duzelt("okul_dyk")
sifir_bir_duzelt("ozel_kurs")
sifir_bir_duzelt("ortaokul_kurs")
sifir_bir_duzelt("ortaokul_ozelders")

df.head()

"""# Aykırı Değer Tespiti"""

sns.boxplot(x = df.ort9)

sns.boxplot(x = df.lgs_puani)

Q1 = df.lgs_puani.quantile(0.25)
Q3 = df.lgs_puani.quantile(0.75)
IQR = Q3-Q1
lower = Q1 - 1.5*IQR
upper = Q3 + 1.5*IQR
df.loc[df["lgs_puani"] > upper,"lgs_puani"] = upper
df.loc[df["lgs_puani"] < lower,"lgs_puani"] = lower
sns.boxplot(x = df.lgs_puani)

Q1 = df.ort9.quantile(0.25)
Q3 = df.ort9.quantile(0.75)
IQR = Q3-Q1
lower = Q1 - 1.5*IQR
upper = Q3 + 1.5*IQR
df.loc[df["ort9"] > upper,"ort9"] = upper

sns.boxplot(x = df.ort9)

"""## Standardization"""

# Get column names first
names = df.columns
# Create the Scaler object
scaler = preprocessing.StandardScaler()
# Fit your data on the scaler object
scaled_df = scaler.fit_transform(df)
scaled_df = pd.DataFrame(scaled_df, columns=names)

scaled_df

df_data = scaled_df

x = scaled_df.drop(["ort9", "ort10", "ort11"], axis=1)
y = scaled_df["ort9"]

def backward_elimination(data, target,significance_level = 0.05):
  features = data.columns.tolist()
  while(len(features)>0):
    features_with_constant = sm.add_constant(data[features])
    p_values = sm.OLS(target, features_with_constant).fit().pvalues[1:]
    max_p_value = p_values.max()

    if(max_p_value >= significance_level):
      excluded_feature = p_values.idxmax()
      features.remove(excluded_feature)
    else:
      break 
  return features

ort9_futures = backward_elimination(x, y)

ort9_futures

"""#ort9, 10, 11 tahminleri

## Regresyon Analizi
"""

x = df_data[ort9_futures]
y = df_data["ort9"]

"""İstatistik modellerini kullandığımız için, sabit terimi X değerine eklememiz gerekiyor."""

x = sm.add_constant(x)

train_x, test_x, train_y, test_y = train_test_split(x, y, train_size = 0.8, random_state = 42)

model = sm.OLS(train_y, train_x)
model = model.fit()
print(model.summary2())

"""`Aogrenim` değişkenlerinin p-value'su 0.05'den büyük olduğu için değişkenler arasından çıkarmamız gerekir.

Değişkenlerin sonuca etki yüzdelerini inceleyelim;
"""

coefs = model.params
coefs = pd.DataFrame(coefs, columns=["coefficients"])
coefs.drop(index=["const", "Aogrenim"], inplace=True)
coefs

coef_sum = coefs.coefficients.abs().sum()
coefs_abs = coefs.coefficients.abs().values
coefs_abs

percentages = []
for i in coefs_abs:
  perc = i*100/coef_sum
  percentages.append(perc)

coefs["Percentages"] = percentages

coefs.sort_values(by="Percentages", ascending=False, inplace=True)
print(coefs)

"""### Split Data"""

x = df[["ders_calisma", "internet", "Asag", "okul_dyk", 
        "turkce9","mat9", "lgs_puani"]]
#x = df[ort9_futures]
#x=x.drop(columns=['Aogrenim'])
y = df[["ort9", "ort10", "ort11"]]

train_x, val_x, train_y, val_y = train_test_split(x, y, random_state=42)

train_x

"""### Specify and Fit the Model"""

model =LinearRegression()

ChainRegression= RegressorChain(model, order=[0, 1, 2])
ChainRegression.fit(train_x,train_y)
print(ChainRegression.score(val_x, val_y))

val_predictions = ChainRegression.predict(val_x)

print("Eğitim doğruluğu: ", ChainRegression.score(train_x, train_y)*100)
print("Test doğruluğu: ", ChainRegression.score(val_x, val_y)*100)

val_y[:10]

#val_predictions = scaler_valy.inverse_transform(val_predictions)
val_predictions = val_predictions.astype("int64")
val_predictions[:10]

"""#ort10, 11 tahminleri"""

x = scaled_df.drop(["ort10", "ort11"], axis=1)
y = scaled_df["ort10"]

def backward_elimination(data, target,significance_level = 0.05):
  features = data.columns.tolist()
  while(len(features)>0):
    features_with_constant = sm.add_constant(data[features])
    p_values = sm.OLS(target, features_with_constant).fit().pvalues[1:]
    max_p_value = p_values.max()

    if(max_p_value >= significance_level):
      excluded_feature = p_values.idxmax()
      features.remove(excluded_feature)
    else:
      break 
  return features

ort10_futures = backward_elimination(x, y)

ort10_futures

"""## Regresyon Analizi"""

x = df_data[ort10_futures]
y = df_data["ort10"]

"""İstatistik modellerini kullandığımız için, sabit terimi X değerine eklememiz gerekiyor."""

x = sm.add_constant(x)

train_x, test_x, train_y, test_y = train_test_split(x, y, train_size = 0.8, random_state = 42)

model = sm.OLS(train_y, train_x)
model = model.fit()
print(model.summary2())

"""`sosyal_kulturel`, `internet`, `Boz` değişkenlerinin p-value'su 0.05'den büyük olduğu için değişkenler arasından çıkarmamız gerekir.

Değişkenlerin sonuca etki yüzdelerini inceleyelim;
"""

coefs = model.params
coefs = pd.DataFrame(coefs, columns=["coefficients"])
coefs.drop(index=["const", "sosyal_kulturel", "internet", "Boz"], inplace=True)
coefs

coef_sum = coefs.coefficients.abs().sum()
coefs_abs = coefs.coefficients.abs().values
coefs_abs

percentages = []
for i in coefs_abs:
  perc = i*100/coef_sum
  percentages.append(perc)

coefs["Percentages"] = percentages

coefs.sort_values(by="Percentages", ascending=False, inplace=True)
print(coefs)

"""### Split Data"""

x = df[["ort9", "lgs_puani", "ders_calisma", "cinsiyet", 
        "okul_dyk","ortaokul_turu", "lgs_puani"]]
#x = df[ort9_futures]
#x=x.drop(columns=['Aogrenim'])
y = df[["ort10", "ort11"]]

train_x, val_x, train_y, val_y = train_test_split(x, y, random_state=42)

train_x

"""### Specify and Fit the Model"""

model =LinearRegression()

ChainRegression= RegressorChain(model, order=[0, 1])
ChainRegression.fit(train_x,train_y)
print(ChainRegression.score(val_x, val_y))

val_predictions = ChainRegression.predict(val_x)

print("Eğitim doğruluğu: ", ChainRegression.score(train_x, train_y)*100)
print("Test doğruluğu: ", ChainRegression.score(val_x, val_y)*100)

val_y[:10]

#val_predictions = scaler_valy.inverse_transform(val_predictions)
val_predictions = val_predictions.astype("int64")
val_predictions[:10]

"""#Ortaokullar"""

os.chdir("/content/drive/MyDrive/Works/Bitirme")

data_file = "Data/Veriseti_Ortaokullar_GONDERILEN.xlsx"
data_original = pd.read_excel(data_file)
df = data_original.copy()
#df = df.drop(columns=["okuladi", "okulno"])
df = df.drop(["okuladi","okulno"], axis=1)

df.iloc[:, -3:] = df.iloc[:, -3:].astype("int64")

df.dtypes

def sifir_bir_duzelt(degisken):
  for i in df[degisken].index:
    if df[degisken][i] ==0:
      df[degisken][i] = 1
    elif df[degisken][i]==1:
      df[degisken][i]=0

sifir_bir_duzelt("Asag")
sifir_bir_duzelt("Bsag")
sifir_bir_duzelt("Aoz")
sifir_bir_duzelt("Boz")
sifir_bir_duzelt("ABayri")
sifir_bir_duzelt("Abirlikte")
sifir_bir_duzelt("Acalisma")
sifir_bir_duzelt("Bcalisma")
sifir_bir_duzelt("oda")
sifir_bir_duzelt("hastalik")
sifir_bir_duzelt("okul_dyk")
sifir_bir_duzelt("ozel_kurs")

"""## Standardization"""

# Get column names first
names = df.columns
# Create the Scaler object
scaler = preprocessing.StandardScaler()
# Fit your data on the scaler object
scaled_df = scaler.fit_transform(df)
scaled_df = pd.DataFrame(scaled_df, columns=names)

scaled_df



df_data = scaled_df

x = scaled_df.drop(["ort6", "ort7"], axis=1)
y = scaled_df["ort6"]

def backward_elimination(data, target,significance_level = 0.05):
  features = data.columns.tolist()
  while(len(features)>0):
    features_with_constant = sm.add_constant(data[features])
    p_values = sm.OLS(target, features_with_constant).fit().pvalues[1:]
    max_p_value = p_values.max()

    if(max_p_value >= significance_level):
      excluded_feature = p_values.idxmax()
      features.remove(excluded_feature)
    else:
      break 
  return features

ort6_futures = backward_elimination(x, y)

ort6_futures

"""## Regresyon Analizi"""

x = df_data[ort6_futures]
y = df_data["ort6"]

"""İstatistik modellerini kullandığımız için, sabit terimi X değerine eklememiz gerekiyor."""

x = sm.add_constant(x)

train_x, test_x, train_y, test_y = train_test_split(x, y, train_size = 0.8, random_state = 42)

model = sm.OLS(train_y, train_x)
model = model.fit()
print(model.summary2())

"""`Aoz`, `ozel_kurs`, `sosyal_kulturel` değişkenlerinin p-value'su 0.05'den büyük olduğu için değişkenler arasından çıkarmamız gerekir.

Değişkenlerin sonuca etki yüzdelerini inceleyelim;
"""

coefs = model.params
coefs = pd.DataFrame(coefs, columns=["coefficients"])
coefs.drop(index=["const", "Aoz", "ozel_kurs", "sosyal_kulturel"], inplace=True)
coefs

coef_sum = coefs.coefficients.abs().sum()
coefs_abs = coefs.coefficients.abs().values
coefs_abs

percentages = []
for i in coefs_abs:
  perc = i*100/coef_sum
  percentages.append(perc)

coefs["Percentages"] = percentages

coefs.sort_values(by="Percentages", ascending=False, inplace=True)
print(coefs)

"""### Split Data"""

x = df[["ort5", "Bsag", "ders_calisma", "Aogrenim", 
        "Abirlikte","Bogrenim"]]
#x = df[ort9_futures]
#x=x.drop(columns=['Aogrenim'])
y = df[["ort6", "ort7"]]

train_x, val_x, train_y, val_y = train_test_split(x, y, random_state=42)

train_x

"""### Specify and Fit the Model"""

from sklearn.svm import SVR
model =SVR(C= 1000, gamma= 0.0001, kernel= 'rbf')

'''
param_grid = {"alpha": [1, 10, 100, 290, 500],
              "fit_intercept": [True, False],
              "solver": ['svd', 'cholesky', 'lsqr', 'sparse_cg', 'sag', 'saga'], 
             }

CV_rfc = GridSearchCV(estimator=model, param_grid=param_grid, cv= 5)
CV_rfc.fit(train_x, train_y)
print(CV_rfc.best_params_)'''

ChainRegression= RegressorChain(model, order=[0, 1])
ChainRegression.fit(train_x,train_y)
print(ChainRegression.score(val_x, val_y))

val_predictions = ChainRegression.predict(val_x)

print("Eğitim doğruluğu: ", ChainRegression.score(train_x, train_y)*100)
print("Test doğruluğu: ", ChainRegression.score(val_x, val_y)*100)

val_y[:10]

#val_predictions = scaler_valy.inverse_transform(val_predictions)
val_predictions = val_predictions.astype("int64")
val_predictions[:10]

"""##ort5, 6, 7 tahminleri"""



x = scaled_df.drop(["ort5","ort6", "ort7"], axis=1)
y = scaled_df["ort5"]

def backward_elimination(data, target,significance_level = 0.05):
  features = data.columns.tolist()
  while(len(features)>0):
    features_with_constant = sm.add_constant(data[features])
    p_values = sm.OLS(target, features_with_constant).fit().pvalues[1:]
    max_p_value = p_values.max()

    if(max_p_value >= significance_level):
      excluded_feature = p_values.idxmax()
      features.remove(excluded_feature)
    else:
      break 
  return features

ort5_futures = backward_elimination(x, y)

ort5_futures

"""## Regresyon Analizi"""

x = df_data[ort5_futures]
y = df_data["ort5"]

"""İstatistik modellerini kullandığımız için, sabit terimi X değerine eklememiz gerekiyor."""

x = sm.add_constant(x)

train_x, test_x, train_y, test_y = train_test_split(x, y, train_size = 0.8, random_state = 42)

model = sm.OLS(train_y, train_x)
model = model.fit()
print(model.summary2())

"""`gelir` değişkenlerinin p-value'su 0.05'den büyük olduğu için değişkenler arasından çıkarmamız gerekir.

Değişkenlerin sonuca etki yüzdelerini inceleyelim;
"""

coefs = model.params
coefs = pd.DataFrame(coefs, columns=["coefficients"])
coefs.drop(index=["const", "gelir"], inplace=True)
coefs

coef_sum = coefs.coefficients.abs().sum()
coefs_abs = coefs.coefficients.abs().values
coefs_abs

percentages = []
for i in coefs_abs:
  perc = i*100/coef_sum
  percentages.append(perc)

coefs["Percentages"] = percentages

coefs.sort_values(by="Percentages", ascending=False, inplace=True)
print(coefs)

"""### Split Data"""

#x = df[["ort5", "Bsag", "ders_calisma", "Aogrenim", 
#        "Abirlikte","Bogrenim"]]
x = df[ort5_futures]
x=x.drop(columns=['gelir'])
y = df[["ort5","ort6", "ort7"]]

train_x, val_x, train_y, val_y = train_test_split(x, y, random_state=42)

train_x

"""### Specify and Fit the Model"""

from sklearn.svm import SVR
model =SVR(C= 1000, gamma= 0.0001, kernel= 'rbf')

ChainRegression= RegressorChain(model, order=[0, 1, 2])
ChainRegression.fit(train_x,train_y)
print(ChainRegression.score(val_x, val_y))

val_predictions = ChainRegression.predict(val_x)

print("Eğitim doğruluğu: ", ChainRegression.score(train_x, train_y)*100)
print("Test doğruluğu: ", ChainRegression.score(val_x, val_y)*100)

val_y[:10]

#val_predictions = scaler_valy.inverse_transform(val_predictions)
val_predictions = val_predictions.astype("int64")
val_predictions[:10]