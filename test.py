import numpy as np
import pandas as pd
from varname import nameof

class logData:
    def __init__(self, input_data,name):
        self.rawData = input_data
        self.clData = []
        self.olData = []
        self.name = name

class Data:
    def __init__(self, params, log):
        self.data = {}
        for param in params: #params must be given as a list of strings, log corresponding Pandas Dataframe
            input_data = logfile[param].to_numpy() #get the raw data
            self.data[param] = logData(input_data, param) #should create a dictionary of names and values


log = "datalog17.csv" #this is a short file
logfile = pd.DataFrame(pd.read_csv(log, sep = ',', header = 0))#creates the logfile

params = ["Oil Temp (F)", "AF Learning 1 (%)"] #test values
data_set = Data(params, logfile)
print('printing raw data for oil temp to test')
print(data_set.data["Oil Temp (F)"].rawData)
locs = np.where(data_set.data["Oil Temp (F)"].rawData > 200)
for key in data_set.data.keys():
    data_set.data[key].clData = data_set.data[key].rawData[locs]

print(data_set.data["Oil Temp (F)"].clData)

#this works
