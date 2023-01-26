#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd


# In[ ]:


def clean_tong(tong_cntry_fix):
    
    # this data is in Gt, so need to be modified and converted to Mt
    tong_cntry_fix.iloc[:,2:] =  tong_cntry_fix.iloc[:,2:] * 1000
    
    # modify the data types so country names can be grouped by, and so years can be numerically filtered
    tong_cntry_fix['country.name.en'] = tong_cntry_fix['country.name.en'].astype(str)
    tong_cntry_fix['Year'] = tong_cntry_fix['Year'].astype(int)
    tong_cntry_fix = tong_cntry_fix[tong_cntry_fix['Year'] > 2020]
    tong_cntry_fix['Year'] = tong_cntry_fix['Year'].astype(str)
    
    # Group the data by the indices which will be used for row and column indices: country, status, and start.
    country_posterior_pivot = tong_cntry_fix.pivot_table(index = 'country.name.en', columns = ['Year']).sort_values('Year', axis = 1, ascending = True)
    
    # make a copy of this data where the multi-index is converted to single column names joined by dots
    # aka format for panel data and export
    reset_pivot = country_posterior_pivot.reset_index()
    reset_pivot.columns = reset_pivot.columns.map('.'.join).str.strip('.')
    tong_country_sector_CO2 = reset_pivot.rename(columns = {'country.name.en':'country'})
    
    tong_country_sector_CO2.to_csv('data/tong_country_sector_CO2.csv')
    
    return(tong_country_sector_CO2)


# In[ ]:


if __name__ == "__main__":
    clean_tong

