from ast import Continue
import pandas as pd
import numpy as np
import warnings
from collections import Counter
import matplotlib
import matplotlib.pylab as plt
from matplotlib_venn import venn2, venn3
import sys, os
matplotlib.use('agg')

import plotly.tools as tls 
import plotly.graph_objects as go
import scipy

def GET_COLOR(x):
    if str(x)[:3].lower() == "rgb":
        vals=x.split("rgb(")[-1].split(")")[0].split(",")
        vals=[ float(s.strip(" ")) for s in vals ]
        #vals=tuple(vals)
        return vals
    else:
        return str(x)



def make_figure(pa):
    """Generates figure.

    Args:
        pa (dict): A dictionary of the style { "argument":"value"} as outputted by `figure_defaults`.

    Returns:
        A Matplotlib figure
        
    """

    #fig=plt.figure(figsize=(float(pa["fig_width"]),float(pa["fig_height"])))
    fig, axes = plt.subplots(1, 1,figsize=(float(pa["fig_width"]),float(pa["fig_height"])))

    pa_={}
    sets={}

    for set_index in ["set1","set2","set3"]:

        if pa["%s_values" %set_index] != "":
            set_values=pa["%s_values" %set_index].split("\n")
            set_values=[ s.rstrip("\r") for s in set_values ]
            set_values=[ s for s in set_values if s != "" ]
            sets[set_index]=set(set_values)

        if pa[ "%s_color_rgb" %set_index] != "":
            pa_["%s_color_value" %set_index ] = GET_COLOR( pa[ "%s_color_rgb" %set_index ] )
        else:
            pa_["%s_color_value" %set_index ] = pa["%s_color_value" %set_index ]

        if pa[ "%s_line_rgb" %set_index] != "":
            #pa_["%s_line_color" %set_index ] = GET_COLOR( pa[ "%s_line_rgb" %set_index ] )
            pa_["%s_line_color" %set_index ] =  pa[ "%s_line_rgb" %set_index ] 
        else:
            pa_["%s_line_color" %set_index ] = pa["%s_line_color" %set_index ]

    if len(sets) == 0:
        message="Please make sure that at lease two sets have non empty values."
        raise ValueError(message)

    #print(pa["set1_values"])
    #print(pa["set2_values"])
    if len( list(sets.keys()) ) == 2:
        set1=list(sets.keys())[0]
        set2=list(sets.keys())[1]
        print(sets[set1])
        print(sets[set2])
        #Define color list for sets
        L_color=[ pa_[ "%s_color_value" %(set1)], pa_[ "%s_color_value" %(set2)] ]

        LINE_color=[ pa_[ "%s_line_color" %(set1)], pa_[ "%s_line_color" %(set2)] ]
        LINE_width=[ float(pa[ "%s_linewidth" %(set1)]), float(pa[ "%s_linewidth" %(set2)]) ]
        LINE_style=[ pa[ "%s_linestyle_value" %(set1)], pa[ "%s_linestyle_value" %(set2)] ]
        
        v=venn2( [ sets[set1], sets[set2] ], \
                 [ pa[ "%s_name" %(set1)], pa[ "%s_name" %(set2)] ]
                )
       
        plt.close()

    elif len( list(sets.keys()) ) == 3:
        set1=list(sets.keys())[0]
        set2=list(sets.keys())[1]
        set3=list(sets.keys())[2]
        #Define color list for sets
        L_color=[ pa_[ "%s_color_value" %(set1)], pa_[ "%s_color_value" %(set2)], pa_[ "%s_color_value" %(set3)] ]
        LINE_color=[ pa_[ "%s_line_color" %(set1)], pa_[ "%s_line_color" %(set2)], pa_[ "%s_line_color" %(set3)] ]
        LINE_width=[ float(pa[ "%s_linewidth" %(set1)]), float(pa[ "%s_linewidth" %(set2)]), float(pa[ "%s_linewidth" %(set3)]) ]
        LINE_style=[ pa[ "%s_linestyle_value" %(set1)], pa[ "%s_linestyle_value" %(set2)], pa[ "%s_linestyle_value" %(set3)] ]
        
        v=venn3( [ sets[set1], sets[set2], sets[set3]  ], \
                 [ pa[ "%s_name" %(set1)], pa[ "%s_name" %(set2)], pa[ "%s_name" %(set3) ] ]
                )
        plt.close()
    
    n_sets=len( list(sets.keys()) )

    #Create empty lists to hold shapes and annotations
    L_shapes = []
    L_annotation = []

    #Create empty list to make hold of min and max values of set shapes
    L_x_max = []
    L_y_max = []
    L_x_min = []
    L_y_min = []


    for i in range(0,n_sets):
        # print(i)
        # print(L_color[i])
        # print(LINE_color[i])
        # print(LINE_width[i])
        #create circle shape for current set
        shape = go.layout.Shape(
                type="circle",
                xref="x",
                yref="y",
                x0= v.centers[i][0] - v.radii[i],
                y0=v.centers[i][1] - v.radii[i],
                x1= v.centers[i][0] + v.radii[i],
                y1= v.centers[i][1] + v.radii[i],
                fillcolor=L_color[i],
                line_color=LINE_color[i],
                line_width=LINE_width[i],
                line_dash=LINE_style[i],
                opacity = float(pa["fill_alpha"])
                )

        L_shapes.append(shape)

        #create set label for current set
        anno_set_label = go.layout.Annotation(
                xref="x",
                yref="y",
                x = v.set_labels[i].get_position()[0],
                y = v.set_labels[i].get_position()[1],
                text = v.set_labels[i].get_text(),
                showarrow=False
                )
        L_annotation.append(anno_set_label)
    
        #get min and max values of current set shape
        L_x_max.append(v.centers[i][0] + v.radii[i])
        L_x_min.append(v.centers[i][0] - v.radii[i])
        L_y_max.append(v.centers[i][1] + v.radii[i])
        L_y_min.append(v.centers[i][1] - v.radii[i])

        #determine number of subsets
        n_subsets = sum([scipy.special.binom(n_sets,i+1) for i in range(0,n_sets)])
    
        for i in range(0,int(n_subsets)): 
            if v.subset_labels[i] is not None:
                #create subset label (number of common elements for current subset
                anno_subset_label = go.layout.Annotation(
                        xref="x",
                        yref="y",
                        x = v.subset_labels[i].get_position()[0],
                        y = v.subset_labels[i].get_position()[1],
                        text = v.subset_labels[i].get_text(),
                        showarrow=False
                )
                
                L_annotation.append(anno_subset_label)
            else:
                Continue
        
        
    #define off_set for the figure range    
    off_set = 0.2
    
    #get min and max for x and y dimension to set the figure range
    x_max = max(L_x_max) + off_set
    x_min = min(L_x_min) - off_set
    y_max = max(L_y_max) + off_set
    y_min = min(L_y_min) - off_set
    
    #create plotly figure
    fig = go.Figure()
    
    #set xaxes range and hide ticks and ticklabels
    fig.update_xaxes(
        range=[x_min, x_max], 
        showticklabels=False, 
        ticklen=0
    )
    
    #set yaxes range and hide ticks and ticklabels
    fig.update_yaxes(
        range=[y_min, y_max], 
        scaleanchor="x", 
        scaleratio=1, 
        showticklabels=False, 
        ticklen=0
    )
    
    #set figure properties and add shapes and annotations
    fig.update_layout(
        plot_bgcolor='white', 
        margin = dict(b = 0, l = 10, pad = 0, r = 10, t = 40),
        width=float(pa["fig_width"]), 
        height=float(pa["fig_height"]),
        shapes= L_shapes, 
        annotations = L_annotation,
        title = dict(text = pa["title"], x=0.5, y=0.90, xanchor = 'center', 
        font=dict(
            family="Arial",
            size=float(pa["title_size_value"]),
            color='#000000')
        )
        
    )

    #fig.show()

    all_values=[]
    for set_index in list( sets.keys() ):
        all_values=all_values+ list(sets[set_index])
    df=pd.DataFrame(index=list(set(all_values)))
    for set_index in list( sets.keys() ):
        tmp=pd.DataFrame( { pa[ "%s_name" %(set_index)]:list(sets[set_index]) } ,index=list(sets[set_index]) )
        df=pd.merge(df,tmp,how="left",left_index=True, right_index=True)

    cols=df.columns.tolist()
    def check_common(df, left,right,third=None):
        if not third:
            left=df[left]
            right=df[right]
            if ( str(left) != str(np.nan) ) &  ( str(right) != str(np.nan) ):
                if left == right:
                    return "yes"
                else:
                    return "no"
            else:
                return "no"
        else:
            left=df[left]
            right=df[right]
            third=df[third]
            if ( str(left) != str(np.nan) ) &  ( str(right) != str(np.nan) ) & ( str(third) != str(np.nan) ):
                if (left == right) & (left == third):
                    return "yes"
                else:
                    return "no"
            else:
                return "no"
                
    df["%s & %s" %(cols[0],cols[1])]=df.apply(check_common,args=(cols[0],cols[1]), axis=1 )
    if len(cols) == 3:
        df["%s & %s" %(cols[1],cols[2])]=df.apply(check_common,args=(cols[1],cols[2]), axis=1 )
        df["%s & %s" %(cols[0],cols[2])]=df.apply(check_common,args=(cols[0],cols[2]), axis=1 )
        df["%s & %s & %s" %(cols[0],cols[1],cols[2])]=df.apply(check_common,args=(cols[0],cols[1],cols[2]), axis=1 )

    if pa["population_size"]!="":
        pvalues={}
        from scipy.stats import hypergeom
        def hypergeomtest(set_1,set_2):
            M=float(pa["population_size"]) # total number of geness
            n=len(sets[set_1]) # genes in group I
            N=len(sets[set_2]) # genes in group II
            x=len( [ s for s in list(sets[set_1]) if s in list(sets[set_2]) ] ) # intersect
            p=hypergeom.sf(x-1, M,n,N)
            return p, M, n, N, x
        p, M, n, N, x = hypergeomtest("set1","set2")
        pvalues["%s vs. %s" %(pa["set1_name"],pa["set2_name"])]={"n %s" %pa["set1_name"]:n,"n %s" %pa["set2_name"]:N,"common":x,"total":M,"p value":str(p)}

        if len( list(sets.keys()) ) == 3:
            p, M, n, N, x=hypergeomtest("set1","set3")
            pvalues["%s vs. %s" %(pa["set1_name"],pa["set3_name"])]={"n %s" %pa["set1_name"]:n,"n %s" %pa["set3_name"]:N,"common":x,"total":M,"p value":str(p)}

            p, M, n, N, x=hypergeomtest("set2","set3")
            pvalues["%s vs. %s" %(pa["set2_name"],pa["set3_name"])]={"n %s" %pa["set2_name"]:n,"n %s" %pa["set3_name"]:N,"common":x,"total":M,"p value":str(p)}

    else:
        pvalues=None
    

    return fig, df, pvalues


STANDARD_SIZES=[ str(i) for i in list(range(101)) ]
STANDARD_COLORS=["blue","green","red","cyan","magenta","yellow","black","white"]
LINE_STYLES=["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"]

def figure_defaults():
    """Generates default figure arguments.

    Returns:
        dict: A dictionary of the style { "argument":"value"}
    """

    plot_arguments={
        "fig_width":"800",\
        "fig_height":"400",\
        "title":'Venn diagram',\
        "title_size":STANDARD_SIZES,\
        "title_size_value":"20",\
        "set1_name":"Set1",\
        "set2_name":"Set2",\
        "set3_name":"Set3",\
        "set1_values":"",\
        "set2_values":"",\
        "set3_values":"",\
        "colors":STANDARD_COLORS,\
        "set1_color_value":"red",\
        "set2_color_value":"blue",\
        "set3_color_value":"green",\
        "set1_color_rgb":"",\
        "set2_color_rgb":"",\
        "set3_color_rgb":"",\
        "fill_alpha":"0.5",\
        "set1_linewidth":"0.2",\
        "set2_linewidth":"0.2",\
        "set3_linewidth":"0.2",\
        "linestyles":LINE_STYLES,\
        "set1_linestyle_value":"solid",\
        "set2_linestyle_value":"solid",\
        "set3_linestyle_value":"solid",\
        "set1_line_alpha":"0.8",\
        "set2_line_alpha":"0.8",\
        "set3_line_alpha":"0.8",\
        "set1_line_color":"red",\
        "set2_line_color":"blue",\
        "set3_line_color":"green",\
        "set1_line_rgb":"",\
        "set2_line_rgb":"",\
        "set3_line_rgb":"",\
        "population_size":"",\
        "download_format":["png","pdf","svg"],\
        "downloadf":"pdf",\
        "downloadn":"venndiagram",\
        "session_downloadn":"MySession.venndiagram.plot",\
        "inputsessionfile":"Select file..",\
        "session_argumentsn":"MyArguments.venndiagram.plot",\
        "inputargumentsfile":"Select file..",\
        #"groups_value":None\
    }
    # grid colors not implemented in UI

    return plot_arguments