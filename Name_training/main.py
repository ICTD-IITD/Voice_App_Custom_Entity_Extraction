import os
import sys
import copy
import numpy as np
import pandas as pd
import os

from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import accuracy_score

from util import replaceNameTags, getFiveGrams, getFiveGrams_2, removeBlanks
from util import vectoriseData, insertColumn, loadModel, predict, getLabels
from util import save_obj, load_obj, predictMain, getLabelsMain, getfivegrams
from util import svm_predict

from name_utils import getName

######################################
######################################
### SVM on Polyglot
######################################

def get_name(t):
    vocabData = load_obj('vocabData')
    pn = str(getName(t))
    print("Pn is : {}".format(pn))
    xp, x_mid = getfivegrams(t, pn)
    print("xp is : ", xp)
    print("x_mid is :", x_mid)
    xp = pd.DataFrame(xp)


    model = loadModel()
    labels_output, labels_confidence = predictMain(model, vocabData, xp)
    print("Labels : ", labels_output)
    labels = getLabelsMain(labels_output, labels_confidence, x_mid)
    return labels

