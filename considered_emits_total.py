#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import warnings
warnings.filterwarnings('ignore')

from plotting import make_plot_vars


# In[ ]:


# read in the maximally complete dataset (the master file) from which simplified versions are aggregated
master_file = pd.read_csv('data/master.csv').drop(columns = {'Unnamed: 0', 'Unnamed: 0.1'})


# In[ ]:


# call the standard column grouping function used in plotting, this will collect the considered emit cols
# this groups together the columns that get added together for plotting
commit_total_cols, consid_total_cols, comm_cons_cols, consid_commit_scen_total_cols, expectable, yr_cols = make_plot_vars(master_file, 'raw')

# create a dataframe with metdata columns and a column for total considered emissions
considered_emissions_total = pd.DataFrame()

# add the identifying metadata back to the df of considered emissions totals
# these are data based values, and won't change as a function of SSP or RCP 
considered_emissions_total['country'] = master_file['country']
considered_emissions_total['region'] = master_file['region']

# add to the total considered column the row-wise sum of the considered emissions cols 2021-2100 for all rows of df
considered_emissions_total['total consid emit'] = master_file[consid_total_cols].sum(axis = 1)

# filter the data to also evaluate emission up until a certain point, s.t. I get totals for different periods
considered_emissions_total['2050 total consid emit'] = master_file[consid_total_cols].iloc[:,:30].sum(axis = 1)
considered_emissions_total['2030 total consid emit'] = master_file[consid_total_cols].iloc[:,:10].sum(axis = 1)

# sort the df by total considered emissions to identify the geographies with the highest considered emissions
# (to get the total considered emissions, it's as easy as grouping the yearly consid total columns together
# with the function that we're using for plotting anyways, and then summing these according to row (cnrty/scenario))
ordered_consid_emit_totals = considered_emissions_total.sort_values(by = 'total consid emit', ascending = False)

# since the values are constant per country, drop the duplicated rows in the data
ordered_consid_emit_totals = ordered_consid_emit_totals.drop_duplicates().reset_index().drop(columns = 'index')


# #### Plotting the global aggregate distribution of considered emissions

# In[ ]:


short_cntry_map = pd.read_csv('data/cntry_short_region_map.csv')[['short', 'country']]
consid_emit_codes = ordered_consid_emit_totals.merge(short_cntry_map, on = 'country', how = 'inner')

# make a df which excludes the countries with the largest considered emissions 
minus_major_emitters = consid_emit_codes[(consid_emit_codes['country'] != 'China') & (consid_emit_codes['country'] != 'India')]


# In[ ]:


def consid_emits_chloropleth(data, to_plot, file_name):
    
    fig = px.choropleth(data, 
                locations = "short",
                color = to_plot,
                hover_name = "country", # column to add to hover information
                color_continuous_scale = px.colors.sequential.Plasma)

    fig.update_layout(title_text='Global considered emissions (MtCO2-eq)')
    fig.show()

    fp = "data/" + str(file_name) + "misc_report_plots.jpeg"
    fig.write_image(fp)
    
    return(fig)


# In[ ]:


consid_emits_chloropleth(consid_emit_codes, 'total consid emit', 'all_2100')
consid_emits_chloropleth(minus_major_emitters, 'total consid emit', 'select_2100')
consid_emits_chloropleth(consid_emit_codes, '2030 total consid emit', 'all_2030')
consid_emits_chloropleth(minus_major_emitters, '2030 total consid emit', 'select_2030')

