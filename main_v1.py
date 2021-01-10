#This file now require the user to have the following parameters in their logfiles and will not run without them
#       AF Learning 1 (%)
#       AF Correction 1 (%)
#       AF Sens 1 Ratio (AFR)
#       CL Fuel Target (AFR)
#       Calculated Load (g/rev)
#       Comm Fuel Final (AFR)
#       Closed Loop Sw (on/off)
#       MAF Corr (g/s)
#       MAF Volt (V)
#       Oil Temp (F)
#       Feedback Knock (�)
#       Gear Position (gear)
#       RPM (RPM)

#should add some stuff using DAM next to filter the knock events more We do not want any DAM

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob, os
import manipulations


#get logfile name --> import file
filenames = []
#make array of dataframes
for file in glob.glob("*.csv"):
    filenames.append(file)

#now there are going to be different types of log files

logs = []
#get rid of this thing
for file in filenames:
    temp = pd.DataFrame(pd.read_csv(file, sep = ',', header = 0))

    logs.append(temp)

#now we have two seperate lists, time to sort them into two seperate dataframes
logfile = pd.concat(logs, ignore_index = True)          #--> without CL fueling switch

#prune data to get only what is during warm engine operation
oil_temp_cutoff = 180.0 #arbitary cutoff, could go higher
oil_temp = logfile["Oil Temp (F)"].to_numpy()

invalid_temp_locs = np.where(oil_temp < oil_temp_cutoff)

logfile.drop(invalid_temp_locs[0], axis = 0,inplace = True)

time = (len(logfile))*(1/15)#approximate dt
if time > 60:
    print('logs represent approximately', time/60,' minutes')
else:
    print('logs represent approximately ',time,' seconds' )


#list of desired parameters
desired_params = ["AF Learning 1 (%)", "AF Correction 1 (%)", "MAF Corr (g/s)", "MAF Volts (V)"]
params = logfile.columns.values.tolist()

for param in desired_params:
    #check if in list
    if not (param in params):
        print(param+" is not in current logfile")

AF_learning = logfile["AF Learning 1 (%)"].to_numpy()
AF_corr = logfile["AF Correction 1 (%)"].to_numpy()
MAF_Corr = logfile["MAF Corr (g/s)"].to_numpy()
MAF_V = logfile["MAF Volts (V)"].to_numpy()
calc_load = logfile["Calculated Load (g/rev)"].to_numpy()
CL_Sw = logfile["Closed Loop Sw (on/off)"].to_numpy() #this should contain strings
AFR = logfile["AF Sens 1 Ratio (AFR)"].to_numpy()
comm_AFR = logfile["Comm Fuel Final (AFR)"].to_numpy()
CL_AFR = logfile["CL Fuel Target (AFR)"].to_numpy()

locs = np.where(CL_Sw == 'on')

AFR_CL= AFR[locs]
comm_AFR_CL =comm_AFR[locs]
MAF_Corr_CL = MAF_Corr[locs]
MAF_V_CL= MAF_V[locs]
calc_load_CL = calc_load[locs]
AF_learning_CL = AF_learning[locs]
AF_corr_CL = AF_corr[locs]
CL_AFR_CL = CL_AFR[locs]



offset_CL = manipulations.CL_MAF_calibration(AF_learning = AF_learning_CL, AF_corr = AF_corr_CL, MAF_Corr = MAF_Corr_CL,MAF_V =  MAF_V_CL,calc_load = calc_load_CL, CL_Sw = CL_Sw, AFR = AFR_CL, comm_AFR = comm_AFR_CL,CL_AFR =  CL_AFR_CL)
#new MAF correction is old maf corr*offsets at certain voltages
#need more data to be less noisy. This is not smooth and would result in less noise
#for open loop operation adjust MAF against MAF voltage against the wideband O2 (AFR) vs ECU target AFR (Comm fuel final)
#       MAF Corr (g/s)
#       MAF Volt (V)
#       AF Sens 1 Ratio (AFR)
#       Comm Fuel Final (AFR)
#       Calculated Load (g/rev)
#***this is only applicable in open loop fueling regions (  (1) high load situations, (2) open loop aggressive start)

#need to perform the same zeroing nonsense as before
locs = np.where(CL_Sw == 'off')
AFR_OL = AFR[locs]
comm_AFR_OL = comm_AFR[locs]
MAF_Corr_OL = MAF_Corr[locs]
MAF_V_OL = MAF_V[locs]

offset_OL  = manipulations.OL_MAF_calibration(AFR_OL,comm_AFR_OL, MAF_Corr_OL, MAF_V_OL)

print(offset_CL)
print(offset_OL)
##find some nice interpolants of the final desired corrections
manipulations.MAF_calibration_interp(AF_learning, AF_corr,offset_CL, offset_OL,CL_Sw)


#want to compute approximate distributions
#sort the data
manipulations.fuel_trim_distribution(AF_learning, AF_corr)

#make a plot of knock w/ gear position vs RPM and load
#load all the values
#       --Feedback Knock (�)
#       --Gear Position (Gear)

fb_knock = logfile["Feedback Knock (�)"].to_numpy()
gear = logfile["Gear Position (Gear)"].to_numpy()
RPM = logfile["RPM (RPM)"].to_numpy()
load = logfile["Calculated Load (g/rev)"].to_numpy()
DAM = logfile["Dyn Adv Mult (DAM)"].to_numpy()

#get rid of all entries where there is no knock
manipulations.knock_3d(fb_knock, gear, RPM, load,DAM)
