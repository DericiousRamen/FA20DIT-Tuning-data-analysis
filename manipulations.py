import numpy as np
import matplotlib.pyplot as plt


#computes and displays relevant MAF correction given the input data
def CL_MAF_calibration(AF_learning, AF_corr, MAF_Corr, MAF_V, calc_load, CL_Sw, AFR, comm_AFR, CL_AFR):
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

    return offsets
#compute open loop calibrations
def OL_MAF_calibration(AFR, comm_AFR, MAF_Corr, MAF_V):
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

    return avg_offsets
def MAF_calibration_interp(AF_learning, AF_corr, offsets, avg_offsets,CL_Sw):
    p1 = np.polyfit(offsets[:,0], offsets[:,1],3)
    min = np.minimum(offsets[0,0], avg_offsets[0,0])
    max = np.maximum(offsets[len(offsets)-1,0], avg_offsets[len(avg_offsets)-1,0])
    p2 = np.polyfit(avg_offsets[:,0], avg_offsets[:,1],3)

    x = np.arange(min,max,.01)

    # % time in closed loop
    in_CL_per = (np.size(np.where(CL_Sw == 'on')))/(len(CL_Sw))

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
def fuel_trim_distribution(AF_learning, AF_corr):
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
def knock_3d(fb_knock, gear, RPM , load, DAM):

    locs = np.where(fb_knock < -2.) #large signal relative
    loc_DAM = np.where(DAM < 1.) #also want to find where DAM is low triggered

    locs_DAM_filtered = []
    for loc in np.array(loc_DAM[0]): #need to do this weird filter to DAM

        if DAM[loc-1] > DAM[loc]: #DAM drop
            locs_DAM_filtered.append((range(loc-10,loc+10)))#take some frame
    locs_DAM_filtered = np.array(locs_DAM_filtered)
    locs = np.append(locs, locs_DAM_filtered)
    fb_knock = fb_knock[locs]
    gear = gear[locs]
    RPM = RPM[locs]
    load = load[locs ]
    #this filter still isn't good enough. Mainly because if there is knock when DAM is returning, we only care about knock that causes DAM to drop

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
            ax.scatter(xs= sorted_rpm[i], ys = sorted_load[i], zs = sorted_knock[i], s = 4, color = color(i))

        ax.set_xlabel('RPM')
        ax.set_ylabel('Calculated Load (g/rev)')
        ax.set_zlabel('Feedback Knock')
        plt.title('Knock vs RPM and Load')
        plt.show()
