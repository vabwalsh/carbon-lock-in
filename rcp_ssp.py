#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd


# In[ ]:


def clean_rcpssp_co2():
    
    # Read in emissions data with corrected country names produced by previous script
    # extract GDPpp, CO2, and population data from entity column and concat to df, filter for scenarios in Mt only
    data = pd.read_csv('data/scen_cntry_fix.csv', index_col = 0)

    # see here for data details, file:///Users/Violet/Downloads/RCP-SSP_dwn_v1.0_data-description.pdf
    # From Gütschow et al. 2020
    # this filtering results in only using source values for 'SSPIAMBIE', meaning:
        # 1) "SSPIAM" --> unharmonized downscaled SSP IAM scenarios
        # 2) "B" --> emissions from bunkers have been removed before downscaling
        # 3) "IE" --> Convergence downscaling w/ exponential convergence of emissions intensities, and convergence before transition to negative emissions

    # filter out the population, CO2, and GDP data into different DFs, with CO2 in Mt
    population = data[(data['entity'] == 'POP')]
    CO2 = data[(data['entity'] == 'CO2')]
    CO2 = CO2[CO2['unit'] == 'Mt']
    gdp = data[(data['entity'] == 'GDPPPP')]

    # make a new df from the separate data on each variable
    entity_data = pd.concat([CO2, gdp, population])

    # collect cntry, ssp/rcp, data type, and unit columns
    metadata = entity_data[['country.name.en', 'scenario', 'entity', 'unit']]

    # append the actual data values to this "metadata"
    metadata[entity_data.iloc[:,7:257].columns] = entity_data.iloc[:,7:257]

    # order the emissions df created by country alphabetically and scenario
    sorted_data = metadata.sort_values(['country.name.en','scenario'])
    sorted_data = sorted_data.reset_index().drop(columns = 'index')

    # take the mean of the data for each country + ssp/rcp combination and take the mean across models 
    # (like a CMIP average). Then make the multi index object into a normal df again
    multi_index_data = sorted_data.groupby(by = ['country.name.en','scenario','entity']).mean()
    multi_index_data = multi_index_data.reset_index(level=[0,1,2])

    # separate the strings with model/rcp/ssp into three separate columns, and add them back to the df
    rcps = []
    models = []
    ssps = []

    for val in multi_index_data['scenario']:

        ssps.append(val[:4])
        models.append(val[6:])

        if 'BL' in val:
            rcps.append(val[4:6])
        elif 'BL' not in val:
            val_flt = float(val[4:6]) / 10
            rcps.append(val_flt)

    multi_index_data['SSP'] = ssps
    multi_index_data['model'] = models
    multi_index_data['RCP'] = rcps

    # Reorder DF columns to put RCP and SSP in front
    cols = list(multi_index_data.columns.values) 
    cols.pop(cols.index('country.name.en')) 
    cols.pop(cols.index('model'))
    cols.pop(cols.index('SSP')) 
    cols.pop(cols.index('RCP')) 
    cols.pop(cols.index('entity'))

    #Create new dataframe with columns in the order desired
    multi_index_data = multi_index_data[['country.name.en','model','SSP','RCP','entity']+cols] 

    #13 regions * 3 entities * 6 RCPs * 5 SSPs
    #yearly CO2 per region
    yr_region_CO2 = multi_index_data[multi_index_data['entity'] == 'CO2'].groupby(['country.name.en','SSP','RCP']).mean()

    # this is the time series of CO2 emissions in MT for every country in the data
    CO2_emit = yr_region_CO2.reset_index(level=[0,1,2])
    CO2_emit.to_csv('data/scen_CO2_cntry.csv')

    return(CO2_emit)


# In[ ]:


if __name__ == "__main__":
    clean_rcpssp_co2()

