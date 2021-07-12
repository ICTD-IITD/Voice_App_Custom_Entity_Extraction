def find_between(df, col, v1, v2):
    vals = df[col].values
    mx1, mx2 = (vals == v1).argmax(), (vals == v2).argmax()
    idx = df.index.values
    i1, i2 = idx.searchsorted([mx1, mx2])
    if(v2==36):
        return df.iloc[i1:]
    else:
        return df.iloc[i1:i2]

