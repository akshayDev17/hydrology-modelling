''' this module is used for watershed delineation '''

import math
from copy import deepcopy

import numpy as np
import pandas as pd

from osgeo import gdal
from scipy.io import loadmat, savemat

def get_delineated_watershed(dem_data, basin_data, tif_data, discharge_file, output_fname):

    dem = loadmat(dem_data)['DEM_filled']
    INCR_ROW, INCR_COL = [0, 1, 1, 1, -1, -1, -1, 0], [1, 0, -1, 1, -1, 1, 0, -1]
    D8_SIZE = 8
    NUM_ROWS, NUM_COLS = dem.shape[0], dem.shape[1]

    def is_inside(row, col):
        ''' check if the cell (row,col) is a valid cell or not'''
        if row < NUM_ROWS and row >= 0 and col < NUM_COLS and col >= 0:
            return True
        else:
            return False

    # load the basin, latitude-longitude limits, 
    # precipitation .mats , these are to be custom inputs
    basin_mat = loadmat(basin_data)['rev_new']

    flow_grid = np.ones((NUM_ROWS, NUM_COLS))*-1
    prev = -1
    for r in range(NUM_ROWS):
        if prev == -1:
            prev = (r/NUM_ROWS) * 100
            print("%d%% processing done" % (prev))
        else:
            curr = (r/NUM_ROWS) * 100
            if curr - prev >= 1 :
                print("%d%% processing done" % (curr))
                prev = curr
        for c in range(NUM_COLS):
            ''' iterate through each grid of DEM data'''
            if math.isnan(dem[r, c]) :
                continue

            max_flow = -1
            for i in range(D8_SIZE):
                new_r, new_c = r + INCR_ROW[i], c + INCR_COL[i]
                if is_inside(new_r, new_c):
                    cur_flow = (dem[r, c] - dem[new_r, new_c])/ math.sqrt(INCR_ROW[i]**2 + INCR_COL[i]**2)
                    if cur_flow >= max_flow:
                        max_flow = cur_flow
                        if max_flow > 0:
                            flow_grid[r, c] = i
                        else:
                            flow_grid[r, c] = -2
            if max_flow == -1:
                flow_grid[r, c] = -1
        
    # save the flow grid as a CSV file
    np.savetxt('flow_dir.csv', flow_grid, delimiter=',')

    # read the discharge location as a csv file, CUSTOM INPUT
    disch_loc = pd.read_csv(discharge_file)

    # get the latitude and longitude limits from the .tif file
    # the tif file is supposed to be USER INPUT
    ds = gdal.Open(tif_data)
    width = ds.RasterXSize
    height = ds.RasterYSize
    gt = ds.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width*gt[4] + height*gt[5] 
    maxx = gt[0] + width*gt[1] + height*gt[2]
    maxy = gt[3]

    longitude_range, latitude_range = np.linspace(minx, maxx, NUM_COLS), np.linspace(miny, maxy, NUM_ROWS)

    def locate_sink(lat, long): 
        ''' locate sinks manually '''
        temp = 25

        x = deepcopy(dem[lat-temp:lat+temp, long-temp:long+temp])
        y = deepcopy(flow_grid[lat-temp:lat+temp, long-temp:long+temp])

        d_lat, d_long = np.where(y == -2)
        a = [(d_lat[i], d_long[i]) for i in range(len(d_lat))]

        
        min_alt = x[temp, temp]
        for i in a:
            if min_alt >= x[i] and not math.isnan(x[i]):
                min_alt = x[i]
        m_lat, m_long = np.where(x == min_alt)
        b = [(m_lat[i], m_long[i]) for i in range(len(m_lat))]
        
        c = [np.asarray(i) for i in list(set(a).intersection(b))]
        #c = [np.asarray(i) for i in list(set(a))]
        if len(c) > 0:
            return [tuple(i + np.array([-temp+lat, -temp + long])) for i in c]
        else:
            return [(lat, long)]


    sink_list = []
    for index, row in disch_loc.iterrows():
        curr_lat, curr_long = row['latitude'], row['longitude']
        lat_row = (np.abs(latitude_range - curr_lat)).argmin()
        long_col = (np.abs(longitude_range - curr_long)).argmin()
        sink_list.append(locate_sink(lat_row, long_col))


    # Initialization of Visited Array and Watershed data for performing a DFS
    visited = np.zeros((NUM_ROWS, NUM_COLS))
    watershed = np.zeros((NUM_ROWS, NUM_COLS))

    def DFS(curr_row, curr_col, index):
        visited[curr_row, curr_col] = 1
        watershed[curr_row, curr_col] = index
        for i in range(D8_SIZE):
            new_row, new_col = curr_row + INCR_ROW[i], curr_col + INCR_COL[i]
            if is_inside(new_row, new_col):
                # If the water flows from the new cell to the this cell
                if (flow_grid[new_row, new_col] == 7 - i or flow_grid[new_row, new_col] == -2) and visited[new_row, new_col] == 0:
                    DFS(new_row, new_col, index)

    # iterate through all sink locations, backtracking for each of them to the highest point. 
    for i, sink_list in enumerate(sink_list):
        for start_node in sink_list:
            try:
                DFS(start_node[0], start_node[1], i+1 )
            except RecursionError as re:
                print("Could not compute for (%d, %d)" % (start_node[0], start_node[1]))

    # store the delineated watershed
    basin_mat_x, basin_mat_y = basin_mat.shape[0], basin_mat.shape[1]
    basin_mat_delineated = np.zeros((basin_mat_x, basin_mat_y))
    for r in range(basin_mat.shape[0]):
        for c in range(basin_mat.shape[1]):
            # Resolution of basin files is 0.25 and that of dem file
            # is 0.0083. Thus, one cell in basin is equivalent to
            # 30 cells of the DEM file.
            top, bottom = r * 30, (r + 1) * 30
            left, right = c * 30, (c + 1) * 30

            # Get the corresponding indexes in dem file
            cell_group = watershed[top:bottom, left:right]

            if cell_group.size:
                # Find the most common watershed in given cells
                values, counts = np.unique(cell_group, return_counts=True) 
                ind = np.argmax(counts)
                # Assign the most common watershed in DEM to the corresponding cell in basin
                basin_mat_delineated[r, c] = values[ind]

    savemat(output_fname, {
        'basin_mat_delineated': basin_mat_delineated
    })