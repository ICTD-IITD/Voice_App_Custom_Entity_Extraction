import re
import os
import sys
import warnings

import pandas as pd
import numpy as np

from collections import Counter
from nltk import word_tokenize
from tqdm import tqdm

warnings.filterwarnings("ignore")

# out of food
of_words = ['खाना', 'पीने', 'चावल', 'भोजन', 'भरण', 'खाने', 'खाने-पीने', 'खाना-वाना', 'खाद्य', 'अन्न', 'रोटी', 'अनाज', 'भूका', 'भूखा', 'भुखमरी', 'भूख', 'भूखे', 'प्यासा', 'प्यासे', 'भूखा-प्यासा', 'परेशान', 'भुकमरी', 'राशन', 'पानी', 'कार्ड', 'राशनकार्ड', 'राशन-कार्ड', 'मर', 'खान', 'रोज़ी-रोटी', 'तड़प', ]
# migrants stuck in city
msc_words = ['फसे', 'फस्स', 'फस', 'काम', 'फस्से', 'फ़से', 'फसें', 'फंस', 'फंसा', 'फँसे', 'फंसे', 'फसी', 'फसा', 'वापस', 'फँस', 'घर', 'गाँव', 'साधन', 'मज़दूर', 'मजदूर', 'तड़प', ]
# gas relief not received
gas_words = ['गैस', 'उज्ज्वला', 'योजना', 'योजनाओ', 'आयोजना', 'लाभ', 'सिलिंडर', ]
# cash relief not received
cash_words = ['कॅश', 'पैसे', 'पैसा', 'वेतन', 'आमदनी', 'राहत', 'पैकेज', 'सुविधा', 'सुविधाएँ', 'धन', 'सहायता', 'पेंशन', 'वृत्ति', 'पेन्शन', 'राशि', 'राशी', '2000', 'हज़ार', 'सब्सिडी', '1000', 'अकाउंट', 'नंबर', 'टेंशन', 'पेंशन', '₹1000', ]
# agri livelihood
agri_words = ['फसल', 'तैयार', 'खेती', 'किसान', 'कृषि', 'कृशि', 'क़ृषि', 'गल्ला', ]
# isolation center issues
iso_center_words = ['क्वारंटाइन', 'कोरोनाटाइन', 'क्वॉरेंटाइन', 'क्वारंटीन', 'वार्ड', 'हंगामा', 'आइसोलेशन', ]
# health_issues
health_issues_words = ['अस्पताल', 'हॉस्पिटल', 'दवा', 'ईलाज', 'औषधि', 'दवाई', 'डाक्टर', 'चिकित्सक', 'मेडिकल', 'बन्द', 'बंद',]
# bank not accessible
bank_words = ['बैंक', 'पैसे', 'पैसा', 'निकल', 'एटीएम', ]
# Social Distancing not being followed
social_dist_words = ['सोशल', 'डिस्टेसिंग', 'डिस्टेंस', 'अनुपालन', 'भीड़', 'धज्जियां', 'पालन', 'झुंड', 'उल्लंघन', ]
# Black marketing and price rise
bm_words = ['तुलना', 'भाव', 'उछाल', 'स्टोर', 'मुनाफा', 'ब्लैक', 'मार्केटिंग', ] 
# Health services issue
health_service_words = ['फार्मासिस्ट', 'मास्क', 'मार्क्स', 'सांइटिज़ेर', 'सनितीज़ेर', 'सनिटिज़र', ]
# Bias words
bias_words = ['उज्ज्वला', 'योजना', 'फँसे', 'फसे', 'फस्स', 'भूखा', 'खाने-पीने', 'भूखे', 'प्यासा', 'प्यासे', \
    'खेती', 'क्वारंटाइन', 'अस्पताल', 'बैंक', 'ब्लैक', 'सोशल', ]

reverse_map = {'of_words' : 'Out of Food', 'msc_words' : 'Migrant stuck in city', 'gas_words' : 'Gas relief not received', \
    'cash_words': 'Cash relief not received', 'agri_words' : 'Agricultural livelihood issue', 'iso_center_words' : 'Isolation center facilities issue',\
    'health_issues_words' : 'Health Emergency unmet', 'bank_words' : 'Bank not accessible', 'social_dist_words': 'social distancing not being followed',\
    'bm_words':'Black marketing and price rise', 'health_service_words':'Health services like vaccination or pharmacists unmet','':''}

def get_clean_data(filedf):
    # Return the audio items which contains the tag 'coronavirus' & ('sos'|'impact')
    clean_df = filedf[filedf['tags'].apply(lambda x: 'coronavirus' and ('sos' or 'impact') in x)]
    # clean_df = filedf[filedf.tags.str.contains('coronavirus', flags=re.IGNORECASE, regex=True)]
    # clean_df = clean_df[clean_df.tags.str.contains('sos|impact', flags=re.IGNORECASE, regex=True)]
    # or : clean_df = filedf[filedf['tags'].apply(lambda x: 'coronavirus' and ('sos' or 'impact') in x)]
    return clean_df

def get_category(transcript_cnt):
    categories = ['of_words', 'msc_words', 'gas_words', 'cash_words', 'agri_words',\
        'iso_center_words', 'health_issues_words', 'bank_words', 'social_dist_words',\
        'bm_words', 'health_service_words', ]
    max_category_score = 0
    max_category = ''
    secondary_max_category = ''
    total_words = sum(transcript_cnt.values())
    category_scores = []
    for category in categories:
        score = 0
        for word in transcript_cnt:
            if word in globals()[category]:
                score += transcript_cnt[word]
        score /= total_words
        category_scores.append((category, score))
        if score > max_category_score:
            max_category_score = score
            max_category = category
    category_scores = sorted(category_scores, key=lambda x: x[1], reverse=True)
    if category_scores[1][1] != 0:
        secondary_max_category = category_scores[1][0]
    else:
        secondary_max_category = ''
    # print(category_scores)
    return reverse_map[max_category], reverse_map[secondary_max_category]

def get_categories(transcripts, tags):
    categories = []
    infer_tags = []
    secondary_categories = []
    print("Starting classification")
    for transcript, tag in zip(transcripts, tags):
        cnt = Counter()
        try:
            if 'impact' in tag:
                infer_tags.append('impact')
            else:
                infer_tags.append('sos')
        except:
            infer_tags.append('')
        try:
            transcript = ' '.join(re.split('\||।', transcript)).strip()
            words = word_tokenize(transcript)
            for word in words:
                if word in bias_words:
                    cnt[word] += 3
                else:
                    cnt[word] += 1
            primary_category, secondary_category = get_category(cnt)
            categories.append(primary_category)
            secondary_categories.append(secondary_category)
        except:
            categories.append('')
            secondary_categories.append('')
    print("Classification finished")
    return categories, secondary_categories, infer_tags

if __name__ == '__main__':
    covid_filename = 'coronavirus_and_sos.xlsx'
    filedf = pd.read_excel(covid_filename)
    clean_df = get_clean_data(filedf)
    transcripts = clean_df['transcription'].tolist()
    tags = clean_df['tags'].tolist()
    categories, infer_tags = get_categories(transcripts, tags)
    clean_df['inferred_tag'] = infer_tags
    clean_df['auto_categories'] = categories
    clean_df.to_csv('auto_categories.csv', index=False)
