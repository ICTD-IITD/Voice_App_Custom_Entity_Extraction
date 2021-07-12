import argparse
import contextlib
import datetime
import math
import re
import requests
import os
import pickle
import sys
import warnings
import wave

import pandas as pd
import numpy as np

from collections import Counter
from geopy.geocoders import Nominatim
from googletrans import Translator
from nltk import word_tokenize
from polyglot.text import Text
from tqdm import tqdm

from get_location import get_locations
from get_category import get_categories
from generate_audio_files import download_audio
from get_transcripts import generate_transcripts

warnings.filterwarnings("ignore")

translator = Translator()

state_abrevs = {'JK':'जम्मू और कश्मीर', 'HP':'हिमाचल प्रदेश', 'PB':'पंजाब', 'CH':'चण्डीगढ़', 'UK':'उत्तराखण्ड',\
    'HR':'हरियाणा', 'Dl- Ncr':'दिल्ली', 'RJ':'राजस्थान', 'UP':'उत्तर प्रदेश', 'BR':'बिहार', 'SK':'सिक्किम',\
    'AR':'अरूणाचल प्रदेश', 'NL':'नागालैंड', 'MN':'मणिपुर', 'MZ':'मिज़ोरम', 'TR':'त्रिपुरा', 'ML':'मेघालय', 'AS':'असम',\
    'WB':'पश्चिम बंगाल', 'JH':'झारखण्ड', 'OD':'ओडिशा', 'CG':'छत्तीसगढ़', 'MP':'मध्य प्रदेश', 'GJ':'गुजरात', 'DD':'दमन और दीव',\
    'DH':'दादरा और नागर हवेली', 'MH':'महाराष्ट्र', 'AP':'आन्ध्र प्रदेश', 'KA':'कर्नाटक', 'GA':'गोवा', 'LD':'लक्षद्वीप',\
    'KL':'केरल', 'TN':'तमिलनाडु', 'PY':'पुदुच्चेरी', 'Andaman And Nicobar':'अण्डमान एवं निकोबार द्वीपसमूह'}

format_map = {1:'Questions', 3:'News reports', 7:'User or reporter generated content',\
    8:'song or poetry', 9: 'Information or answer', 10: 'Interview', 15: 'SGC episode',\
    16: 'UGC episode', 0:''}

def get_clean_data(filedf):
    # Return the audio items which contains the tag 'coronavirus' & ('sos'|'impact')
    clean_df = filedf[filedf['tags'].apply(lambda x: 'coronavirus' and ('sos' or 'impact') in x)]
    clean_df = clean_df[clean_df['state'].apply(lambda x: x != 'UNM' and x != 'REJ')]
    return clean_df

def get_clean_locs(locs):
    # Unpack the tuples to make the locs a list of tuples. [(['पंजाब', 'उत्तर प्रदेश'], ['फिरोज़पुर', 'शाहजहाँपुर'], ['जलालाबाद'])] -> [(पंजाब, फिरोज़पुर, जलालाबाद), (उत्तर प्रदेश, शाहजहाँपुर, जलालाबाद)]
    max_len = 0
    new_locs = []
    for loc in locs:
        new_loc = []
        for l in loc:
            max_len = max(len(l[0]), len(l[1]), len(l[2]))
            for idx in range(3):
                while len(l[idx]) < max_len:
                    if len(l[idx]) != 0:
                        l[idx].append(l[idx][-1])
                    else:
                        l[idx].append('')
            new_loc.extend([i for i in zip(l[0], l[1], l[2])])
        new_locs.append(new_loc)
    return new_locs

def get_max_tup_len(loc_tups):
    final_lens = []
    for loc_tup in loc_tups:
        len_tup = 0
        for val in loc_tup:
            if len(val) != 0:
                len_tup += 1
        final_lens.append(len_tup)
    if len(final_lens) > 0:
        return max(final_lens)
    else:
        return 0

def get_transliterated_locs(locs, transliterated_locs_pth):
    states_roman = {'जम्मू और कश्मीर': 'Jammu and Kashmir','हिमाचल प्रदेश': 'Himachal Pradesh', 'पंजाब':'Punjab', 'चण्डीगढ़':'Chandigarh', 'उत्तराखण्ड':'Uttarakhand',\
        'हरियाणा':'Haryana', 'दिल्ली':'Delhi', 'राजस्थान':'Rajasthan', 'उत्तर प्रदेश':'Uttar Pradesh', 'बिहार':'Bihar', 'सिक्किम':'Sikkim',\
        'अरूणाचल प्रदेश':'Arunachal Pradesh', 'नागालैंड':'Nagaland', 'मणिपुर':'Manipur', 'मिज़ोरम':'Mizoram', 'त्रिपुरा': 'Tripura', 'मेघालय':'Meghalaya', 'असम':'Assam',\
        'पश्चिम बंगाल':'West Bengal', 'झारखण्ड':'Jharkhand', 'ओडिशा':'Odisha', 'छत्तीसगढ़':'Chhattisgarh', 'मध्य प्रदेश':'Madhya Pradesh', 'गुजरात':'Gujarat', 'दमन और दीव':'Daman and Diu',\
        'दादरा और नागर हवेली':'Dadra and Nagar Haveli', 'महाराष्ट्र':'Maharashtra', 'आन्ध्र प्रदेश':'Andhra Pradesh', 'कर्नाटक':'Karnataka', 'गोवा':'Goa', 'लक्षद्वीप':'Lakshwadeep',\
        'केरल':'Kerala', 'तमिलनाडु':'Tamil Nadu', 'पुदुच्चेरी':'Puducherry', 'अण्डमान एवं निकोबार द्वीपसमूह': 'Andaman and Nicobar Islands'}

    common_districts = {'चेन्नई':'Chennai', 'गोंदिया':'Gondia', 'मुंगेर':'Munger', 'समस्तीपुर':'Samastipur', 'फिरोज़पुर':'Firozpur', 'बलिया':'Boliya',\
        'अलीगढ़':'Aligarh', 'बेगूसराय':'Begusarai', 'पूर्वी':'East Delhi', 'बोकारो':'Bokaro', 'जलालाबाद':'Jalalabad', 'गाज़ीपुर':'Ghazipur', 'गुड़गांव':'Gurugram',\
        'पन्ना': 'Panna', 'गिद्धौर':'Gidhaur', 'पटना':'Patna', 'शाहजहाँपुर':'Shahjahanpur', 'सारण':'Saran', 'मुंबई':'Mumbai', 'टाटीझरिया':'Tati Jharia',\
        'मानेसर':'Manesar', 'बरियारपुर':'Bariyarpur', 'पेटरवार':'Petarwar', 'खगड़िया':'Khagaria', 'रायपुर':'Raipur', 'चतरा':'Chatra', 'कटिहार':'Katihar',\
        'जलालपुर':'Jalalpur', 'अजमेर':'Ajmer', 'सिंघिया':'Singhia', 'औरंगाबाद':'Aurungabad', 'जमुई':'Jamui', 'हरदोई':'Hardoi', 'इटावा':'Etawah',\
        'सोलन':'Solan', 'परसा':'Parsa', 'शिवपुरी':'Shivpuri', 'भागलपुर':'Bhagalpur', 'चकाई':'Chakkai', 'खगड़िया':'Khagariya', 'प्रकाशम':'Prakasam',\
        'छपरा':'Chhapra', 'हजारीबाग':'Hazaribagh', 'बरेली':'Bareilly', 'कटकमसांडी':'Katkamsandi', '':''}

    inferred_locs = []
    devanagari_locs = set() # set of locations which need to be transliterated

    try:
        with open(transliterated_locs_pth, 'rb') as f:
            translated_locs = pickle.load(f)
    except:
        translated_locs = {}

    for loc in locs:
        for l in loc:
            for val in l:
                if val not in states_roman and re.search('[a-zA-Z]', val) == None and val not in common_districts and val not in translated_locs:
                    devanagari_locs.add(val)
        
    devanagari_locs_list = list(devanagari_locs)        # This list has been converted to get all transliterations in single API call
    
    print("Transliteration is beginning")
    try:
        translations = translator.translate(devanagari_locs_list, dest='en')
    except:
        translations = devanagari_locs
    print("Transliteration is done")

    for loc in translations:
        try:
            translated_locs[loc.origin] = loc.text
        except:
            pass
    with open(transliterated_locs_pth, 'wb') as f:
        pickle.dump(translated_locs, f, pickle.HIGHEST_PROTOCOL)

    for loc in locs:
        locs_en = []
        for l in loc:
            loc_en = []
            for val in l:
                if val in states_roman:
                    loc_en.append(states_roman[val])
                elif val in common_districts:
                    loc_en.append(common_districts[val])
                elif val in translated_locs:
                    loc_en.append(translated_locs[val])
                else:
                    loc_en.append(val)
            locs_en.append(tuple(loc_en))
        inferred_locs.append(locs_en)
    
    return inferred_locs

def get_best_inference(moderator_locs, module_locs, categories):
    inferred_locs = []
    clash_cnt = 0
    for moderator_loc, module_loc, category in zip(moderator_locs, module_locs, categories):
        if get_max_tup_len([moderator_loc]) == 0 and get_max_tup_len(module_loc) == 0:  # moderator_loc has been turned into a list for equivalence with module_loc
            inferred_locs.append([''])
        elif get_max_tup_len([moderator_loc]) == 0:
            inferred_locs.append(module_loc)
        elif get_max_tup_len(module_loc) == 0:
            inferred_locs.append([moderator_loc])
        else:
            locs = []
            mod_marked_st = moderator_loc[0]
            same_st = tuple()
            for loc in module_loc:
                if loc[0] == mod_marked_st:
                    same_st = loc
                else:
                    if category == "Migrant stuck in city":
                        locs.append(loc)
                    else:
                        clash_cnt += 1
            if len(same_st) > 0:
                if get_max_tup_len([same_st]) > get_max_tup_len([moderator_loc]):
                    locs.append(same_st)
                else:
                    locs.append(moderator_loc)
            else:
                locs.append(moderator_loc)
            inferred_locs.append(locs)
    print("Clash Count : {}".format(clash_cnt))
    return inferred_locs

def get_clean_mod_locs(moderator_locs):
    locs = []
    for loc in moderator_locs:
        curr_loc = []
        for l in loc:
            try:
                if l == 'Not Known' or l == 'NA' or l == 'Others' or len(l) == 0:
                    curr_loc.append('')
                else:
                    if l == 'Manesar' or l == 'Gurugram' or l == 'Gurgaon':
                        curr_loc[0] = 'हरियाणा'
                    curr_loc.append(l)
            except:
                curr_loc.append('')
        locs.append(tuple(curr_loc))
    return locs

def get_wps(fname, transcript):
    """
        Function to return the words per second in the transcript 
    """
    try:
        with contextlib.closing(wave.open(fname,'r')) as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
    except:
        print("Could not find the downloaded file")
        return 0, 0
    try:
        number_words = len(transcript.strip().split())
    except:
        number_words = 0
    if duration > 0:
        wps = number_words / duration
        return wps, duration
    return 0, 0

def get_final_coordinates(locs, use_MMI_API=True):
    coordinates = []
    elocs = []
    headers = dict()
    text_search_url = ''
    final_saved_coordinates = {}
    saved_elocs = {}
    print("Getting location coordinates")
    if use_MMI_API:
        # Parse MMI specific arguments
        # parser = argparse.ArgumentParser()
        # parser.add_argument("--mmi_client_id", type=str, default='XLV-89n-6i1DIsX_G475rTERuo160IHnTUgHNqnkcsWsw9cm9vTP9irdaesZb2s2Y0S_gR_m9mR_6zSMjD5Ihw==',
        #     help='Client ID for MMI OAuth2 post request')
        # parser.add_argument("--mmi_client_secret", type=str, default='ebEc8GH231dqVttygIPY2ayoQxdhgWcU5Mmho7lclSaRl0EXPB3ocuROVmBC_ytGSJPpr1NteqHMot0c56kNtVynXBayYYKD',
        #     help='Client Secret ID for MMI OAuth2 post request')
        # mmi_args = parser.parse_args()

        mmi_client_id = "XLV-89n-6i1DIsX_G475rTERuo160IHnTUgHNqnkcsWsw9cm9vTP9irdaesZb2s2Y0S_gR_m9mR_6zSMjD5Ihw=="
        mmi_client_secret = "ebEc8GH231dqVttygIPY2ayoQxdhgWcU5Mmho7lclSaRl0EXPB3ocuROVmBC_ytGSJPpr1NteqHMot0c56kNtVynXBayYYKD"

        # Call the OAuth2 authorization API
        mmi_auth_url = 'https://outpost.mapmyindia.com/api/security/oauth/token'
        auth_params = {'grant_type':'client_credentials', 'client_id':mmi_client_id, 'client_secret':mmi_client_secret}
        auth_granted = requests.post(mmi_auth_url, data=auth_params)
        if auth_granted.status_code == 200:
            print("Authorization granted from Map My India APIs")
            # Access the auth keys
            token_type = auth_granted.json()['token_type']
            access_token = auth_granted.json()['access_token']
            headers = {'Authorization':token_type + ' ' + access_token}
            text_search_url = 'https://atlas.mapmyindia.com/api/places/textsearch/json?'
        else:
            print("Could not get the authorization from Map My India and hence cannot get cooridinates")
            coordinates = ['']*len(locs)
            return coordinates

        # try opening the saved location coordinates from MMI
        try:
            with open('final_mmi_loc_coordinates.pkl', 'rb') as f:
                final_saved_coordinates = pickle.load(f)
        except:
            pass

        # try opening saved elocs locations from MMI
        try:
            with open('final_mmi_elocs.pkl', 'rb') as f:
                saved_elocs = pickle.load(f)
        except:
            pass

    else:
        geolocator = Nominatim(user_agent="covid_locations")
        try:
            with open('final_loc_coordinates.pkl', 'rb') as f:
                final_saved_coordinates = pickle.load(f)
        except:
            pass
    
    for loc in tqdm(locs):
        coordinate = ''
        eloc = ''
        addresses = loc.split('\n')
        for idx, l in enumerate(addresses):
            if idx > 0:
                coordinate += '\n'
                eloc += '\n'
            try:
                address = ' '.join(l.split(',')).strip()
                if address in saved_elocs:
                    el = saved_elocs[address]
                    eloc += el
                if address in final_saved_coordinates:
                    location = final_saved_coordinates[address]
                    coordinate += location
                else:
                    if use_MMI_API:
                        location = requests.get(text_search_url+'query='+address, headers=headers)
                        first_loc = location.json()['suggestedLocations'][0]
                        lat = first_loc['latitude']
                        longi = first_loc['longitude']
                        el = first_loc['eLoc']
                        coordinate += str((lat, longi))
                        eloc += el
                        final_saved_coordinates[address] = str((lat, longi))
                        saved_elocs[address] = el
                    else:
                        location = geolocator.geocode(address)
                        final_saved_coordinates[address] = str((location.latitude, location.longitude))  # For convenience in pickle reading
                        coordinate += str((location.latitude, location.longitude))
            except:
                coordinate += ''
        coordinates.append(coordinate)
        if use_MMI_API:
            elocs.append(eloc)
        else:
            elocs.append('')
    if use_MMI_API:
        with open('final_mmi_loc_coordinates.pkl', 'wb') as f:
            pickle.dump(final_saved_coordinates, f, pickle.HIGHEST_PROTOCOL)
    else:
        with open('final_loc_coordinates.pkl', 'wb') as f:
            pickle.dump(final_saved_coordinates, f, pickle.HIGHEST_PROTOCOL)
    with open('final_mmi_elocs.pkl', 'wb') as f:
        pickle.dump(saved_elocs, f, pickle.HIGHEST_PROTOCOL)
    print("Extracted location coordinates")
    return coordinates, elocs

def all_tups_zero_len(tups):
    max_len = 0
    for tup in tups:
        max_len = max(len(tup), max_len)
    if max_len == 0:
        return True
    else:
        return False

def get_final_inferences(transcripts, auto_transcripts, inferred_locs, inferred_auto_locs, categories, 
    auto_categories, wps_manual_transcript, wps_automatic_transcript, secondary_categories, auto_secondary_categories):
    final_transcripts = []
    final_wps = []
    for manual_transcript, auto_transcript, man_wps, auto_wps in zip(transcripts, auto_transcripts,\
        wps_manual_transcript, wps_automatic_transcript):
        if man_wps >= auto_wps:
            final_wps.append(man_wps)
            final_transcripts.append(manual_transcript)
        else:
            final_wps.append(auto_wps)
            final_transcripts.append(auto_transcript)

    final_locs = []
    for manual_loc, auto_loc in zip(inferred_locs, inferred_auto_locs):
        loc_val = ''
        if len(manual_loc) == 0 or all_tups_zero_len(manual_loc):
            for idx, loc in enumerate(auto_loc):
                if idx > 0:
                    loc_val += '\n'
                try:
                    if len(loc[2]) != 0:
                        loc_val += loc[2] + ', ' + loc[1] + ', ' + loc[0]
                    elif len(loc[1]) != 0:
                        loc_val += loc[1] + ', ' + loc[0]
                    else:
                        loc_val += loc[0]
                except:
                    loc_val += ''
        else:
            for idx, loc in enumerate(manual_loc):
                if idx > 0:
                    loc_val += '\n'
                try:
                    if len(loc[2]) != 0:
                        loc_val += loc[2] + ', ' + loc[1] + ', ' + loc[0]
                    elif len(loc[1]) != 0:
                        loc_val += loc[1] + ', ' + loc[0]
                    else:
                        loc_val += loc[0]
                except:
                    loc_val += ''
        final_locs.append(loc_val)

    final_categories = []
    for manual_cat, auto_cat in zip(categories, auto_categories):
        if len(manual_cat) == 0:
            final_categories.append(auto_cat)
        else:
            final_categories.append(manual_cat)
    
    final_secondary_categories = []
    for manual_sec_cat, auto_sec_cat in zip(secondary_categories, auto_secondary_categories):
        if len(manual_sec_cat) == 0:
            final_secondary_categories.append(auto_sec_cat)
        else:
            final_secondary_categories.append(manual_sec_cat)

    final_coordinates, final_elocs = get_final_coordinates(final_locs)

    return final_transcripts, final_locs, final_categories, final_coordinates, final_wps, final_elocs, final_secondary_categories

def get_secondary_locs(final_locs):
    primary_locs = []
    secondary_locs = []
    for loc in final_locs:
        l = loc.split('\n')
        try:
            l1 = l[0]
        except:
            l1 = ''
        try:
            l2 = '\n'.join(l[1:])
        except:
            l2 = ''
        primary_locs.append(l1)
        secondary_locs.append(l2)
    return primary_locs, secondary_locs

def split_locations(locations):
    states = []
    districts = []
    blocks = []
    for loc in locations:
        try:
            locs = loc.split(',')
            if len(locs) == 3:
                state = locs[2]
                district = locs[1]
                block = locs[0]
            elif len(locs) == 2:
                state = locs[1]
                district = locs[0]
                block = ''
            elif len(locs) == 1:
                state = locs[0]
                district = ''
                block = ''
            else:
                state = ''
                district = ''
                block = ''
        except:
            state = ''
            district = ''
            block = ''
        states.append(state.strip())
        districts.append(district.strip())
        blocks.append(block.strip())
    return states, districts, blocks
        

def create_map_my_india_excel(dates, final_locs, final_coordinates, final_categories, final_transcripts, audio_links, mmi_out_dir, final_elocs):
    dates = [date.split(' ')[0] for date in dates]
    final_dates = []
    for date in dates:
        final_date = []
        date = date.split('-')
        final_date.append(date[2])
        final_date.append(date[1])
        final_date.append(date[0])
        final_dates.append('/'.join(final_date))
    
    mmi_dates = []
    mmi_locs = []
    mmi_categories = []
    mmi_transcriptions = []
    mmi_audio_links = []
    mmi_coordinates = []
    mmi_elocs = []
    for date, loc, coord, cat, trans, link, eloc in zip(final_dates, final_locs, final_coordinates, final_categories, final_transcripts, audio_links, final_elocs):
        if len(date) == 0 or len(loc) == 0 or len(cat) == 0 or len(trans) == 0 or len(link) == 0:
            continue
        else:
            mmi_dates.append(date)
            mmi_locs.append(loc)
            mmi_categories.append(cat)
            mmi_transcriptions.append(trans)
            mmi_audio_links.append(link)
            mmi_coordinates.append(coord)
            mmi_elocs.append(eloc)

    assert len(mmi_dates) == len(mmi_locs) == len(mmi_categories) == len(mmi_transcriptions) == len(mmi_audio_links) == len(mmi_coordinates) == len(mmi_elocs), "Lengths are not equal"

    final_mmi_data = {'Date' : mmi_dates, 'Location' : mmi_locs, 'Coordinates':mmi_coordinates, 'Eloc':mmi_elocs, 'Category' : mmi_categories,\
        'URL link to voice report mp3 file' : mmi_audio_links}
    mmi_df = pd.DataFrame(data=final_mmi_data)
    today_date = str(datetime.datetime.now()).split(' ')[0]
    today_date = today_date.split('-')
    out_date = [today_date[2], today_date[1], today_date[0]]
    out_date = '_'.join(out_date)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mmi_out_dir = os.path.join(base_dir, mmi_out_dir)
    mmi_df.to_excel(os.path.join(mmi_out_dir, 'GV Report' + '_' + out_date + '.xlsx'), index=False)


def get_stats(transcripts, inferred_locs, categories, infer_tags):
    print("Total audio samples : {}".format(len(transcripts)))
    trans_cnt = loc_cnt = cat_cnt = impact_cnt = sos_cnt = sos_with_trans = 0
    for trans, locs, cat, tag in zip(transcripts, inferred_locs, categories, infer_tags):
        try:
            if len(trans) > 0:
                trans_cnt += 1
                if tag == 'sos':
                    sos_with_trans += 1
        except:
            pass
        if locs[0] != '':
            loc_cnt += 1
        if len(cat) > 0:
            cat_cnt += 1
        if tag == 'impact':
            impact_cnt += 1
        if tag == 'sos':
            sos_cnt += 1
    print("Audio samples with available transcript : {}".format(trans_cnt))
    print("Audio samples with locations inferred : {}".format(loc_cnt))
    print("Audio samples with categories inferred : {}".format(cat_cnt))
    print("Audio samples with sos tag : {}".format(sos_cnt))
    print("Audio samples with sos tag and transcript : {}".format(sos_with_trans))
    print("Audio samples with impact tag : {}".format(impact_cnt))

def main():
    # Parse the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_filepath", type=str, default='coronavirus_only_21_04_2020.xlsx',
        help='Input Excel filepath', required=True)
    parser.add_argument("--output_dirpath", type=str, default='output_datafiles',
        help='Output directory path', required=True)
    parser.add_argument("--transliterated_locs", type=str, default='transliterated_locs.pkl',
        help='Path for saved Devanagari to Roman transliterated locations to limit calling transliteration API')
    parser.add_argument("--loc_coordinates", type=str, default='final_loc_coordinates.pkl',
        help='Path for saved location coordinates to limit calling the location API again')
    parser.add_argument("--audio_dest_pth", type=str, default="./audio_files",
        help="Path of the folder where audio files need to downloaded")
    parser.add_argument("--key_json", type=str, default="mapmyindia-gv-781b65a2d6b3.json",
        help="API Key for speech2text transcription")
    parser.add_argument("--transcript_dest_pth", type=str, default="auto_transcripts",
        help="Path to store the generated transcripts")
    parser.add_argument("--bucket_name", type=str, default="mmitranscriptaudio",
        help="Bucket name on the Google cloud storage")
    parser.add_argument("--MMI_output_dir", type=str, default="MMI_reports",
        help="Folder name for MMI report")
    args = parser.parse_args()

    # Define path variables
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_filepath = args.input_filepath
    out_dirpath = os.path.join(base_dir, args.output_dirpath)
    transliterated_locs_pth = args.transliterated_locs
    loc_coordinates_pth = args.loc_coordinates
    aud_dir_pth = args.audio_dest_pth
    mmi_out_dir = args.MMI_output_dir

    # Create Data Frame
    filedf = pd.read_excel(input_filepath)
    clean_df = get_clean_data(filedf)

    # Get data from excel
    transcripts = clean_df['transcription'].tolist()
    tags = clean_df['tags'].tolist()
    states = clean_df['State'].tolist()
    districts = clean_df['District'].tolist()
    subdistricts = clean_df['Block'].tolist()
    audio_links = clean_df['Recording audio link'].tolist()
    dates = clean_df['Item created date'].tolist()
    formats = clean_df['Format'].tolist()
    genders = clean_df['Gender'].tolist()
    try:
        ml_transcripts = clean_df['ML transcript'].tolist()
        ml_trans_is_avail = True
    except:
        ml_trans_is_avail = False

    # Convert state abbreviations to full forms in Devanagari
    full_states = []
    for state in states:
        if state in state_abrevs:
            full_states.append(state_abrevs[state])
        else:
            full_states.append('')

    # Clean the moderators marked locations
    moderator_locs = [loc for loc in zip(full_states, districts, subdistricts)]
    moderator_locs = get_clean_mod_locs(moderator_locs)

    # Get inferences from manual transcripts
    categories, secondary_categories, infer_tags = get_categories(transcripts, tags)
    locs = get_locations(transcripts)
    module_locs = get_clean_locs(locs)
    inferred_locs = get_best_inference(moderator_locs, module_locs, categories)
    trans_inferred_locs = get_transliterated_locs(inferred_locs, transliterated_locs_pth)

    # Download all the audios which either do not have moderator transcript or WPS < 0.75 or less precise location inference
    print("Downloading audios")
    wps_manual_transcript = []  # list to store the wps for manual transcripts
    durations = []  # lsit to store the duration of each audio
    generate_speech2text = []
    for audio_link, transcript, inferred_loc in tqdm(zip(audio_links, transcripts, inferred_locs), total=len(transcripts)):
        download_audio(audio_link, aud_dir_pth)
        fname = audio_link.split('/')[-1].split('.mp3')[0] + '.wav'
        fname = os.path.join(aud_dir_pth, fname)
        wps, duration = get_wps(fname, transcript)
        durations.append(duration)
        wps_manual_transcript.append(wps)
        try:
            len_transcript = len(transcript)
        except:
            len_transcript = 0
        if len_transcript == 0 or wps < 0.75 or get_max_tup_len(inferred_loc) <= 1:
            generate_speech2text.append(1)
        else:
            generate_speech2text.append(0)
    print("Downloaded all the required audio files")

    # Get the automatic transcription
    print("Generating transcripts")
    if ml_trans_is_avail:
        auto_transcripts = ml_transcripts
    else:
        auto_transcripts = generate_transcripts(audio_links, args.transcript_dest_pth,\
            args.audio_dest_pth, args.bucket_name, args.key_json, transcripts, generate_speech2text)
    print("Generated all the required transcripts")

    # Get the wps for automatic transcripts
    wps_automatic_transcript = []
    for auto_trans, duration in zip(auto_transcripts, durations):
        try:
            number_words = len(auto_trans.strip().split())
        except:
            number_words = 0
        if duration > 0:
            wps = number_words / duration
        else:
            wps = 0
        wps_automatic_transcript.append(wps) 

    # Get automatic transcripts
    # auto_trans_pth = "auto_transcripts"
    # dir_pth = os.path.dirname(os.path.abspath(__file__))
    # auto_transcripts = []
    # for audio_link in audio_links:
    #     aud_name = audio_link.split('/')[-1].split('.mp3')[0]
    #     trans_name = aud_name + '.txt'
    #     try:
    #         with open(os.path.join(dir_pth, auto_trans_pth, trans_name), 'r') as f:
    #             auto_transcript = f.read()
    #     except:
    #         auto_transcript = ''
    #     auto_transcripts.append(auto_transcript)

    # Get inference from automatic transcripts
    auto_categories, auto_secondary_categories, _ = get_categories(auto_transcripts, tags)
    auto_locs = get_locations(auto_transcripts)
    module_auto_locs = get_clean_locs(auto_locs)
    inferred_auto_locs = get_best_inference(moderator_locs, module_auto_locs, auto_categories)
    trans_inferred_auto_locs = get_transliterated_locs(inferred_auto_locs, transliterated_locs_pth)

    # Get the final outputs
    final_transcripts, final_locs, final_categories, final_coordinates, final_wps,\
        final_elocs, final_secondary_categories = get_final_inferences(transcripts,\
            auto_transcripts, trans_inferred_locs, trans_inferred_auto_locs,\
            categories, auto_categories, wps_manual_transcript, wps_automatic_transcript,\
            secondary_categories, auto_secondary_categories)

    # Get the category inference from the final transcript
    final_categories, final_secondary_categories, _ = get_categories(final_transcripts, tags)

    # Mark wps as good, bad or okay
    for idx, wps in enumerate(final_wps):
        if wps < 0.75:
            final_wps[idx] = 'Bad'
        elif 0.75 <= wps < 1.5:
            final_wps[idx] = 'Okay'
        else:
            final_wps[idx] = 'Good'
    
    # Get clean date and time
    clean_dates = [d.split(' ')[0] for d in dates]
    clean_times = [t.split(' ')[1] for t in dates]

    # Get clean format and gender
    clean_formats = []
    for f in formats:
        try:
            clean_formats.append(format_map[int(f)])
        except:
            clean_formats.append(f)
    
    clean_genders = []
    for g in genders:
        try:
            if int(g) == 1:
                clean_genders.append('Male')
            elif int(g) == 2:
                clean_genders.append('Female')
            else:
                clean_genders.append(g)
        except:
            clean_genders.append(g)

    # Write the inferred data to csv
    # clean_df['audio link'] = audio_links
    # clean_df['duration'] = durations
    clean_df['Item format'] = clean_formats
    clean_df['Item gender'] = clean_genders
    clean_df = clean_df.drop(columns=['Format', 'Gender'])
    clean_df['best_type_inference'] = infer_tags
    clean_df['Date'] = clean_dates
    clean_df['Time'] = clean_times
    # clean_df['module_location_inference'] = module_locs
    # clean_df['best_location_inference'] = inferred_locs
    # clean_df['location_coordinates'] = coordinates
    # clean_df['best_trans_location_inference'] = trans_inferred_locs
    # clean_df['best_category_inference'] = categories

    # Write the inferred data from auto transcripts to csv
    # clean_df['auto_transcripts'] = auto_transcripts
    # clean_df['module_auto_location_inference'] = module_auto_locs
    # clean_df['best_auto_location_inference'] = inferred_auto_locs
    # clean_df['auto_location_coordinates'] = auto_coordinates
    # clean_df['best_trans_auto_location_inference'] = trans_inferred_auto_locs
    # clean_df['best_auto_category_inference'] = auto_categories

    final_primary_locs, final_secondary_locs = get_secondary_locs(final_locs)
    primary_coords, secondary_coords = get_secondary_locs(final_coordinates)    # Same function applies for coordinates

    # Split primary location in State, District and Block
    inferred_states, inferred_districts, inferred_blocks = split_locations(final_primary_locs)

    # Write the final inferences
    clean_df['Best inferred transcript'] = final_transcripts
    clean_df['Best words per second'] = final_wps
    # clean_df['Best inferred Primary location'] = final_primary_locs
    clean_df['Inferred Primary state'] = inferred_states
    clean_df['Inferred Primary district'] = inferred_districts
    clean_df['Inferred Primary block'] = inferred_blocks
    clean_df['Inferred Primary coorindate'] = primary_coords
    clean_df['Best inferred Secondary location'] = final_secondary_locs
    clean_df['Inferred Secondary coordinate'] = secondary_coords
    clean_df['Best inferred category'] = final_categories
    clean_df['Best inferred secondary category'] = final_secondary_categories

    # Split the sos and impact dataframes
    sos_df = clean_df[clean_df['best_type_inference'] == 'sos']
    sos_df = sos_df.drop(columns=['best_type_inference'])
    impact_df = clean_df[clean_df['best_type_inference'] == 'impact']
    impact_df = impact_df.drop(columns=['best_type_inference'])

    # Save the csv and excel
    today_date = str(datetime.datetime.now()).split(' ')[0]
    today_date = today_date.split('-')
    out_date = [today_date[2], today_date[1], today_date[0]]
    out_date = '_'.join(out_date)
    clean_df.to_csv(os.path.join(out_dirpath, 'inference_' + out_date + '.csv'), index=False)
    with pd.ExcelWriter(os.path.join(out_dirpath, 'inference_' + out_date + '.xlsx')) as writer:
        sos_df.to_excel(writer, index=False, sheet_name='SOS')
        impact_df.to_excel(writer, index=False, sheet_name='Impact')

    # Save the csv in the Map My India format
    create_map_my_india_excel(dates, final_primary_locs, primary_coords, final_categories, final_transcripts, audio_links, mmi_out_dir, final_elocs)

    # Get result statistics
    get_stats(transcripts, inferred_locs, categories, infer_tags)

    # Get statistics from automatic transcripts
    get_stats(auto_transcripts, inferred_auto_locs, auto_categories, infer_tags)

if __name__ == '__main__':
    # TODO : convert the status audio links to mp3 links
    main()
