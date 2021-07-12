# -*- coding: utf-8 -*-
import csv
import pandas
import textdistance
import math
import csv
import time
from collections import OrderedDict
from utils import find_between
import sys

def getEntityLocation(location_string):
    try:
        # location_string = location_string.encode("utf-8")
        # census_hi_file = "census_hindi_sd.csv"
        census_hi_file = "hi_eng_cesus_data.csv"
        cdf = pandas.read_csv(census_hi_file)
        cdf['name_hi'] = cdf['name_hi'].str.strip()


        ############ SEGREGATING ALL THE STATE, DISTRICTS, SUB-DISTRICTs, PANCHAYATS/TOWNS, M. CORP. INTO DIFFERENT DATAFRAMES################

        states = cdf[['state_code', 'name_en', 'name_hi']][(cdf.district_code == 0) & (cdf.subdistrict_code == 0) & (cdf.panchayat_town_code == 0) & (cdf.state_code != 0)]
        state=states.set_index('state_code')
        districts = cdf[['district_code', 'name_en', 'name_hi']][(cdf.subdistrict_code == 0) & (cdf.panchayat_town_code == 0) & (cdf.state_code != 0) & (cdf.district_code != 0)]
        district=districts.set_index('district_code')
        sub_districts = cdf[['subdistrict_code', 'name_en', 'name_hi']][(cdf.panchayat_town_code == 0) & (cdf.state_code != 0) & (cdf.district_code != 0) & (cdf.subdistrict_code != 0)]
        sub_district=sub_districts.set_index('subdistrict_code')
        panchayats_towns = cdf[['panchayat_town_code', 'name_en', 'name_hi']][(cdf.state_code != 0) & (cdf.district_code != 0) & (cdf.subdistrict_code != 0) & (cdf.panchayat_town_code != 0)]

        ################################################# MAIN LOOP STARTS ##################################################################
        flag_perfectmatch=False #flag to track the perfect match or not
        S=[]
        D=[]
        SD=[]
        st_codes = []
        dist_codes = []
        subdist_codes = []
        PT=""
        Loc_hd=""
        list_output=[]
        locations = location_string

        if locations == 'n': #location contains NaN and can't be processed
            # print("can't understand")
            return (-1, S, D, SD, PT)
        location_entity=list(dict.fromkeys(locations.split(','))) #separating the entities
        # print("Entities : ",location_entity)
        for location in location_entity:
            #### for a single entity in a loop
            #### State Direct Match Code
            for loc in list(states["name_hi"]):
               if " " + loc+" " in location:
                    S.append(loc)
                    location = location.replace(loc,'')
                    alphastate = 0
                    flag_perfectmatch = True
                    indexnum = cdf[cdf['name_hi']==loc].index.values.astype(int)[0]
                    statenum = cdf["state_code"][indexnum]
                    st_codes.append(statenum)
                    break
            #### District Direct Match Code
            if len(S)!=0:
                for s in S:
                    indexnum = cdf[cdf['name_hi']==s].index.values.astype(int)[0]
                    statenum = cdf["state_code"][indexnum]
                    inState = find_between(cdf, 'state_code', statenum, statenum+1)
                    districtsinState = inState[['district_code', 'name_en', 'name_hi']][(cdf.subdistrict_code == 0) & (cdf.panchayat_town_code == 0) & (cdf.state_code != 0) & (cdf.district_code != 0)]
                possibledistricts = districtsinState
                # print(possibledistricts)
            else:
                possibledistricts = districts

            for loc, dist_code in zip(list(possibledistricts["name_hi"]), list(possibledistricts["district_code"])):
               if " " + loc+" " in location:
                    D.append(loc)
                    dist_codes.append(dist_code)
                    location = location.replace(loc,'')
                    alphadistrict = 0
                    flag_perfectmatch = True
                    break
            #### Subdistrict Direct Match Code
            if len(D)!=0:
                for d in D:
                    indexnum = cdf[cdf['name_hi']==d].index.values.astype(int)[0]
                    districtnum = cdf["district_code"][indexnum]
                    inDistrict = find_between(cdf, 'district_code', districtnum, districtnum+1)
                    subdistrictsinstate = inDistrict[['subdistrict_code', 'name_en', 'name_hi']][(cdf.panchayat_town_code == 0) & (cdf.state_code != 0) & (cdf.district_code != 0) & (cdf.subdistrict_code != 0)]
                possiblesubdistricts = subdistrictsinstate
            elif len(S)!=0:         # Not imposing limited search to widen the search scope
                for s in S:
                    indexnum = cdf[cdf['name_hi']==s].index.values.astype(int)[0]
                    statenum = cdf["state_code"][indexnum]
                    inState = find_between(cdf, 'state_code', statenum, statenum+1)
                    subdistrictsinstate = inState[['subdistrict_code', 'name_en', 'name_hi']][(cdf.panchayat_town_code == 0) & (cdf.state_code != 0) & (cdf.district_code != 0) & (cdf.subdistrict_code != 0)]
                possiblesubdistricts = subdistrictsinstate
            else:
                possiblesubdistricts = sub_districts
            for loc, subdist_code in zip(list(possiblesubdistricts["name_hi"]), list(possiblesubdistricts["subdistrict_code"])):
               if " " + loc+" " in location:
                    SD.append(loc)
                    subdist_codes.append(subdist_code)
                    location = location.replace(loc,'')
                    alphasubdistrict = 0
                    flag_perfectmatch = True
                    break
            #### Backpropagate States, Districts
            if len(S) == 0 and len(D) == 0 and len(SD) != 0:    # Making changes
                for sd in SD:
                    l=(possiblesubdistricts[possiblesubdistricts["name_hi"]==sd]).index.tolist() #Index of all matched rows
                    for ll in l:#for each index print corresponding District,State
                        # print("District Code: ",cdf.at[ll,'district_code'],", District: ",district.at[cdf.at[ll,'district_code'],'name_hi'])
                        D.append(district.at[cdf.at[ll,'district_code'],'name_hi'])
                        dist_codes.append(cdf.at[ll,'district_code'])
                for d in D:
                    l=(possibledistricts[possibledistricts["name_hi"]==d]).index.tolist() #Index of all matched rows
                    for ll in l: #for each index print corresponding State
                        # print("State Code: ",cdf.at[ll,'state_code'],", State: ",state.at[cdf.at[ll,'state_code'],'name_hi'])
                        S.append(state.at[cdf.at[ll,'state_code'],'name_hi'])
                        st_codes.append(cdf.at[ll,'state_code'])

            elif len(S) == 0 and len(D) != 0:   # This covers the case when len(SD)==0 and len(SD)!=0
                for d in D:
                    l=(possibledistricts[possibledistricts["name_hi"]==d]).index.tolist() #Index of all matched rows
                    for ll in l: #for each index print corresponding State
                        # print("State Code: ",cdf.at[ll,'state_code'],", State: ",state.at[cdf.at[ll,'state_code'],'name_hi'])
                        S.append(state.at[cdf.at[ll,'state_code'],'name_hi'])
                        st_codes.append(cdf.at[ll,'state_code'])

            #### Approximate Matching
            if len(S)==0:
                min_d_state = 10
                min_s_state = ""
                min_st_code = -1
                for loc, min_code in zip(list(states["name_hi"]), list(states["state_code"])):
                    lenloc = len(loc.split())
                    tokenised_instance = location.split()
                    ngrams = list(zip(*[tokenised_instance[i:] for i in range(lenloc)]))
                    ngrams = [' '.join(ngram) for ngram in ngrams]
                    for ng in ngrams:
                        d=textdistance.hamming(ng, loc)/len(ng) #Hamming textdistance algo
                        if(d< min_d_state):
                            min_s_state = loc
                            min_d_state = d
                            min_st_code = min_code
            if len(D)==0:
                min_d_district = 10
                min_s_district = ""
                min_dist_code = -1
                for loc, dist_code in zip(list(possibledistricts["name_hi"]), list(possibledistricts["district_code"])):
                    lenloc = len(loc.split())
                    tokenised_instance = location.split()
                    ngrams = list(zip(*[tokenised_instance[i:] for i in range(lenloc)]))
                    ngrams = [' '.join(ngram) for ngram in ngrams]
                    for ng in ngrams:
                        d=textdistance.hamming(ng, loc)/len(ng) #Hamming textdistance algo
                        if(d< min_d_district):
                            min_s_district = loc
                            min_dist_code = dist_code
                            min_d_district = d
            alpha = 10
            if len(S)==0 and len(D)==0:
                flag_perfectmatch = False
                if min_s_state != "" and min_s_district != "":
                    if min_d_district<min_d_state :
                        D.append(min_s_district)
                        dist_codes.append(min_dist_code)
                        alpha = min_d_district
                    else:
                        S.append(min_s_state)
                        st_codes.append(min_st_code)
                        alpha = min_d_state
                elif min_s_district != "":
                    D.append(min_s_district)
                    dist_codes.append(min_dist_code)
                    alpha = min_d_district
                elif min_s_state != "":
                    S.append(min_s_state)
                    st_codes.append(min_st_code)
                    alpha = min_d_state
            elif len(D)==0:
                if min_s_district != "":
                    D.append(min_s_district)
                    dist_codes.append(min_dist_code)
                    alpha = min_d_district

            #### Backpropagate States, Districts
            if len(D)==0 and len(SD)!=0:
                for sd in SD:
                    l=(possiblesubdistricts[possiblesubdistricts["name_hi"]==sd]).index.tolist() #Index of all matched rows
                    for ll in l:#for each index print corresponding District,State
                        # print("District Code: ",cdf.at[ll,'district_code'],", District: ",district.at[cdf.at[ll,'district_code'],'name_hi'])
                        D.append(district.at[cdf.at[ll,'district_code'],'name_hi'])
                        dist_codes.append(cdf.at[ll,'district_code'])

            if len(S)==0 and len(D)!=0:
                for d in D:
                    l=(possibledistricts[possibledistricts["name_hi"]==d]).index.tolist() #Index of all matched rows
                    for ll in l: #for each index print corresponding State
                        # print("State Code: ",cdf.at[ll,'state_code'],", State: ",state.at[cdf.at[ll,'state_code'],'name_hi'])
                        S.append(state.at[cdf.at[ll,'state_code'],'name_hi'])
                        st_codes.append(cdf.at[ll,'state_code'])



            list_output.append(locations)

            # print(S, D, SD, PT)
            S1 = list(zip(S, st_codes))
            D1 = list(zip(D, dist_codes))
            SD1 = list(zip(SD, subdist_codes))
            if alpha==10:
                list_output.append("Yes")
                return (0, S1, D1, SD1, PT)
            else:
                list_output.append("No")
                return (alpha, S1, D1, SD1, PT)
    except Exception as e:
        print("exception" + str(e))
    return


if __name__ == "__main__":
    a = [u' \u092a\u094d\u0930\u0916\u0902\u0921 ', u' \u0938\u093f\u0902\u0939\u092d\u0942\u092e \u091d\u093e\u0930\u0916\u0902\u0921 ']
    cur_loc = []
    for e in a:
        cur_loc.append(getEntityLocation(e))
    print(cur_loc)
