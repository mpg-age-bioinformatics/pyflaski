# from scipy import stats
from tarfile import PAX_FIELDS
import numpy as np
import pandas as pd
from lifelines import KaplanMeierFitter
import math
import seaborn as sns
from functools import reduce
from lifelines import CoxPHFitter
from lifelines.statistics import logrank_test
from lifelines.statistics import multivariate_logrank_test
from lifelines.statistics import proportional_hazard_test
import matplotlib.pyplot as plt
from collections import OrderedDict
from plotly.graph_objs import *
import plotly.graph_objs as go


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

    for a in ["tick_x_axis","tick_y_axis"]:
        if a in pa["show_ticks"]:
            pa_[a]=True
        else:
            pa_[a]=False

    for a in ["Conf_Interval","show_censors","ci_legend","ci_force_lines"]:
        if a in pa["model_settings"]:
            pa_[a]=True
        else:
            pa_[a]=False

    df_ls=df.copy()
    
    durations=df_ls[pa["xvals"]]
    event_observed=df_ls[pa["yvals"]]

    ## UPDATE AXES ARGUMENTS 
    fig = go.Figure()
    fig.update_layout( width=pa_["fig_width"], height=pa_["fig_height"] )

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
            title_font = {"size": int(pa["ylabels"]), "color":"black"} ) )

    if ( not pa_["lower_axis"] ) & ( pa_["upper_axis"] ) :
        fig.update_layout(xaxis={'side': 'top'})
        pa_["lower_axis"]=True
        pa_["upper_axis"]=False

    if ( not pa_["left_axis"] ) & ( pa_["right_axis"] ) :
        fig.update_layout(yaxis={'side': 'right'})
        pa_["left_axis"]=True
        pa_["right_axis"]=False
    
    fig.update_xaxes(zeroline=False, showline=pa_["lower_axis"], linewidth=float(pa["axis_line_width"]), linecolor='black', mirror=pa_["upper_axis"])
    fig.update_yaxes(zeroline=False, showline=pa_["left_axis"], linewidth=float(pa["axis_line_width"]), linecolor='black', mirror=pa_["right_axis"])


    if pa_["tick_x_axis"] :
        fig.update_xaxes(ticks=pa["ticks_direction_value"], tickwidth=float(pa["axis_line_width"]), tickcolor='black', ticklen=float(pa["ticks_length"]) )
    else:
        fig.update_xaxes(ticks="", tickwidth=float(pa["axis_line_width"]), tickcolor='black', ticklen=float(pa["ticks_length"]) )

    if pa_["tick_y_axis"] :
        fig.update_yaxes(ticks=pa["ticks_direction_value"], tickwidth=float(pa["axis_line_width"]), tickcolor='black', ticklen=float(pa["ticks_length"]) )
    else:
        fig.update_yaxes(ticks="", tickwidth=float(pa["axis_line_width"]), tickcolor='black', ticklen=float(pa["ticks_length"]) )

    
    fig.update_xaxes(tickangle=float(pa["xticks_rotation"]), tickfont=dict(size=float(pa["xticks_fontsize"]), color="black" ))
    fig.update_yaxes(tickangle=float(pa["yticks_rotation"]), tickfont=dict(size=float(pa["yticks_fontsize"]), color="black" ))


    if ( pa["x_lower_limit"] ) and ( pa["x_upper_limit"] ) :
        xmin=float(pa["x_lower_limit"])
        xmax=float(pa["x_upper_limit"])
        fig.update_xaxes(range=[xmin, xmax])

    if ( pa["y_lower_limit"] ) and ( pa["y_upper_limit"] ) :
        ymin=float(pa["y_lower_limit"])
        ymax=float(pa["y_upper_limit"])
        fig.update_yaxes(range=[ymin, ymax])


    if pa["grid_value"] :
        if str(pa["grid_color_text"]) != "":
            grid_color=pa["grid_color_text"]
        else:
            grid_color=pa["grid_color_value"]
        

        if pa["grid_value"] in ["both","x"]:
            fig.update_xaxes(showgrid=True, gridwidth=float(pa["grid_linewidth"]), gridcolor=grid_color) #griddash=pa["grid_linestyle_value"]
        else:
            fig.update_xaxes(showgrid=False, gridwidth=float(pa["grid_linewidth"]), gridcolor=grid_color) #griddash=pa["grid_linestyle_value"]
        
        if pa["grid_value"] in ["both","y"]:
            fig.update_yaxes(showgrid=True, gridwidth=float(pa["grid_linewidth"]), gridcolor=grid_color,) #griddash=pa["grid_linestyle_value"]
        else:
            fig.update_yaxes(showgrid=False, gridwidth=float(pa["grid_linewidth"]), gridcolor=grid_color) #griddash=pa["grid_linestyle_value"]
    else:
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)

    fig.update_layout(template='plotly_white')


    ## instantiate the class to create an object
    km = KaplanMeierFitter() 

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
    
        ## Line arguments
        linewidth=float(pa["linewidth_write"])
        linestyle=pa["linestyle_value"]
        
        if str(pa["linecolor_write"]) != "":
            linecolor=pa["linecolor_write"]
        else:
            linecolor=pa["line_color_value"]

        ## Confidence Interval arguments
        ci_linewidth=float(pa["ci_linewidth_write"])
        ci_linestyle=pa["ci_linestyle_value"]
        
        CI_alpha=pa["ci_alpha"]

        if str(pa["ci_linecolor_write"]) != "":
            ci_linecolor=pa["ci_linecolor_write"]
            ci_color_rgba=ci_linecolor.strip(")")+","+str(CI_alpha)+")"
            ci_color_rgba=ci_color_rgba.replace("rgb","rgba")
        else:
            ci_linecolor=pa["ci_line_color_value"]
            from matplotlib import colors
            ci_color_rgba="rgba("+str(colors.to_rgba(ci_linecolor)[0])+","+str(colors.to_rgba(ci_linecolor)[1])+","+str(colors.to_rgba(ci_linecolor)[2])+","+CI_alpha+")"

        if pa_["ci_legend"]:
            CI_legend=True
        else:
            CI_legend=False

        ## Censors arguments
        markerShape=pa["censor_marker_value"]
        markerSize=float(pa["censor_marker_size_val"])
        edgeLineWidth=float(pa["edge_linewidth"])
        
        if str(pa["markerc_write"]) != "":
            markerColor=pa["markerc_write"]
        else:
            markerColor=pa["markerc"]
        
        markerAlpha=pa["marker_alpha"]
        
        if str(pa["edgecolor_write"]) != "":
            edgeColor=pa["edgecolor_write"]
        else:
            edgeColor=pa["edgecolor"]


       ## Main line
        fig.add_trace(go.Scatter(
            x=km.survival_function_.index, y=km.survival_function_['Kaplan Meier Estimate'],
            line=dict(shape='hv', width=linewidth, color=linecolor,  dash=linestyle),
            showlegend=CI_legend,
            name="KM Estimate"
        ))

        if pa_["ci_force_lines"] and pa_["Conf_Interval"]:

            ## Adding line for upper conf interval
            fig.add_trace(go.Scatter(
            x=km.confidence_interval_.index, y=km.confidence_interval_["Kaplan Meier Estimate"+"_upper_0.95"],
            line=dict(shape='hv', width=ci_linewidth, color=ci_linecolor,  dash=ci_linestyle),
            showlegend=CI_legend,
            name="95% Conf. Interval - Upper"
            ))

            ## Adding line for lower conf interval
            fig.add_trace(go.Scatter(
            x=km.confidence_interval_.index, y=km.confidence_interval_["Kaplan Meier Estimate"+"_lower_0.95"],
            line=dict(shape='hv', width=ci_linewidth, color=ci_linecolor,  dash=ci_linestyle),
            showlegend=CI_legend,
            name="95% Conf. Interval - Lower"
            ))

            ## Adding shade for upper conf interval
            fig.add_trace(go.Scatter(
                x=km.confidence_interval_.index, 
                y=km.confidence_interval_["Kaplan Meier Estimate"+"_upper_0.95"],
                line=dict(shape='hv', width=0),
                showlegend=False,
                name="95% Conf. Interval"
            ))

            ## Adding shade for lower conf interval
            fig.add_trace(go.Scatter(
                x=km.confidence_interval_.index,
                y=km.confidence_interval_["Kaplan Meier Estimate"+"_lower_0.95"],
                line=dict(shape='hv', width=0),
                fill='tonexty',
                fillcolor=ci_color_rgba,
                showlegend=False,
                name="95% Conf. Interval"
            ))

        elif pa_["ci_force_lines"]:
            ## Adding line for upper conf interval
            fig.add_trace(go.Scatter(
            x=km.confidence_interval_.index, y=km.confidence_interval_["Kaplan Meier Estimate"+"_upper_0.95"],
            line=dict(shape='hv', width=ci_linewidth, color=ci_linecolor,  dash=ci_linestyle),
            showlegend=CI_legend,
            name="95% Conf. Interval - Upper"
            ))

            ## Adding line for lower conf interval
            fig.add_trace(go.Scatter(
            x=km.confidence_interval_.index, y=km.confidence_interval_["Kaplan Meier Estimate"+"_lower_0.95"],
            line=dict(shape='hv', width=ci_linewidth, color=ci_linecolor,  dash=ci_linestyle),
            showlegend=CI_legend,
            name="95% Conf. Interval - Lower"
            ))

        elif pa_["Conf_Interval"]:
            ## Adding shade for upper conf interval
            fig.add_trace(go.Scatter(
                x=km.confidence_interval_.index, 
                y=km.confidence_interval_["Kaplan Meier Estimate"+"_upper_0.95"],
                line=dict(shape='hv', width=0),
                showlegend=False,
                name="95% Conf. Interval"
            ))

            ## Adding shade for lower conf interval
            fig.add_trace(go.Scatter(
                x=km.confidence_interval_.index,
                y=km.confidence_interval_["Kaplan Meier Estimate"+"_lower_0.95"],
                line=dict(shape='hv', width=0),
                fill='tonexty',
                fillcolor=ci_color_rgba,
                showlegend=False,
                name="95% Conf. Interval"
            ))

        if pa_["show_censors"]:

            #censors=df.loc[df["Kaplan Meier Estimate"+"_censored"] > 0, ["time", "Kaplan Meier Estimate"+"_KMestimate"]]
            censors=df.loc[df["censored"] > 0, ["time", "Kaplan Meier Estimate"]]
            #print(censors)

            censors_x=censors["time"].tolist()
            #censors_y=censors[cond+"_KMestimate"].tolist()
            censors_y=censors["Kaplan Meier Estimate"].tolist()
        
            fig.add_trace(go.Scatter(x=censors_x, y=censors_y, 
                    mode='markers', 
                    marker=dict(symbol=markerShape,\
                            color=markerColor,
                            size=markerSize,
                            opacity=float(markerAlpha),
                            line=dict(
                                color=edgeColor,
                                width=edgeLineWidth)), \
                    showlegend=False,\
                    name='Censors'))

        fig.show()

        return df, fig

    elif str(pa["groups_value"]) != "None":
        
        df_long=pd.DataFrame(columns=['day','status',str(pa["groups_value"])])

        
        for row in range (0, len(df_ls)):

            if int(df_ls.loc[row, pa["yvals"]]) >= 1:
                dead=int(df_ls.loc[row, pa["yvals"]])
                #print(dead)
                for i in range (0,dead):
                    #print(i)
                    tmp_d=pd.DataFrame( [{'day':float(df_ls.loc[row,pa["xvals"]]), 'status':1, str(pa["groups_value"]):str(df_ls.loc[row,pa["groups_value"]])}] )
                    df_long=pd.concat([df_long, tmp_d ])
                    #df_long=df_long.append({'day':int(df_ls.loc[row,pa["xvals"]]), 'status':1, str(pa["groups_value"]):str(df_ls.loc[row,pa["groups_value"]])}, ignore_index=True)
                    i=i+1

            elif int(df_ls.loc[row, pa["yvals"]]) == 0:
                tmp_=pd.DataFrame( [{'day':float(df_ls.loc[row,pa["xvals"]]), 'status':0, str(pa["groups_value"]):str(df_ls.loc[row,pa["groups_value"]])}] )
                df_long=pd.concat([df_long, tmp_ ])

        df_long=df_long.reset_index(drop=True)
        df_output=df_long.copy()
        
        #     elif pa["censors_val"] and int(df_ls.loc[row, pa["censors_val"]]) >= 1:
        #         censored=int(df_ls.loc[row, pa["censors_val"]])
        #         #print(censored)
        #         for c in range (0,censored):
        #             #print(c)
        #             tmp_c=pd.DataFrame( [ {'day':int(df_ls.loc[row,pa["xvals"]]), 'status':0, str(pa["groups_value"]):str(df_ls.loc[row,pa["groups_value"]])} ] )
        #             df_long=pd.concat([df_long, tmp_c ])
        #             #df_long=df_long.append({'day':int(df_ls.loc[row,pa["xvals"]]), 'status':0, str(pa["groups_value"]):str(df_ls.loc[row,pa["groups_value"]])}, ignore_index=True)
        #             c=c+1

        # df_dummy=pd.get_dummies(df_long, drop_first=True, columns=[pa["groups_value"]])
        # print(df_dummy)

        # results = logrank_test(df_dummy.loc[df_dummy['status'] == 1,'day'].tolist(),
        #                df_dummy.loc[df_dummy['status'] == 0,'day'].tolist(),
        #                df_dummy.loc[df_dummy['status'] == 1,'status'].tolist(),
        #                df_dummy.loc[df_dummy['status'] == 0,'status'].tolist(), alpha=.99)


        results = multivariate_logrank_test(event_durations=df_long["day"], event_observed=df_long["status"], groups=df_long[pa["groups_value"]])
        print(results.p_value)

        
        n_dict={}
        for  con in pa["list_of_groups"]:
            n_dict[con] = len( df_long.loc[ df_long[pa["groups_value"]] == con] )

        for count, con in enumerate(pa["list_of_groups"]):
            print (count+1, con)
            df_long.loc[ df_long[pa["groups_value"]] == con, pa["groups_value"] ] = str(count+1)

        cph = CoxPHFitter()
        cph.fit(df_long, duration_col='day', event_col='status')

        pht_ = proportional_hazard_test(cph, df_long, time_transform='rank')
        pht_=dict(zip(pht_.name,pht_.p_value))
        pht=pht_[pa["groups_value"]]
        print(pht)

        if pht >= 0.05:
            assumptions="Yes"
        else:
            assumptions="No"

        cph_coeff=cph.summary
        cph_coeff=cph_coeff.reset_index()

        df_info={}
        df_info['model']='lifelines.CoxPHFitter'
        df_info['duration col']=cph.duration_col
        df_info['event col']=cph.event_col
        df_info['baseline estimation']='breslow'
        df_info['number of observations']=cph._n_examples
        df_info['number of events observed']=len(df_long.loc[df_long['status']==1,])
        df_info['partial log-likelihood']=cph.log_likelihood_
        df_info['Concordance']=cph.concordance_index_
        df_info['Partial AIC']=cph.AIC_partial_
        df_info['log rank test']=results.test_statistic
        df_info['P.value(log rank test)']=results.p_value
        df_info['log-likelihood ratio test']=cph.log_likelihood_ratio_test().test_statistic
        df_info['P.value(log-likelihood ratio test)']=cph.log_likelihood_ratio_test().p_value
        df_info['P.value(proportional-hazard-test)']=pht
        df_info["Proportional hazard assumptions met"]=assumptions

        cph_stats=pd.DataFrame(df_info.items())
        cph_stats=cph_stats.rename(columns={0:'Statistic',1:'Value'})
        #cph_stats

        print(cph_stats)

        tmp=[]
        
        #fig = go.Figure()
        #fig.update_layout( width=pa_["fig_width"], height=pa_["fig_height"] )

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
            
            ## Figure starting here
            PA_=[ g for g in pa["groups_settings"] if g["name"]==cond ][0]
            print(PA_)
            
            ## Main Line arguments per group
            linewidth=float(PA_["linewidth_write"])
            linestyle=PA_["linestyle_value"]

            if str(PA_["linecolor_write"]) != "":
                linecolor=PA_["linecolor_write"]
            else:
                linecolor=PA_["line_color_value"]

            ## Plot settings
            for a in ["Conf_Interval","show_censors","ci_legend","ci_force_lines"]:
                if a in PA_["model_settings"]:
                    PA_[a]=True
                else:
                    PA_[a]=False

            
            if PA_["ci_legend"]:
                CI_legend=True
            else:
                CI_legend=False

            ## Conf interval Lines arguments per group
            ci_linewidth=float(PA_["ci_linewidth_write"])
            ci_linestyle=PA_["ci_linestyle_value"]

            CI_alpha=PA_["ci_alpha"]

            if str(PA_["ci_linecolor_write"]) != "":
                ci_linecolor=PA_["ci_linecolor_write"]
                ci_color_rgba=ci_linecolor.strip(")")+","+str(CI_alpha)+")"
                ci_color_rgba=ci_color_rgba.replace("rgb","rgba")
                #print(ci_color_rgba)
            else:
                ci_linecolor=PA_["ci_line_color_value"]
                from matplotlib import colors
                ci_color_rgba="rgba("+str(colors.to_rgba(ci_linecolor)[0])+","+str(colors.to_rgba(ci_linecolor)[1])+","+str(colors.to_rgba(ci_linecolor)[2])+","+CI_alpha+")"
                 #print(ci_color_rgba)

            ## Censors arguments
            markerShape=PA_["censor_marker_value"]
            markerSize=float(PA_["censor_marker_size_val"])
            edgeLineWidth=float(PA_["edge_linewidth"])

            if str(PA_["markerc_write"]) != "":
                markerColor=PA_["markerc_write"]
            else:
                markerColor=PA_["markerc"]

            markerAlpha=PA_["marker_alpha"]

            if str(PA_["edgecolor_write"]) != "":
                edgeColor=PA_["edgecolor_write"]
            else:
                edgeColor=PA_["edgecolor"]

            name_label=cond+" , n="+str(n_dict[cond])
            ## Main line 'rgb(31, 119, 180)'
            fig.add_trace(go.Scatter(
                x=km.survival_function_.index, y=km.survival_function_[cond],
                line=dict(shape='hv', width=linewidth, color=linecolor,  dash=linestyle),
                showlegend=CI_legend,mode='lines',
                name=name_label
            ))
            
            ann_text='p(log_likelihood_ratio_test) : '+ str(round(df_info['P.value(log-likelihood ratio test)'], 5))+'<br>p(proportional_hazard_test) : '+str(round(df_info['P.value(proportional-hazard-test)'], 5))
            fig.add_annotation(text=ann_text, 
                    align='right',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    #xanchor="right",
                    #yanchor="middle",
                    x=1.0,
                    y=1.0,
                    bordercolor='black',
                    borderpad=2.5,
                    font={'size':12},
                    borderwidth=0)



            if PA_["ci_force_lines"] and PA_["Conf_Interval"]:

                ## Adding line for upper conf interval
                fig.add_trace(go.Scatter(
                x=km.confidence_interval_.index, y=km.confidence_interval_[cond+"_upper_0.95"],
                line=dict(shape='hv', width=ci_linewidth, color=ci_linecolor,  dash=ci_linestyle),
                showlegend=CI_legend,mode='lines',
                name="95% Conf. Interval - "+cond
                ))

                ## Adding line for lower conf interval
                fig.add_trace(go.Scatter(
                x=km.confidence_interval_.index, y=km.confidence_interval_[cond+"_lower_0.95"],
                line=dict(shape='hv', width=ci_linewidth, color=ci_linecolor,  dash=ci_linestyle),
                showlegend=CI_legend,mode='lines',
                name="95% Conf. Interval - "+cond
                ))

                ## Adding shade for upper conf interval
                fig.add_trace(go.Scatter(
                    x=km.confidence_interval_.index, 
                    y=km.confidence_interval_[cond+"_upper_0.95"],
                    line=dict(shape='hv', width=0),
                    showlegend=False,mode='lines',
                    name="95% Conf. Interval - "+cond
                ))

                ## Adding shade for lower conf interval
                fig.add_trace(go.Scatter(
                    x=km.confidence_interval_.index,
                    y=km.confidence_interval_[cond+"_lower_0.95"],
                    line=dict(shape='hv', width=0),
                    fill='tonexty',
                    fillcolor=ci_color_rgba,
                    showlegend=False,mode='lines',
                    name="95% Conf. Interval - "+cond
                ))

            elif PA_["ci_force_lines"]:
                ## Adding line for upper conf interval
                fig.add_trace(go.Scatter(
                x=km.confidence_interval_.index, y=km.confidence_interval_[cond+"_upper_0.95"],
                line=dict(shape='hv', width=ci_linewidth, color=ci_linecolor,  dash=ci_linestyle),
                showlegend=CI_legend,mode='lines',
                name="95% Conf. Interval - "+cond
                ))

                ## Adding line for lower conf interval
                fig.add_trace(go.Scatter(
                x=km.confidence_interval_.index, y=km.confidence_interval_[cond+"_lower_0.95"],
                line=dict(shape='hv', width=ci_linewidth, color=ci_linecolor,  dash=ci_linestyle),
                showlegend=CI_legend,mode='lines',
                name="95% Conf. Interval - "+cond
                ))

            elif PA_["Conf_Interval"]:
                ## Adding shade for upper conf interval
                fig.add_trace(go.Scatter(
                    x=km.confidence_interval_.index, 
                    y=km.confidence_interval_[cond+"_upper_0.95"],
                    line=dict(shape='hv', width=0),
                    showlegend=False, mode='lines',
                    name="95% Conf. Interval - "+cond
                ))

                ## Adding shade for lower conf interval
                fig.add_trace(go.Scatter(
                    x=km.confidence_interval_.index,
                    y=km.confidence_interval_[cond+"_lower_0.95"],
                    line=dict(shape='hv', width=0),
                    fill='tonexty',mode='lines',
                    fillcolor=ci_color_rgba,
                    showlegend=False,
                    name="95% Conf. Interval - "+cond
                ))

            if PA_["show_censors"]:

                censors=df.loc[df[cond+"_censored"] > 0, ["time", cond+"_KMestimate"]]
                
                censors_x=censors["time"].tolist()
                censors_y=censors[cond+"_KMestimate"].tolist()
            
                fig.add_trace(go.Scatter(x=censors_x, y=censors_y, 
                        mode='markers', 
                        marker=dict(symbol=markerShape,\
                                color=markerColor,
                                size=markerSize,
                                opacity=float(markerAlpha),
                                line=dict(
                                    color=edgeColor,
                                    width=edgeLineWidth)), \
                        showlegend=False,\
                        name=cond))


        fig.show()

        print(df_output)

        return df, fig, cph_coeff, cph_stats,df_output
        

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
STANDARD_SIZES=[ str(i) for i in list(range(101)) ]
STANDARD_COLORS=["blue","green","red","cyan","magenta","yellow","black","white",None]
LINE_STYLES=["solid", "dot", "dash", "longdash", "dashdot", "longdashdot"]
HIST_TYPES=['bar', 'barstacked', 'step',  'stepfilled']
STANDARD_ORIENTATIONS=['vertical','horizontal']
STANDARD_ALIGNMENTS=['left','right','mid']
TICKS_DIRECTIONS=["inside","outside"]
LEGEND_LOCATIONS=['best','upper right','upper left','lower left','lower right','right','center left','center right','lower center','upper center','center']
LEGEND_FONTSIZES=['xx-small', 'x-small', 'small', 'medium', 'large', 'x-large', 'xx-large']
MODES=["expand",None]


def figure_defaults():
    """Generates default figure arguments.

    Returns:
        dict: A dictionary of the style { "argument":"value"}
    """
    plot_arguments={
        "fig_width":"800",\
        "fig_height":"600",\
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
        "model_settings":["Conf_Interval", "show_censors", "ci_legend", "ci_force_lines"],\
        # "Conf_Interval":".off",\
        # "show_censors":".off",\
        # "ci_legend":".off",\
        # "ci_force_lines":".off",\
        "censor_marker":ALLOWED_MARKERS,\
        "censor_marker_value":"x",\
        "censor_marker_size":STANDARD_SIZES,\
        "censor_marker_size_val":"4",\
        #"censor_marker_size_cols":["select a column.."], \
        #"censor_marker_size_col":"select a column..", \
        "marker_color":STANDARD_COLORS,\
        "markerc":"black",\
        #"markerc_cols":["select a column.."], \
        #"markerc_col":"select a column..", \
        "markerc_write":"",\
        "ci_alpha":"0.3",\
        "ci_linewidth_write":"1.0",\
        "ci_linestyle_value":"solid",\
        "ci_line_color_value":"blue",\
        "ci_linecolor_write":"",\
        "colors":STANDARD_COLORS,\
        "linestyles":LINE_STYLES,\
        "linestyle_value":"solid",\
        #"linestyle_cols":["select a column.."],\
        #"linestyle_col":"select a column..",\
        "linestyle_write":"", \
        #"linewidth_cols":["select a column.."],\
        #"linewidth_col":"select a column..",\
        "linewidth_write":"1.0",\
        "line_colors":STANDARD_COLORS,\
        "line_color_value":"blue",\
        #"linecolor_cols":["select a column.."],\
        #"linecolor_col":"select a column..",\
        "linecolor_write":"",\
        "edge_linewidths":STANDARD_SIZES,\
        "edge_linewidth":"1",\
        #"edge_linewidth_cols":["select a column.."],\
        #"edge_linewidth_col":"select a column..",\
        "edge_colors":STANDARD_COLORS,\
        "edgecolor":"black",\
        #"edgecolor_cols":["select a column.."], \
        #"edgecolor_col":"select a column..", \
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
        #"show_ticks":["tick_left_axis", "tick_right_axis", "tick_upper_axis", "tick_lower_axis"],\
        "show_ticks":["tick_x_axis","tick_y_axis"],\
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
        "grid":["None","both","x","y"],\
        "grid_value":"None",\
        "grid_color_text":"",\
        "grid_colors":STANDARD_COLORS,\
        "grid_color_value":"black",\
        "grid_linestyle":LINE_STYLES,\
        "grid_linestyle_value":'solid',\
        "grid_linewidth":"1",\
        "grid_alpha":"0.1",\
        # "download_format":["tsv","xlsx"],\
        # "downloadf":"xlsx",\
        # "download_fig_format":["png","pdf","svg"], \
        # "download_fig":"pdf", \
        # "downloadn":"LifeSpan",\
        # "downloadn_fig":"LifeSpan",\
        # "session_downloadn":"MySession.LifeSpan",\
        # "inputsessionfile":"Select file..",\
        # "session_argumentsn":"MyArguments.LifeSpan",\
        # "inputargumentsfile":"Select file.."
        }

    return plot_arguments