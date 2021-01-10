import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob, os


#get logfile name --> import file
filenames = []
#make array of dataframes
for file in glob.glob("*.csv"):
    filenames.append(file)

#now there are going to be different types of log files

logs = []
logs_with_CL_sw = []
 for file in filenames:
    temp = pd.DataFrame(pd.read_csv(file, sep = ',', header = 0))
    #need to check if the temp dataframe has the entry "Closed Loop Sw (on/off)"
    #print("Closed Loop Sw (on/off)" in temp.columns.values.tolist())       -->this works
    if ("Closed Loop Sw (on/off)" in temp.columns.values.tolist()): #to new log list
        logs_with_CL_sw.append(temp)
    else: #to original loglist
        logs.append(temp)

#now we have two seperate lists, time to sort them into two seperate dataframes
logfile = pd.concat(logs, ignore_index = True)          #--> without CL fueling switch
logfile_with_CL_sw = pd.concat(logs_with_CL_sw, ignore_index= True)        #--> with CL fueling switch
AF_learning_1 = pd.DataFrame(pd.read_csv("AF_learning_1.csv", sep = ',', header = None))


#prune data to get only what is during warm engine operation
oil_temp_cutoff = 180.0 #arbitary cutoff, could go higher
oil_temp = logfile["Oil Temp (F)"].to_numpy()
oil_temp_CL = logfile_with_CL_sw["Oil Temp (F)"].to_numpy()

invalid_temp_locs = np.where(oil_temp < oil_temp_cutoff)
invalid_temp_locs_CL = np.where(oil_temp_CL < oil_temp_cutoff)

logfile.drop(invalid_temp_locs[0], axis = 0,inplace = True)
logfile_with_CL_sw.drop(invalid_temp_locs_CL[0], axis = 0, inplace = True)

time = (len(logfile)+ len(logfile_with_CL_sw))*(1/15)#approximate dt
if time > 60:
    print('logs represent approximately', time/60,' minutes')
else:
    print('logs represent approximately ',time,' seconds' )
#print(logfile["Closed Loop Sw (on/off)"])
#print(df.values[:,1])
#print(logfile.columns.values.tolist()) #---> returns full list of parameters

#to check if a parameter is in the logfile ----> print("AF Learning 1 (%)" in logfile.columns.values.tolist())


#to pull a single column --> print(logfile["Time (sec)"])
#                            print(logfile["AF Learning 1 (%)"])
#                            print(logfile["AF Correction 1 (%)"])

#need the following for some stuff: (case and space sensitive for searches)
#       AF Learning 1 (%)
#       AF Correction 1 (%)
#       Time (sec)
#       AF Sens 1 Ratio (AFR)
#       CL Fuel Target (AFR)
#       Calculated Load (g/rev)
#       Comm Fuel Final (AFR)
#       Fuel Mode (mode)
#       Inj Duty Cycle (%)
#       MAF Corr (g/s)
#       MAF Volt (V)


#for closed loop operation compare MAF ratios vs MAF voltage against the corrected fuel trim total the sum of AF Learning and AF correction
#       AF Learning 1 (%)
#       AF Correction 1 (%)
#       MAF Corr (g/s)
#       MAF Volt (V)

#stuff for closed loop operation
#list of desired parameters
desired_params = ["AF Learning 1 (%)", "AF Correction 1 (%)", "MAF Corr (g/s)", "MAF Volt (V)"]
params = logfile.columns.values.tolist()

for param in desired_params:
    #check if in list
    if not (param in params):
        print(param+" is not in current logfile")

AF_learning = logfile["AF Learning 1 (%)"].to_numpy()
AF_corr = logfile["AF Correction 1 (%)"].to_numpy()
MAF_Corr = logfile["MAF Corr (g/s)"].to_numpy()
MAF_V = logfile["MAF Volt (V)"].to_numpy()
calc_load = logfile["Calculated Load (g/rev)"].to_numpy()

#don't need to correct these, just need to load in "Closed Loop Sw (on/off)"
AF_learning_with_CL = logfile_with_CL_sw["AF Learning 1 (%)"].to_numpy()
AF_corr_with_CL = logfile_with_CL_sw["AF Correction 1 (%)"].to_numpy()
MAF_Corr_with_CL = logfile_with_CL_sw["MAF Corr (g/s)"].to_numpy()
MAF_V_with_CL = logfile_with_CL_sw["MAF Volts (V)"].to_numpy()
CL_Sw = logfile_with_CL_sw["Closed Loop Sw (on/off)"].to_numpy() #this should contain strings

AFR = logfile["AF Sens 1 Ratio (AFR)"].to_numpy()
AFR_with_CL = logfile_with_CL_sw["AF Sens 1 Ratio (AFR)"].to_numpy()
comm_AFR = logfile["Comm Fuel Final (AFR)"].to_numpy()
comm_AFR_with_CL = logfile_with_CL_sw["Comm Fuel Final (AFR)"].to_numpy()
CL_AFR = logfile["CL Fuel Target (AFR)"].to_numpy()
CL_AFR_with_CL = logfile_with_CL_sw["CL Fuel Target (AFR)"].to_numpy()

load_val_critical = AF_learning_1[3].to_numpy()

locs = np.where(calc_load <= load_val_critical)
AFR= AFR[locs]
comm_AFR =comm_AFR[locs]
MAF_Corr = MAF_Corr[locs]
MAF_V = MAF_V[locs]
AF_learning = AF_learning[locs]
AF_corr = AF_corr[locs]
CL_AFR = CL_AFR[locs]

locs = np.where(CL_Sw == 'on')
AF_learning_with_CL = AF_learning_with_CL[locs]
AF_corr_with_CL = AF_corr_with_CL[locs]
AFR_with_CL = AFR_with_CL[locs]
comm_AFR_with_CL = comm_AFR_with_CL[locs]
MAF_Corr_with_CL = MAF_Corr_with_CL[locs]
MAF_V_with_CL = MAF_V_with_CL[locs]
CL_AFR_with_CL = CL_AFR_with_CL[locs]


AF_learning = np.append(AF_learning,AF_learning_with_CL)
AF_corr = np.append(AF_corr,AF_corr_with_CL)
MAF_Corr= np.append(MAF_Corr, MAF_Corr_with_CL)
MAF_V= np.append(MAF_V, MAF_V_with_CL)
AFR = np.append(AFR, AFR_with_CL)
comm_AFR = np.append(comm_AFR, comm_AFR_with_CL)
CL_AFR = np.append(CL_AFR,CL_AFR_with_CL)


total_fuel_trim = AF_learning + AF_corr

fig, axs = plt.subplots(2,2)
#plot1= plt.figure(1)
axs[0,0].plot(AF_learning, label = 'AF Learning')
axs[0,0].plot(AF_corr, label = 'AF Correction')
axs[0,0].plot(total_fuel_trim, label = 'fuel trim (%)')
axs[0,0].set(ylabel='fuel trim')
axs[0,0].legend()
axs[0,0].set_title("AF ratios vs time")


#plot2= plt.figure(2)
axs[0,1].scatter(MAF_V, MAF_Corr, s=.05, alpha = .3)
axs[0,1].set(xlabel = "MAF Voltage",ylabel='MAF (g/s)')
axs[0,1].set_title('MAF calibrations')

#it would be interesting to compare closed loop fuel targets vs actual AFR
# axs[2,1].scatter(AFR,comm_AFR, s = .05, alpha = .4)
# axs[2,1].plot([11,15],[11,15])
# axs[2,1].set_title('Commanded AFR vs actual')
# axs[2,1].set(xlabel = 'Actual AFR', ylabel = 'Commanded AFR')
# axs[2,1].axis('scaled')
# axs[2,1].set(ylim = (11,15))
#
# axs[2,0].scatter(AFR,CL_AFR, s= 0.05, alpha = .4)
# axs[2,0].plot([11,15],[11,15])
# axs[2,0].set_title('Actual AFR vs CL Fuel Target')
# axs[2,0].set(xlabel='Actaul AFR', ylabel = 'CL Fuel Target')
# axs[2,0].axis('scaled')
# axs[2,0].set(ylim=(11,15))



#need to correlate average change to MAF based on the fuel trim
#print(MAF_V)
#print(total_fuel_trim)
#find = np.where(MAF_V == .96)
#plot3 = plt.figure(3)
axs[1,0].scatter(MAF_V, total_fuel_trim, s = .05, alpha = .3)
axs[1,0].set(xlabel = 'MAF Voltage',ylabel="fuel trim (%)")
axs[1,0].set_title('MAF voltage vs fuel trim')


maf_correction_new =np.array([MAF_V, total_fuel_trim])
#print(maf_correction_new)
#print(np.sort(maf_correction_new))
maf_correction_new = maf_correction_new[:,maf_correction_new[0,:].argsort()] #sort the data
#print(maf_correction_new)
#need to find averages for each item
offsets = [] #stored in voltage average pairs
prev_val = 0.
count = 1
avg = 0
for i in range(len(MAF_V)):
    #print(avg, prev_val, maf_correction_new[1,i], maf_correction_new[0,i],i)
    #print(prev_val == maf_correction_new[0,i])
    if prev_val == maf_correction_new[0,i]:
        #add to running sum
        avg = avg + maf_correction_new[1,i]

        count = count + 1
    else:
        #new sum
        avg = avg/count     #compute true average
        offsets.append([prev_val,avg])
        #update values
        prev_val = maf_correction_new[0,i]
        count = 1
        avg =maf_correction_new[1,i];
offsets.remove([0,0])
#print(offsets)
offsets = np.array(offsets)
#plot4 = plt.figure(4)
axs[1,1].plot(offsets[:,0],offsets[:,1])
axs[1,1].set(xlabel='MAF Voltage', ylabel = 'offset (%)')
axs[1,1].set_title("Desired Offsets")
plt.show()

#new MAF correction is old maf corr*offsets at certain voltages
#need more data to be less noisy. This is not smooth and would result in less noise




#for open loop operation adjust MAF against MAF voltage against the wideband O2 (AFR) vs ECU target AFR (Comm fuel final)
#       MAF Corr (g/s)
#       MAF Volt (V)
#       AF Sens 1 Ratio (AFR)
#       Comm Fuel Final (AFR)
#       Calculated Load (g/rev)
#***this is only applicable in open loop fueling regions (  (1) high load situations, (2) open loop aggressive start)



desired_params = []
desired_params = ["AF Sens 1 Ratio (AFR)", "Comm Fuel Final (AFR)", "MAF Corr (g/s)", "MAF Volt (V)", "Calculated Load (g/rev)"]
params = logfile.columns.values.tolist()

for param in desired_params:
    #check if in list
    if not (param in params):
        print(param+" is not in current logfile")

AFR = logfile["AF Sens 1 Ratio (AFR)"].to_numpy()
comm_AFR = logfile["Comm Fuel Final (AFR)"].to_numpy()
MAF_Corr = logfile["MAF Corr (g/s)"].to_numpy()
MAF_V = logfile["MAF Volt (V)"].to_numpy()
calc_load = logfile["Calculated Load (g/rev)"].to_numpy()

#don't need to correct these, just need to load in "Closed Loop Sw (on/off)"
AFR_with_CL = logfile_with_CL_sw["AF Sens 1 Ratio (AFR)"].to_numpy()
comm_AFR_with_CL = logfile_with_CL_sw["Comm Fuel Final (AFR)"].to_numpy()
MAF_Corr_with_CL = logfile_with_CL_sw["MAF Corr (g/s)"].to_numpy()
MAF_V_with_CL = logfile_with_CL_sw["MAF Volts (V)"].to_numpy()
CL_Sw = logfile_with_CL_sw["Closed Loop Sw (on/off)"].to_numpy() #this should contain strings


#we want to filter the results where load is in the open loop fueling **
#need to pull actual data
load_val_critical = AF_learning_1[3].to_numpy()
#AFR = np.where(calc_load >= load_val_critical, AFR)      #zeros out where load is high
#comm_AFR = np.where(calc_load >= load_val_critical, comm_AFR)
#MAF_Corr = np.where(calc_load >= load_val_critical, MAF_Corr)
#MAF_V = np.where(calc_load >= load_val_critical, MAF_V)
locs = np.where(calc_load >= load_val_critical)
AFR= AFR[locs]
comm_AFR =comm_AFR[locs]
MAF_Corr = MAF_Corr[locs]
MAF_V = MAF_V[locs]

#need to perform the same zeroing nonsense as before
locs_with_CL = np.where(CL_Sw == 'off')
#AFR_with_CL = np.where(CL_Sw == 'off', AFR_with_CL)
#comm_AFR_with_CL = np.where(CL_Sw == 'off', comm_AFR_with_CL)
#MAF_Corr_with_CL = np.where(CL_Sw == 'off', MAF_Corr_with_CL)
#MAF_V_with_CL = np.where(CL_Sw == 'off', MAF_V_with_CL)
AFR_with_CL = AFR_with_CL[locs_with_CL]
comm_AFR_with_CL = comm_AFR_with_CL[locs_with_CL]
MAF_Corr_with_CL = MAF_Corr_with_CL[locs_with_CL]
MAF_V_with_CL = MAF_V_with_CL[locs_with_CL]
#don't zero out the comm_AFR because this will cause a weird divide by zero error
#now append them together

AFR= np.append(AFR,AFR_with_CL)
comm_AFR = np.append(comm_AFR,comm_AFR_with_CL)
MAF_Corr= np.append(MAF_Corr, MAF_Corr_with_CL)
MAF_V= np.append(MAF_V, MAF_V_with_CL)

#now also need to parse the data for tip-in effects

dAFR = np.divide(AFR,comm_AFR) #compute the ratio to find the multiplier for the change required to MAF


fig, axs = plt.subplots(2,2)
axs[0,0].plot(dAFR)
axs[0,0].set(xlabel = 'time', ylabel='Desired MAF correction (%)')
axs[0,0].set_title('Desired MAF correction vs time')


axs[1,0].scatter(MAF_V, dAFR, s = .05, alpha = .3)
axs[1,0].set(xlabel = 'MAF Voltage (V)', ylabel = 'Desired change (%)')
axs[1,0].set_title('Desired MAF change raw')


maf_v_dafr = np.array([MAF_V, dAFR])
#print(maf_v_dafr)
maf_v_dafr = maf_v_dafr[:,maf_v_dafr[0,:].argsort()] #sort the data

avg_offsets = [] #stored in voltage average pairs
prev_val = 0.
count = 1
avg = 0
for i in range(len(MAF_V)):
    #print(avg, prev_val, maf_correction_new[1,i], maf_correction_new[0,i],i)
    #print(prev_val == maf_correction_new[0,i])
    if prev_val == maf_v_dafr[0,i]:
        #add to running sum
        avg = avg + maf_v_dafr[1,i]

        count = count + 1
    else:
        #new sum
        avg = avg/count     #compute true average
        avg_offsets.append([prev_val,avg])
        #update values
        prev_val = maf_v_dafr[0,i]
        count = 1
        avg =maf_v_dafr[1,i];
avg_offsets.remove([0,0])
avg_offsets = np.array(avg_offsets)
#print(avg_offsets)
axs[0,1].plot(avg_offsets[:,0],avg_offsets[:,1])
axs[0,1].set(xlabel="MAF Voltage", ylabel= 'MAF offset (&)')
axs[0,1].set_title('MAF Correction multiplier for open loop fueling')
#this is meaningless
#axs[1,1].plot(comm_AFR,label= 'Commanded AFR')
#axs[1,1].plot(AFR, label = 'Actual AFR')
#axs[1,1].set_title('AFR comparison')
#axs[1,1].legend()
#axs[1,1].set(xlabel = 'time', ylabel = 'AFR')
plt.show()

##find some nice interpolants of the final desired corrections
AF_learning = logfile["AF Learning 1 (%)"].to_numpy()
AF_corr = logfile["AF Correction 1 (%)"].to_numpy()
AF_learning =np.append(AF_learning, logfile_with_CL_sw["AF Learning 1 (%)"].to_numpy())
AF_corr =np.append(AF_corr, logfile_with_CL_sw["AF Correction 1 (%)"].to_numpy())

p1 = np.polyfit(offsets[:,0], offsets[:,1],3)
min = np.minimum(offsets[0,0], avg_offsets[0,0])
max = np.maximum(offsets[len(offsets)-1,0], avg_offsets[len(avg_offsets)-1,0])
p2 = np.polyfit(avg_offsets[:,0], avg_offsets[:,1],3)

x = np.arange(min,max,.01)

# % time in closed loop
in_CL_per = (np.size(np.where(calc_load <= load_val_critical)) + np.size(np.where(CL_Sw == 'on')))/(len(calc_load) + len(CL_Sw))

print('Closed loop fueling for ',(100*in_CL_per),'% of the time')
y1 = np.polyval(p1,x)
y2 = np.polyval(p2,x)
y3 = in_CL_per*y1 + (1-in_CL_per)*y2

plt.plot(x, y1,label = 'Closed Loop Polyfit')
plt.plot(x,y2, label = 'Open Loop Polyfit')
plt.plot(x,y3, label = 'Average Polyfit')
plt.plot(offsets[:,0], offsets[:,1], label = 'Closed Loop Data')
plt.plot(avg_offsets[:,0], avg_offsets[:,1], label = 'Open Loop Data')
plt.xlabel('MAF Voltage(V)')
plt.ylabel('Desired (%) change')
plt.legend()
plt.title('Combined desired MAF (%) change')
plt.grid()
plt.show()

#want to compute approximate distributions
#sort the data
trim = AF_learning + AF_corr
trim = np.sort(trim) #sort the combined trims
avg = np.sum(trim)/len(trim)
#print(avg)
frequencies = {}
for x in trim:
    if x in frequencies:
        frequencies[x] += 1
    else:
        frequencies[x] = 1
#frequencies = np.array(frequencies.items())
values = frequencies.keys()
freqs = frequencies.values()

#weighted sum of square of distances
var = 0
total = len(trim)
for key in frequencies.keys():
    freq = frequencies[key] #find the number
    var += ((avg - key)**2)*(freq/total)
print(np.sqrt(var))
var = np.sqrt(var)
#plt.plot(AF_learning, label = "AF Learning (%)")
#plt.plot(AF_corr, label = "AF Correction (%)")

plt.bar(values, freqs)
plt.bar(avg,[5000], color = 'red', label = 'Mean',width = .3)
plt.bar([avg-var, avg+var], [500,500], color = 'green', label = 'variance',width = .3)
plt.bar([avg-2*var, avg+2*var], [300,300], color = 'orange', label = '2*variance',width = .3)
plt.bar([avg-3*var, avg+3*var], [200,200], color = 'pink', label = '3*variance',width = .3)
plt.legend()
plt.xlabel('Correction (%)')
plt.ylabel('Frequency')
plt.title("Distribution of combined fuel trim")
plt.show()



#make a plot of knock w/ gear position vs RPM and load
#load all the values
#       --Feedback Knock (�)
#       --Gear Position (Gear)

fb_knock = logfile["Feedback Knock (�)"].to_numpy()
gear = logfile["Gear Position (Gear)"].to_numpy()
RPM = logfile["RPM (RPM)"].to_numpy()
load = logfile["Calculated Load (g/rev)"].to_numpy()
fb_knock = np.append(fb_knock, logfile_with_CL_sw["Feedback Knock (�)"].to_numpy())
gear = np.append(gear, logfile_with_CL_sw["Gear Position (Gear)"].to_numpy())
RPM = np.append(RPM, logfile_with_CL_sw["RPM (RPM)"].to_numpy())
load = np.append(load, logfile_with_CL_sw["Calculated Load (g/rev)"].to_numpy())
#loaded all the values

#get rid of all entries where there is no knock
locs = np.where(fb_knock != 0.)
fb_knock = fb_knock[locs]
gear = gear[locs]
RPM = RPM[locs]
load = load[locs]
if fb_knock.size == 0:
    print('there is no knock')
else:
    def color(p):
        if (p == 1):
            return 'blue'
        elif (p==2):
            return 'red'
        elif (p==3):
            return 'green'
        elif (p==4):
            return 'orange'
        elif (p==5):
            return 'pink'
        elif (p==6):
            return 'purple'

    #plot the remaining things
    #print(fb_knock)
    #need to sort into subarrays
    sorted_knock = []
    sorted_rpm = []
    sorted_load = []
    for i in range(6): #because six gears
        locs = np.where(gear == i)
        sorted_knock.append(fb_knock[locs])
        sorted_rpm.append(RPM[locs])
        sorted_load.append(load[locs])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    #better plotting routine!!
    for i in range(6):
        ax.scatter(xs= sorted_rpm[i], ys = sorted_load[i], zs = sorted_knock[i], s = .5, color = color(i))

    plt.title('3d knock plot, if empty, no knock')
    plt.show()
