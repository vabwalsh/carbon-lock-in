#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import numpy as np


# In[ ]:


def parse_raw_data():
    
    # read in the country names column from each of the initial datasets used in affetcable emissions
    tong_ctry = pd.read_csv('data/tong_cntry_industry_year_emits.csv', encoding = 'latin1', usecols = ['Country', 'Year', 'Industry', 'Road Transport', 'Other Transport', 
                          'International Transport', 'Residential', 'Commerical', 'Other Energy'])
    scen_ctry = pd.read_csv('data/Guetschow_PMSSPBIE_downscaled_ssps_february2020.csv', encoding = 'latin1')
    coal_ctry = pd.read_csv('data/GEM_coalplants_july2022.csv')
    gas_ctry = pd.read_csv('data/GEM_gasplants_august2022.csv')
    steel_ctry = pd.read_csv('data/GEM_steelplants_march2022.csv', dtype = 'str')
    
    return(tong_ctry, scen_ctry, coal_ctry, gas_ctry, steel_ctry)


# In[ ]:


#Beta version used to generate a list of missing names not in the alt names file

#Only execute this unless more data with different countries (which aren't already fixes in the mapping) is added
def gen_missing_names_list(tong_ctry, scen_ctry, coal_ctry, gas_ctry, steel_ctry):
    
    # combine all these country names into a seires, and remove the repeats
    countries_in_data = pd.concat([tong_ctry['Country']] + [scen_ctry['country']] + [coal_ctry['Country']] + [gas_ctry['Country']] + [steel_ctry['Country']])
    strip_dups = countries_in_data.drop_duplicates(keep='first')

    # import a two column file with correct country names in one col, and things that each country could possibly
    # be specified as ("alternative names") in the next column. Some alt names from the data aren't in this file.
    alt_names_file = pd.read_csv('data/alternative_cntry_names_map.csv', index_col = 0, dtype = str, encoding = 'latin1')
    
    # output all of the country names in our data which are not found based on the matchings above, 
    # output this to a file, then, open the file locally to see what remain unspecified, and fix this
    need_to_add = []
    for alt_name in strip_dups:
        if alt_name not in alt_names_file['country.name.alt']:
            need_to_add.append(alt_name)

    adds = pd.DataFrame(need_to_add)
    adds.to_csv('data/missing_alt_names.csv')
    
    return(print('names without matches written to a csv'))


# In[ ]:


# Check if there are any country names in the dataset currently in use which aren't listed as a possible 
# alternative specification in the country name mapping file, and create a list of new names to manually
# define a match for 

def parse_and_check_cleaned_names(tong_ctry, scen_ctry, coal_ctry, gas_ctry, steel_ctry):
    
    # Read the file with a two column list mapping the correct country names to all alternative specifications
    clean_country_mapping = pd.read_csv('data/accurate_cntry_name_mapping.csv', usecols = ['country.name.en', 'country.name.alt'])
    
    # Combine all these country names into a series, and remove any repeated items with drop_duplicates
    countries_in_data = pd.concat([tong_ctry['Country']] + [scen_ctry['country']] + [coal_ctry['Country']] + [gas_ctry['Country']] + [steel_ctry['Country']])
    strip_dups = countries_in_data.drop_duplicates(keep='first')
    
    # Now check if there are any values from this list of all country names which are not in the alternative specification
    # If they aren't already specified, output all of the unsepcified to a file
    # Then, open the file locally and manually specify whichever new and unmatched names have been used for countries
    
    # Initialize a list
    missing_specifications = []
    
    # For every name of a country in the data
    for alt_name in strip_dups:
        
        # See if this name maps to something proper, if not, add it to the list
        if alt_name not in clean_country_mapping['country.name.alt']:
            missing_specifications.append(alt_name)
    
    # Write the weird names of countries (from the list) not in the existing set of alternative possibilities to a df
    updated_alt_names = pd.DataFrame(missing_specifications)
    updated_alt_names.to_csv('data/upated_alt_names.csv')
    
#     # Then, throw an error if the list of alternative names is NOT empty, this implies there are 
#     # countries in the data which can't be cleanly mapped with the existing mapping file.
#     if len(missing_specifications) > 0:
#         print('Return to the countrynamefix.py check_missing_names_list() function and the modified country names file, you have some possible country name specifications which are not being mapped to an offical name') 
    
#     # Specify in the error exactly where to find and how to edit the country mapping manually
#     # in order to map all files, then re-run the function and if it still errors you didn't
#     # do it right.
#     print('re-run until no country names follow this text:', missing_specifications)
    
    print('manually corrected list of country names parsed')
    
    return(clean_country_mapping)


# In[ ]:


def export_cntry_data_fix(clean_country_mapping, tong_ctry, scen_ctry, coal_ctry, gas_ctry, steel_ctry):

    # try to replace the country names in each dataset with the country names suggested by the mapping
    tong_cntry_fix = clean_country_mapping.merge(tong_ctry, left_on = 'country.name.alt', right_on = 'Country', how = 'inner').drop(columns = ['country.name.alt', 'Country'])
    scen_cntry_fix = clean_country_mapping.merge(scen_ctry, left_on = 'country.name.alt', right_on = 'country', how = 'inner').drop(columns = ['country.name.alt', 'country'])
    coal_cntry_fix = clean_country_mapping.merge(coal_ctry, left_on = 'country.name.alt', right_on = 'Country', how = 'inner').drop(columns = ['country.name.alt', 'Country'])
    gas_cntry_fix = clean_country_mapping.merge(gas_ctry, left_on = 'country.name.alt', right_on = 'Country', how = 'inner').drop(columns = ['country.name.alt', 'Country'])
    steel_cntry_fix = clean_country_mapping.merge(steel_ctry, left_on = 'country.name.alt', right_on = 'Country', how = 'inner').drop(columns = ['country.name.alt', 'Country'])

    # write the data with cleaned country names to the appropriate file
    tong_cntry_fix.to_csv('data/tong_cntry_fix.csv')
    scen_cntry_fix.to_csv('data/scen_cntry_fix.csv')
    coal_cntry_fix.to_csv('data/coal_cntry_fix.csv')
    gas_cntry_fix.to_csv('data/gas_cntry_fix.csv')
    steel_cntry_fix.to_csv('data/steel_cntry_fix.csv')
    
    print('initial data inputs written to files with corrected country names')
    
    return(tong_cntry_fix, scen_cntry_fix, coal_cntry_fix, gas_cntry_fix, steel_cntry_fix)


# In[ ]:


def countrynamefix():
   
    # execute component functions in order
    tong_ctry, scen_ctry, coal_ctry, gas_ctry, steel_ctry = parse_raw_data()
    gen_missing_names_list(tong_ctry, scen_ctry, coal_ctry, gas_ctry, steel_ctry)
    clean_country_mapping = parse_and_check_cleaned_names(tong_ctry, scen_ctry, coal_ctry, gas_ctry, steel_ctry)
    tong_cntry_fix, scen_cntry_fix, coal_cntry_fix, gas_cntry_fix, steel_cntry_fix = export_cntry_data_fix(clean_country_mapping, tong_ctry, scen_ctry, coal_ctry, gas_ctry, steel_ctry)
    
    return(tong_cntry_fix, scen_cntry_fix, coal_cntry_fix, gas_cntry_fix, steel_cntry_fix)


# In[ ]:


if __name__ == "__main__":
    countrynamefix

