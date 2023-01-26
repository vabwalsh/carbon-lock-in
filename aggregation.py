#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np


# In[ ]:


def parse_data_to_aggregate():

    # Scenario emissions pathways
    # This data is in units of Mt, meaning million tonnes
    scenario_CO2 = pd.read_csv('data/scen_CO2_cntry.csv').fillna(0).rename(columns = {'country.name.en':'country'})

    # Committed emissions
    # This data is in units of Mt (million tonnes per annum, from GEM)
    electricity_commit = pd.read_csv('data/electricity.committed.csv', index_col = 0).fillna(0)
    # This data was in units of Gt, and gets converted to Mt (is multiplied by 1000) in the commit_Tong-GEM.ipynb script
    other_sector_commit = pd.read_csv('data/tong_country_sector_CO2.csv', index_col = 0).fillna(0) # Tong data on emissions from other sectors

    # Considered Emissions
    # This data is in units of Mt (million tonnes per annum, from GEM)
    gas_consid = pd.read_csv('data/gas-considered.csv', index_col = 0).fillna(0)
    # This data is in units of Mt (million tonnes per annum, from GEM)
    coal_consid = pd.read_csv('data/coal-considered.csv', index_col = 0).fillna(0)
    # This data was in units of Gt, and gets converted to Mt (is multiplied by 1000) in the commit_Tong-GEM.ipynb script
    steel_consid = pd.read_csv('data/steel-considered.csv', index_col = 0).fillna(0)
    # This data was in units of Gt, and gets converted to Mt (is multiplied by 1000) in the commit_Tong-GEM.ipynb script
    industry_consid = pd.read_csv('data/otherindustry-considered.csv', index_col = 0).fillna(0)
   
    return(scenario_CO2, electricity_commit, other_sector_commit, gas_consid, coal_consid, steel_consid, industry_consid)


# In[ ]:


def make_custom_total(df, new_col_name):
    var_sum = []

    for year in range(2021,2101):
        cols_to_total = []

        for col_name in df.columns[1:]:
            if 'total' not in col_name and str(year) == str(col_name[-4:]):

                    cols_to_total.append(col_name)
        
        df[new_col_name + str(year)] = np.nansum(df[cols_to_total], axis = 1)
    
    # This changes the function by returning only the newly created columns, instead of including the ones which created it
    new_cols = df.iloc[:,-80:]
    new_cols['country'] = df['country']
    
    return(new_cols)


# In[ ]:


def agg_inital_totals(gas_consid, coal_consid, electricity_commit, other_sector_commit):

    # Merge considered gas and coal to a DF which only contains the total considered sum, and not its components
    gas_coal_consid = pd.merge(coal_consid, gas_consid, on = "country", how = 'outer')
    consid_elec = make_custom_total(gas_coal_consid, 'consid.elec.')

    # coal.permitted + coal.pre-permit + coal.announced + coal.construction = coal.total
    coal = make_custom_total(coal_consid, 'consid.coal.')

    # gas.commit + coal.commit = electricity.total
    electricity = make_custom_total(electricity_commit, 'commit.elec.')

    # sum(Other Energy, International Transport, Road Transport, Industry, Other Transport, Residential, Commerical) = sectors.total
    sector_commit = make_custom_total(other_sector_commit, 'commit.tong.')
    
    return(gas_coal_consid, consid_elec, coal, electricity, sector_commit)


# In[ ]:


# The scaling of industrial emissions rewrites the existing industrial emissions variable with one scaled by 
# considered electricity values
def scale_industrial_emits(electricity, consid_elec, other_sector_commit):
    
    new_df = pd.DataFrame()

    # First, define the set of countries in each of the 3 inputs
    common_cntry = list(set(electricity["country"]) & set(consid_elec["country"]) & set(other_sector_commit["country"]))
    
    # Set the countries for which this can be defined to only be the ones included in all three input 
    # datsets 
    new_df["country"] = common_cntry
    
    for country in new_df["country"]:
        for year in range(2021, 2101):
        
        # make a condition for whether the country actually has considered emissions from industry
            if country in consid_elec["country"]:
            
                    # committed emissions from electricity == 'commit.elec.'
                    # considered emissions from electricity == 'consid.elec.'
                    # comitted emissions from industry == 'Industry.'
                    # considered emissions from industry == 'otherindustry.proposed.'

                new_df['industry.consid.scaled.' + str(year)] = (consid_elec['consid.elec.' + str(year)] / 
                            electricity['commit.elec.2021']) * other_sector_commit['Industry.2021']
                print(electricity['commit.elec.2021'], other_sector_commit['Industry.2021'])
                
            else:
                new_df['industry.consid.scaled.' + str(year)] = 0  
            
    return(new_df.fillna(0))

# moved call to make_consid_commit_scen() function: scaled_industry = scale_industrial_emits()


# In[ ]:


def make_consid_commit_scen(scaled_industry, gas_consid, coal_consid, consid_elec, coal, other_sector_commit,
                            sector_commit, electricity_commit, electricity, scenario_CO2):
    
    # Define the considered emissions variables which contribute to total consid emits
    # gas, coal, and industry
    all_consid = coal_consid.merge(gas_consid, on = "country", 
                                   how = 'outer').merge(scaled_industry, 
                                   on = "country",how = 'outer').fillna(0)
    consid = make_custom_total(all_consid, 'consid.total.') 

    # Define the committed emissions variables which contribute to the totals
    # electricity, other_sector
    all_commit = electricity.merge(sector_commit, on = "country", 
                                   how = 'outer').merge(electricity_commit, 
                                   on = "country", how = 'outer')
    commit = make_custom_total(all_commit, 'commit.total.')

    # combine consid/commit df with scenario data, making final step in the data agg before more totals
    # This removes the data from 1850-2020, which is introduced by the complete GEM datasets
    scenario_CO2_2021_on = scenario_CO2.iloc[:,:4].join(scenario_CO2.iloc[:,174:])
    
    # Combine the totals from unique column combinations with the all_consid and all_commit totals to 
    # give the end result
    
    # make total committed and considered emissions from the aggregated consid & commit dfs
    # this includes many disaggregated totals which are not included in the final plotting mechanism
    consid_commit = pd.merge(consid, commit, on = "country", how = 'outer').merge(consid_elec, on = "country",
                                             how = 'outer').merge(coal_consid, on = "country",
                                             how = 'outer').merge(gas_consid, on = "country",
                                             how = 'outer').merge(coal, on = "country",
                                             how = 'outer').merge(electricity_commit, on = "country",
                                             how = 'outer').merge(electricity, on = "country",
                                             how = 'outer').merge(sector_commit, on = "country",
                                             how = 'outer').merge(other_sector_commit, on = "country",
                                             how = 'outer').merge(scaled_industry, on = "country",
                                             how = 'outer')

    # combine the consid_commit df with all the scenario data in one final merge
    consid_commit_scen = scenario_CO2_2021_on.merge(consid_commit, on = 'country', how = 'left')
    
    return(consid_commit_scen)


# In[ ]:


# Make "expectable" emissions from scenario - (consid + commit)
def make_expectable_emits(consid_commit_scen):

    for year in range(2021,2101):
        consid_commit_sum = []
        consid_commit_scen_sum = []

        for col_name in consid_commit_scen.columns[3:]:

            if str(year) == str(col_name[-4:]):

                if 'consid.total.' in col_name:
                    consid_commit_sum.append(col_name)
                    consid_commit_scen_sum.append(col_name)
                if 'commit.total.' in col_name: 
                    consid_commit_sum.append(col_name)
                    consid_commit_scen_sum.append(col_name)
                if len(col_name) == 4:
                    consid_commit_scen_sum.append(col_name)
        
        # create columns which total consid+commit and consid+commit+scen
        consid_commit_scen['commit+consid.' + str(year)] = np.nansum(consid_commit_scen[consid_commit_sum], axis = 1)
        consid_commit_scen['commit+consid+scen.' + str(year)] = np.nansum(consid_commit_scen[consid_commit_scen_sum], axis = 1)
                
        for col_name in consid_commit_scen.columns[1:]:
            if str(year) == str(col_name):
                consid_commit_scen['expectable.' + str(year)] = consid_commit_scen[col_name] - (consid_commit_scen['commit+consid.' + str(year)])
                    # This line is IMPORTANT! It makes expectable emissions values < 0 equal to 0
                    # Do not execute this in the present version, because in order to plot abs(expectable)
                    # for affectability plots, we need the original negative values in the master file
                    # consid_commit_scen['expectable.' + str(year)][consid_commit_scen['expectable.' + str(year)] < 0] = 0

    return(consid_commit_scen.fillna(0))


# In[ ]:


def add_regions(expectable):
    
    # merge data on all countries with the region mapping
    regions = pd.read_csv('data/cntry_short_region_map.csv').drop(columns = 'short')
    
    # .iloc here is a hacky fix for the below not quite working, it removes defunct rows
    # this is what makes the master file not have lines for the countries in the not-working code below (e.g. N. Korea)
    region_merge = pd.merge(expectable, regions, how = 'left', on = 'country')#.iloc[:-8,:]

    # make a list of the countries with no scenario data (to remove)
    # remove = ['Guadeloupe', 'Kosovo', 'North Korea', 'Isle of Man', 'Palestinian Territories', 
    #           'Curaçao', 'Gibraltar', 'Micronesia (Federated States of)']

    # # remove the rows with this data for these countries
    # region_merge['country'] = region_merge['country'].drop(labels = remove)

    # put region column at the front of the df
    reg = region_merge.pop('region')
    region_merge.insert(1, reg.name, reg)
    region_merge.to_csv('data/master.csv')
    
    return(region_merge)


# In[ ]:


def aggregate():
    
    scenario_CO2, electricity_commit, other_sector_commit, gas_consid, coal_consid, steel_consid, industry_consid = parse_data_to_aggregate()
    #new_cols = make_custom_total(df, new_col_name)
    gas_coal_consid, consid_elec, coal, electricity, sector_commit = agg_inital_totals(gas_consid, 
                                                                                       coal_consid, 
                                                                                       electricity_commit, 
                                                                                       other_sector_commit)
    scaled_industry = scale_industrial_emits(electricity, 
                                             consid_elec, 
                                             other_sector_commit)
    consid_commit_scen = make_consid_commit_scen(scaled_industry, 
                                                 gas_consid, 
                                                 coal_consid, 
                                                 consid_elec, 
                                                 coal, other_sector_commit, 
                                                 sector_commit, 
                                                 electricity_commit, 
                                                 electricity, scenario_CO2)
    w_expectable = make_expectable_emits(consid_commit_scen)
    region_merge = add_regions(w_expectable)
    
    return(region_merge)


# In[ ]:


if __name__ == "__main__":
    aggregate

