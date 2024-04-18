def indexchecker(df):
    i=df.index.tolist()
    s=set(i)
    if len(s) != len(i) :
        raise ValueError('DataFrame contains duplicated entries in the index!')