import datetime
import difflib
import json
import os
import re
import sys

import textdistance as td

from dateparser.search import search_dates
from dateutil.relativedelta import relativedelta

def get_digits(word):
    if not re.search('\d+', word):
        # no digits from 0-9
        if not re.search('[०१२३४५६७८९]+', word):
            return -1
        return re.search('[०१२३४५६७८९]+', word).group()
    return re.search('\d+', word).group()

def get_month(sent):    # Similar to get education
    thresh = 0.65
    possible_words = {'शून्य':0,'एक':1,'दो':2,'तीन':3,'चार':4,'पांच':5,'छः':6,'सात':7,'आठ':8,'नौ':9,'लास्ट':9,'पहला':1,
                    'दूसरा':2,'तीसरा':3,'चौथा':4,'पांचवा':5,'छत्ता':6,'चट्टा':6,'सातवा':7,'आठवा':8,'नौंवा':9,'नवा':9,'शुरू':1,
                    'नाना':9}
    suffix = ['वी','टी','वा']
    general_words = {'हां':1,'हाँ':1,'सब':9,'नहीं':0,'ना':0}

    sent = sent.strip()
    words = sent.split()
    for word in words:
        digits = get_digits(word)
        if digits != -1:
            return int(digits)
        for pos_word in possible_words:
            if td.levenshtein.normalized_similarity(pos_word, word) >= thresh:
                return possible_words[pos_word]
            elif td.levenshtein.normalized_similarity(pos_word+suffix[0], word) >= thresh\
             or td.levenshtein.normalized_similarity(pos_word+suffix[1], word) >= thresh\
             or td.levenshtein.normalized_similarity(pos_word+suffix[2], word) >= thresh:
                return possible_words[pos_word]
        for gen_word in general_words:
            if gen_word == word:    # It is better to have exact match here
#                 print(word, gen_word)
                return general_words[gen_word]
    return -1


# This function returns 1 for haa, 0 for na and -1 if none present
def findYesNo(sentence):
    yesList = ['हां','हाँ']
    noList = [ 'नहीं' , 'ना']
    ans = -1
    for word in sentence.split():
        if word in yesList:
            ans = 1
            break
        elif word in noList:
            ans = 0
            break
        else:
            continue
            
    if ans == -1:
        yesMatchList, noMatchList = [], []
        for word in sentence.split():
            yesMatchList.append(difflib.get_close_matches(word, yesList))
            noMatchList.append(difflib.get_close_matches(word, noList))
        
        if len(noMatchList)!=0 and len(yesMatchList) != 0:
            ans = -1
        elif len(noMatchList)!=0 :
            ans = 0
        elif len(yesMatchList)!=0 :
            ans = 1
        return ans
    else:
        return ans


def findDate(sentence):
    outSentence = {'Date':'-1','Month':'-1','Year':'-1'}

    rawMonths=['जनवरी','फरवरी','मार्च','अप्रैल','मई','जून','जुलाई','अगस्त','सितंबर','अक्टूबर','नवंबर','दिसंबर']
    hindiMonths=['चैत्र','बैसाख','ज्येष्ठ','आषाढ़','सावन','भाद्रपद','आश्विन','कार्तिक','अग्रहायण','पौष','माघ','फाल्गुन']
    hindiMonthsDict = {i:j for (j,i) in enumerate(hindiMonths)}
    hindiMonthPrefix=['पहला','दूसरा','तीसरा','चौथा','पांचवां','छठा','सातवां','आठवां','नौवां','दसवां','ग्यारहवां','बारहवां']
    hindiMonthPrefixDict = {i:j for (j,i) in enumerate(hindiMonthPrefix)}

    #Now for date and month
    flag=0
    for month in rawMonths:
        if month in sentence:
            outSentence['Month']=month
            flag=1
            break

    #Now checking for months in hindi
    if flag==0:
        for month in hindiMonths:
            if month in sentence:
                outSentence['Month']=month #rawMonths[hindiMonthsDict[month]]
                flag=1
                break

    item=sentence.replace("-"," ").split()

    #Now for hindi prefix like pehla mahina, dusra mahine, teesra mahina and continued till 12th months

    if(len(item)>=2):
        for i in range(len(item)-1):
            if item[i] in hindiMonthPrefix and (item[i+1]=='महीना' or item[i+1] == "महिना"):
                if flag==0:
                    outSentence['Month'] =  rawMonths[hindiMonthPrefixDict[item[i]]] #item[i]
                    flag=1
                    break

#     total+=len(item)

    #For Months
    if(len(item)>=2):
        for i in range(len(item)-1):
                if item[i].isdigit() and item[i+1].isdigit() and len(item[i])!=4 and len(item[i+1])!=4:
                    if flag==0:
                        if (int(item[i+1])) <= 12:
                            outSentence['Month'] =  rawMonths[int(item[i+1])-1] #item[i+1]
                            flag=1
                            break
                elif item[i].isdigit() and item[i+1].isdigit() and len(item[i])!=4 and len(item[i+1])==4:
                    if flag==0:
                        if len(item[i])==1 and int(item[i])!=0:
                            outSentence['Month'] = rawMonths[int(item[i])-1] #item[i]
                            flag=1
                            break
                        elif len(item[i])==3:
                            if int(item[i][:2]) <= 31 and int(item[i][2]) != 0:
                                outSentence['Month'] =  rawMonths[int(item[i][2])-1] #item[i][2]
                                flag = 1
                                break
                            elif int(item[i][:2]) <= 31 and int(item[i][2]) == 0:
                                if int(item[i][1])==1:
                                    outSentence['Month'] =  rawMonths[int(item[i][1:])-1] #item[i][1:]
                                    flag = 1
                                    break
                        elif len(item[i])==2:
                            if int(item[i])<=12:
                                outSentence['Month'] =  rawMonths[int(item[i])-1] #item[i]
                                flag=1
                                break
                            else:
                                outSentence['Month'] =  rawMonths[int(item[i][1])-1] #item[i][1]
                                flag = 1
                                break
                        else:
                            z = 2 #dummy

                elif item[i].isdigit() and item[i+1].isdigit() and len(item[i])==4 and len(item[i+1])==4:
                    if flag==0:
                        if int(item[i+1]) <= 2100 and int(item[i+1]) >= 1900:
                            if int(item[i][2:]) <= 12:
                                outSentence['Month'] =  rawMonths[int(item[i][2:])-1] #item[i][2:]
                                flag = 1
                                break
                else:
                    z=2 #Dummy

#     if truthMonths[-1]==1:
#         trainMonthOut.append(1)
#     else:
#         trainMonthOut.append(0)

    flagDate=0
    if len(item)>=2:
        for i in range(len(item)-1):
                if item[i].isdigit() and item[i+1].isdigit() and len(item[i])!=4 and len(item[i+1])!=4:
                    if flagDate==0:
                        outSentence['Date'] = item[i]
                        flagDate=1
                        break
                elif item[i].isdigit() and len(item[i])!=4 and not item[i+1].isdigit() and int(item[i])<32:
                    if flagDate==0:
                        suppList = ["साल","महीना","महिना"]
                        if not(item[i+1] in suppList):
                            outSentence['Date'] = item[i]
                            flagDate=1
                            break
                elif item[i].isdigit() and item[i+1].isdigit() and len(item[i])!=4 and len(item[i+1])==4:
                    if flagDate==0:
                        if len(item[i])==3:
                            if int(item[i][:2]) <= 31 and int(item[i][2]) != 0:
                                outSentence['Date'] = item[i][:2]
                                flagDate = 1
                                break
                            elif int(item[i][:2]) <= 31 and int(item[i][2]) == 0:
                                if int(item[i][1])==1:
                                    outSentence['Date'] = item[i][0]
                                    flagDate = 1
                                    break
                        elif len(item[i])==2:
                            if int(item[i])<=12:
                                z = 2 #Do  nothing
                            else:
                                outSentence['Date'] = item[i][0]
                                flagDate = 1
                                break
                        else:
                            z = 2 #dummy
                elif item[i].isdigit() and item[i+1].isdigit() and len(item[i])==4 and len(item[i+1])==4:
                    if flagDate==0:
                        if int(item[i+1]) <= 2100 and int(item[i+1]) >= 1900:
                            if int(item[i][2:]) <= 12:
                                outSentence['Date'] = item[i][:2]
                                flagDate = 1
                                break
                else:
                    z=2
    elif len(item) == 1:
        try:
            if type(int(item[0]))==int:
                if int(item[0]) <= 31:
                    outSentence['Date'] = item[0]
                    flagDate = 1
        except:
            z = 2 # Basically do nothing

    ##############################################################################################
    flagYear=0
    for items in sentence.replace("-"," ").split():
        try:
            if len(items) == 4 and int(items) > 1900 and int(items) < 2100:
                outSentence['Year'] = items
                flagYear=1
                break
        except:
            z=2 #Dummy z
    if flagYear!=1:
        words = sentence.replace("-"," ").split()
        for i in range(len(words)-2):
            try:
                if (type(int(words[i])) == int)  and (type(int(words[i+1]))==int) and (type(int(words[i+2]))==int):
                    if len(words[i+2])==2:
                        if int(words[i+2]) > 50:
                            outSentence['Year'] = "19"+words[i+2]
                        else:
                            outSentence['Year'] = "20"+words[i+2]
                        flagYear = 1
                        break
            except:
                z=2
    if flagYear!=1:
        words = sentence.replace("-"," ").split()
        for i in range(len(words)-1):
            if words[i] in rawMonths or words[i] in hindiMonths or words[i] in hindiMonthPrefix:
                if words[i+1].isdigit() and len(words[i+1])==2:
                    if int(words[i+1])>=50:
                        outSentence['Year'] = "19"+str(words[i+1])
                    else:
                        outSentence['Year'] = "20"+str(words[i+1])
                    flagYear =1
                    break

#     json_Output = json.dumps(outSentence,ensure_ascii=False)
    return outSentence
    

def preprocess_date(sent):
    thresh = 0.80
    hi_nums = ['शून्य','एक','दो','तीन','चार','पांच','छः','सात','आठ','नौ','दस','ग्यारह','बारह','तेरह','चौदह',
             'पंद्रह','सोलह','सत्रह','अट्ठारह','उन्निस','बीस','इक्कीस','बाईस','तेईस','चौबीस','पच्चीस','छब्बीस','सत्ताईस','अट्ठाईस','उनतीस','तीस','इकतीस',
             'बत्तीस','तैंतीस','चौंतीस','पैंतीस','छ्त्तीस','सैंतीस','अड़तीस','उनतालीस','चालीस','इकतालीस','बयालीस','तैंतालीस','चौंतालीस',
             'पैंतालीस','छियालीस','सैंतालीस','अड़तालीस','उनचास','पचास','इक्याबन','बावन','तिरेपन','चौबन','पचपन','छप्पन','सत्तावन',
            'अट्ठावन','उनसठ','साठ','इकसठ','बासठ','तिरसठ','चौंसठ','पैंसठ','छियासठ','सड़सठ','अड़सठ','उनहत्तर','सत्तर','इकहत्तर',
            'बहत्तर','तिहत्तर','चौहत्तर','पचहत्तर','छिहत्तर','सतहत्तर','अठहत्तर','उनासी','अस्सी','इक्यासी','बयासी','तिरासी','चौरासी',
             'पचासी','छियासी','सतासी','अठासी' ,'नवासी','नब्बे','इक्यानबे','बानवे','तिरानवे','चौरानवे','पचानवे','छियानवे','सत्तानवे',
             'अट्ठानवे','निन्यानवे' ,'सौ']
    
    pos_words = {'डेढ़':'1 साल 6 महीना', 'ढाई':'2 साल 6 महीना','डाइट':'2 साल 6 महीना', 'चार्ट':'साल', 'वर्स':'साल',
                 'वर्ष':'साल', 'नव':'9','नाना':'9', 'चैप्टर':'4', 'वाट':'साल'}
    
    words = sent.split(' ')
    out_sent = []
    for idx, word in enumerate(words):    
        for pw_idx, pos_word in enumerate(hi_nums):
            if td.levenshtein.normalized_similarity(pos_word, word) >= thresh:
                words[idx] = str(pw_idx)
        for pos_word in pos_words:
            if td.levenshtein.normalized_similarity(pos_word, word) >= thresh:
                words[idx] = pos_words[pos_word]
    
    words = ' '.join(words)
#     print(words)
    return words


def get_age(sent):
    curr_date = datetime.datetime.now()

    sent = preprocess_date(sent)
    out = search_dates(sent)
    if out == None and re.search('\d+', sent) != None:
        idx = re.search('\d+', sent).end()
        out = search_dates(sent[:idx]+' साल'+sent[idx:])
    out_date = []
    age = []
    if out != None:
        for o in out:
            out_date.append(str(o[1].year) + ' years ' + str(o[1].month) + ' months ' + str(o[1].day) + ' days')
            age_diff = relativedelta(curr_date.date(),o[1].date())
            age.append(str(age_diff.years) + ' years ' + str(age_diff.months) + ' months ' + str(age_diff.days) + ' days ')
    return age
