import argparse
import datetime
import json
import os
import sys

import numpy as np
import pandas as pd
import textdistance as td

def near_str(word1, word2):
    word1 = str(word1)
    word2 = str(word2)
    return td.levenshtein.normalized_similarity(word1, word2)

def checkInSen(word, sentence):
    word = str(word)
    sentence = str(sentence)
    for pos_words in sentence.split():
        if near_str(word, pos_words) >= 0.65:
            return True
    return False

def findDate(sentence):
    sentence = str(sentence)
    import json
    outSentence = {'Date':'-1','Month':'-1','Year':'-1'}

    rawMonths=['जनवरी','फरवरी','मार्च','अप्रैल','मई','जून','जुलाई','अगस्त','सितंबर','अक्टूबर','नवंबर','दिसंबर']
    rawMonthsDict = {i:j%12+1 for (j,i) in enumerate(rawMonths)}
    hindiMonths=['चैत्र','बैसाख','ज्येष्ठ','आषाढ़','सावन','भाद्रपद','आश्विन','कार्तिक','अग्रहायण','पौष','माघ','फाल्गुन']
    hindiMonthsDict = {i:((j+3)%12+1) for (j,i) in enumerate(hindiMonths)}
    hindiMonthPrefix=['पहला','दूसरा','तीसरा','चौथा','पांचवां','छठा','सातवां','आठवां','नौवां','दसवां','ग्यारहवां','बारहवां']
    hindiMonthPrefixDict = {i:j%12+1 for (j,i) in enumerate(hindiMonthPrefix)}

    #Now for date and month
    flag=0
    for month in rawMonths:
        if month in sentence:
            outSentence['Month']=str(rawMonthsDict[month])
            flag=1
            break
            

    #Now checking for months in hindi
    if flag==0:
        for month in hindiMonths:
            if month in sentence:
                outSentence['Month']=str(hindiMonthsDict[month]) 
                flag=1
                break
    
    
    
    item=sentence.replace("-"," ").replace("/"," ").split()
    
    for i in range(len(item)):
        item[i]= item[i].lstrip('0')
    
    # Near string matching for rawMonths
    
    if flag==0:
        for senWords in item:
            for month in rawMonths:
                if near_str(senWords,month) >= 0.65:
                    outSentence['Month'] = str(rawMonthsDict[month])
                    flag = 1
                    break
            
            if flag==1:
                break
    
    # Near String Matching for hindiMonths
    if flag==0:
        for senWords in item:
            for month in hindiMonths:
                if near_str(senWords, month) >= 0.65:
                    outSentence['Month'] = str(hindiMonthsDict[month])
                    flag = 1
                    break
            
            if flag==1:
                break
        

    # Now for hindi prefix like pehla mahina, dusra mahine, teesra mahina and continued till 12th months

    if(len(item)>=2):
        for i in range(len(item)-1):
            if checkInSen(item[i], hindiMonthPrefix) and (near_str(item[i+1],'महीना') >= 0.65 or near_str(item[i+1],'महिना')
                                                >= 0.65):
                if flag==0:
                    outSentence['Month'] =  hindiMonthPrefixDict[item[i]] #item[i]
                    flag=1
                    break

#     total+=len(item)
    
    
    
    #For Months
    if(len(item)>=2):
        for i in range(len(item)-1):
                if item[i].isdigit() and item[i+1].isdigit() and len(item[i])!=4 and len(item[i+1])!=4:
                    if flag==0:
                        if (int(item[i+1])) <= 12:
                            outSentence['Month'] =  str(int(item[i+1])) #item[i+1]
                            flag=1
                            break
                elif item[i].isdigit() and item[i+1].isdigit() and len(item[i])!=4 and len(item[i+1])==4:
                    if flag==0:
                        if len(item[i])==1 and int(item[i])!=0:
                            outSentence['Month'] = str(int(item[i])) #item[i]
                            flag=1
                            break
                        elif len(item[i])==3:
                            if int(item[i][:2]) <= 31 and int(item[i][2]) != 0:
                                outSentence['Month'] =  str(int(item[i][2])) #item[i][2]
                                flag = 1
                                break
                            elif int(item[i][:2]) <= 31 and int(item[i][2]) == 0:
                                if int(item[i][1])==1:
                                    outSentence['Month'] =  str(int(item[i][1:])) #item[i][1:]
                                    flag = 1
                                    break
                        elif len(item[i])==2:
                            if int(item[i])<=12:
                                outSentence['Month'] =  str(int(item[i])) #item[i]
                                flag=1
                                break
                            else:
                                outSentence['Month'] =  str(int(item[i][1])) #item[i][1]
                                flag = 1
                                break
                        else:
                            z = 2 #dummy

                elif item[i].isdigit() and item[i+1].isdigit() and len(item[i])==4 and len(item[i+1])==4:
                    if flag==0:
                        if int(item[i+1]) <= 2100 and int(item[i+1]) >= 1900:
                            if int(item[i][2:]) <= 12:
                                outSentence['Month'] =  str(int(item[i][2:])) #item[i][2:]
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

def main(query):
    if type(query)==datetime.datetime:
        tempDate = datetime.datetime.date(query)
        query = tempDate.strftime("%d-%m-%Y")
    
    out = findDate(query)

    return out['Date'], out['Month'], out['Year']

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', type=str, help='User response in natural langugage', required=True)
    args = parser.parse_args()
    date, month, year = main(args.query)
    print("Date value : {} \nMonth value : {} \nYear value : {}".format(date, month, year))
