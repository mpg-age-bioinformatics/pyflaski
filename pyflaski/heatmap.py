import scipy.cluster.hierarchy as sch
import scipy.spatial as scs
from scipy import stats
import plotly.graph_objects as go
import plotly.figure_factory as ff
from scipy.cluster.hierarchy import fcluster
from scipy.spatial.distance import squareform
import numpy as np
import pandas as pd

STANDARD_SIZES=[ str(i) for i in list(range(101)) ]
STANDARD_COLORS=["blue","green","red","cyan","magenta","yellow","black","white"]


def make_figure(df,pa):
    """Generates figure.

    Args:
        df (pandas.core.frame.DataFrame): Pandas DataFrame containing the input data.
        pa (dict): A dictionary of the style { "argument":"value"} as outputted by `figure_defaults`.

    Returns:
        A Plotly figure.
        A Pandas DataFrame with columns clusters.
        A Pandas DataFrame with rows clusters.
        A Pandas DataFrame as displayed in the the Maptlotlib figure.

    """

    #fig = go.Figure( )
    #fig.update_layout( width=pa_["fig_width"], height=pa_["fig_height"] ) #  autosize=False,

    tmp=df.copy()
    tmp.index=tmp[pa["xvals"]].tolist()
    tmp=tmp[pa["yvals"]]

    if pa["add_constant"]!="":
        tmp=tmp+float(pa["add_constant"])

    if pa["log_transform_value"] == "log2":
        tmp=np.log2(tmp)
    elif pa["log_transform_value"] == "log10":
        tmp=np.log10(tmp)

    pa_={}

    for n in ["fig_width","fig_height"]:
        if pa[n]:
            pa_[n]=float(pa[n])
        else:
            pa_[n]=pa[n]

    fig = go.Figure( )
    fig.update_layout( width=pa_["fig_width"], height=pa_["fig_height"] ) #  autosize=False,


    # checkboxes=["row_cluster","col_cluster","xticklabels","yticklabels","row_dendogram_dist", "col_dendogram_dist","reverse_color_scale"] # "robust"
    # for c in checkboxes:
    #     if (pa[c] =="on") | (pa[c] ==".on"):
    #         pa_[c]=True
    #     else:
    #         pa_[c]=False
    
    for v in ["col_color_threshold","row_color_threshold" ,"upper_value", "center_value", "lower_value"]:
        if pa[v] == "":
            pa_[v]=None
        else:
            pa_[v]=float(pa[v])

    pab={}

    if "reverse_color_scale" in pa["reverse_color_scale"]:
        pab["reverse_color_scale"]=True
    else:
        pab["reverse_color_scale"]=False

    for a in ["row_cluster","col_cluster"]:
        if a in pa["show_clusters"]:
            pab[a]=True
        else:
            pab[a]=False

    for a in ["xticklabels","yticklabels"]:
        if a in pa["show_labels"]:
            pab[a]=True
        else:
            pab[a]=False

    for a in ["row_dendogram_dist", "col_dendogram_dist"]:
        if a in pa["dendogram_dist"]:
            pab[a]=True
        else:
            pab[a]=False


    if pab["reverse_color_scale"]:
        pa_["colorscale_value"]=pa["colorscale_value"]+"_r"
    else:
        pa_["colorscale_value"]=pa["colorscale_value"]

    selfdefined_cmap=True
    for value in ["lower_value","center_value","upper_value","lower_color","center_color","upper_color"]:
        if pa[value]=="":
            selfdefined_cmap=False
            break
    if selfdefined_cmap:
        range_diff=float(pa["upper_value"]) - float(pa["lower_value"])
        center=float(pa["center_value"]) - float(pa["lower_value"])
        center=center/range_diff

        color_continuous_scale=[ [0, pa["lower_color"]],\
            [center, pa["center_color"]],\
            [1, pa["upper_color"] ]]
        
        pa_["colorscale_value"]=color_continuous_scale


    if pa["zscore_value"] == "row":
        tmp=pd.DataFrame(stats.zscore(tmp, axis=1, ddof=1),columns=tmp.columns.tolist(), index=tmp.index.tolist())
    elif pa["zscore_value"] == "columns":
        tmp=pd.DataFrame(stats.zscore(tmp, axis=0, ddof=1),columns=tmp.columns.tolist(), index=tmp.index.tolist())

    if len(pa["findrow"]) > 0 :
        rows_to_find=pa["findrow"]

        possible_rows=tmp.index.tolist()
        not_found=[ s for s in rows_to_find if s not in possible_rows ]
        if len(not_found) > 0:
            message="˜The following rows could not be found: %s. Please check your entries for typos." %(", ".join(not_found) )
            flash(message,'error')

        rows_to_plot=[]+rows_to_find


        if ( pa["findrowup"] != "" ) | (pa["findrowdown"] != ""):

            d = scs.distance.pdist(tmp, metric=pa["distance_value"])
            d = squareform(d)
            d = pd.DataFrame(d,columns=tmp.index.tolist(), index=tmp.index.tolist())
            d = d[ rows_to_find ]


            for r in rows_to_find:
                dfrow=d[[r]]


                if pa["findrowtype_value"]=="percentile":

                    row_values=dfrow[r].tolist()

                    if pa["findrowup"] != "":
                        upperc=np.percentile(row_values, float(pa["findrowup"]) )
                        upperc=dfrow[ dfrow[r] >= upperc ]
                        rows_to_plot=rows_to_plot+upperc.index.tolist()
                    
                    if pa["findrowdown"] != "":
                        downperc=np.percentile(row_values, float(pa["findrowdown"]) )
                        downperc=dfrow[ dfrow[r] <= downperc ]
                        rows_to_plot=rows_to_plot+downperc.index.tolist()

                if pa["findrowtype_value"]=="n rows":
                    dfrow=dfrow.sort_values(by=[r],ascending=True)
                    row_values=dfrow.index.tolist()

                    if pa["findrowdown"] != "":
                        rows_to_plot=rows_to_plot+row_values[:int(pa["findrowdown"])]

                    if pa["findrowup"] != "":
                        rows_to_plot=rows_to_plot+row_values[-int(pa["findrowup"]):]

                if pa["findrowtype_value"]=="absolute":

                    if pa["findrowup"] != "":
                        upperc=dfrow[ dfrow[r] >= float(pa["findrowup"]) ]
                        rows_to_plot=rows_to_plot+upperc.index.tolist()
                    
                    if pa["findrowdown"] != "":
                        downperc=dfrow[ dfrow[r] <= float(pa["findrowdown"]) ]
                        rows_to_plot=rows_to_plot+downperc.index.tolist()

                rows_to_plot=list(set(rows_to_plot))

        tmp=tmp[tmp.index.isin(rows_to_plot)]

    data_array=tmp.values
    data_array_=tmp.transpose().values
    labels=tmp.columns.tolist()
    rows=tmp.index.tolist()
    
    # # Initialize figure by creating upper dendrogram
    if pab["col_cluster"]:
        fig = ff.create_dendrogram(data_array_, orientation='bottom', labels=labels, color_threshold=pa_["col_color_threshold"],\
                                distfun = lambda x: scs.distance.pdist(x, metric=pa["distance_value"]),\
                                linkagefun= lambda x: sch.linkage(x, pa["method_value"]))
        for i in range(len(fig['data'])):
            fig['data'][i]['yaxis'] = 'y2'
        dendro_leaves_y_labels = fig['layout']['xaxis']['ticktext']
        #dendro_leaves_y = [ labels.index(i) for i in dendro_leaves_y_labels ]

        #for data in dendro_up['data']:
        #    fig.add_trace(data)

        if pa_["col_color_threshold"]:
            d = scs.distance.pdist(data_array_, metric=pa["distance_value"])
            Z = sch.linkage(d, pa["method_value"]) #linkagefun(d)
            max_d = pa_["col_color_threshold"]
            clusters_cols = fcluster(Z, max_d, criterion='distance')
            clusters_cols=pd.DataFrame({"col":tmp.columns.tolist(),"cluster":list(clusters_cols)})
        else:
            clusters_cols=pd.DataFrame({"col":tmp.columns.tolist()})

    else:
        fig = go.Figure( )
        dendro_leaves_y_labels=tmp.columns.tolist()
    dendro_leaves_y = [ labels.index(i) for i in dendro_leaves_y_labels ]


    # Create Side Dendrogram
    if pab["row_cluster"]:
        dendro_side = ff.create_dendrogram(data_array, orientation='right', labels=rows, color_threshold=pa_["row_color_threshold"],\
                                            distfun = lambda x: scs.distance.pdist(x, metric=pa["distance_value"]),\
                                            linkagefun= lambda x: sch.linkage(x, pa["method_value"] ))
        for i in range(len(dendro_side['data'])):
            dendro_side['data'][i]['xaxis'] = 'x2'
        dendro_leaves_x_labels = dendro_side['layout']['yaxis']['ticktext']
        #dendro_leaves_x = [ rows.index(i) for i in dendro_leaves_x_labels ]

        if pa_["row_color_threshold"]:
            d = scs.distance.pdist(data_array, metric=pa["distance_value"])
            Z = sch.linkage(d, pa["method_value"]) #linkagefun(d)
            max_d =pa_["row_color_threshold"]
            clusters_rows = fcluster(Z, max_d, criterion='distance')
            clusters_rows = pd.DataFrame({"col":tmp.index.tolist(),"cluster":list(clusters_rows)})
        else:
            clusters_rows = pd.DataFrame({"col":tmp.index.tolist()})

        #if pa_["col_cluster"]:
            # Add Side Dendrogram Data to Figure
            #print(dendro_side['data'][0])
        for data in dendro_side['data']:
            fig.add_trace(data)
        #else:
        #    fig=dendro_side

    else:
        dendro_leaves_x_labels=tmp.index.tolist()
    dendro_leaves_x = [ rows.index(i) for i in dendro_leaves_x_labels ]

    if pa["robust"] != "":
        vals=tmp.values.flatten()
        up=np.percentile(vals, 100-float(pa["robust"]) )
        down=np.percentile(vals, float(pa["robust"]) )
        tmp[ tmp>up ] = up
        tmp[ tmp<down ] = down
        data_array=tmp.values

    # Create Heatmap
    heat_data=data_array
    heat_data = heat_data[dendro_leaves_x,:]
    heat_data = heat_data[:,dendro_leaves_y]

    if not pa_["fig_height"]:
        colorbar_len=None
    else:
        colorbar_len=pa_["fig_height"]/4

    heatmap = [
        go.Heatmap(
            x = dendro_leaves_x_labels,
            y = dendro_leaves_y_labels,
            z = heat_data,
            zmax=pa_["upper_value"], zmid=pa_["center_value"], zmin=pa_["lower_value"], 
            colorscale = pa_['colorscale_value'],
            colorbar={"title":{"text":pa["color_bar_label"] ,"font":{"size": float(pa["color_bar_font_size"]) }},
                    "lenmode":"pixels", "len":colorbar_len,
                    "xpad":float(pa["color_bar_horizontal_padding"]),"tickfont":{"size":float(pa["color_bar_ticks_font_size"])}}
        )
    ]
    
    if pab["col_cluster"]:
        heatmap[0]['x'] = fig['layout']['xaxis']['tickvals']
    else:
        heatmap[0]['x'] = dendro_leaves_y_labels

    if pab["row_cluster"]:
        heatmap[0]['y'] = dendro_side['layout']['yaxis']['tickvals']
    else:
        fake_vals=[]
        i=0
        for f in range(len(dendro_leaves_x_labels)):
            fake_vals.append(i)
            i+=1
        #dendro_leaves_x_labels=tuple(fake_vals)
        heatmap[0]['y']=tuple(fake_vals) #dendro_leaves_x_labels

    # Add Heatmap Data to Figure
    # if (pa_["col_cluster"]) | (pa_["row_cluster"]):
    for data in heatmap:
        fig.add_trace(data)
    # else:
    #     fig = go.Figure(data=heatmap[0])

    # Edit Layout
    #'width':pa_["fig_width"], 'height':pa_["fig_height"]
    fig.update_layout({'showlegend':False, 'hovermode': 'closest',
                            "yaxis":{"mirror" : "allticks", 
                                    'side': 'right',
                                    'showticklabels':pab["xticklabels"],
                                    'ticktext':dendro_leaves_x_labels},
                            "xaxis":{"mirror" : "allticks", 
                                    'side': 'right',
                                    'showticklabels':pab["yticklabels"],
                                    'ticktext':dendro_leaves_y_labels}} )

    # Edit xaxis
    fig.update_layout(xaxis={'domain': [ float(pa["row_dendogram_ratio"]), 1],
                                    'mirror': False,
                                    'showgrid': False,
                                    'showline': False,
                                    'zeroline': False,
                                    'showticklabels': pab["yticklabels"],
                                    "tickfont":{"size":float(pa["yaxis_font_size"])},
                                    'ticks':"",\
                                    'ticktext':dendro_leaves_y_labels})

    # Edit xaxis2
    if pab["row_cluster"]:
        fig.update_layout(xaxis2={'domain': [0, float(pa["row_dendogram_ratio"])],
                                        'mirror': False,
                                        'showgrid': False,
                                        'showline': False,
                                        'zeroline': False,
                                        'showticklabels': pab["row_dendogram_dist"],
                                        'ticks':""})

    # Edit yaxis 
    fig.update_layout(yaxis={'domain': [0, 1-float(pa["col_dendogram_ratio"]) ],
                                    'mirror': False,
                                    'showgrid': False,
                                    'showline': False,
                                    'zeroline': False,
                                    'showticklabels': pab["xticklabels"],
                                    "tickfont":{"size":float(pa["xaxis_font_size"])} ,
                                    'ticks': "",\
                                    'tickvals':heatmap[0]['y'],\
                                    'ticktext':dendro_leaves_x_labels})
    #'tickvals':dendro_side['layout']['yaxis']['tickvals'],\
    # Edit yaxis2 showticklabels
    if pab["col_cluster"]:
        fig.update_layout(yaxis2={'domain':[1-float(pa["col_dendogram_ratio"]), 1],
                                        'mirror': False,
                                        'showgrid': False,
                                        'showline': False,
                                        'zeroline': False,
                                        'showticklabels': pab["col_dendogram_dist"],
                                        'ticks':""})

    fig.update_layout(template='plotly_white')

    fig.update_layout(title={"text":pa["title"],"yanchor":"top","font":{"size":float(pa["title_size_value"])}})

    cols=list(fig['layout']['xaxis']['ticktext'])
    rows=list(fig['layout']['yaxis']['ticktext'])
    df_=pd.DataFrame({"i":range(len(rows))}, index=rows )
    df_=df_.sort_values(by=["i"], ascending=False)
    df_=df_.drop(["i"], axis=1)    
    df_=pd.merge(df_,tmp, how="left", left_index=True, right_index=True)
    df_=df_[cols]

    clusters_cols_=pd.DataFrame({"col":cols})
    if pab["col_cluster"]:
        clusters_cols=pd.merge(clusters_cols_,clusters_cols,on=["col"],how="left")
    else:
        clusters_cols=clusters_cols_

    clusters_rows_=pd.DataFrame({"col":df_.index.tolist()})
    if pab["row_cluster"]:
        clusters_rows=pd.merge(clusters_rows_,clusters_rows,on=["col"],how="left")
    else:
        clusters_rows=clusters_rows_

    df_.reset_index(inplace=True, drop=False)
    cols=df_.columns.tolist()
    cols[0]="rows"
    df_.columns=cols

    return fig, clusters_cols, clusters_rows, df_

def figure_defaults():
    """Generates default figure arguments.

    Returns:
        dict: A dictionary of the style { "argument":"value"}
    """
    plot_arguments={
        "fig_width":"800",\
        "fig_height":"800",\
        "xcols":[],\
        "xvals":"",\
        "ycols":[],\
        "yvals":"",\
        "available_rows":[],\
        "title":'Heatmap',\
        "title_size":STANDARD_SIZES,\
        "title_size_value":"10",\
        #"xticklabels":'.off',\
        #"yticklabels":".on",\
        "show_labels":["xticklabels", "yticklabels"],\
        "method":['single','complete','average', 'weighted','centroid','median','ward'],\
        "method_value":"ward",\
        "distance":["euclidean","minkowski","cityblock","seuclidean","sqeuclidean",\
                   "cosine","correlation","hamming","jaccard","chebyshev","canberra",\
                   "braycurtis","mahalanobis","yule","matching","dice","kulsinski","rogerstanimoto",\
                   "russellrao","sokalmichener","sokalsneath","wminkowski"],\
        "distance_value":"euclidean",\
        "col_color_threshold":"",\
        "row_color_threshold":"",\
        "colorscale":['aggrnyl','agsunset','blackbody','bluered','blues','blugrn','bluyl','brwnyl',\
                    'bugn','bupu','burg','burgyl','cividis','darkmint','electric','emrld','gnbu',\
                    'greens','greys','hot','inferno','jet','magenta','magma','mint','orrd','oranges',\
                    'oryel','peach','pinkyl','plasma','plotly3','pubu','pubugn','purd','purp','purples',\
                    'purpor','rainbow','rdbu','rdpu','redor','reds','sunset','sunsetdark','teal',\
                    'tealgrn','viridis','ylgn','ylgnbu','ylorbr','ylorrd','algae','amp','deep','dense',\
                    'gray','haline','ice','matter','solar','speed','tempo','thermal','turbid','armyrose',\
                    'brbg','earth','fall','geyser','prgn','piyg','picnic','portland','puor','rdgy',\
                    'rdylbu','rdylgn','spectral','tealrose','temps','tropic','balance','curl','delta',\
                        'edge','hsv','icefire','phase','twilight','mrybm','mygbm'],\
        "colorscale_value":"blues",\
        "color_bar_label":"",\
        "color_bar_font_size":"10",\
        "color_bar_ticks_font_size":"10",\
        "color_bar_horizontal_padding":"100",\
        #"row_cluster":".on",\
        #"col_cluster":".on",\
        "show_clusters":["row_cluster", "col_cluster"],\
        "robust":"0",\
        "color_continuous_midpoint":"",\
        #"reverse_color_scale":".off",\
        "reverse_color_scale":"reverse_color_scale",\
        "lower_value":"",\
        "center_value":"",\
        "upper_value":"",\
        "lower_color":"",\
        "center_color":"",\
        "upper_color":"",\
        "col_dendogram_ratio":"0.15",\
        "row_dendogram_ratio":"0.15",\
        #"row_dendogram_dist":".off", \
        #"col_dendogram_dist":".off",\
        "dendogram_dist":["row_dendogram_dist","col_dendogram_dist"],\
        "add_constant":"",\
        "log_transform":["none","log10","log2"],\
        "log_transform_value":"none",\
        "zscore":["none","row","columns"],\
        "zscore_value":"none",\
        "xaxis_font_size":"10",\
        "yaxis_font_size":"10",\
        "findrow":[],\
        "findrowtype":["percentile","n rows", "absolute",],\
        "findrowtype_value":"n rows",\
        "findrowup":"",\
        "findrowdown":"",\
        "download_format":["png","pdf","svg"],\
        "downloadf":"pdf",\
        "downloadn":"heatmap",\
        "session_downloadn":"MySession.iheatmap",\
        "inputsessionfile":"Select file..",\
        "session_argumentsn":"MyArguments.iheatmap",\
        "inputargumentsfile":"Select file.."}
    
    return plot_arguments