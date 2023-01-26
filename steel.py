#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np


# In[ ]:


def process_steel():
    ### Cleaning Steel Data
    # read in steel data with already corrected country names
    steel = pd.read_csv('data/steel_cntry_fix.csv', index_col = 0)

    # subset the steel data, only selecting the production columns so they can be filtered differently
    production_cols = []
    for col in steel.columns:
        if 'capacity' in col:
            production_cols.append(col)

    # select the relevant data columns, and clean them
    steel_subset = steel[['country.name.en', 'Region', 'Status', 'Start year','Main production process']].join(steel[production_cols])
    steel_subset[production_cols] = steel_subset[production_cols].replace(to_replace = [' ','unknown','>0',np.nan], value = 1)#.astype(float)
    steel_subset[production_cols] = steel_subset[production_cols].replace('10,000',10000).astype(float)

    # filter the data for active plants only 
    steel_oper = steel_subset[(steel_subset['Status'] == 'proposed') ^ (steel_subset['Status'] == 'operating') 
                              ^ (steel_subset['Status'] == 'construction') ^ (steel_subset['Status'] == 'unknown')]

    # reindex the df to retain standard integer indexing and prevent random index loss
    steel_indexed = steel_oper.reset_index(drop = 'index')

    # rename the data to be consistent with coal and gas data
    steel_clean = steel_indexed.rename(columns = {'Start': 'Start year'})#.fillna(0)

    # filter years for blanks and not found values, replace these with 2028 as a placeholder
    steel_clean['Start year'] = steel_clean['Start year'].replace(to_replace = ['NA', ' ', '', 'unknown', 
                                                                                np.nan, 0], value = '2027')

    # remove '(anticipated)' tag from the years in steel, clean years by taking only the last four digits
    clean_yrs = []
    for yr in steel_clean['Start year']:
        clean_yrs.append(float(yr[:4]))

    # add the years without this tag to the yr column
    steel_clean['Start year'] = clean_yrs

    ### Create an output matrix which for weighting the steel data, including:
        #     - utilization capacity for each production type
        #     - emissions intensity for each production type
        #     - every country

        # It should at the country level so that we can assume utilization and emissions intensity might vary locally

        # This code creates an output matrix propograted with arbitrary weights

    # utilization_rate_cols = []
    # emit_int_cols = []
    # for prod_type in production_cols:
    #     utilization_rate_cols.append(prod_type)
    #     emit_int_cols.append(prod_type)

    # utilization_rate_df = pd.DataFrame(index = steel_clean['Country'].unique(), columns = utilization_rate_cols).fillna(1)
    # emit_int_df = pd.DataFrame(index = steel_clean['Country'].unique(), columns = emit_int_cols).fillna(1)

    # utilization_rate_df = utilization_rate_df.reset_index().rename(columns = {'index': 'country'})
    # emit_int_df = emit_int_df.reset_index().rename(columns = {'index': 'country'})

    # utilization_rate_df.to_csv('~/Desktop/Founders_Pledge/affectable_emissions_active_repo/Affectable-Emissions/data_files/steel_data/steel_country_UR_prod.csv')
    # emit_int_df.to_csv('~/Desktop/Founders_Pledge/affectable_emissions_active_repo/Affectable-Emissions/data_files/steel_data/steel_country_EI_prod.csv')

    ### Import locally modified versions of the steel weighting files
        #     - each df weighting file has a copy made of it locally, which gets modified and has another name
        #     - after being locally adjusted to reflect weighting differences by country, that file is imported again here

    # Now import the weighted data output by Tom. This is versions of what was output above modified to include
    # our priors on industry/steel emissions. See detailed estimates here: https://docs.google.com/spreadsheets/d/1TOH_Xq8rIaLiOM_cr0IwZuX5jw6KlRkpv2sJQSciHoc/edit?usp=sharing

    # Data in tonnes CO2 / tonne steel
    emit_int_weight = pd.read_csv('~/Desktop/Founders_Pledge/affectable_emissions_active_repo/Affectable-Emissions/data_files/steel_data/EMIT_INT_WEIGHTS.csv', index_col = 0)
    utr_rate_weight = pd.read_csv('~/Desktop/Founders_Pledge/affectable_emissions_active_repo/Affectable-Emissions/data_files/steel_data/UTILIZATION_RT_WEIGHTS.csv', index_col = 0)

    ### Weight steel data by emit int and utilization capacity

    assert len(utr_rate_weight) == len(emit_int_weight)

    # Converting data units from thousand tonnes steel/yr [aka (1/1000)(tonnes CO2/yr)] to (tonnes CO2/yr)
    # data/1000 = tonnes steel / per year
    steel_clean.iloc[:,4:] = steel_clean.iloc[:,4:] * 1000

    # Convert emissions intensity units from tonnes CO2/tonne steel to Mt CO2/tonne steel
    # emit_int/1000 = (tonne CO2/tonne Steel) /1000 = Mt CO2 / tonne steel
    emit_int_weight_mt = emit_int_weight / 1000

    # create a weighting factor by multiplying together the emissions intensity values and the utilization rates
    # this multiplies steel prod data in tonnes by an emit int in Mt CO2 / tonne steel, yielding Mt CO2
    weight_factor = pd.DataFrame(utr_rate_weight.iloc[1:,:].values * emit_int_weight_mt.iloc[1:,:].values)
    weight_factor['country.name.en'] = emit_int_weight_mt.index[1:]

    # merge the weighting factors and the data based on country, so every plant in a country gets weighted
    merged = steel_clean.merge(weight_factor)

    # make a new df from the weighted data, and give it proper columns, formatting, etc.
    weighted_steel_data = pd.DataFrame(data = merged.iloc[:,5:16].values * merged.iloc[:,16:].values)
    weighted_steel_data.columns = merged.iloc[:,5:16].columns
    weighted_steel_data[['country.name.en', 'Status', 'Start year','Main production process']] = steel_clean[['country.name.en', 'Status', 'Start year','Main production process']]

    ### Merge Weighted Steel Data with Country mapping

    steel_merged = weighted_steel_data.rename(columns = {'country.name.en':'country'})

    # Make the column dtypes numeric, so that they add during the merge instead of concatenating as strings
    steel_merged['Start year'] = steel_merged['Start year'].astype(int).astype(str)

    # Group the data by the indices which will be used for row and column indices: country, status, and start.
    steel_pivot = steel_merged.pivot_table(index = 'country', columns = ['Status', 'Start year']).sort_values('Start year', axis = 1, ascending = True).fillna(0).groupby(by = ['Status','Start year'], axis =1).sum()

    # Combine the multi-index pivot tables into panel data with standardized column names by reassigning
    # an adapted version of the column names to the data with .map()
    reset_steel = steel_pivot.reset_index()
    reset_steel.columns = reset_steel.columns.map('.'.join).str.strip('.')

    # Rename columns for R
    reset_steel.columns = ['steel.' + 'cap.' + str(col) for col in reset_steel.columns]
    steel_panel = reset_steel.rename(columns = {'steel.cap.country': 'country'})

    # Now in units of Mt CO2
    steel_panel.to_csv('data/steel_panel_clean.csv')
    return(steel_panel)


# In[ ]:


if __name__ == "__main__":
    process_steel

