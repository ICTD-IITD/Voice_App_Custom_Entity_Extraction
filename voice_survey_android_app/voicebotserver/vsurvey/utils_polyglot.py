import os
import sys
import pkg_resources
import pickle
import json
import numpy as np
from subprocess import Popen
import codecs
import csv
import copy
#done with standard imports

import DOB.main as mainDOB
import Name.main as mainName
import Location.main as mainLoc


#*******************************************************************************
# Input to this function would be basically transcript in hindi from some audio file
def find_date_final(sentence):

  vectorizer, dateModel = pickle.load(open('./DOB/vectorizer','rb')), pickle.load(open('./DOB/dateModel','rb'))
  monthModel, yearModel  = pickle.load(open('./DOB/monthModel','rb')), pickle.load(open('./DOB/yearModel','rb'))

  valid = 0
  inputX = np.array([sentence])
  x_Encoded = np.array([vectorizer.transform(inputX).toarray().squeeze()])

  #First SVM Model will predict if there exists any of Date, Month or Year in the sentence, if it exists then it would call findDate.
  dateP, monthP, yearP = dateModel.predict(x_Encoded), monthModel.predict(x_Encoded), yearModel.predict(x_Encoded)
  valid = 1 if (dateP!=0 or monthP!=0 or yearP!=0) else 0

  if valid == 0:
      finalDOB = json.dumps({'Date':-1,'Month':-1,'Year':-1})
      # print(json.loads(finalDOB))
      return finalDOB
  else:
      #It will call findDate function of main.py file from DOB Module
      finalDOB = mainDOB.findDate(sentence)
      #finalDOB is be a JSON Object converted from python dictionary containing 'Date', 'Month' and 'Year' as key with their values
      # print(json.loads(finalDOB))
      return finalDOB

def get_name_final(input_string):
	naam = mainName.get_name(input_string)
	if(len(naam)==0):
		jsonnaam = json.dumps({"नाम":[]}).encode('utf8')
	else:
		jsonnaam = json.dumps({"नाम":naam}, ensure_ascii=False).encode('utf8')
	return jsonnaam.decode()

def get_loc_final(input_string):
	sthaan = mainLoc.get_loc(input_string)
	if(sthaan[0][0]==-1):
		jsonsthaan = json.dumps({"जगह":[]}).encode('utf8')
	else:
		sthaandict = []
		for s in sthaan:
			sthaandict.append({"राज्य":s[1], "शहर":s[2],"जिला":s[3],"समानता":s[0]})
		jsonsthaan = json.dumps({"जगह":sthaandict}, ensure_ascii=False).encode('utf8')
	return jsonsthaan.decode()

#***************************************************---------------------------------------------------------------------------*************************************************


def find_between(df, col, v1, v2):
    vals = df[col].values
    mx1, mx2 = (vals == v1).argmax(), (vals == v2).argmax()
    idx = df.index.values
    i1, i2 = idx.searchsorted([mx1, mx2])
    if(v2==36):
        return df.iloc[i1:]
    else:
        return df.iloc[i1:i2]

