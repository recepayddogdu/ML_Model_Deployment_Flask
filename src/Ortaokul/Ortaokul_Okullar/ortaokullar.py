# -*- coding: utf-8 -*-
"""Ortaokullar.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1IUuwNiMChTJ7aOIBaOO9r8PY2OyVvU_o

## Değişkenler
**KURUM ADI**: okul_adi  
**Toplam Öğrenci Sayısı**: ogr_sayisi  
**Taşımalı Öğrenci Sayısı**: tasimali_ogr_say  
**Toplam Kapalı Bina Alanı**: bina_alani  
**Toplam Bahçe Alanı**: bahce_alani  
**Toplam Kapalı Spor Alanı**: kapali_spor_alani  
**Toplam Açık Spor Alanı**: acik_spor_alani  
**Toplam Kantin Alanı**: kantin_alani  
**Çok Amaçlı Salon Var Mı?**: cok_amacli_salon  
**Toplam Aktif Derslik Sayısı Nedir?**: derslik_sayisi  
**Personelin Ortalama Hizmet Süresi Nedir?**: personel_hizmet_suresi  
**Personelin Ortalama Yaşı Nedir?**: personel_yas  
**Doktora Öğrenimine Devam Eden Personel Sayısı**: doktora_devam_personel  
**Doktora Mezunu Personel Sayısı**: doktora_mezunu  
**Yüksek Lisansına Devam Eden Personel Sayısı**: yuksek_devam  
**Yüksek Lisans Mezunu Personel Sayısı**: yuksek_mezun  
**Tasarım Beceri Atölyesi Var Mı?**: tasarim_atolyesi  
**Fen Laboratuvarı Var Mı?**: fen_laboratuvari  
**Bilişim Teknolojileri Laboratuvarı Var Mı?**: bilisim_laboratuvari
"""

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
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import plot_confusion_matrix

os.chdir("/content/drive/MyDrive/Works/Bitirme")

"""# Okul Verilerinin Çekilmesi"""

data_file = "Data/Ortaokullar.xlsx"
data_original = pd.read_excel(data_file)
df_okullar = data_original.copy()
#df = df.drop(columns=["okuladi", "okulno"])
df_okullar.head()

"""## Evet->1 Hayır->0 olacak şekilde düzeltme"""

def evet_hayir(degisken):
  for i in df_okullar[degisken].index:
    if df_okullar[degisken][i] =="EVET":
      df_okullar[degisken][i] = 1
    elif df_okullar[degisken][i]=="HAYIR":
      df_okullar[degisken][i]=0

evet_hayir("cok_amacli_salon")
evet_hayir("tasarim_atolyesi")
evet_hayir("fen_laboratuvari")
evet_hayir("bilisim_laboratuvari")

df_okullar.head()

"""# Aykırı Değerlerin Tespiti"""

sns.boxplot(x = df_okullar.bina_alani)

sns.boxplot(x = df_okullar.yuksek_mezun)

"""#Not Verileri Çekilmesi"""

data_file = "Data/Veriseti_Ortaokullar_GONDERILEN.xlsx"
data_original = pd.read_excel(data_file)
df_notlar = data_original.copy()
#df = df.drop(columns=["okuladi", "okulno"])
df_notlar

df_notlar["okuladi"].value_counts()

"""##30'dan fazla veri içeren okulların tespit edilmesi"""

df_not_okul = pd.DataFrame(df_notlar["okuladi"].value_counts() > 29)
df_not_okul

df_not_okul = df_not_okul.index[df_not_okul['okuladi'] == True].tolist()

"""30'dan fazla veri içeren okul isimleri;"""

df_not_okul

type(df_not_okul)

"""### Bu okullara ait öğrenci bilgilerinin çekilmesi"""

value_list = df_not_okul
boolean_series = df_notlar.okuladi.isin(value_list)
filtered_df = df_notlar[boolean_series]

filtered_df

"""### Okulların gruplanması ve verilerin ortalamalarının alınması"""

df_group = filtered_df.groupby("okuladi")

df_group.mean()

ortalama_df = pd.DataFrame(df_group.mean())

type(ortalama_df)

"""###Sene sonu notlarının okullardaki ortalamaları"""

okul_ortalamalari = pd.DataFrame(ortalama_df.iloc[:, -3:].mean(axis=1), columns=["ortalamalar"])

okul_ortalamalari = okul_ortalamalari.reset_index()

okul_ortalamalari = okul_ortalamalari.sort_values("ortalamalar")

okul_ortalamalari = okul_ortalamalari.reset_index()
okul_ortalamalari = okul_ortalamalari.iloc[:, -2:]

okul_ortalamalari

"""#Okul ortalamalarının görselleştirilmesi"""

sns.set_palette("RdBu")
plt.figure(figsize=(16,9))
sns.set(font_scale=1.3)
sns.barplot(x="okuladi", y="ortalamalar", data=okul_ortalamalari)
plt.xticks(rotation=60)
plt.show()

"""#Okulların özelliklerinin ve not ortalamalarının incelenmesi

## Okul özelliklerini içeren veriseti ile ortalama sütunu birleştirilmesi
"""

df_okul_ozellik = pd.merge(df_okullar, okul_ortalamalari, how='right', left_on='okul_adi', right_on='okuladi')

df_okul_ozellik.drop(columns = "okuladi", inplace=True)

df_okul_ozellik

"""###Okul özellikleri ile not ortalamalarının ilişkilerinin incelenmesi"""

fig, ax = plt.subplots(figsize=(25,10)) 
plt.xticks(rotation=60)
sns.heatmap(df_okul_ozellik.corr(), annot=True, linewidths=0.3, ax=ax)

reduced_col_names = df_okul_ozellik.corr().abs()["ortalamalar"].index
df_okul_ozellik[reduced_col_names].corr()["ortalamalar"]

fig, ax = plt.subplots(figsize=(16,8), dpi=100) 
sns.set(font_scale=1.1)
sns.heatmap(df_okul_ozellik[reduced_col_names].corr(), annot=True, linewidths=0.3, ax=ax)
plt.xticks(rotation=60)

"""---

##Sene sonu notlarının teker teker incelenmesi
"""

yeni_df = filtered_df[["okuladi", "ort5", "ort6", "ort7"]]

yeni_df

yeni_ort = pd.merge(df_okullar,yeni_df , how='right', left_on='okul_adi', right_on='okuladi')

yeni_ort.drop(columns="okuladi", axis=1, inplace=True)

yeni_ort

df_yeni_ortalamalar = pd.DataFrame(yeni_ort.iloc[:, -3:].mean(axis=1), columns=["ortalamalar"])

df_yeni_ortalamalar

df_yeni_ortalamalar = pd.merge(yeni_ort, df_yeni_ortalamalar, left_index=True, right_index=True)

df_yeni_ortalamalar

fig, axes = plt.subplots(1, 3, figsize=(25,5), sharey=True)

sns.set(font_scale=1.2)
sns.regplot(ax=axes[0],x=yeni_ort.derslik_sayisi, y=yeni_ort.ort7, ci=100).set_title("7. Sınıf ort. ile derslik sayısı ilişkisi");
#axes[0].set_title('Title of the first chart')
sns.regplot(ax=axes[1], x=yeni_ort.yuksek_mezun, y=yeni_ort.ort7, ci=100).set_title("7. Sınıf ort. ile yüksek lisans mezunu personel sayısı ilişkisi");
sns.regplot(ax=axes[2],x=yeni_ort.bina_alani, y=yeni_ort.ort7, ci=100).set_title("7. Sınıf ort. ile bina alanı ilişkisi");

sns.jointplot(x = yeni_ort.derslik_sayisi, y = yeni_ort.ort7, kind="kde")

sns.jointplot(x = yeni_ort.yuksek_mezun, y = yeni_ort.ort7, kind="kde")

sns.jointplot(x = yeni_ort.bina_alani, y = yeni_ort.ort7, kind="kde")

df_ort5 = yeni_ort.drop(columns = ["ort6", "ort7"], axis = 1)

df_ort5

fig, ax = plt.subplots(figsize=(25,10)) 
plt.xticks(rotation=60)
sns.heatmap(df_ort5.corr(), annot=True, linewidths=0.3, ax=ax)

"""#Okullara göre not ortalamalarının dağılımları"""

plt.figure(figsize=(16,12))
sns.set_context("paper", font_scale=2)
ax = sns.boxplot(x = df_yeni_ortalamalar.okul_adi, y = df_yeni_ortalamalar.ortalamalar)
ax = sns.swarmplot(x="okul_adi", y="ortalamalar", data=df_yeni_ortalamalar, color=".25")
plt.xticks(rotation=60)                                                               
plt.tight_layout()  
plt.show()
