# -*- coding: utf-8 -*-
import pandas as pd
import polyglot
import pprint
import re
import sys
import warnings

from locationEntityMatch import getEntityLocation
from polyglot_location_analysis import getPolyglotLocation, getLocation

warnings.filterwarnings("ignore")

def SortTuples(tup):
    n = len(tup) 
    for i in range(n): 
        for j in range(n-i-1): 
            if tup[j][0] > tup[j + 1][0]: 
                tup[j], tup[j + 1] = tup[j + 1], tup[j]              
    return tup 

def preprocess_text(s):
    s = ' प्रदेश'.join(s.split('प्रदेश'))
    s = s.replace('नालंदा', 'नालन्दा')
    s = s.strip()
    s = ' '.join(s.split())
    return s

def get_super_tup(val1, val2):
    intersecting_states = [val for val in val1[1] if val in val2[1]]
    res_tups = []

    for tup in [val1, val2]:
        if len(tup[2]) != 0 and len(tup[2]) < len(tup[1]):
            while len(tup[2]) != len(tup[1]):
                tup[2].append(tup[2][-1])
        if len(tup[3]) != 0 and len(tup[3]) < len(tup[2]):
            while len(tup[3]) != len(tup[2]):
                tup[3].append(tup[3][-1])
        if len(tup[2]) == 0:
            res_tups.append(tup)
        elif len(tup[3]) == 0:
            for s, d in zip(tup[1], tup[2]):
                res_tups.append((tup[0], [s], [d], tup[3], tup[-1]))
        else:
            for s, d, sd in zip(tup[1], tup[2], tup[3]):
                res_tups.append((tup[0], [s], [d], [sd], tup[-1]))

    max_len = 0
    min_alpha = 10000
    res = []
    for tup in res_tups:
        for state in tup[1]:
            if state in intersecting_states and (len(tup[1]) + len(tup[2]) + len(tup[3]) > max_len):
                max_len = len(tup[1]) + len(tup[2]) + len(tup[3])
    for tup in res_tups:
        for state in tup[1]:
            if state in intersecting_states and (len(tup[1]) + len(tup[2]) + len(tup[3]) == max_len) and tup[0] <= min_alpha:
                min_alpha = tup[0]
                res = tup
    return res



def get_intersect_states(tup):
    """
    function to get only the intersecting states
    For example in two tuples : ([MP], _, _) and ([MP, Bihar], [dist1, dist2], [sd])
    where the subdistrict is common, we take the intersection based on the state since
    that was explicitly included as another entity. Hence result will be (MP, dist1, sd)
    """
    res = []
    intersect_idxs = set()
    for i in range(len(tup)):
        if i not in intersect_idxs:
            for j in range(i+1, len(tup)):
                if len([val for val in tup[i][1] if val in tup[j][1]]) != 0:    # there exists intersecting state
                    intersect_idxs.add(i)
                    intersect_idxs.add(j)
                    super_tup = get_super_tup(tup[i], tup[j])
                    res.append(super_tup)
            if i not in intersect_idxs:
                res.append(tup[i])
    return res

def is_subset(val1, val2):
    # print("val1 : {} val2 : {} and is subset : {}".format(val1, val2, all(x in val1 for x in val2)))
    return all(x in val2 for x in val1)

def removeDuplicates(tup):
    # tup = [(alpha, set(st), set(dst), set(subdst), val) for (alpha, st, dst, subdst, val) in tup]
    res = []
    eq_idxs = set()
    for i in range(len(tup)):
        isSubset = False
        isEq = False
        for j in range(len(tup)):
            if i != j:
                if tup[i][1] == tup[j][1] and tup[i][2] == tup[j][2] and tup[i][3] == tup[j][3]:
                    isEq = True
                    eq_idxs.add(j)
                    continue
                if is_subset(tup[i][1], tup[j][1]) and is_subset(tup[i][2], tup[j][2]) and is_subset(tup[i][3], tup[j][3]):
                    isSubset = True
                    break
        if not isSubset:
            if isEq:
                if i not in eq_idxs:
                    eq_idxs.add(i)
                    res.append(tup[i])
            else:
                res.append(tup[i])
    # tup = [(alpha, list(st), list(dst), list(subdst), val) for (alpha, st, dst, subdst, val) in res]
    return res

def fine_tune(locs, s):
    """
    Placing a little bias on the presence of state
    Eg : (Chattisgarh, _, _) and (MP, d, sd) and sentence contained
    I live in Chattisgarh in sd.
    Then even though sd matched second tuple, higher bias is given to match of state.
    """
    states = set([state[0] for loc in locs for state in loc[1]])
    # print("States : {}".format(states))
    present_states = [state for state in states if state in s]
    # print("Present States : {}".format(present_states))
    if len(present_states) == 0:
        return locs
    best_locs = []
    for loc in locs:
        for state in loc[1]:
            if state[0] in present_states:
                best_locs.append(loc)
                break
    return best_locs

def fine_tune_polyglot(s):
    res = []
    for idx, entity in enumerate(s):
        loc = ''.join(re.split('जिला|ज़िला', entity))
        # loc = loc.strip()
        res.append(loc)
    return res

def sthaan(s):
    s = preprocess_text(s)
    polyglotLocation = getLocation(s)
    # print(polyglotLocation)
    polyglotLocation = fine_tune_polyglot(polyglotLocation)
    print("Polyglot location : {}".format(polyglotLocation))
    # print(polyglotLocation)
    curloc = []
    for entity in polyglotLocation:
        curloc.append(getEntityLocation(entity))
    print(curloc)
    curloc = SortTuples(curloc)
    curloc = get_intersect_states(curloc)
    curloc = removeDuplicates(curloc)
    min_alpha = 10000
    best_locs = []
    for loc in curloc:
        if loc[0] != -1 and loc[0] <= min_alpha:
            min_alpha = loc[0]
            best_locs.append(loc)
    if len(best_locs) == 0:
        return [(-1, [], [], [], "")]
    best_locs = fine_tune(best_locs, s)
    return best_locs
