''' code for class task which gives environmental flows
given the delineated watershed, precipitation data, discharge data '''

from datetime import date
from copy import deepcopy
import pandas as pd
from scipy.io import loadmat
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor, VotingRegressor, BaggingRegressor


def get_data(discharge_df, basin_num, basin_daily_precipitation_mat, basin_mat_delineated, flag):
    
    precipitation_start_date = date(1901, 1, 1)
    discharge_start_date = discharge_df['Date'][0].date()
    
    temp_l = len(discharge_df['Date']) - 1
    discharge_end_date = discharge_df['Date'][temp_l].date()
    
    x_start = (discharge_start_date - precipitation_start_date).days
    x_end = (discharge_end_date - precipitation_start_date).days + 1

    basin_daily_precipitation_mat = basin_daily_precipitation_mat.reshape(-1, basin_daily_precipitation_mat.shape[2])
    basin_mat_delineated = basin_mat_delineated.reshape(-1)
    
    # Create a mask array and select only those cells that belong to the given watershed
    # Watershed here is defined by the basin_num 
    mask_array = (basin_mat_delineated == basin_num)
    masked_data = basin_daily_precipitation_mat[mask_array, x_start:x_end].T
    
    if flag:
        masked_data = masked_data * 0.93

    only_discharges = np.array(discharge_df['Discharge'].tolist())
    return masked_data, only_discharges

def get_this_years_low_flow(l, d):
    llen = len(l)
    num_iter = llen - d + 1
    low_flow_d_days = []
    for i in range(num_iter):
        temp = sum([l[j] for j in range(i, i+d)])/d
        low_flow_d_days.append(temp)
    return min(low_flow_d_days)

def gather_dqt_plot(ip_type, discharge_df, years_list, num_days, num_years, file_name):

    low_flow_list = []

    for year in years_list:
        this_year_data = discharge_df[discharge_df["Year"] == year]

        if ip_type == 0:
            this_year_discharge = this_year_data['Discharge']
        elif ip_type == 1:
            # predicted discharge for this year
            this_year_discharge = this_year_data['New_Discharge']
        l = this_year_discharge.to_list()
        low_flow_list.append([get_this_years_low_flow(l, num_days), year])

    # sort according to discharge value since the rank given will
    # be based on the discharge value
    low_flow_list = sorted(low_flow_list, key=lambda x: x[0])

    for i in range(len(low_flow_list)):
        P = (i + 1) / (num_years + 1)
        T = 1 / P
        low_flow_list[i].append(P)
        low_flow_list[i].append(T)

    low_flow_list = np.array(low_flow_list)

    c = 'b'
    if ip_type == 1:
        c = 'r'

    plt.scatter(low_flow_list[:, 2], low_flow_list[:, 0], c=c)
    plt.plot(low_flow_list[:, 2], low_flow_list[:, 0], c='g')
    plt.xlabel('Probability', fontsize=16)
    plt.ylabel('Minimum Flow', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.title('DQT Plot for D = '+str(num_days)+', T = '+str(num_years), fontsize=20)
    plt.savefig(file_name)

def get_flow(precip_file, delineated_file, discharge_file, D, T, file_name_b4_reg, file_name_after_reg):

    # give precipitation data and delineated watershed data as input
    # inputs should be .mat only
    precip_mat = loadmat(precip_file)['basin_daily_precipitation']
    basin_mat_delineated = loadmat(delineated_file)['basin_mat_delineated']
    print(basin_mat_delineated.shape)

    # read discharge data as .xls input
    discharge_df = pd.ExcelFile(discharge_file)
    discharge_df = discharge_df.parse(0)
    discharge_df = discharge_df.fillna(0) # Replace the nan values with 0's

    all_datetimes = discharge_df['Date']
    all_years = list(map(lambda datetime_obj: int(datetime_obj.date().strftime("%Y")), all_datetimes))
    years_list = list(set(all_years))
    
    discharge_df["Year"] = all_years

    # num days is D and num_years is T in the DQT format
    # D,T are USER INPUTS
    num_days = int(D)
    num_years = int(T)

    gather_dqt_plot(0, discharge_df, years_list, num_days, num_years, file_name_b4_reg)

    basin_num = 5
    reg1 = RandomForestRegressor(n_estimators=100, random_state=42)
    reg4 = BaggingRegressor(n_estimators=100, random_state=50)
    voting_reg = VotingRegressor([('br', reg4), ('rf', reg1)])

    X, y = get_data(discharge_df, basin_num, precip_mat, basin_mat_delineated, False)
    voting_reg.fit(X, y)

    new_discharge_df = deepcopy(discharge_df)
    new_discharge_df = new_discharge_df[(new_discharge_df["Year"] >= years_list[0]) & (new_discharge_df["Year"] <= years_list[-1])]
    print(len(discharge_df['Year']), len(new_discharge_df["Year"]))

    X, y = get_data(new_discharge_df, basin_num, precip_mat, basin_mat_delineated, True)
    y_pred = voting_reg.predict(X)
    new_discharge_df["New_Discharge"] = y_pred

    gather_dqt_plot(1, new_discharge_df, years_list, num_days, num_years, file_name_after_reg)
