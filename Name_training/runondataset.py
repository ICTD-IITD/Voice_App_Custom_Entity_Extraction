import os
import sys
import copy
import numpy as np
import pandas as pd

from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score

from util import replaceNameTags, getFiveGrams, getFiveGrams_2, removeBlanks
from util import vectoriseData, insertColumn, loadModel, predict, getLabels
from util import save_obj, load_obj, root

######################################
# main_file = "/Users/ankit/btech-project/polyglot/polyglot_name/polyglotName_en.csv"
test_file = root+"/polyglotName_en_test.csv"
val_file = root+"/polyglotName_en_val.csv"
all_file = root+"/polyglotName_en35000.csv"

polyglot_out = val_file
datafile = pd.read_csv(polyglot_out)
vocabData = load_obj('vocabData')
######################################
### SVM on Polyglot
######################################

def getDataPoints_1(datafile):
    xp, yp, x_in, x_mid = [], [], [], []
    for i in range(len(datafile)):
        label = datafile["groundtruth"][i]
        if not (datafile["pn"][i] == "no name"):
            
            names = datafile["pn"][i].split(" ")[1:-1]
            while "'," in names:
                names.remove("',")
            while "'" in names:
                names.remove("'")
            while "." in names:
                names.remove(".")
                
                
            for x in names:
                
                
                hi = datafile["t"][i].split(" ")
                try:
                    index = hi.index(x)
                    if(index==0):
                        mystr = "X X "
                    elif(index==1):
                        mystr = "X " + hi[0] + " "
                    else:
                        mystr = hi[index-2] + " " + hi[index-1] + " "

                    mystr = mystr + hi[index] + " "

                    if(index==len(hi)-1):
                        mystr = mystr + "X X "
                    elif(index==len(hi)-2):
                        mystr = mystr + hi[len(hi)-1] + " X "
                    else:
                        mystr = mystr + hi[index+1] + " " + hi[index+2] + " "
                    xp.append(mystr)
                    yp.append(label)
                    x_in.append(i)
                    x_mid.append(hi[index])
                except:
                    # print(i, x)
                    pass
    return xp, yp, x_in, x_mid, len(datafile)

xp, yp, x_in, x_mid, datafile_len = getDataPoints_1(datafile)
xp = pd.DataFrame(xp)
yp = np.array(yp, dtype='int')

model = loadModel()
tX, to, tc = predict(xp, yp, vocabData, model)

labels = getLabels(x_in, x_mid, to, datafile_len)

insertColumn(datafile, "svm", labels)
datafile.to_csv(polyglot_out)

######################################

def getDataPoints_2(datafile):
    xp, yp, x_in, x_mid = [], [], [], []
    for i in range(len(datafile)):
        label = datafile["groundtruth"][i]
    
        if isinstance(datafile["t"][i],float): #location contains NaN and can't be processed
            pass
        else:
            names = datafile["t"][i].split(" ")

            while "'," in names:
                names.remove("',")
            while "'" in names:
                names.remove("'")
            while "." in names:
                names.remove(".")


            for x in names:


                hi = datafile["t"][i].split(" ")
                try:
                    index = hi.index(x)
                    if(index==0):
                        mystr = "X X "
                    elif(index==1):
                        mystr = "X " + hi[0] + " "
                    else:
                        mystr = hi[index-2] + " " + hi[index-1] + " "

                    mystr = mystr + hi[index] + " "

                    if(index==len(hi)-1):
                        mystr = mystr + "X X "
                    elif(index==len(hi)-2):
                        mystr = mystr + hi[len(hi)-1] + " X "
                    else:
                        mystr = mystr + hi[index+1] + " " + hi[index+2] + " "
                    xp.append(mystr)
                    yp.append(label)
                    x_in.append(i)
                    x_mid.append(hi[index])
                except:
                    # print(i, x)
                    pass
    return xp, yp, x_in, x_mid, len(datafile)

xp, yp, x_in, x_mid, datafile_len = getDataPoints_2(datafile)
xp = pd.DataFrame(xp)
yp = np.array(yp, dtype='int')

model = loadModel()
tX, to, tc = predict(xp, yp, vocabData, model)
labels = getLabels(x_in, x_mid, to, datafile_len, tc, alpha=0.5)

insertColumn(datafile, "svm_direct", labels)
datafile.to_csv(polyglot_out)

######################################

def getDataPoints_3(datafile):
    xp = []
    yp = []
    x_in = []
    x_mid = []
    ypoly_svm = [[] for i in range(len(datafile))]
    for i in range(len(datafile)):
        
        if (not datafile["pn"][i] == "no name"):
            label_poly_svm = datafile["svm"][i][1:-1].split(" ")
            ypoly_svm[i] = label_poly_svm

        if (datafile["pn"][i] == "no name"):
            label = datafile["groundtruth"][i]

            if isinstance(datafile["t"][i],float): #location contains NaN and can't be processed
                pass
            else:
                names = datafile["t"][i].split(" ")

                while "'," in names:
                    names.remove("',")
                while "'" in names:
                    names.remove("'")
                while "." in names:
                    names.remove(".")

                for x in names:

                    hi = datafile["t"][i].split(" ")
                    try:
                        index = hi.index(x)
                        if(index==0):
                            mystr = "X X "
                        elif(index==1):
                            mystr = "X " + hi[0] + " "
                        else:
                            mystr = hi[index-2] + " " + hi[index-1] + " "

                        mystr = mystr + hi[index] + " "

                        if(index==len(hi)-1):
                            mystr = mystr + "X X "
                        elif(index==len(hi)-2):
                            mystr = mystr + hi[len(hi)-1] + " X "
                        else:
                            mystr = mystr + hi[index+1] + " " + hi[index+2] + " "
                        xp.append(mystr)
                        yp.append(label)
                        x_in.append(i)
                        x_mid.append(hi[index])
                    except:
                        # print(i, x)
                        pass
    return xp, yp, x_in, x_mid, ypoly_svm, len(datafile)

xp, yp, _, _, _, datafile_len = getDataPoints_3(datafile)
xp = pd.DataFrame(xp)
yp = np.array(yp, dtype='int')


model = loadModel()
tX, to, tc = predict(xp, yp, vocabData, model)

labels = getLabels(x_in, x_mid, to, datafile_len)

insertColumn(datafile, "svm_direct", labels)
datafile.to_csv(polyglot_out)

######################################

def cleanColumns(datafile):
    for col in datafile.columns:
        if 'Unnamed' in col:
            try:
                del datafile[col]
            except:
                pass
    datafile = datafile[['t', 't_e', 'pn', 'svm', 'svm_extra', 'groundtruth']]
    return datafile

datafile = cleanColumns(datafile)
datafile.to_csv(polyglot_out)