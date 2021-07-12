import os
import re
import sys

import numpy as np
import pandas as pd

from tqdm import tqdm

# import the location module
from main_loc import sthaan

def get_clean_data(filedf):
    # Return the audio items which contains the tag 'coronavirus' & ('sos'|'impact')
    clean_df = filedf[filedf.tags.str.contains('coronavirus', flags=re.IGNORECASE, regex=True)]
    clean_df = clean_df[clean_df.tags.str.contains('sos|impact', flags=re.IGNORECASE, regex=True)]
    # or : clean_df = filedf[filedf['tags'].apply(lambda x: 'coronavirus' and ('sos' or 'impact') in x)]
    return clean_df

def get_locations(transcripts):
    locs = []
    print("Getting locations")
    for transcript in tqdm(transcripts):
        try:
            loc = sthaan(transcript)
            loc = [(l[1], l[2], l[3]) for l in loc]
            locs.append(loc)
        except Exception as e:
            locs.append('')
    print("Locations extracted")
    return locs

if __name__ == '__main__':
    covid_filename = 'coronavirus_and_sos.xlsx'
    filedf = pd.read_excel(covid_filename)
    clean_df = get_clean_data(filedf)
    transcripts = clean_df['transcription'].tolist()
    locs = get_locations(transcripts)
    clean_df['auto_trans_loc'] = locs
    clean_df.to_csv('auto_trans_locs.csv', index=False)
