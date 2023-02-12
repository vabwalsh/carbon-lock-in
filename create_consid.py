#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import copy
import csv
import pandas as pd
import numpy as np


# In[ ]:


def createStream(capacity_data, asset_type, var, status, years = list(range(2021,2101))):
	considered = []
	header = []
	nrow = len(capacity_data)
	ncol = len(capacity_data[0])
	header.append('')
	header.append("country")
	considered.append(header)
	for i in range(2,len(years)+2):
		header.append(asset_type+'.'+status+'.'+str(years[i-2]))
	for i in range(1,nrow):
		temp = []
		temp.append(capacity_data[i][0])
		temp.append(capacity_data[i][1])
		for j in range(2,len(years)+2):
			temp.append(0)
		considered.append(temp)
	for i in range(0,len(years)):
		original_head = asset_type+'.'+var+'.'+status+'.'+str(years[i])
		if original_head in capacity_data[0]:
			index_o = capacity_data[0].index(original_head)
			if asset_type == 'gas':
				lifetime = 40
				annual_emissions = 1/12/lifetime
				for j in range(0,lifetime):
					lifetime_years = range(years[i],years[i]+lifetime)
					target_head = asset_type+'.'+status+'.'+str(lifetime_years[j])
					if target_head in considered[0]:
						index_t = considered[0].index(target_head)
						for k in range(1,nrow):
							considered[k][index_t] = considered[k][index_t] + float(capacity_data[k][index_o]) * annual_emissions
			if (asset_type == 'coal') & (var == 'MW'):
				lifetime = 40
				annual_emissions = 1/6/lifetime
				for j in range(0,lifetime):
					lifetime_years = range(years[i],years[i]+lifetime)
					target_head = asset_type+'.'+status+'.'+str(lifetime_years[j])
					if target_head in considered[0]:
						index_t = considered[0].index(target_head)
						for k in range(1,nrow):
							considered[k][index_t] = considered[k][index_t] + float(capacity_data[k][index_o]) * annual_emissions
			if (asset_type == 'coal') & (var == 'CO2'):
				lifetime = 40
				for j in range(0,lifetime):
					lifetime_years = range(years[i],years[i]+lifetime)
					target_head = asset_type+'.'+status+'.'+str(lifetime_years[j])
					if target_head in considered[0]:
						index_t = considered[0].index(target_head)
						for k in range(1,nrow):
							considered[k][index_t] = considered[k][index_t] + float(capacity_data[k][index_o])
			if asset_type == 'steel':
				lifetime = 40
				for j in range(0,lifetime):
					lifetime_years = range(years[i],years[i]+lifetime)
					target_head = asset_type+'.'+status+'.'+str(lifetime_years[j])
					if target_head in considered[0]:
						index_t = considered[0].index(target_head)
						for k in range(1,nrow):
							considered[k][index_t] = considered[k][index_t] + float(capacity_data[k][index_o])
	return considered


# In[ ]:


def merge(a_data, b_data):
	nrow_a = len(a_data)
	nrow_b = len(b_data)
	merged = []
	if nrow_a != nrow_b:
		if nrow_a < nrow_b:
			a_country = []
			b_country = []
			for i in range(1,nrow_a):
				a_country.append(a_data[i][1])
			for i in range(1,nrow_b):
				b_country.append(b_data[i][1])
			country_pre = list(set(a_country).union(b_country))
			country = copy.deepcopy(sorted(country_pre))
			ncol_a = len(a_data[0])
			ncol_b = len(b_data[0])
			merged.append(a_data[0]+b_data[0][2:])
			for i in range(0,len(country)):
				temp = []
				temp.append(i)
				temp.append(country[i])
				if (country[i] in a_country) & (country[i] in b_country):
					index_a = a_country.index(country[i])
					index_b = b_country.index(country[i])
					temp += (a_data[index_a+1][2:] + b_data[index_b+1][2:])
				elif country[i] in a_country:
					index_a = a_country.index(country[i])
					temp += (a_data[index_a+1][2:] + (['NA'] * (ncol_b-2)))
				elif country[i] in b_country:
					index_b = b_country.index(country[i])
					temp += ((['NA'] * (ncol_a-2)) + b_data[index_b+1][2:])
				merged.append(temp)
	else:
		ncol_a = len(a_data[0])
		ncol_b = len(b_data[0])
		for i in range(0,nrow_a):
			temp = []
			for j in range(0,ncol_a):
				temp.append(a_data[i][j])
			for j in range(2,ncol_b):
				temp.append(b_data[i][j])
			merged.append(temp)
	return merged


# In[ ]:


def slice(data, a, b):
	nrow = len(data)
	sliced = []
	for i in range(0,nrow):
		temp = []
		temp.append(data[i][0])
		temp.append(data[i][1])
		for j in range(a,b):
			temp.append(data[i][j])
		sliced.append(temp)
	return sliced


# In[ ]:


def mult(data, a, b):
	nrow = len(data)
	for i in range(1,nrow):
		for j in range(a,b):
			data[i][j] = 1.5 * data[i][j]
	multiplied = list(data)
	return multiplied


# In[ ]:


def mk_consid_commit():
    
    # hard code file import
    filename1="data/gas_panel_data.csv"
    filename2="data/coal_panel_data_CO2.csv"
    filename3="data/steel_panel_clean.csv"
    filename4="data/coal_panel_data_MW.csv"
    
    with open(filename1) as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        capacity_data_gas = [row for row in reader]
    with open(filename2) as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        capacity_data_coal = [row for row in reader]
    with open(filename3) as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        capacity_data_steel = [row for row in reader]
    with open(filename4) as fp:
        reader = csv.reader(fp, delimiter=",", quotechar='"')
        capacity_data_coal_MW = [row for row in reader]
    
    # actually aggregate
    gas_proposed = createStream(capacity_data_gas,"gas","cap","proposed")
    gas_construction = createStream(capacity_data_gas,"gas","cap","construction")
    gas_consid = merge(gas_proposed,gas_construction)

    gas_operating = createStream(capacity_data_gas,"gas","cap","operating",range(1937,2101))
    gas_committed = slice(gas_operating, 86, len(gas_operating[0]))

    coal_permitted = createStream(capacity_data_coal,"coal","CO2","permitted")
    coal_prepermit = createStream(capacity_data_coal,"coal","CO2","pre-permit")
    coal_announced =  createStream(capacity_data_coal,"coal","CO2","announced")
    coal_construction =  createStream(capacity_data_coal,"coal","CO2","construction")
    coal_permitted_MW = createStream(capacity_data_coal,"coal","MW","permitted")
    coal_prepermit_MW = createStream(capacity_data_coal,"coal","MW","pre-permit")
    coal_announced_MW =  createStream(capacity_data_coal,"coal","MW","announced")
    coal_construction_MW =  createStream(capacity_data_coal,"coal","MW","construction")


    coal = merge(coal_permitted,coal_prepermit)
    coal = merge(coal,coal_announced)
    coal = merge(coal,coal_construction)
    coal_MW = merge(coal_permitted_MW,coal_prepermit_MW)
    coal_MW = merge(coal_MW,coal_announced_MW)
    coal_MW = merge(coal_MW,coal_construction_MW)

    coal_operating = createStream(capacity_data_coal,"coal","CO2","operating",range(1937,2101))
    coal_operating_MW = createStream(capacity_data_coal_MW,"coal","MW","operating",range(1937,2101))
    coal_committed = slice(coal_operating, 86, len(coal_operating[0]))

    steel_proposed = createStream(capacity_data_steel,"steel","cap","proposed")
    steel_construction = createStream(capacity_data_steel,"steel","cap","construction")
    steel_consid = merge(steel_proposed,steel_construction)

    electricity_committed = merge(coal_committed,gas_committed)
    for i in range(0,len(electricity_committed[0])):
        electricity_committed[0][i] = electricity_committed[0][i].replace('operating','committed')

    otherindustry_proposed = copy.deepcopy(steel_proposed)
    for i in range(0,len(otherindustry_proposed[0])):
        otherindustry_proposed[0][i] = otherindustry_proposed[0][i].replace('steel','otherindustry')

    otherindustry_proposed_mult = mult(otherindustry_proposed, 2, len(otherindustry_proposed[0]))

    with open("data/gas-considered.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(gas_consid)
    with open("data/coal-considered.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(coal)
    with open("data/steel-considered.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(steel_proposed)
    with open("data/electricity_committed.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(electricity_committed)
    with open("data/otherindustry-considered.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(otherindustry_proposed_mult)
        
    return(gas_consid, coal, steel_proposed, electricity_committed, otherindustry_proposed_mult)


# In[ ]:


if __name__ == "__main__":
    mk_consid_commit

