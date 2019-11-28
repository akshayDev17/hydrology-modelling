''' code for class task which gives predicted discharge
given the delineated watershed, precipitation data, discharge data '''

import pandas as pd
from scipy.io import loadmat
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor, VotingRegressor, BaggingRegressor

from assignment_3 import get_data

def rainfall_runoff(precip_file, delineated_file, discharge_file, plot_fname):
    # give precipitation data and delineated watershed data as input
    # inputs should be .mat only
    precip_mat = loadmat(precip_file)['basin_daily_precipitation']
    basin_mat_delineated = loadmat(delineated_file)['basin_mat_delineated']

    # read discharge data as .xls input
    discharge_df = pd.ExcelFile(discharge_file)
    discharge_df = discharge_df.parse(0)
    discharge_df = discharge_df.fillna(0) # Replace the nan values with 0's

    basin_num = 5
    reg1 = RandomForestRegressor(n_estimators=100, random_state=42)
    reg4 = BaggingRegressor(n_estimators=100, random_state=50)
    voting_reg = VotingRegressor([('br', reg4), ('rf', reg1)])

    X, y = get_data(discharge_df, basin_num, precip_mat, basin_mat_delineated, False)
    voting_reg.fit(X, y)

    y_pred = voting_reg.predict(X)

    plt.scatter(y_pred, y_pred - y, c='r')
    plt.title("Runoff prediction data using a voting-regressor")
    plt.xlabel("Predicted Output")
    plt.ylabel("Error in prediction")
    print(plot_fname)
    plt.savefig(plot_fname)