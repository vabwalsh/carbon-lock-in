#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# import libraries
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings('ignore')


# In[ ]:


#for each dataset, define a function which groups their columns by the plotting variables needed
def make_plot_vars(dataset, affectability_status):
    
    # decide on the plotting variables to creats
    commit_total_cols = []
    consid_total_cols = []
    comm_cons_cols = []
    consid_commit_scen_total_cols = []
    expectable = []
    yr_cols = []

    # append columns in the dataset to the appropriate group based on their name
    for col in dataset.columns:
        if 'commit.total.' in col:
            commit_total_cols.append(col)
        if 'consid.total.' in col:
            consid_total_cols.append(col)
        if 'commit+consid.' in col:
            comm_cons_cols.append(col)
        if 'commit+consid+scen.' in col:
            consid_commit_scen_total_cols.append(col)
        if 'expectable.' in col:
            expectable.append(col)
        if len(col) == 4:
            yr_cols.append(col)
            
    # set expectable emissions >= 0 in all cases, raw become 0 and affectable become abs(expectable)
    for col in dataset[expectable].columns:
        if affectability_status == 'raw':
            dataset[col][dataset[col] < 0] = 0
        elif affectability_status == 'affectable':
            dataset[col][dataset[col] < 0] = np.abs(dataset[col])

    # set considered emissions > 0, so that committed emissions always stack below them
    for col in dataset[consid_total_cols].columns:
        dataset[col][dataset[col] == 0] = 0.000001
    
    # return the newly grouped column lists, so that dataset[list_name] returns data corresponding the group
    return(commit_total_cols, consid_total_cols, comm_cons_cols, consid_commit_scen_total_cols, expectable, yr_cols)


# In[ ]:


# Specify the name of the file to operate on, a base title string which will name the figures and the plot files,
# and a filepath pointing to where the files should be saved.
def plot_data(dataset, affectability_status, title_str, sub_folder):
    
    # make the plotting variables for a dataset by calling the function defined above
    commit_total_cols, consid_total_cols, comm_cons_cols, consid_commit_scen_total_cols, expectable, yr_cols = make_plot_vars(dataset, affectability_status)
    
    X = np.arange(2021, 2101)
    
    for row in range(len(dataset)):
                
        plt.figure(figsize=(10,3))
        plt.tight_layout()
        plt.stackplot(X, 
                      dataset[commit_total_cols].loc[row],
                      dataset[consid_total_cols].loc[row], 
                      dataset[expectable].loc[row], 
                      labels=['Committed Emissions','Considered Emissions','Expectable'],
                      colors = ['firebrick', 'darksalmon', 'navajowhite'])
        
        plt.plot(X, dataset[commit_total_cols].loc[row], color = 'firebrick', linestyle = 'dashed')
        plt.plot(X, dataset[comm_cons_cols].loc[row], color = 'darksalmon', linestyle = 'dashed')
        
        if affectability_status == 'raw':
            plt.plot(X, dataset[yr_cols].loc[row], color = 'black', label = 'Scenario Emissions')
            
            for col in dataset[expectable].columns:
                plt.fill_between(X, dataset[yr_cols].loc[row], 0, 
                     where = dataset[yr_cols].loc[row] < 0, color = 'navajowhite')

        # specify the plot name to work for both expectation aggregated and singular scenario datasets
        if 'SSP' and 'RCP' in dataset.columns:
            if 'country' in dataset.columns:
                fig_name = str(dataset['country'].loc[row] + '_ ' 
                               + dataset['SSP'].loc[row] + ', RCP' 
                               + dataset['RCP'].loc[row] + title_str)
                plt.title(title_str + dataset['country'].loc[row] 
                          + ' _ ' + dataset['SSP'].loc[row] 
                          + ', RCP ' + dataset['RCP'].loc[row])
            elif 'country' not in dataset.columns and 'region' in dataset.columns:
                fig_name = str(dataset['region'].loc[row] + '_ ' 
                               + dataset['SSP'].loc[row] + ', RCP' 
                               + dataset['RCP'].loc[row] + title_str)
                plt.title(title_str + dataset['region'].loc[row] 
                          + ' _ ' + dataset['SSP'].loc[row] 
                          + ', RCP ' + dataset['RCP'].loc[row])
            elif 'country' not in dataset.columns and 'region' not in dataset.columns:
                fig_name = str('world' + '_ ' 
                           + dataset['SSP'].loc[row] + ', RCP' 
                           + dataset['RCP'].loc[row] + title_str)
                plt.title(title_str + 'world' 
                      + ' _ ' + dataset['SSP'].loc[row] 
                      + ', RCP ' + dataset['RCP'].loc[row])
                
        elif 'SSP' and 'RCP' not in dataset.columns:
            if 'country' in dataset.columns:
                fig_name = str(dataset['country'].loc[row] + title_str)
                plt.title(title_str + dataset['country'].loc[row])
            elif 'country' not in dataset.columns and 'region' in dataset.columns:
                fig_name = str(dataset['region'].loc[row] + title_str)
                plt.title(title_str + dataset['region'].loc[row])
            elif 'country' not in dataset.columns and 'region' not in dataset.columns:
                fig_name = str('world' + title_str)
                plt.title(title_str + 'world')
        
        else:
            print('broken plotting & title function!')

        plt.legend(loc='center left', bbox_to_anchor=(1, .8), fancybox=True, ncol=1)
        plt.xlabel('Year')
        plt.ylabel('CO2 Emissions (Mt)')
        plt.xlim(2022,2100)
        
        plt.savefig(sub_folder + str.replace(fig_name, ' ','') + '.jpeg', bbox_inches='tight')
        plt.close()


# In[ ]:


if __name__ == "__main__":
    plot_data
    make_plot_vars

