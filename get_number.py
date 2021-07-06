import argparse
import difflib
import os
import re
import stanza
import sys

import textdistance as td

hi_nlp = stanza.Pipeline('hi', processors='tokenize,lemma,pos,depparse', verbose=False, use_gpu=False)

def findAge(sentence):
    thresh = 0.65
    sentence.replace(',',' ')
    sentence.replace(':',' ')
    sentence.replace('.',' ')
    sentence.replace('_',' ')
    sentence = sentence.strip()
    age = -1
    confd = 1
    hindiNum = ['जीरो','एक' ,'दो' ,'तीन' ,'चार' ,'पांच' ,'छः' ,'सात'   ,'आठ' ,'नौ' ,'दस' , 'ग्यारह' ,'बारह','तेरह','चौदह',
 'पंद्रह','सोलह','सत्रह','अट्ठारह' ,'उन्निस' ,'बीस','इक्कीस','बाईस','तेईस','चौबीस' ,'पच्चीस' ,'छब्बीस','सत्ताईस','अट्ठाईस' ,'उनतीस','तीस' ,'इकतीस' ,
 'बत्तीस','तैंतीस','चौंतीस' ,'पैंतीस','छ्त्तीस' ,'सैंतीस','अड़तीस' ,'उनतालीस' ,'चालीस' ,'इकतालीस' ,'बयालीस','तैंतालीस','चौंतालीस' ,
 'पैंतालीस' ,'छियालीस' ,'सैंतालीस','अड़तालीस','उनचास', 'पचास','इक्याबन' ,'बावन','तिरेपन','चौबन','पचपन', 'छप्पन','सत्तावन',
'अट्ठावन','उनसठ','साठ','इकसठ','बासठ','तिरसठ','चौंसठ','पैंसठ','छियासठ' ,'सड़सठ','अड़सठ','उनहत्तर','सत्तर' ,'इकहत्तर' ,
'बहत्तर','तिहत्तर','चौहत्तर' ,'पचहत्तर','छिहत्तर' ,'सतहत्तर' ,'अठहत्तर' ,'उनासी' ,'अस्सी' ,'इक्यासी' ,'बयासी','तिरासी' ,'चौरासी' ,
 'पचासी' ,'छियासी' ,'सतासी' ,'अठासी' ,'नवासी' ,'नब्बे' ,'इक्यानबे' ,'बानवे' ,'तिरानवे' ,'चौरानवे' ,'पचानवे' ,'छियानवे' ,'सत्तानवे' ,
 'अट्ठानवे' ,'निन्यानवे' ,'सौ']
    
    dictHindi = dict()
    
    # Just assigning numeral values to the hindi letters
    count = 0
    for word in hindiNum:
        dictHindi[word] = count
        count += 1
    
    dictHindi['छे'] = 6
    
    for words in sentence.split():
        if age!=-1:
            break
        try:
            if(type(int(words))==int):
                if(int(words) >= 0 and int(words) <= 1000):
                    age = int(words)
        except:
            z = 2
            
    suffix = ['वी','टी','वा']
    
    if age==-1:
        words = sentence.split()
        for word in words:
            for pos_word in hindiNum:
                first = td.levenshtein.normalized_similarity(pos_word, word)
                second = td.levenshtein.normalized_similarity(pos_word+suffix[0], word)
                third = td.levenshtein.normalized_similarity(pos_word+suffix[1], word)
                fourth = td.levenshtein.normalized_similarity(pos_word+suffix[2], word)
                confd = max(confd, first, second, third, fourth)
                if first >= thresh:
                    return (dictHindi[pos_word],first)
                elif second >= thresh or third >= thresh or fourth >= thresh:
                    return (dictHindi[pos_word],max(second, third, fourth))
                
        
        for word in words:
            if word=='छे':
                return (6,1)
    
    return age,confd

def posTagging(sentence):
    hi_doc = hi_nlp(sentence)
    for idx, sent in enumerate(hi_doc.sentences):
        out = []
        for word in sent.words:
            if word.pos=='NUM':
                out.append(word.text)
        if len(out)==0 and idx<len(list(hi_doc.sentences))-1:
            continue
        return out

def checkZero(sentence):
    thresh = 0.65
    noList = [ 'नहीं' , 'ना', 'नाही']
    words = sentence.split()
    for word in words:
        if word in noList:
            return 1
        else:
            for pos_word in noList:
                if td.levenshtein.normalized_similarity(pos_word, word) >= thresh:
                    return 1
    return 0
    
def findNumeralData(sentence):
    cZero = checkZero(sentence)
    if cZero==1:
        return (0,1)
    out = posTagging(sentence)
    x = len(out)
    if x == 0:
        return findAge(sentence)
    else:
        res = -1
        confd = 1
        for agla in out:
            res,confd = findAge(agla)
            if res!=-1:
                break
    return res, confd

def main(query):
    a, b = findNumeralData(str(query))
    return a

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', type=str, help='User response in natural langugage', required=True)
    args = parser.parse_args()
    number_val = main(args.query)
    print("Number value : {}".format(number_val))
