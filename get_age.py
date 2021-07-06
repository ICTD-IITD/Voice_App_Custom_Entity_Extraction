"""
Using the dateparser library:
https://dateparser.readthedocs.io/en/latest/index.html
"""
import argparse
import datetime
import os
import re
import sys

import textdistance as td

from dateparser.search import search_dates
from dateutil.relativedelta import relativedelta

thresh = 0.80

def preprocess_date(sent):
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
    
    sent = str(sent)
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
    return words

def main(sent):
    curr_date = datetime.datetime.now()

    sent = preprocess_date(sent)
    out = search_dates(sent)
    if out == None and re.search('\d+', sent) != None:
        idx = re.search('\d+', sent).end()
        out = search_dates(sent[:idx]+' साल'+sent[idx:])
    
    out_age = []
    if out != None:
        for o in out:
            age_diff = relativedelta(curr_date.date(),o[1].date())
            out_age.append(str(abs(age_diff.years)) + ' years ' + str(abs(age_diff.months)) + ' months ' + str(abs(age_diff.days)) + ' days ')
    
    return ','.join(out_age)    # There should be a smart merge function to merge the different list items

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', type=str, help='User query', required=True)
    args = parser.parse_args()
    user_age = main(args.query)
    print("Age of the person is : {}".format(user_age))
