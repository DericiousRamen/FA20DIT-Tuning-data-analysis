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
import pyglet
import pickle
import time
from varname import nameof


 #stuff for creating and interactive gui. Mihgt not need threading
#data initialization
#should create a class to describe our custom data type requirements
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

class Button:#a button with some properties that are nice
    def __init__(self,x_box, y_box, button_width, button_height, color, batch, group, name, window_height, window_width,rel_loc,size,text_group):
        kwargs_box = {'x' :x_box, 'y' : y_box,'width':button_width, 'height' : button_height, 'color':color, 'batch': batch, 'group' : group}
        self.box = pyglet.shapes.Rectangle(**kwargs_box)
        self.box.opacity = 100
        label_kwargs = {'font_name': 'Monospace', 'font_size':(size/1080)*window_height, 'x' : window_width*.5,'y':window_height*rel_loc,
                    'anchor_x':'center', 'anchor_y':'center', 'batch':batch, 'group':text_group,'color':(0,0,0,255) }
        self.label = pyglet.text.Label(name, **label_kwargs)

def init():
    global logfile  #should be able to just create a bunch of logdata classes
    global data_set
    #get logfile name --> import file
    logs = []
    #make array of dataframes
    for file in glob.glob("*.csv"):
        temp = pd.DataFrame(pd.read_csv(file, sep = ',', header = 0))
        logs.append(temp)
    #now there are going to be different types of log files
    os.system('del *.pkl')
    #get rid of this thing
    #now we have two seperate lists, time to sort them into two seperate dataframes
    logfile = pd.concat(logs, ignore_index = True)          #--> without CL fueling switch
    #prune data to get only what is during warm engine operation
    oil_temp_cutoff = 180.0 #arbitary cutoff, could go higher
    oil_temp = logfile["Oil Temp (F)"].to_numpy()
    invalid_temp_locs = np.where(oil_temp < oil_temp_cutoff)
    logfile.drop(invalid_temp_locs[0], axis = 0,inplace = True)
    t = (len(logfile))*(1/15)#approximate dt
    if t > 60:
        print('logs represent approximately', t/60,' minutes')
    else:
        print('logs represent approximately ',t,' seconds' )

    #list of desired parameters
    desired_params = ["AF Learning 1 (%)", "AF Correction 1 (%)", "MAF Corr (g/s)",
                    "MAF Volts (V)", "Calculated Load (g/rev)", "Closed Loop Sw (on/off)",
                      "AF Sens 1 Ratio (AFR)", "Comm Fuel Final (AFR)",
                      "CL Fuel Target (AFR)", "Feedback Knock (�)",
                      "Gear Position (Gear)", "RPM (RPM)", "Dyn Adv Mult (DAM)"]
    params = logfile.columns.values.tolist()

    for param in desired_params:
        #check if in list
        if not (param in params):
            print(param+" is not in current logfile")
    #initialize CL data
    data_set = Data(desired_params, logfile)#get the data
    locs =np.where(data_set.data["Closed Loop Sw (on/off)"].rawData == 'on')
    for key in data_set.data.keys():
        data_set.data[key].clData = data_set.data[key].rawData[locs]
    #initialize OL data
    locs =np.where(data_set.data["Closed Loop Sw (on/off)"].rawData == 'off')
    for key in data_set.data.keys():
        data_set.data[key].olData = data_set.data[key].rawData[locs]
    #open and closed loop copies of everything
#need two threads for plotting/processing and managing gui
global logfile
global data_set

init()
window_width = 0
window_height = 0
button_pos = []

CL_args = [data_set.data["AF Learning 1 (%)"].clData, data_set.data["AF Correction 1 (%)"].clData,
                data_set.data["MAF Corr (g/s)"].clData, data_set.data["MAF Volts (V)"].clData, data_set.data["Calculated Load (g/rev)"].clData,
                data_set.data["Closed Loop Sw (on/off)"].rawData, data_set.data["AF Sens 1 Ratio (AFR)"].clData,
                 data_set.data["Comm Fuel Final (AFR)"].clData, data_set.data["CL Fuel Target (AFR)"].clData]
OL_args = [data_set.data["AF Sens 1 Ratio (AFR)"].olData, data_set.data["Comm Fuel Final (AFR)"].olData, data_set.data["MAF Corr (g/s)"].olData,
            data_set.data["MAF Volts (V)"].olData]
AF_args_raw =[data_set.data["AF Learning 1 (%)"].rawData, data_set.data["AF Correction 1 (%)"].rawData]
knock_args = [data_set.data["Feedback Knock (�)"].rawData, data_set.data["Gear Position (Gear)"].rawData,
                data_set.data["RPM (RPM)"].rawData, data_set.data["Calculated Load (g/rev)"].rawData,
                data_set.data["Dyn Adv Mult (DAM)"].rawData]

offset_CL = manipulations.CL_MAF_calibration(*CL_args)
offset_OL  = manipulations.OL_MAF_calibration(*OL_args)

calib_args = [data_set.data["AF Learning 1 (%)"].rawData, data_set.data["AF Correction 1 (%)"].rawData, offset_CL, offset_OL,
                data_set.data["Closed Loop Sw (on/off)"].rawData]
manipulations.MAF_calibration_interp(*calib_args)
manipulations.fuel_trim_distribution(*AF_args_raw)
manipulations.knock_3d(*knock_args)

def update_gui():

    global window_height, window_width, button_pos,button_width, button_height
    global running,lst,state
    window_width = 600
    window_height = 800
    window = pyglet.window.Window(width = window_width, height = window_height)
    window.config.alpha_size = 8
    batch = pyglet.graphics.Batch()
    bg = pyglet.graphics.OrderedGroup(0)
    fg = pyglet.graphics.OrderedGroup(1)
    top = pyglet.graphics.OrderedGroup(2)
    background = pyglet.shapes.Rectangle(x =0, y =0, width = window.width, height = window.height, color = (255,255,255), batch = batch, group = bg)
    background.opacity = 255

    button_width = 500
    button_height = 100
    center_box_x  = window.width*.5 -button_width//2
    #always plot this
    title = Button(center_box_x, window.height*.9-button_height//2, button_width, button_height,
            (128,128,128), batch, fg, "Logfile Data Viewer", window.height, window.width, .9, 50,top)
    title.box.opacity = 255


    #call this the main screen (i guess)
    button_pos = [.75,.6,.45,.3,.15]
    buttons = ["Closed Loop Plots", "Open Loop Plots", "Combined Plots", "Fuel Trim Distribution", "Plot of Knock events"]
    lst = [None]*5 #need to make this dummy list, we never reference them, so oh well
    for i in range(5):
        lst[i] =Button(center_box_x, window.height*button_pos[i]-button_height//2, button_width, button_height,
                (128,128,128), batch, fg, buttons[i], window.height, window.width, button_pos[i], 40,top)



    def redraw(): #update labels based off of state
        global state,lst
        if state == "main":
            labels =  ["Closed Loop Plots", "Open Loop Plots", "Combined Plots", "Fuel Trim Distribution", "Plot of Knock events"]
            for i in range(5):
                lst[i].label.text = labels[i]
        elif state == "CL Plots":
            labels = ["Fuel Trims vs Time", 'MAF Calibration Scatter', 'MAF offset Scatter', 'MAF offset avg', 'Back to Menu']
            for i in range(5):
                    lst[i].label.text = labels[i]
        elif state == "OL Plots":
            labels = ["MAF offset scatter", 'MAF Off set avg', '', '', 'Back to Menu']
            for i in range(5):
                    lst[i].label.text = labels[i]

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.O:
            pyglet.app.exit()

    @window.event
    def on_mouse_press(x,y,button,modifiers):
        global window_height, window_width, button_pos,button_width, button_height, state
        bounds = []
        for pos in button_pos:#find the bounds of the buttons, should move this to improve efficiency
            xbounds = []
            ybounds = []
            #lower bounds
            xbounds.append(window_width*.5-button_width//2)
            xbounds.append(window_width*.5+button_width//2)
            ybounds.append(window_height*pos-button_height//2)
            ybounds.append(window_height*pos+button_height//2)
            bounds.append([xbounds, ybounds])
        #this should generate bounds
        for i in range(len(bounds)):
            xmin = bounds[i][0][0]
            xmax = bounds[i][0][1]
            ymin = bounds[i][1][0]
            ymax = bounds[i][1][1]
            if (x < xmax and x > xmin )and(y < ymax and y > ymin):
                if state == "main":
                    if i == 0:
                        #go to CL plotting options
                        state = "CL Plots"
                    elif i==1:
                        state = "OL Plots"
                    elif i ==2:
                        #this shoudn't work
                        with open('MAF_corr.pkl','rb') as fid:
                            ax = pickle.load(fid)
                        plt.show()
                        print('print figure')
                    elif i == 3:
                        with open('fuel_dist.pkl','rb') as fid:
                            ax = pickle.load(fid)
                        plt.show()
                        print('print figure')
                    elif i == 4:
                        with open('knock.pkl','rb') as fid:
                            ax = pickle.load(fid)
                        plt.show()
                        print('print figure')
                elif state == "CL Plots":
                    if i == 0:
                        with open('CL_maf.pkl','rb') as fid:
                            ax = pickle.load(fid)
                        plt.show()
                        print('print figure')
                    elif i == 1:
                        with open('CL_maf.pkl','rb') as fid:
                            ax = pickle.load(fid)
                        plt.show()
                        print('print figure')
                    elif i == 2:
                        with open('CL_maf.pkl','rb') as fid:
                            ax = pickle.load(fid)
                        plt.show()
                        print('print figure')
                    elif i == 3:
                        with open('CL_maf.pkl','rb') as fid:
                            ax = pickle.load(fid)
                        plt.show()
                        print('print figure')
                    elif i == 4:
                        state = "main"
                elif state == "OL Plots":
                    if i == 0:
                        with open('OL_maf.pkl','rb') as fid:
                            ax = pickle.load(fid)
                        plt.show()
                        print('print figure')
                    elif i == 1:
                        with open('OL_maf.pkl','rb') as fid:
                            ax = pickle.load(fid)
                        plt.show()
                        print('print figure')
                    elif i == 2:
                        #with open('OL_maf.pkl','rb') as fid:
                        #    ax = pickle.load(fid)
                        #plt.show()
                        #print('print figure')
                        print('nothing to print')
                    elif i == 3:
                        #with open('OL_maf.pkl','rb') as fid:
                        #    ax = pickle.load(fid)
                        #plt.show()
                        #print('print figure')
                        print('nothing to print')
                    elif i == 4:
                        state = "main"

        print(state)
        redraw()

    def update(dt):
        global running,state

    pyglet.clock.schedule_interval(update, 1/30.)
    pyglet.app.run()


global state
plt.close('all')
print('press o to exit gui')
print('started graphics ')
state = "main"
update_gui()


#plotting_thread.join()
#this launches all the data manipulations
#offset_CL = manipulations.CL_MAF_calibration(AF_learning = AF_learning_CL, AF_corr = AF_corr_CL, MAF_Corr = MAF_Corr_CL,MAF_V =  MAF_V_CL,calc_load = calc_load_CL, CL_Sw = CL_Sw, AFR = AFR_CL, comm_AFR = comm_AFR_CL,CL_AFR =  CL_AFR_CL)
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
#offset_OL  = manipulations.OL_MAF_calibration(AFR_OL,comm_AFR_OL, MAF_Corr_OL, MAF_V_OL)
##find some nice interpolants of the final desired corrections
#manipulations.MAF_calibration_interp(AF_learning, AF_corr,offset_CL, offset_OL,CL_Sw)
#want to compute approximate distributions
#sort the data
#manipulations.fuel_trim_distribution(AF_learning, AF_corr)
#make a plot of knock w/ gear position vs RPM and load
#load all the values
#       --Feedback Knock (�)
#       --Gear Position (Gear)
#get rid of all entries where there is no knock
#manipulations.knock_3d(fb_knock, gear, RPM, load,DAM)

os.system('del *.pkl')
os.system('del *.pyo')
print("Press enter to end")
input()
