#from matplotlib.figure import Figure
import plotly.express as px
import plotly.graph_objects as go

from collections import OrderedDict
import numpy as np

def make_figure(df,pa):
    """Generates figure.

    Args:
        df (pandas.core.frame.DataFrame): Pandas DataFrame containing the input data.
        pa (dict): A dictionary of the style { "argument":"value"} as outputted by `figure_defaults`.

    Returns:
        A Plotly figure
        
    """
    
    pa_={}
    for n in ["fig_width","fig_height"]:
        if pa[n]:
            pa_[n]=float(pa[n])
        else:
            pa_[n]=pa[n]

    fig = go.Figure( )
    fig.update_layout( width=pa_["fig_width"], height=pa_["fig_height"] ) #  autosize=False,

    # MAIN FIGURE
    # if we have groups
    # the user can decide how the diferent groups should look like 
    # by unchecking the groups_autogenerate check box
    pab={}

    if "show_legend" in pa["show_legend"]:
        pab["show_legend"]=True
    else:
        pab["show_legend"]=False

    if "color_legend" in pa["color_legend"]:
        pab["color_legend"]=True
    else:
        pab["color_legend"]=False

    for a in ["upper_axis","lower_axis","left_axis","right_axis"]:
        if a in pa["show_axis"]:
            pab[a]=True
        else:
            pab[a]=False

    for a in ["tick_x_axis", "tick_y_axis"]:
        if a in pa["tick_axis"]:
            pab[a]=True
        else:
            pab[a]=False

    # for arg in ["show_legend","upper_axis","lower_axis","left_axis","right_axis", "tick_x_axis", "tick_y_axis"]:
    #     if pa[arg] in ["off",".off"]:
    #         pab[arg]=False
    #     else:
    #         pab[arg]=True

    if pa["labels_col_value"]:
        df["___label___"]=df[pa["labels_col_value"]].tolist()
    else:
        df["___label___"]=df.index.tolist()

    if pa["groups_value"] :

        fig.update_layout(legend_title_text=str(pa["groups_value"]), legend=dict( title_font_color="black", font=dict( size=float(pa["legend_font_size"]), color="black" ) ) )
        
        for group in pa["list_of_groups"]:
            tmp=df[df[pa["groups_value"]]==group]

            x=tmp[pa["xvals"]].tolist()
            y=tmp[pa["yvals"]].tolist()
            text=tmp["___label___"].tolist()
            
            pa_=[ g for g in pa["groups_settings"] if g["name"]==group ][0]
            
            # if pa_["markeralpha_col_value"] :
            #     a=[ float(i) for i in tmp[[pa_["markeralpha_col_value"]]].dropna()[pa_["markeralpha_col_value"]].tolist() ][0]
            # else:
            #     a=float(pa_["marker_alpha"])
            a=float(pa_["marker_alpha"])

            # if pa_["markerstyles_col"] :
            #     marker=[ str(i) for i in tmp[[pa_["markerstyles_col"]]].dropna()[pa_["markerstyles_col"]].tolist() ][0]
            # else:
            #     marker=pa_["marker"]
            marker=pa_["marker"]

            # if pa_["markersizes_col"] :
            #     s=[ float(i) for i in tmp[[pa_["markersizes_col"]]].dropna()[pa_["markersizes_col"]].tolist() ][0]
            # else:
            #     s=float(pa_["markers"])
            s=float(pa_["markers"])

            # if pa_["markerc_col"] :
            #     c=[ i for i in tmp[[pa_["markerc_col"]]].dropna()[pa_["markerc_col"]].tolist()][0]
            # elif pa_["markerc_write"]:
            #     c=pa_["markerc_write"]
            # else:
            #     c=pa_["markerc"]

            if pa_["markerc_write"]:
                c=pa_["markerc_write"]
            else:
                c=pa_["markerc"]

            # if pa_["edgecolor_col"]:
            #     edgecolor=[ i for i in tmp[[pa_["edgecolor_col"]]].dropna()[pa_["edgecolor_col"]].tolist()][0]
            # elif pa_["edgecolor_write"] :
            #     edgecolor=pa_["edgecolor_write"]
            # else:
            #     edgecolor=pa_["edgecolor"]
            if pa_["edgecolor_write"] :
                edgecolor=pa_["edgecolor_write"]
            else:
                edgecolor=pa_["edgecolor"]

            # if pa_["edge_linewidth_col"] :
            #     edge_linewidth=[ float(i) for i in tmp[[pa_["edge_linewidth_col"]]].dropna()[pa_["edge_linewidth_col"]].tolist() ][0]
            # else:
            #     edge_linewidth=float(pa_["edge_linewidth"])

            edge_linewidth=float(pa_["edge_linewidth"])


            # https://plotly.com/python/line-and-scatter/
            # https://plotly.com/python/marker-style/
            fig.add_trace(go.Scatter(x=x, y=y, text=text,\
                hovertemplate ='<b>%{text}</b><br><br><b>'+pa["xvals"]+'</b>: %{x}<br><b>'+pa["yvals"]+'</b>: %{y}<br>' ,
                mode='markers',
                marker=dict(symbol=marker,\
                    color=c,
                    size=s,
                    opacity=a,
                    line=dict(
                        color=edgecolor,
                        width=edge_linewidth
                        )),\
                showlegend=pab["show_legend"],\
                name=group) )

        fig.update_layout(legend_title_text=pa["groups_value"], legend=dict( font=dict( size=float(pa["legend_font_size"]), color="black" ) ) )

    
    elif not pa["groups_value"]:

        if pa["markerstyles_col"] :
            markers=[ str(i) for i in df[pa["markerstyles_col"]].tolist() ]
            df["__marker__"]=markers
        else:
            df["__marker__"]=pa["marker"]
    
        for marker in list(OrderedDict.fromkeys(df["__marker__"].tolist())):

            tmp=df[df["__marker__"]==marker]
            x=tmp[pa["xvals"]].tolist()
            y=tmp[pa["yvals"]].tolist()
            text=tmp["___label___"].tolist()
            high=None
            low=None


            if pa["markeralpha_col_value"] :
                a=[ float(i) for i in tmp[[pa["markeralpha_col_value"]]].dropna()[pa["markeralpha_col_value"]].tolist() ][0]
            else:
                a=float(pa["marker_alpha"])
            
            if pa["markersizes_col"]:
                # map here the sizes to a different range
                s=[ float(i) for i in tmp[pa["markersizes_col"]].tolist() ]
                if pa['lower_size_value'] != "" and pa['upper_size_value'] != "":
                    s=[np.interp(i,[float(pa['lower_size_value']), float(pa['upper_size_value'])],[float(pa['lower_size']), float(pa['upper_size'])]) for i in s]
            else:
                s=float(pa["markers"])

            if pa["markerc_col"]:
                c=[ float(i) for i in tmp[pa["markerc_col"]].tolist() ]
                # if value range is set
                if pa["lower_value"] != "":
                    low=float(pa["lower_value"])
                else:
                    low=min(c)
                if pa["upper_value"] != "":
                    high=float(pa["upper_value"])
                else:
                    high=max(c)
            elif pa["markerc_write"]:
                c=pa["markerc_write"]
            else:
                c=pa["markerc"]
            
            if "reverse_color_scale" in pa["reverse_color_scale"]:
                pab["reverse_color_scale"]=True
            else:
                pab["reverse_color_scale"]=False

            if pab["reverse_color_scale"]:
                pa_["colorscale_value"]=pa["colorscale_value"]+"_r"
            else:
                pa_["colorscale_value"]=pa["colorscale_value"]

            selfdefined_cmap=True
            for value in ["lower_color","center_color","upper_color"]:
                if pa[value]=="":
                    selfdefined_cmap=False
                    break
            if selfdefined_cmap:
                given_values=True
                for value in ["lower_value","center_value","upper_value"]:
                    if pa[value]=="":
                        given_values=False
                        break
                
                if given_values:
                    low=float(pa["lower_value"])
                    high=float(pa["upper_value"])

                    range_diff=float(pa["upper_value"]) - float(pa["lower_value"])
                    center=float(pa["center_value"]) - float(pa["lower_value"])
                    center=center/range_diff
                    
                else:
                    range_diff=high - low
                    center=( (high-low)/2+low ) - low
                    center=center/range_diff

                pa_["colorscale_value"]=[ [0, pa["lower_color"]],\
                    [center, pa["center_color"]],\
                    [1, pa["upper_color"] ]]

            if pa["edgecolor_col"]:
                edgecolor=tmp[[pa["edgecolor_col"]]].dropna()[pa["edgecolor_col"]].tolist()
            elif pa["edgecolor_write"]:
                edgecolor=pa["edgecolor_write"]
            else:
                edgecolor=pa["edgecolor"]

            if pa["edge_linewidth_col"]:
                edge_linewidth=[ float(i) for i in tmp[[pa["edge_linewidth_col"]]].dropna()[pa["edge_linewidth_col"]].tolist() ][0]
            else:
                edge_linewidth=float(pa["edge_linewidth"])

            fig.add_trace(go.Scatter(x=x, y=y,text=text,\
                hovertemplate ='<b>%{text}</b><br><br><b>'+pa["xvals"]+'</b>: %{x}<br><b>'+pa["yvals"]+'</b>: %{y}<br>' ,
                hoverinfo='skip',
                mode='markers',
                marker=dict(symbol=marker,\
                    color=c,
                    size=s,
                    opacity=a,
                    cmax=high,
                    cmin=low,
                    colorscale=pa_["colorscale_value"],
                    colorbar={"title":{"text":pa['colorscaleTitle']}, },
                    line=dict(
                        color=edgecolor,
                        width=edge_linewidth
                        )),\
                showlegend=False,
                name="" ))
            if pa["markerc_col"] != 'None':
                fig.update_traces(marker_showscale=pab["color_legend"])

    if  ( not pab["lower_axis"] ) & ( pab["upper_axis"] ) :
        fig.update_layout(xaxis={'side': 'top'})
        pab["lower_axis"]=True
        pab["upper_axis"]=False

    if  ( not pab["left_axis"] ) & ( pab["right_axis"] ) :
        fig.update_layout(yaxis={'side': 'right'})
        pab["left_axis"]=True
        pab["right_axis"]=False

    fig.update_xaxes(zeroline=False, showline=pab["lower_axis"], linewidth=float(pa["axis_line_width"]), linecolor='black', mirror=pab["upper_axis"])
    fig.update_yaxes(zeroline=False, showline=pab["left_axis"], linewidth=float(pa["axis_line_width"]), linecolor='black', mirror=pab["right_axis"])

    # fig.update_xaxes(showline=True)

    #"tick_left_axis", "tick_right_axis", "tick_upper_axis","tick_lower_axis"
    # print("\n\n************\n","!"+pa["ticks_direction_value"]+"!",type(pa["ticks_direction_value"]),"\n************\n\n")
    if pab["tick_x_axis"] :
        fig.update_xaxes(ticks=pa["ticks_direction_value"], tickwidth=float(pa["axis_line_width"]), tickcolor='black', ticklen=float(pa["ticks_length"]) )
    else:
        fig.update_xaxes(ticks="", tickwidth=float(pa["axis_line_width"]), tickcolor='black', ticklen=float(pa["ticks_length"]) )

    if pab["tick_y_axis"] :
        fig.update_yaxes(ticks=pa["ticks_direction_value"], tickwidth=float(pa["axis_line_width"]), tickcolor='black', ticklen=float(pa["ticks_length"]) )
    else:
        fig.update_yaxes(ticks="", tickwidth=float(pa["axis_line_width"]), tickcolor='black', ticklen=float(pa["ticks_length"]) )


    if ( pa["x_lower_limit"] ) and ( pa["x_upper_limit"] ) :
        xmin=float(pa["x_lower_limit"])
        xmax=float(pa["x_upper_limit"])
        fig.update_xaxes(range=[xmin, xmax])

    if ( pa["y_lower_limit"] ) and ( pa["y_upper_limit"] ) :
        ymin=float(pa["y_lower_limit"])
        ymax=float(pa["y_upper_limit"])
        fig.update_yaxes(range=[ymin, ymax])

    if pa["maxxticks"] :
        fig.update_xaxes(nticks=int(pa["maxxticks"]))

    if pa["maxyticks"] :
        fig.update_yaxes(nticks=int(pa["maxyticks"]))

    fig.update_layout(
        title={
            'text': pa['title'],
            'xanchor': 'left',
            'yanchor': 'top' ,
            "font": {"size": float(pa["titles"]), "color":"black"  } } )

    fig.update_layout(
        xaxis = dict(
        title_text = pa["xlabel"],
        title_font = {"size": int(pa["xlabels"]),"color":"black"}),
        yaxis = dict(
        title_text = pa["ylabel"],
        title_font = {"size": int(pa["xlabels"]), "color":"black"} ) )

    fig.update_xaxes(tickangle=float(pa["xticks_rotation"]), tickfont=dict(size=float(pa["xticks_fontsize"]), color="black" ))
    fig.update_yaxes(tickangle=float(pa["yticks_rotation"]), tickfont=dict(size=float(pa["yticks_fontsize"]), color="black" ))


    if pa["grid_value"] :
        if pa["grid_color_text"] :
            grid_color=pa["grid_color_text"]
        else:
            grid_color=pa["grid_color_value"]
        if pa["grid_value"] in ["both","x"]:
            fig.update_xaxes(showgrid=True, gridwidth=float(pa["grid_linewidth"]), gridcolor=grid_color)
        else:
            fig.update_xaxes(showgrid=False, gridwidth=float(pa["grid_linewidth"]), gridcolor=grid_color)
        if pa["grid_value"] in ["both","y"]:
            fig.update_yaxes(showgrid=True, gridwidth=float(pa["grid_linewidth"]), gridcolor=grid_color)
        else:
            fig.update_yaxes(showgrid=False, gridwidth=float(pa["grid_linewidth"]), gridcolor=grid_color)
    else:
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)

    fig.update_layout(template='plotly_white')

    if pa["labels_col_value"]:
        labels_col_value=True
    else:
        labels_col_value=False

    if pa["fixed_labels"]:
        fixed_labels=True
    else:
        fixed_labels=False

    if ( labels_col_value ) & ( fixed_labels ):
        if not pa["labels_arrows_value"]:
            showarrow=False
            arrowhead=0
            standoff=0
            yshift=10
        else:
            showarrow=True
            arrowhead=int(pa["labels_arrows_value"])
            standoff=4
            yshift=0
        tmp=df[df["___label___"].isin( pa["fixed_labels"]  )]
            
        x_values=tmp[pa["xvals"]].tolist()
        y_values=tmp[pa["yvals"]].tolist()
        text_values=tmp["___label___"].tolist()

        for x,y,text in zip(x_values,y_values,text_values):
            fig.add_annotation(
                    x=x,
                    y=y,
                    text=text,
                    showarrow=showarrow,
                    arrowhead=arrowhead,
                    clicktoshow="onoff",
                    visible=True,
                    standoff=standoff,
                    yshift=yshift,
                    opacity=float(pa["labels_alpha"]),
                    arrowwidth=float(pa["labels_line_width"]),
                    arrowcolor=pa["labels_colors_value"],
                    font=dict(
                        size=float(pa["labels_font_size"]),
                        color=pa["labels_font_color_value"]
                        )
                    )
        #fig.update_traces(textposition='top center')
    
    if pa["vline"] :
        if pa["vline_color_text"] :
            vline_color=pa["vline_color_text"]
        else:
            vline_color=pa["vline_color_value"]

        if pa["vline_linestyle_value"] == '-':
            vline_linetype=None
        elif pa["vline_linestyle_value"] == ':':
            vline_linetype="dot"
        elif pa["vline_linestyle_value"] == '-.':
            vline_linetype="dashdot"
        else:
            vline_linetype='dash'

        fig.add_shape(type="line", x0=pa["vline"], x1=pa["vline"],\
            xref='x', yref='paper',\
            y0=0, y1=1,\
            line=dict(color=vline_color,width=float(pa["vline_linewidth"]), dash=vline_linetype))

    if pa['hline'] :
        if pa["hline_color_text"] :
            hline_color=pa["hline_color_text"]
        else:
            hline_color=pa["hline_color_value"]

        if pa["hline_linestyle_value"] == '-':
            hline_linetype=None
        elif pa["hline_linestyle_value"] == ':':
            hline_linetype="dot"
        elif pa["hline_linestyle_value"] == '-.':
            hline_linetype="dashdot"
        else:
            hline_linetype='dash'

        fig.add_shape(type="line", x0=0, x1=1,\
            xref='paper', yref='y',\
            y0=pa["hline"], y1= pa["hline"],\
            line=dict(color=hline_color,width=float(pa["hline_linewidth"]), dash=hline_linetype))

    return fig

STANDARD_SIZES=[ str(i) for i in list(range(101)) ]
ALLOWED_MARKERS=['circle', 'circle-open', 'circle-dot', 'circle-open-dot', 'square', 'square-open', 
'square-dot', 'square-open-dot', 'diamond', 'diamond-open', 'diamond-dot', 'diamond-open-dot', 
'cross', 'cross-open', 'cross-dot', 'cross-open-dot', 'x', 'x-open', 'x-dot', 'x-open-dot', 
'triangle-up', 'triangle-up-open', 'triangle-up-dot', 'triangle-up-open-dot', 'triangle-down', 
'triangle-down-open', 'triangle-down-dot', 'triangle-down-open-dot', 'triangle-left', 'triangle-left-open', 
'triangle-left-dot', 'triangle-left-open-dot', 'triangle-right', 'triangle-right-open', 'triangle-right-dot', 
'triangle-right-open-dot', 'triangle-ne', 'triangle-ne-open', 'triangle-ne-dot', 'triangle-ne-open-dot', 
'triangle-se', 'triangle-se-open', 'triangle-se-dot', 'triangle-se-open-dot', 'triangle-sw', 
'triangle-sw-open', 'triangle-sw-dot', 'triangle-sw-open-dot', 'triangle-nw', 'triangle-nw-open',
 'triangle-nw-dot', 'triangle-nw-open-dot', 'pentagon', 'pentagon-open', 'pentagon-dot', 'pentagon-open-dot', 
 'hexagon', 'hexagon-open', 'hexagon-dot', 'hexagon-open-dot', 'hexagon2', 'hexagon2-open', 'hexagon2-dot',
  'hexagon2-open-dot', 'octagon', 'octagon-open', 'octagon-dot', 'octagon-open-dot', 'star', 'star-open', 
  'star-dot', 'star-open-dot', 'hexagram', 'hexagram-open', 'hexagram-dot', 'hexagram-open-dot', 
  'star-triangle-up', 'star-triangle-up-open', 'star-triangle-up-dot', 'star-triangle-up-open-dot', 
  'star-triangle-down', 'star-triangle-down-open', 'star-triangle-down-dot', 'star-triangle-down-open-dot', 
  'star-square', 'star-square-open', 'star-square-dot', 'star-square-open-dot', 'star-diamond', 
  'star-diamond-open', 'star-diamond-dot', 'star-diamond-open-dot', 'diamond-tall', 'diamond-tall-open', 
  'diamond-tall-dot', 'diamond-tall-open-dot', 'diamond-wide', 'diamond-wide-open', 'diamond-wide-dot', 
  'diamond-wide-open-dot', 'hourglass', 'hourglass-open', 'bowtie', 'bowtie-open', 'circle-cross', 
  'circle-cross-open', 'circle-x', 'circle-x-open', 'square-cross', 'square-cross-open', 'square-x', 
  'square-x-open', 'diamond-cross', 'diamond-cross-open', 'diamond-x', 'diamond-x-open', 'cross-thin', 
  'cross-thin-open', 'x-thin', 'x-thin-open', 'asterisk', 'asterisk-open', 'hash', 'hash-open', 
  'hash-dot', 'hash-open-dot', 'y-up', 'y-up-open', 'y-down', 'y-down-open', 'y-left', 'y-left-open', 
  'y-right', 'y-right-open', 'line-ew', 'line-ew-open', 'line-ns', 'line-ns-open', 'line-ne', 
  'line-ne-open', 'line-nw', 'line-nw-open']
TICKS_DIRECTIONS=["outside", "inside"]
STANDARD_COLORS=["blue","green","red","cyan","magenta","yellow","black","white"]


def figure_defaults():
    """Generates default figure arguments.

    Returns:
        dict: A dictionary of the style { "argument":"value"}
    """
    
    # https://matplotlib.org/3.1.1/api/markers_api.html
    # https://matplotlib.org/2.0.2/api/colors_api.html


    # lists allways need to have thee default value after the list
    # eg.:
    # "title_size":standard_sizes,\
    # "titles":"20"
    # "fig_size_x"="6"
    # "fig_size_y"="6"

    plot_arguments={
        "fig_width":"600",\
        "fig_height":"600",\
        "title":'Scatter plot',\
        "title_size":STANDARD_SIZES,\
        "titles":"20",\
        "xcols":[],\
        "xvals":None,\
        "ycols":[],\
        "yvals":None,\
        "groups":[],\
        "groups_value":None,\
        "list_of_groups":[],\
        "groups_settings":[],\
        "show_legend":"show_legend",\
        "legend_font_size":"14",\
        "markerstyles":ALLOWED_MARKERS,\
        "marker":"circle",\
        "markerstyles_cols":[],\
        "markerstyles_col":None,\
        "marker_size":STANDARD_SIZES,\
        "markers":"4",\
        "markersizes_cols":[],\
        "markersizes_col":None,\
        "min_markersize":0,\
        "max_markersize":5,\
        "marker_color":STANDARD_COLORS,\
        "markerc":"black",\
        "markerc_write":None,\
        "markerc_cols":[],\
        "markerc_col":None,\
        "marker_alpha":"1",\
        "markeralpha_col":[],\
        "markeralpha_col_value":None,\
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
        "reverse_color_scale":"",\
        "lower_value":"",\
        "center_value":"",\
        "upper_value":"",\
        "lower_color":"",\
        "center_color":"",\
        "upper_color":"",\
        "lower_size_value":"",\
        "center_size_value":"",\
        "upper_size_value":"",\
        "lower_size":"",\
        "center_size":"",\
        "upper_size":"",\
        'color_legend':'',\
        'colorscaleTitle':"",\
        "edge_colors":STANDARD_COLORS,\
        "edgecolor":"black",\
        "edgecolor_cols":[],\
        "edgecolor_col":None,\
        "edgecolor_write":None,\
        "edge_linewidth_cols":[],\
        "edge_linewidth_col":None,\
        "edge_linewidths":STANDARD_SIZES,\
        "edge_linewidth":"0",\
        "available_labels":[],\
        "fixed_labels":[],\
        "labels_col":[],\
        "labels_col_value":None,\
        "labels_font_size":"10",\
        "labels_font_color":STANDARD_COLORS ,\
        "labels_font_color_value":"black",\
        "labels_arrows":["0","1","2","3","4","5","6","7","8"],\
        "labels_arrows_value":[],\
        "labels_line_width":"0.5",\
        "labels_alpha":"0.5",\
        "labels_colors":STANDARD_COLORS,\
        "labels_colors_value":"black",\
        "xlabel":"x",\
        "xlabel_size":STANDARD_SIZES,\
        "xlabels":"14",\
        "ylabel":"y",\
        "ylabel_size":STANDARD_SIZES,\
        "ylabels":"14",\
        "axis_line_width":"1.0",\
        "show_axis":["left_axis","right_axis","upper_axis","lower_axis"],\
        "tick_axis":["tick_x_axis","tick_y_axis"],\
        "ticks_direction":TICKS_DIRECTIONS,\
        "ticks_direction_value":TICKS_DIRECTIONS[1],\
        "ticks_length":"6.0",\
        "xticks_fontsize":"14",\
        "yticks_fontsize":"14",\
        "xticks_rotation":"0",\
        "yticks_rotation":"0",\
        "x_lower_limit":None,\
        "y_lower_limit":None,\
        "x_upper_limit":None,\
        "y_upper_limit":None,\
        "maxxticks":None,\
        "maxyticks":None,\
        "grid":["both","x","y"],\
        "grid_value":[],\
        "grid_color_text":None,\
        "grid_colors":STANDARD_COLORS,\
        "grid_color_value":"black",\
        "grid_linestyle":['-', '--', '-.', ':'],\
        "grid_linestyle_value":'--',\
        "grid_linewidth":"1",\
        "grid_alpha":"0.1",\
        "hline":None,\
        "hline_color_text":None,\
        "hline_colors":STANDARD_COLORS,\
        "hline_color_value":"black",\
        "hline_linestyle":['-', '--', '-.', ':'],\
        "hline_linestyle_value":'--',\
        "hline_linewidth":"1",\
        "hline_alpha":"0.1",\
        "vline":None,\
        "vline_value":None,\
        "vline_color_text":None,\
        "vline_colors":STANDARD_COLORS,\
        "vline_color_value":"black",\
        "vline_linestyle":['-', '--', '-.', ':'],\
        "vline_linestyle_value":'--',\
        "vline_linewidth":"1",\
        "vline_alpha":"0.1",\
        "download_format":["png","pdf","svg"],\
        "downloadf":"pdf",\
        "downloadn":"scatterplot",\
        "session_downloadn":"MySession.scatter.plot",\
        "inputsessionfile":"Select file..",\
        "session_argumentsn":"MyArguments.scatter.plot",\
        "inputargumentsfile":"Select file.."
    }

    # grid colors not implemented in UI

    return plot_arguments