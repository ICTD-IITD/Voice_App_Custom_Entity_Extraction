def get_st_abrev(st):
    abrev_dict = {'JAMMU & KASHMIR': ['jk'], 'HIMACHAL PRADESH': ['hp'], 'PUNJAB': ['pb'],
        'CHANDIGARH': ['ch'], 'UTTARAKHAND': ['uk'], 'HARYANA': ['hr'],
        'NCT OF DELHI': ['delhi', 'dl- ncr', 'dl'], 'RAJASTHAN': ['rj'], 
        'UTTAR PRADESH': ['up','uttar pradesh'], 'BIHAR': ['bihar', 'br'], 
        'SIKKIM': ['sk'], 'ARUNACHAL PRADESH': ['ar'], 'NAGALAND': ['nl'], 'MANIPUR': ['mn'], 
        'MIZORAM': ['mz'], 'TRIPURA': ['tr'], 'MEGHALAYA': ['ml'], 'ASSAM': ['assam', 'as'] , 
        'WEST BENGAL': ['wb'], 'JHARKHAND': ['jh', 'jharkhand'], 'ODISHA': ['odisha', 'od', 'or'], 
        'CHHATTISGARH': ['cg', 'chhattisgarh'], 'MADHYA PRADESH': ['mp'], 'GUJARAT': ['gj'], 
        'DAMAN & DIU': ['dd'], 'DADRA & NAGAR HAVELI': ['dh'], 'MAHARASHTRA': ['mh'], 
        'ANDHRA PRADESH': ['andhra pradesh', 'ap'], 'KARNATAKA': ['ka'], 'GOA': ['ga'], 
        'LAKSHADWEEP': ['ld'], 'KERALA': ['kl'], 'TAMIL NADU': ['tn'], 'PUDUCHERRY': ['py'], 
        'ANDAMAN & NICOBAR ISLANDS': ['andaman', 'andaman and nicobar',], 'TELANGANA': ['ts']
    }
    return abrev_dict[st]

def get_filetered_id(server_loc_df, st_en_list, dist_en, sd_en, blk_en='', panch_en=''):
    loc_id = -1

    try:
        # print("dist ", dist_en.strip())
        server_loc_df = server_loc_df[server_loc_df['States'].str.strip().apply(lambda x: x in st_en_list)\
            & (server_loc_df['Districts'].str.strip() == dist_en.strip()) & (server_loc_df['Sub Districts'].str.strip() == sd_en.strip())\
            & (server_loc_df['Blocks'].str.strip() == blk_en.strip()) & (server_loc_df['Panchayats'].str.strip() == panch_en.strip())]
        # print("server loc df ", server_loc_df)
        if not server_loc_df.empty and len(server_loc_df) == 1:
            loc_id = int(server_loc_df['id'])
    except Exception as e:
        print("Exception in ID data frame : {}".format(str(e)))
        loc_id = -1

    return loc_id

def get_loc_id(inferred_loc, ai_id, server_id, hi_en_df, server_loc_df):
    # Ensure that na values are filled with '' in the Dataframes
    locs = inferred_loc.split(',')
    locs = [l.strip() for l in locs]

    for idx in range(len(locs), 3):         # to make all locations of form sd, dist, st
        locs.insert(0,'')

    # Get the locations and convert them into English
    sd, dist, st = locs
    st_en, dist_en, sd_en = [hi_en_df[hi_en_df['name_hi']==x]['TownVillgName'].iloc[0].strip() for x in [st, dist, sd]]
    dist_en = dist_en.lower()
    sd_en = sd_en.lower()

    # Get the location id from server location sheet
    try:
        st_en_list = get_st_abrev(st_en) # get the state abbreviation as available in server data
    except:
        print("Abrev dict error")
        return -1

    # hierarchical search
    server_loc_df = server_loc_df[(server_loc_df['ai']==ai_id) & (server_loc_df['server']==server_id)]

    # print("server loc df", server_loc_df)
    loc_id = -1 # this ID gets updated hierarchically
    try:
        if len(sd_en) > 0:  # This means state and district are also present
            loc_id = get_filetered_id(server_loc_df, st_en_list, dist_en, sd_en)   # Get complete st, dist, sd ID
        if len(dist_en) > 0 and loc_id == -1:
            loc_id = get_filetered_id(server_loc_df, st_en_list, dist_en, '')  # Get only the state and district ID
        if len(st_en_list) > 0 and loc_id == -1:
            loc_id = get_filetered_id(server_loc_df, st_en_list, '', '')       # Get only the state ID
    except Exception as e:
        print("Exception in extracting IDs : {}".format(str(e)))
        loc_id = -1

    return loc_id
