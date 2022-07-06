# from scipy import stats
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter
import math
import seaborn as sns
from functools import reduce
from lifelines import CoxPHFitter
from lifelines.statistics import logrank_test
import matplotlib.pyplot as plt
from collections import OrderedDict
import plotly.tools as tls 

marker_dict={'point':'.',\
             'pixel':',',\
             'circle':'o',\
             'triangle_down':'v',\
             'triangle_up':'^',\
             'triangle_left':'<',\
	         'triangle_right':'>',\
	         'tri_down': '1',\
	         'tri_up': '2',\
	         'tri_left': '3',\
	         'tri_right': '4',\
	         'square': 's',\
	         'pentagon': 'p',\
	         'star': '*',\
	         'hexagon1': 'h',\
	         'hexagon2': 'H',\
	         'plus': '+',\
	         'x': 'x',\
	         'diamond': 'D',\
             'thin_diamond':'d',\
             'vline':'|',\
             'hline':'_'}

def make_figure(df,pa):

    pa_={}
    for n in ["fig_width","fig_height"]:
        if pa[n]:
            pa_[n]=float(pa[n])
        else:
            pa_[n]=pa[n]


    for a in ["left_axis", "right_axis", "upper_axis", "lower_axis"]:
        if a in pa["show_axis"]:
            pa_[a]=True
        else:
            pa_[a]=False

    for a in ["tick_left_axis", "tick_right_axis", "tick_upper_axis", "tick_lower_axis"]:
        if a in pa["show_ticks"]:
            pa_[a]=True
        else:
            pa_[a]=False




    df_ls=df.copy()
    
    durations=df_ls[pa["xvals"]]
    event_observed=df_ls[pa["yvals"]]

    km = KaplanMeierFitter() ## instantiate the class to create an object

    pl=None
    fig = plt.figure(frameon=False, figsize=(float(pa["fig_width"]),float(pa["fig_height"])))

    ## Fit the data into the model

    if str(pa["groups_value"]) == "None":
        km.fit(durations, event_observed,label='Kaplan Meier Estimate')

        df_survival=km.survival_function_
        df_conf=km.confidence_interval_
        df_event=km.event_table

        df=pd.merge(df_survival,df_conf, how='left', left_index=True, right_index=True)
        df=pd.merge(df,df_event, how='left', left_index=True, right_index=True)

        df['time']=df.index.tolist()
        df=df.reset_index(drop=True)
        df=df[["time","at_risk","removed","observed","censored","entrance","Kaplan Meier Estimate","Kaplan Meier Estimate_lower_0.95","Kaplan Meier Estimate_upper_0.95"]]
    
        #pa_={}
        for arg in ["Conf_Interval","show_censors","ci_legend","ci_force_lines"]:
            if pa[arg] in ["off", ".off"]:
                pa_[arg]=False
            else:
                pa_[arg]=True

        if str(pa["markerc_write"]) != "":
            pa_["marker_fc"]=pa["markerc_write"]
        else:
            pa_["marker_fc"]=pa["markerc"]

        if str(pa["edgecolor_write"]) != "":
            pa_["marker_ec"]=pa["edgecolor_write"]
        else:
            pa_["marker_ec"]=pa["edgecolor"]

        if str(pa["grid_color_text"]) != "":
            pa_["grid_color_write"]=pa["grid_color_text"]
        else:
            pa_["grid_color_write"]=pa["grid_color_value"]

        pl=km.plot(show_censors=pa_["show_censors"], \
                censor_styles={"marker":marker_dict[pa["censor_marker_value"]], "markersize":float(pa["censor_marker_size_val"]), "markeredgecolor":pa_["marker_ec"], "markerfacecolor":pa_["marker_fc"], "alpha":float(pa["marker_alpha"])}, \
               ci_alpha=float(pa["ci_alpha"]), \
               ci_force_lines=pa_["ci_force_lines"], \
               ci_show=pa_["Conf_Interval"], \
               ci_legend=pa_["ci_legend"], \
               linestyle=pa["linestyle_value"], \
               linewidth=float(pa["linewidth_write"]), \
               color=pa["line_color_value"])

        pl.spines['right'].set_visible(pa_["right_axis"])
        pl.spines['top'].set_visible(pa_["upper_axis"])
        pl.spines['left'].set_visible(pa_["left_axis"])
        pl.spines['bottom'].set_visible(pa_["lower_axis"])

        pl.spines['right'].set_linewidth(pa["axis_line_width"])
        pl.spines['left'].set_linewidth(pa["axis_line_width"])
        pl.spines['top'].set_linewidth(pa["axis_line_width"])
        pl.spines['bottom'].set_linewidth(pa["axis_line_width"])
        
        pl.tick_params(axis="both", direction=pa["ticks_direction_value"], length=float(pa["ticks_length"]))

        pl.tick_params(axis='x',which='both',bottom=pa_["tick_lower_axis"],top=pa_["tick_upper_axis"],labelbottom=pa_["lower_axis"], 
                       labelrotation=float(pa["xticks_rotation"]), labelsize=float(pa["xticks_fontsize"]))
                       
        pl.tick_params(axis='y',which='both',left=pa_["tick_left_axis"],right=pa_["tick_right_axis"],labelleft=pa_["left_axis"], 
                       labelrotation=float(pa["yticks_rotation"]), labelsize=float(pa["yticks_fontsize"]))

        if str(pa["grid_value"]) != "None":
            pl.grid(True, which='both',axis=pa["grid_value"], color=pa_["grid_color_write"], linewidth=float(pa["grid_linewidth"]))
                       
        if str(pa["x_lower_limit"]) != "" and str(pa["x_upper_limit"]) != "":
            pl.set_xlim(float(pa["x_lower_limit"]),float(pa["x_upper_limit"]))
        if str(pa["y_lower_limit"]) != "" and str(pa["y_upper_limit"]) != "":
            pl.set_ylim(float(pa["y_lower_limit"]),float(pa["y_upper_limit"])) 

        pl.set_title(pa["title"], fontdict={'fontsize':float(pa['titles'])})
        pl.set_xlabel(pa["xlabel"], fontdict={'fontsize':float(pa['xlabels'])})
        pl.set_ylabel(pa["ylabel"], fontdict={'fontsize':float(pa['ylabels'])})

        return df, pl

    elif str(pa["groups_value"]) != "None":

        df_long=pd.DataFrame(columns=['day','status',str(pa["groups_value"])])

        for row in range (0, len(df_ls)):

            if int(df_ls.loc[row, pa["yvals"]]) >= 1:
                dead=int(df_ls.loc[row, pa["yvals"]])
                #print(dead)
                for i in range (0,dead):
                    #print(i)
                    df_long=df_long.append({'day':int(df_ls.loc[row,pa["xvals"]]), 'status':1, str(pa["groups_value"]):str(df_ls.loc[row,pa["groups_value"]])}, ignore_index=True)
                    i=i+1    

            elif int(df_ls.loc[row, pa["censors_val"]]) >= 1:
                censored=int(df_ls.loc[row, pa["censors_val"]])
                #print(censored)
                for c in range (0,censored):
                    #print(c)
                    df_long=df_long.append({'day':int(df_ls.loc[row,pa["xvals"]]), 'status':0, str(pa["groups_value"]):str(df_ls.loc[row,pa["groups_value"]])}, ignore_index=True)
                    c=c+1

        df_dummy=pd.get_dummies(df_long, drop_first=True, columns=[pa["groups_value"]])

        results = logrank_test(df_dummy.loc[df_dummy['status'] == 1,'day'].tolist(),
                       df_dummy.loc[df_dummy['status'] == 0,'day'].tolist(),
                       df_dummy.loc[df_dummy['status'] == 1,'status'].tolist(),
                       df_dummy.loc[df_dummy['status'] == 0,'status'].tolist(), alpha=.99)


        cph = CoxPHFitter()
        cph.fit(df_dummy, duration_col='day', event_col='status')
        
        cph_coeff=cph.summary
        cph_coeff=cph_coeff.reset_index()

        df_info={}
        df_info['model']='lifelines.CoxPHFitter'
        df_info['duration col']=cph.duration_col
        df_info['event col']=cph.event_col
        df_info['baseline estimation']='breslow'
        df_info['number of observations']=cph._n_examples
        df_info['number of events observed']=len(df_dummy.loc[df_dummy['status']==1,])
        df_info['partial log-likelihood']=cph.log_likelihood_
        df_info['Concordance']=cph.concordance_index_
        df_info['Partial AIC']=cph.AIC_partial_
        df_info['log-likelihood ratio test']=cph.log_likelihood_ratio_test().test_statistic
        df_info['P.value(log-likelihood ratio test)']=cph.log_likelihood_ratio_test().p_value
        df_info['log rank test']=results.test_statistic
        df_info['P.value(log rank test)']=results.p_value

        cph_stats=pd.DataFrame(df_info.items())
        cph_stats=cph_stats.rename(columns={0:'Statistic',1:'Value'})
        #cph_stats

        tmp=[]
        
        for cond in pa["list_of_groups"]:
            df_tmp=df_ls.loc[df_ls[pa["groups_value"]] == cond]

            km.fit(df_tmp[pa["xvals"]], df_tmp[pa["yvals"]], label=cond)

            df_survival=km.survival_function_
            df_conf=km.confidence_interval_
            df_event=km.event_table
            
            df=pd.merge(df_survival,df_conf, how='left', left_index=True, right_index=True)
            df=pd.merge(df,df_event, how='left', left_index=True, right_index=True)

            df['time']=df.index.tolist()
            df=df.reset_index(drop=True)
            df=df.rename(columns={"at_risk":cond+"_at_risk",
                                 "removed":cond+"_removed",
                                 "observed":cond+"_observed",
                                 "censored":cond+"_censored",
                                 "entrance":cond+"_entrance",
                                 cond:cond+"_KMestimate"})
            
            df=df[["time",cond+"_at_risk",cond+"_removed",cond+"_observed",cond+"_censored",cond+"_entrance",cond+"_KMestimate",cond+"_lower_0.95",cond+"_upper_0.95"]]
            tmp.append(df)

            df=reduce(lambda df1,df2: pd.merge(df1,df2,on='time'), tmp)


            PA_=[ g for g in pa["groups_settings"] if g["name"]==cond ][0]

            if str(PA_["linecolor_write"]) != "":
                linecolor=PA_["linecolor_write"]
            else:
                linecolor=PA_["line_color_value"]

            if str(PA_["linestyle_write"]) != "":
                linestyle=PA_["linestyle_write"]
            else:
                linestyle=PA_["linestyle_value"]
            
            if str(PA_["markerc_write"]) != "":
                markerColor=PA_["markerc_write"]
            else:
                markerColor=PA_["markerc"]

            if str(PA_["edgecolor_write"]) != "":
                edgeColor=PA_["edgecolor_write"]
            else:
                edgeColor=PA_["edgecolor"]

            if PA_["show_censors"] in ["off", ".off"]:
                showCensors=False
            else:
                showCensors=True

            if PA_["Conf_Interval"] in ["off", ".off"]:
                ConfidenceInterval=False
            else:
                ConfidenceInterval=True

            if PA_["ci_legend"] in ["off", ".off"]:
                CI_legend=False
            else:
                CI_legend=True

            if PA_["ci_force_lines"] in ["off", ".off"]:
                CI_lines=False
            else:
                CI_lines=True

            linewidth=PA_["linewidth_write"]
            edgeLineWidth=PA_["edge_linewidth"]
            markerSize=PA_["censor_marker_size_val"]

            markerAlpha=PA_["marker_alpha"]
            CI_alpha=PA_["ci_alpha"]
            markerVal=PA_["censor_marker_value"]

            pa_={}
            for arg in ["left_axis", "right_axis" , "upper_axis", "lower_axis","tick_left_axis","tick_right_axis","tick_upper_axis","tick_lower_axis"]:
                if pa[arg] in ["off", ".off"]:
                    pa_[arg]=False
                else:
                    pa_[arg]=True

            if str(pa["grid_color_text"]) != "":
                pa_["grid_color_write"]=pa["grid_color_text"]
            else:
                pa_["grid_color_write"]=pa["grid_color_value"]
        
            pl=km.plot(show_censors=showCensors, \
                censor_styles={"marker":marker_dict[markerVal], "markersize":float(markerSize), "markeredgecolor":edgeColor, "markerfacecolor":markerColor, "alpha":float(markerAlpha), "mew":float(edgeLineWidth)}, \
                ci_alpha=float(CI_alpha), \
                ci_force_lines=CI_lines, \
                ci_show=ConfidenceInterval, \
                ci_legend=CI_legend, \
                linestyle=linestyle, \
                linewidth=float(linewidth), \
                color=linecolor)

            pl.spines['right'].set_visible(pa_["right_axis"])
            pl.spines['top'].set_visible(pa_["upper_axis"])
            pl.spines['left'].set_visible(pa_["left_axis"])
            pl.spines['bottom'].set_visible(pa_["lower_axis"])

            pl.spines['right'].set_linewidth(pa["axis_line_width"])
            pl.spines['left'].set_linewidth(pa["axis_line_width"])
            pl.spines['top'].set_linewidth(pa["axis_line_width"])
            pl.spines['bottom'].set_linewidth(pa["axis_line_width"])

            pl.tick_params(axis="both", direction=pa["ticks_direction_value"], length=float(pa["ticks_length"]))

            pl.tick_params(axis='x',which='both',bottom=pa_["tick_lower_axis"],top=pa_["tick_upper_axis"],labelbottom=pa_["lower_axis"], 
                           labelrotation=float(pa["xticks_rotation"]), labelsize=float(pa["xticks_fontsize"]))
       
            pl.tick_params(axis='y',which='both',left=pa_["tick_left_axis"],right=pa_["tick_right_axis"],labelleft=pa_["left_axis"], 
                           labelrotation=float(pa["yticks_rotation"]), labelsize=float(pa["yticks_fontsize"]))

            if str(pa["grid_value"]) != "None":
                pl.grid(True, which='both',axis=pa["grid_value"], color=pa_["grid_color_write"], linewidth=float(pa["grid_linewidth"]), linestyle=pa["grid_linestyle_value"])

            if str(pa["x_lower_limit"]) != "" and str(pa["x_upper_limit"]) != "":       
                pl.set_xlim(float(pa["x_lower_limit"]),float(pa["x_upper_limit"]))
            if str(pa["y_lower_limit"]) != "" and str(pa["y_upper_limit"]) != "":  
                pl.set_ylim(float(pa["y_lower_limit"]),float(pa["y_upper_limit"]))    

            pl.set_title(pa["title"], fontdict={'fontsize':float(pa['titles'])})
            pl.set_xlabel(pa["xlabel"], fontdict={'fontsize':float(pa['xlabels'])})
            pl.set_ylabel(pa["ylabel"], fontdict={'fontsize':float(pa['ylabels'])})

        return df, pl, cph_coeff, cph_stats
        

ALLOWED_MARKERS=['point','pixel','circle','triangle_down','triangle_up','triangle_left','triangle_right','tri_down','tri_up',
'tri_left','tri_right','square','pentagon','star','hexagon1','hexagon2','plus','x','diamond','thin_diamond','vline','hline']
STANDARD_SIZES=[ str(i) for i in list(range(101)) ]
STANDARD_COLORS=["blue","green","red","cyan","magenta","yellow","black","white",None]
LINE_STYLES=["solid","dashed","dashdot","dotted"]
HIST_TYPES=['bar', 'barstacked', 'step',  'stepfilled']
STANDARD_ORIENTATIONS=['vertical','horizontal']
STANDARD_ALIGNMENTS=['left','right','mid']
TICKS_DIRECTIONS=["in","out", "inout"]
LEGEND_LOCATIONS=['best','upper right','upper left','lower left','lower right','right','center left','center right','lower center','upper center','center']
LEGEND_FONTSIZES=['xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large']
MODES=["expand",None]


def figure_defaults():
    """Generates default figure arguments.

    Returns:
        dict: A dictionary of the style { "argument":"value"}
    """
    plot_arguments={
        "fig_width":"8.0",\
        "fig_height":"6.0",\
        "title":'Survival Analysis',\
        "title_size":STANDARD_SIZES,\
        "titles":"20",\
        "xcols":[],\
        "xvals":"",\
        "ycols":[],\
        "yvals":"",\
        "groups":["None"],\
        "groups_value":"",\
        "list_of_groups":[],\
        "groups_settings":[],\
        "censors_col":["None"],\
        "censors_val":"",\
        "Conf_Interval":".off",\
        "show_censors":".off",\
        "ci_legend":".off",\
        "ci_force_lines":".off",\
        "censor_marker":ALLOWED_MARKERS,\
        "censor_marker_value":"x",\
        "censor_marker_size":STANDARD_SIZES,\
        "censor_marker_size_val":"4",\
        "censor_marker_size_cols":["select a column.."], \
        "censor_marker_size_col":"select a column..", \
        "marker_color":STANDARD_COLORS,\
        "markerc":"black",\
        "markerc_cols":["select a column.."], \
        "markerc_col":"select a column..", \
        "markerc_write":"",\
        "ci_alpha":"0.3",\
        "colors":STANDARD_COLORS,\
        "linestyles":LINE_STYLES,\
        "linestyle_value":"solid",\
        "linestyle_cols":["select a column.."],\
        "linestyle_col":"select a column..",\
        "linestyle_write":"", \
        "linewidth_cols":["select a column.."],\
        "linewidth_col":"select a column..",\
        "linewidth_write":"1.0",\
        "line_colors":STANDARD_COLORS,\
        "line_color_value":"blue",\
        "linecolor_cols":["select a column.."],\
        "linecolor_col":"select a column..",\
        "linecolor_write":"",\
        "edge_linewidths":STANDARD_SIZES,\
        "edge_linewidth":"1",\
        "edge_linewidth_cols":["select a column.."],\
        "edge_linewidth_col":"select a column..",\
        "edge_colors":STANDARD_COLORS,\
        "edgecolor":"black",\
        "edgecolor_cols":["select a column.."], \
        "edgecolor_col":"select a column..", \
        "edgecolor_write":"",\
        "marker_alpha":"1",\
        "xlabel":"Time",\
        "xlabel_size":STANDARD_SIZES,\
        "xlabels":"14",\
        "ylabel":"Survival Probability",\
        "ylabel_size":STANDARD_SIZES,\
        "ylabels":"14",\
        "axis_line_width":"1.0",\
        # "left_axis":".on",\
        # "right_axis":".on",\
        # "upper_axis":".on",\
        # "lower_axis":".on",\
        "show_axis":["left_axis", "right_axis", "upper_axis", "lower_axis"],\
        "show_ticks":["tick_left_axis", "tick_right_axis", "tick_upper_axis", "tick_lower_axis"],\
        # "tick_left_axis":".on" ,\
        # "tick_right_axis":".off",\
        # "tick_upper_axis":".off",\
        # "tick_lower_axis":".on",\
        "ticks_direction":TICKS_DIRECTIONS,\
        "ticks_direction_value":TICKS_DIRECTIONS[1],\
        "ticks_length":"6.0",\
        "xticks_fontsize":"14",\
        "yticks_fontsize":"14",\
        "xticks_rotation":"0",\
        "yticks_rotation":"0",\
        "x_lower_limit":"",\
        "y_lower_limit":"",\
        "x_upper_limit":"",\
        "y_upper_limit":"",\
        "maxxticks":"",\
        "maxyticks":"",\
        "grid":["None","both","x","y"],\
        "grid_value":"None",\
        "grid_color_text":"",\
        "grid_colors":STANDARD_COLORS,\
        "grid_color_value":"black",\
        "grid_linestyle":['-', '--', '-.', ':'],\
        "grid_linestyle_value":'--',\
        "grid_linewidth":"1",\
        "grid_alpha":"0.1",\
        "download_format":["tsv","xlsx"],\
        "downloadf":"xlsx",\
        "download_fig_format":["png","pdf","svg"], \
        "download_fig":"pdf", \
        "downloadn":"LifeSpan",\
        "downloadn_fig":"LifeSpan",\
        "session_downloadn":"MySession.LifeSpan",\
        "inputsessionfile":"Select file..",\
        "session_argumentsn":"MyArguments.LifeSpan",\
        "inputargumentsfile":"Select file.."}

    return plot_arguments