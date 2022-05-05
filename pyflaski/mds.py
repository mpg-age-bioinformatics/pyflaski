import math
import numpy as np
import pandas as pd
from sklearn.manifold import MDS
from sklearn import preprocessing

def make_figure(df,pa):
    pab = dict()
    if "groups" in pa["groups"]:
        pab["groups"]=True
    else:
        pab["groups"]=False


    df_mds=df.copy()
    df_mds.index=df_mds[pa["xvals"]].tolist()
    df_mds=df_mds[pa["yvals"]]
    # include a group row
    if pab["groups"]:
        groups = df_mds.iloc[0].tolist()
        group_column = list(df_mds.index)[0]
        df_mds = df_mds.drop(group_column)
    if float( pa["percvar"].replace(",",".") ) < 100 :
        df_mds["__std__"]=df_mds.std(axis=1)
        df_mds=df_mds.sort_values( by=["__std__"],ascending=False )
        nrows=round(len(df_mds)*float( pa["percvar"].replace(",",".") )/100)
        df_mds=df_mds[:nrows] 
        df_mds=df_mds.drop(["__std__"],axis=1)

    df_mds=df_mds.T 

    mds = MDS(n_components=int(pa["ncomponents"]), metric=True, n_init=4, max_iter=300, verbose=0, eps=0.001, n_jobs=None, random_state=None, dissimilarity="euclidean")
    if pa["scale_value"] == "feature":
        axis=0
    elif pa["scale_value"] == "sample":
        axis=1
    df_mds_scaled = preprocessing.scale(df_mds,axis=axis)
    
    projected = mds.fit_transform(df_mds_scaled)

    projected=pd.DataFrame(projected)
    cols=projected.columns.tolist()
    cols=["Component"+str(c+1) for c in cols]
    projected.index=df_mds.index.tolist()
    projected.reset_index(inplace=True, drop=False)
    if pab['groups']:
        projected[group_column] = groups
        projected.columns=["row"]+cols + [group_column]
        projected = projected[['row', group_column] + cols]
    else:
        projected.columns=["row"]+cols
    return projected

def figure_defaults():
    """Generates default figure arguments.

    Returns:
        dict: A dictionary of the style { "argument":"value"}
    """
    plot_arguments={
        "xcols":[],\
        "xvals":"",\
        "ycols":[],\
        "yvals":"",\
        "groups":"",\
        "ncomponents":"2",\
        "percvar":"100",\
        "scale":["feature","sample"],\
        "scale_value":"sample",\
        "download_format":["tsv","xlsx"],\
        "downloadf":"xlsx",\
        "downloadn":"MDS",\
        "session_downloadn":"MySession.MDS",\
        "inputsessionfile":"Select file..",\
        "session_argumentsn":"MyArguments.MDS",\
        "inputargumentsfile":"Select file.."}

        #"scale":".on",\

    return plot_arguments   
