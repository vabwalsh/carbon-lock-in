#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np


# In[ ]:


def make_expectation_over_data(data, area):
    
    # create emissions projections based on probability weighted of different rcp/ssp scneraios
    credence = pd.read_csv('data/rcp_ssp_credences.csv', index_col = 0)
#     raw = pd.read_csv('data/master.csv', index_col = 0)
    
    # make a column in the data data which will match the creedences data, merge on this column
    clean_rcp = data['RCP'].str.replace('.', '')
    data['cred_scen_match'] = data['SSP'] + '-' + clean_rcp
    data['cred_scen_match'] = data['cred_scen_match'].str.replace('BL', 'Baseline')

    scen_and_prob = data.merge(credence, left_on = 'cred_scen_match', right_on = 'scenario', how = 'inner').fillna(0)
    sort_scen_prob = scen_and_prob.sort_values(by = 'country').reset_index().drop(columns = 'index')

    # make a copy of the merged data in order to weight it
    scen_and_prob_weighted = sort_scen_prob.copy()

    # Multiply every emissions value in the dataset by it's affectability, converting the data to affectable emissions

    # make active cols which should be weighted separate variable, matters b/c prob vars shouldn't be included
    # in final output or get weighted by the following calculation
    prob_cols_to_ignore = ['country', 'region', 'SSP', 'RCP', 'cred_scen_match','scenario','credence','posterior','p']

    # multiply each row of emissions (but not p itself) in the merged dataset of global emissions 
    # by its data's p value
    for col in scen_and_prob_weighted:
        if col not in prob_cols_to_ignore:
            scen_and_prob_weighted[col] = scen_and_prob_weighted[col] * scen_and_prob_weighted['p']

    expectation = scen_and_prob_weighted.groupby(by = area).agg(np.nansum).reset_index()
    
    return(expectation)


# In[ ]:


if __name__ == "__main__":
    make_expectation_over_data

