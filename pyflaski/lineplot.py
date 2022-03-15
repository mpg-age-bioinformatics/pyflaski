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

    if pa["labels_col_value"]:
        df["___label___"]=df[pa["labels_col_value"]].tolist()
    else:
        df["___label___"]=df.index.tolist()

    if pa["groups_value"] :

        fig.update_layout(legend_title_text=str(pa["groups_value"]), legend=dict( title_font_color="black", font=dict( size=float(pa["legend_font_size"]), color="black" ) ) )
        
        for group in pa["list_of_groups"]:
            tmp=df[df[pa["groups_value"]]==group]
 
            pa_=[ g for g in pa["groups_settings"] if g["name"]==group ][0]
           
            l_main=pa_["main_line"]
            s_main=float(pa_["main_lines"])

            if pa_["main_linec_write"]:
                c_main=pa_["main_linec_write"]
            else:
                c_main=pa_["main_linec"]

            l_side=pa_["side_line"]
            s_side=float(pa_["side_lines"])

            if pa_["side_linec_write"]:
                c_side=pa_["side_linec_write"]
            else:
                c_side=pa_["side_linec"]

            cf=pa_["fill_color"]

            if pa_["plot"] == "mean-st.dev":
                tmp_=tmp.groupby(pa["xvals"], as_index=False).agg( mean = (pa["yvals"],'mean'), std = (pa["yvals"],'std'), 
                var = (pa["yvals"],lambda x: np.var(x)), percentile_50 = (pa["yvals"],lambda x: np.percentile(x,50)) )

                x=tmp_[pa["xvals"]].tolist()
                y=tmp_["mean"].tolist()

                tmp_["y_upper"]=tmp_["mean"]+tmp_["std"]
                tmp_["y_lower"]=tmp_["mean"]-tmp_["std"]
                
                y_upper=tmp_["y_upper"].tolist()
                y_lower=tmp_["y_lower"].tolist()
                y_lower = y_lower[::-1]
                x_rev = x[::-1]

            elif pa_["plot"] == "mean-variance":
                tmp_=tmp.groupby(pa["xvals"], as_index=False).agg( mean = (pa["yvals"],'mean'), std = (pa["yvals"],'std'), 
                var = (pa["yvals"],lambda x: np.var(x)), percentile_50 = (pa["yvals"],lambda x: np.percentile(x,50)) )

                x=tmp_[pa["xvals"]].tolist()
                y=tmp_["mean"].tolist()

                tmp_["y_upper"]=tmp_["mean"]+tmp_["var"]
                tmp_["y_lower"]=tmp_["mean"]-tmp_["var"]
                
                y_upper=tmp_["y_upper"].tolist()
                y_lower=tmp_["y_lower"].tolist()
                y_lower = y_lower[::-1]
                x_rev = x[::-1]
     
            elif "percentile-" in pa_["plot"]:
                range_val=pa_["plot"]
                range_val=range_val.split("percentile-")[1]
                upper=float(range_val.split("/")[2])
                lower=float(range_val.split("/")[0])
                
                tmp_=tmp.groupby(pa["xvals"], as_index=False).agg( mean = (pa["yvals"],'mean'), std = (pa["yvals"],'std'), var = (pa["yvals"],lambda x: np.var(x)),
                percentile_up = (pa["yvals"],lambda x: np.percentile(x,upper)), percentile_50 = (pa["yvals"],lambda x: np.percentile(x,50)),
                percentile_low = (pa["yvals"],lambda x: np.percentile(x,lower)) )
                
                x=tmp_[pa["xvals"]].tolist()
                y=tmp_["percentile_50"].tolist()

                y_upper=tmp_["percentile_up"].tolist()
                y_lower=tmp_["percentile_low"].tolist()
                y_lower = y_lower[::-1]
                x_rev = x[::-1]

            ## Bands
            fig.add_trace(go.Scatter(x=x+x_rev, y=y_upper+y_lower,  \
                        hovertemplate =pa["xvals"]+'</b>: %{x}<br><b>'+pa["yvals"]+'</b>: %{y}<br>' ,
                        fill="toself",
                        fillcolor=cf,
                        line=dict(color=c_side, \
                            width=s_side,
                            dash=l_side),
                        showlegend=False,\
                        name=group) )
                        
            
            # https://plotly.com/python/line-and-scatter/
            # https://plotly.com/python/marker-style/
            ## Main
            fig.add_trace(go.Scatter(x=x, y=y, \
                hovertemplate =pa["xvals"]+'</b>: %{x}<br><b>'+pa["yvals"]+'</b>: %{y}<br>' ,
                #line_color=c,
                line=dict(color=c_main, \
                            width=s_main,
                            dash=l_main),
                showlegend=pab["show_legend"],\
                name=group) )

        fig.update_traces(mode='lines')
        fig.update_layout(legend_title_text=pa["groups_value"], legend=dict( font=dict( size=float(pa["legend_font_size"]), color="black" ) ) )

    
    elif not pa["groups_value"]:
        
        tmp=df.copy()

        l_main=pa["main_line"]
        s_main=float(pa["main_lines"])

        if pa["main_linec_write"]:
            c_main=pa["main_linec_write"]
        else:
            c_main=pa["main_linec"]

        l_side=pa["side_line"]
        s_side=float(pa["side_lines"])

        if pa["side_linec_write"]:
            c_side=pa["side_linec_write"]
        else:
            c_side=pa["side_linec"]

        cf=pa["fill_color"]
        

        if pa["plot"] == "mean-st.dev":
            tmp_=tmp.groupby(pa["xvals"], as_index=False).agg( mean = (pa["yvals"],'mean'), std = (pa["yvals"],'std'), 
            var = (pa["yvals"],lambda x: np.var(x)), percentile_50 = (pa["yvals"],lambda x: np.percentile(x,50)) )

            x=tmp_[pa["xvals"]].tolist()
            y=tmp_["mean"].tolist()

            tmp_["y_upper"]=tmp_["mean"]+tmp_["std"]
            tmp_["y_lower"]=tmp_["mean"]-tmp_["std"]
            
            y_upper=tmp_["y_upper"].tolist()
            y_lower=tmp_["y_lower"].tolist()
            y_lower = y_lower[::-1]
            x_rev = x[::-1]

        elif pa["plot"] == "mean-variance":
            tmp_=tmp.groupby(pa["xvals"], as_index=False).agg( mean = (pa["yvals"],'mean'), std = (pa["yvals"],'std'), 
            var = (pa["yvals"],lambda x: np.var(x)), percentile_50 = (pa["yvals"],lambda x: np.percentile(x,50)) )

            x=tmp_[pa["xvals"]].tolist()
            y=tmp_["mean"].tolist()

            tmp_["y_upper"]=tmp_["mean"]+tmp_["var"]
            tmp_["y_lower"]=tmp_["mean"]-tmp_["var"]
            
            y_upper=tmp_["y_upper"].tolist()
            y_lower=tmp_["y_lower"].tolist()
            y_lower = y_lower[::-1]
            x_rev = x[::-1]
    
        elif "percentile-" in pa["plot"]:
            range_val=pa["plot"]
            range_val=range_val.split("percentile-")[1]
            upper=float(range_val.split("/")[2])
            lower=float(range_val.split("/")[0])
            
            tmp_=tmp.groupby(pa["xvals"], as_index=False).agg( mean = (pa["yvals"],'mean'), std = (pa["yvals"],'std'), var = (pa["yvals"],lambda x: np.var(x)),
            percentile_up = (pa["yvals"],lambda x: np.percentile(x,upper)), percentile_50 = (pa["yvals"],lambda x: np.percentile(x,50)),
            percentile_low = (pa["yvals"],lambda x: np.percentile(x,lower)) )
            
            x=tmp_[pa["xvals"]].tolist()
            y=tmp_["percentile_50"].tolist()

            y_upper=tmp_["percentile_up"].tolist()
            y_lower=tmp_["percentile_low"].tolist()
            y_lower = y_lower[::-1]
            x_rev = x[::-1]

        fig.add_trace(go.Scatter(x=x+x_rev, y=y_upper+y_lower, \
                    hovertemplate =pa["xvals"]+'</b>: %{x}<br><b>'+pa["yvals"]+'</b>: %{y}<br>' ,
                    fill="toself",
                    fillcolor=cf,
                    line=dict(
                        color=c_side,
                        width=s_side,
                        dash=l_side),\
                    showlegend=False,\
                    name="") )
                    

        fig.add_trace(go.Scatter(x=x, y=y,\
            hovertemplate =pa["xvals"]+'</b>: %{x}<br><b>'+pa["yvals"]+'</b>: %{y}<br>' ,
            #hoverinfo='skip',
            line=dict(
                color=c_main,
                width=s_main,
                dash=l_main),\
            showlegend=False,
            name="" ) )

    if  ( not pab["lower_axis"] ) & ( pab["upper_axis"] ) :
        fig.update_layout(xaxis={'side': 'top'})
        pab["lower_axis"]=True
        pab["upper_axis"]=False

    if  ( not pab["left_axis"] ) & ( pab["right_axis"] ) :
        fig.update_layout(yaxis={'side': 'right'})
        pab["left_axis"]=True
        pab["right_axis"]=False

    fig.update_traces(mode='lines')
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
ALLOWED_LINES=['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']
TICKS_DIRECTIONS=["outside", "inside"]
STANDARD_COLORS=["blue","green","red","cyan","magenta","yellow","black","white"]
PLOT_TYPES=["mean-st.dev","mean-variance","percentile-2.5/50/97.5","percentile-5.0/50/95.0", "percentile-7.5/50/92.5", "percentile-10.0/50/90.0",
"percentile-12.5/50/87.5", "percentile-15.0/50/85.0", "percentile-17.5/50/82.5", "percentile-20.0/50/80.0"]


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
        "title":'Line plot',\
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
        "linestyles":ALLOWED_LINES,\
        "main_line":"solid",\
        "side_line":"solid",\
        "line_size":STANDARD_SIZES,\
        "main_lines":"1",\
        "side_lines":"1",\
        "line_color":STANDARD_COLORS,\
        "main_linec":"black",\
        "main_linec_write":None,\
        "side_linec":"black",\
        "side_linec_write":None,\
        "fill_color":None,\
        "plot_types":PLOT_TYPES,\
        "plot":"mean-st.dev",\
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