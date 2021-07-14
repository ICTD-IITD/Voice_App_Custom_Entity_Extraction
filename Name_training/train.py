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
from util import save_obj, load_obj, root

######################################
data_hi_file = root+"/hindi_en_labelled_alldata.csv"
outdf = pd.read_csv(data_hi_file)["hi"][:20000]

def getPersons(outdf):
    persons = []
    person_raw = []
    notpersons = []
    notperson_raw = []
    for i, script in enumerate(outdf):
        replaceNameTags(script)
        splitscript = script.split(" ")
        removeBlanks(splitscript)
        for j, ss in enumerate(splitscript):
            if "#(person)" in ss:
                person_raw.append(splitscript)
                mystr = getFiveGrams(splitscript, j)
                persons.append([i, mystr])
            elif "#(person)" != splitscript[j-1]:
                notperson_raw.append(splitscript)
                mystr = getFiveGrams_2(splitscript, j)
                notpersons.append([i, mystr])
        else:
            i-0
    persons = pd.DataFrame(persons)
    notpersons = pd.DataFrame(notpersons)
    return persons, person_raw, notpersons, notperson_raw


######################################
def buildVocab(persons, notpersons):
    """ Builds vocabulary of words occuring """
    dataPerson = np.asarray(persons)
    vocabPerson = dataPerson[:,1]
    i = 0
    vocabData={}
    traceData={}
    labelData={}
    for sentence in vocabPerson:
        for words in sentence.split():
            if words not in vocabData:
                vocabData[words]=i
                traceData[i]=sentence
                labelData[i]=1
                i=i+1

    datanotPerson=np.asarray(notpersons)
    vocabNotPerson=datanotPerson[:,1]
    for sentence in vocabNotPerson:
        for words in sentence.split():
            if words not in vocabData:
                vocabData[words]=i
                traceData[i]=sentence
                labelData[i]=0
                i=i+1
    return vocabData, traceData, labelData

persons, _, notpersons, _ = getPersons(outdf)[:int(len(outdf)/2)] 
vocabData, traceData, labelData = buildVocab(persons, notpersons)
save_obj(vocabData, "vocabData")

print("vocabulary size", len(vocabData))
######################################
def onehotData(persons, notpersons):   
    """ Transfers regular data into vectorised form with nxVocabSize dimension """ 
    personsData=np.array(persons)
    (a,b)=personsData.shape
    dataMade=np.zeros((a,len(vocabData)+1))
    for j in range(a):
        for word in personsData[j][1].split():
            if word in vocabData:
                dataMade[j][vocabData[word]]=1
            else:
                dataMade[j][-1]=1
        
    notpersonsData=np.array(notpersons)
    notdataMade=np.zeros((a,len(vocabData)+1))
    for j in range(a):
        for word in notpersonsData[j][1].split():
            if word in vocabData:
                notdataMade[j][vocabData[word]]=1
            else:
                notdataMade[j][-1]=1
    return dataMade, notdataMade

persons, _, notpersons, _ = getPersons(outdf) 
dataMade, notdataMade = onehotData(persons, notpersons)

######################################
def addExtraData(sampleX, vocabData, traceData, labelData):
    """ Adds extra data to make sure all words of vocabData has atleast 1 element in training set"""
    """ Internal Function : used inside of getTrainingData function"""
    wordcount = np.sum(sampleX, axis=0)
    a = np.sum(wordcount==0)
    extradataMade=np.zeros((a,len(vocabData)+1))
    extray = np.zeros(a, dtype=int)
    j = 0
    for i in range(len(wordcount)):
        if (wordcount[i]==0):
            for word in traceData[i].split():
                extradataMade[j][vocabData[word]] = 1
                extray[j] = labelData[i]
            j = j+1
    return extradataMade, extray
            
def getTrainingData(dataMade, notdataMade, vocabData, traceData, labelData):
    """ Generate Training Dataset """
    trainingsize = int(min(len(dataMade), len(notdataMade))) #10000
    X1 = dataMade[:trainingsize]
    X2 = notdataMade[:trainingsize]

    m = X1.shape[0]
    n = X2.shape[0]

    y1 = np.ones(m, dtype=int)
    y2 = np.zeros(n, dtype=int)

    sampleX = np.concatenate((X1, X2))
    sampley = np.concatenate((y1, y2))
    sampley = sampley.reshape(sampley.shape[0],1)

    X3, y3 = addExtraData(sampleX, vocabData, traceData, labelData)
    y3 = y3.reshape(y3.shape[0],1)

    sampleFX = np.concatenate((sampleX, X3))
    sampleFy = np.concatenate((sampley, y3))
    sampleFy = sampleFy.reshape(sampleFy.shape[0],1)
    
    return sampleFX, sampleFy

sampleX_enc, sampley = getTrainingData(dataMade, notdataMade, vocabData, traceData, labelData)

def getTestData(dataMade, notdataMade):
    """ Extract Test Dataset """
    trainingsize = int(min(len(dataMade), len(notdataMade))) #10000
    testX1 = dataMade[trainingsize:]
    testX2 = notdataMade[trainingsize:]


    m = testX1.shape[0]
    n = testX2.shape[0]

    testy1 = np.ones(m, dtype=int)
    testy2 = np.zeros(n, dtype=int)

    testX = np.concatenate((testX1, testX2))
    testy = np.concatenate((testy1, testy2))
    testX = testX.astype(int)
    testy = testy.reshape(testy.shape[0],1)
    return testX, testy

testX_enc, testy = getTestData(dataMade, notdataMade)
absentwords = np.sum(testX_enc, axis=0)


def trainModel(sampleX_enc, sampley):
    """Train SVM Model and save it to file """
    y = sampley.squeeze()
    p = svm_problem(y, sampleX_enc)

    parameter = svm_parameter()
    parameter.kernel_type = RBF
    parameter.gamma = 0.05
    parameter.C = 1

    model = svm_train(p, parameter)
    svm_save_model('libsvm.model', model)
    return

trainModel(sampleX_enc, sampley)

def testModel(sampleX_enc, sampley, testX_enc, testy):
    """Loads model from file and print accuracy metrics on train and test set"""
    model = svm_load_model('libsvm.model')
    y = sampley.squeeze()
    labels = svm_predict(y, sampleX_enc, model)
    printAccuracy("On training set",labels, sampleX_enc, sampley)

    ty = testy.squeeze()
    labels = svm_predict(ty, testX_enc, model)
    printAccuracy("On testing set",labels, testX_enc, testy)
    return

def printAccuracy(mystr, labels, testX, testy):  
    """Used inside of testModel Function """
    ty = testy.squeeze()  
    labels_output = np.array(labels[0])
    labels_confidence = np.array(labels[2])
    tX = testX.squeeze()
    to = labels_output.astype(int)
    tc = labels_confidence.squeeze()

    print(mystr)
    print("----------------------")
    print("accuracy ", accuracy_score(testy,to))
    print("confusion ", confusion_matrix(testy,to))
    print("precision_score ", precision_score(testy,to))
    print("recall_score ", recall_score(testy,to))
    print("f1_score ", f1_score(testy,to))
    return
    
testModel(sampleX_enc, sampley, testX_enc, testy)




