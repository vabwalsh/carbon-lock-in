#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np


# In[ ]:


def clean_gas_coal(coal_cntry_fix, gas_cntry_fix):
    ### Import and Clean Global Energy Monitor Gas and Coal Data

    # For the electricity sector of committed emissions, we use the Coal and Gas data from Global Energy Monitor
    # instead of the data from Tong et al. The GEM data has higher resolution because it is not weighted, 
    # and therefore doesn't assume the same trends in electricity intensity over time across all regions like
    # we have to in order to extract the Tong data.

    # Import only the columns which are relevant for our investigation, relating to electrical generation
    # capacity, location, and status.
    GEM_coal = coal_cntry_fix[['country.name.en', 'Status', 'Planned Retire', 'RETIRED', 
                               'Year', 'Capacity (MW)', 'Remaining plant lifetime (years)', 
                               'Annual CO2 (million tonnes / annum)']]
    GEM_gas = gas_cntry_fix[['country.name.en', 'Status', 'Planned retire', 
                             'Retired year', 'Start year', 'Capacity elec. (MW)']]

    # Clean the data by making all values stipped of extra spaces, and lowercase
    GEM_coal['country.name.en'] = GEM_coal['country.name.en'].str.strip()#.str.lower()
    GEM_gas['country.name.en'] = GEM_gas['country.name.en'].str.strip()#.str.lower()

    # Standardize the names of columns across the two datasets
    GEM_coal.columns = ['Country', 'Status', 'Planned retire', 'Retired year', 'Start Year', 'Capacity (MW)', 'Annual CO2 (million tonnes / annum)', 'Remaining plant lifetime (years)']
    GEM_gas.columns = ['Country', 'Status', 'Planned retire', 'Retired year', 'Start Year', 'Capacity (MW)']

    # For committed emissions from existing infastructure AND considered emissions, we are interested in the
    # and plants which are already operating, planned, permitted, announced, or under construction.
    coal_oper = GEM_coal[(GEM_coal['Status'] == 'operating') ^ (GEM_coal['Status'] == 'construction') 
                         ^ (GEM_coal['Status'] == 'pre-permit') ^ (GEM_coal['Status'] == 'announced') 
                         ^ (GEM_coal['Status'] == 'permitted')]
    gas_oper = GEM_gas[(GEM_gas['Status'].isin(['operating', 'construction', 'proposed']))]

    # Replace NaN start years (including ambiguous NaN designations) with the year 2027
    coal_oper['Start Year'] = coal_oper['Start Year'].replace(to_replace = ['unclear','',' ','Unclear','NA',
                                                                            'TBD','lear','tbd', '13th plan',
                                                                            np.nan], value = '2027')

    gas_oper['Start Year'] = gas_oper['Start Year'].replace(to_replace = ['not found', '', 'Not found', '0:00',' ',
                                                                          'nan',np.nan], value = '2027')

    # # Take the last 4 digits of each value in the years, to assume the later of the potential start dates when 
    # # multiple are listed. Then, make them into floats so they can be sorted numerically for future years.
    coal_yrs = []
    for i in coal_oper['Start Year']:
        coal_yrs.append(str(i)[-4:])

    coal_oper['Start Year'] = coal_yrs
    coal_oper['Start Year'] = coal_oper['Start Year'].astype(float)

    # # Do the same for the gas data, by taking the last 4 digits of the years written
    gas_yrs = []
    for i in gas_oper['Start Year']:
        if '-' not in str(i)[-4:] and ':' not in str(i)[-4:]:
            gas_yrs.append(str(i)[-4:])
        elif ':' in i:
            gas_yrs.append('2027')
        else:
            gas_yrs.append(str(i).split('-')[0])

    gas_oper['Start Year'] = gas_yrs
    
    ### Format GEM Datasets for Export
    # Merge together the gas and coal data with the correctly formatted region mapping
    coal_merged = coal_oper.rename(columns = {'Country':'country'})
    gas_merged = gas_oper.rename(columns = {'Country':'country'})

    # Make the column dtypes numeric, so that they add during the merge instead of concatenating as strings
    # Capacity as a float so it can be added across plants, and year as a string so that column names can be revised
    # .asytpe(int) is not redundant, it's a convienent way to round and remove decimals from that column.
    coal_merged['Capacity (MW)'] = coal_merged['Capacity (MW)'].astype(float).fillna(0)
    coal_merged['Annual CO2 (million tonnes / annum)'] = coal_merged['Annual CO2 (million tonnes / annum)'].astype(float).fillna(0)
    coal_merged['Start Year'] = coal_merged['Start Year'].astype(int).astype(str)

    no_commas = []
    for num in gas_merged['Capacity (MW)'].fillna(0).astype(str):
        clean = num.replace(',','').replace('not found','0')
        no_commas.append(float(clean))
    gas_merged['Capacity (MW)'] = no_commas

    gas_merged['Start Year'] = gas_merged['Start Year'].astype(str).replace('ound','2027')
    
    # Group the data by the indices which will be used for row and column indices: country, status, and start.
    # Fill NaNs with 0s
    coal_pivot = coal_merged.pivot_table(index = 'country', columns = ['Status', 'Start Year'], values = 'Capacity (MW)', 
                                         aggfunc = np.nansum).sort_values('Start Year', axis = 1, ascending = True).fillna(0)
    coal_pivotCO2 = coal_merged.pivot_table(index = 'country', columns = ['Status', 'Start Year'], values = 'Annual CO2 (million tonnes / annum)', 
                                         aggfunc = np.nansum).sort_values('Start Year', axis = 1, ascending = True).fillna(0)
    gas_pivot = gas_merged.pivot_table(index = 'country', columns = ['Status', 'Start Year'], values = 'Capacity (MW)'
                                       , aggfunc = np.nansum).sort_values('Start Year', axis = 1, ascending = True).fillna(0)
    
    ### Export Formatted CSVs for Coal and Gas Datasets with Mapped Countries
    # Assign a version of the data with a reset index to a new variable to do operations based on it
    reset_coal = coal_pivot.reset_index()
    reset_coalCO2 = coal_pivotCO2.reset_index()
    reset_gas = gas_pivot.reset_index()

    # Combine the multi-index pivot tables into panel data with standardized column names by reassigning
    # an adapted version of the column names to the data with .map()
    reset_coal.columns = reset_coal.columns.map('.'.join).str.strip('.')
    reset_coalCO2.columns = reset_coalCO2.columns.map('.'.join).str.strip('.')
    reset_gas.columns = reset_gas.columns.map('.'.join).str.strip('.')

    # Rename columns for R
    reset_coal.columns = ['coal.' + 'MW.' + str(col) for col in reset_coal.columns]
    reset_coalCO2.columns = ['coal.' + 'CO2.' + str(col) for col in reset_coalCO2.columns]
    reset_gas.columns = ['gas.' + 'cap.' + str(col) for col in reset_gas.columns]
    coal_panel = reset_coal.rename(columns = {'coal.MW.country': 'country'})
    coalCO2_panel = reset_coalCO2.rename(columns = {'coal.CO2.country': 'country'})
    gas_panel = reset_gas.rename(columns = {'gas.cap.country': 'country'})

    # Write the data to a csv file
    coal_panel.to_csv('data/coal_panel_data_MW.csv')
    coalCO2_panel.to_csv('data/coal_panel_data_CO2.csv')
    gas_panel.to_csv('data/gas_panel_data.csv')
    
    return(coal_panel, coalCO2_panel, gas_panel)


# In[ ]:


if __name__ == "__main__":
    clean_gas_coal

