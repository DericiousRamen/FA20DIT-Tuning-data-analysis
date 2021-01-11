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
import threading

 #stuff for creating and interactive gui. Mihgt not need threading

#need two threads for plotting/processing and managing gui


#get logfile name --> import file
filenames = []
#make array of dataframes
for file in glob.glob("*.csv"):
    filenames.append(file)

#now there are going to be different types of log files
os.system('del  *.pkl')
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

t = (len(logfile))*(1/15)#approximate dt
if t > 60:
    print('logs represent approximately', t/60,' minutes')
else:
    print('logs represent approximately ',t,' seconds' )

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
fb_knock = logfile["Feedback Knock (�)"].to_numpy()
gear = logfile["Gear Position (Gear)"].to_numpy()
RPM = logfile["RPM (RPM)"].to_numpy()
load = logfile["Calculated Load (g/rev)"].to_numpy()
DAM = logfile["Dyn Adv Mult (DAM)"].to_numpy()

#initialize CL data
locs = np.where(CL_Sw == 'on')
AFR_CL= AFR[locs]
comm_AFR_CL =comm_AFR[locs]
MAF_Corr_CL = MAF_Corr[locs]
MAF_V_CL= MAF_V[locs]
calc_load_CL = calc_load[locs]
AF_learning_CL = AF_learning[locs]
AF_corr_CL = AF_corr[locs]
CL_AFR_CL = CL_AFR[locs]
#initialize OL data
locs = np.where(CL_Sw == 'off')
AFR_OL = AFR[locs]
comm_AFR_OL = comm_AFR[locs]
MAF_Corr_OL = MAF_Corr[locs]
MAF_V_OL = MAF_V[locs]
window_width = 0
window_height = 0
button_pos = []


offset_CL = manipulations.CL_MAF_calibration(AF_learning_CL, AF_corr_CL,  MAF_Corr_CL,MAF_V_CL, calc_load_CL, CL_Sw,  AFR_CL, comm_AFR_CL,  CL_AFR_CL)
offset_OL  = manipulations.OL_MAF_calibration(AFR_OL,comm_AFR_OL, MAF_Corr_OL, MAF_V_OL)
manipulations.MAF_calibration_interp(AF_learning, AF_corr,offset_CL, offset_OL,CL_Sw)
manipulations.fuel_trim_distribution(AF_learning, AF_corr)
manipulations.knock_3d(fb_knock, gear, RPM, load,DAM)
fig_CL_show = False
fig_OL_show = False
fig_cal_show = False
fig_fuel_show = False
fig_knock_show = False
running = True
def update_gui():
    global AFR_CL, comm_AFR_CL, MAF_Corr_CL, MAF_V_CL
    global calc_load_CL, AF_learning_CL, AF_corr_CL, CL_AFR_CL
    global AFR_OL, comm_AFR_OL, MAF_Corr_OL, MAF_V_OL
    global fig_CL_show, fig_OL_show, fig_cal_show, fig_fuel_show, fig_knock_show
    global window_height, window_width, button_pos,button_width, button_height
    global running
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

    #percentile position
    button_pos = [.75,.6,.45,.3,.15]
    button_width = 500
    button_height = 100
    kwargs_box = {'width':button_width, 'height' : button_height, 'color':(128,128,128), 'batch': batch, 'group' : fg}
    center_box_x  = window.width*.5 -button_width//2
    title_box = pyglet.shapes.Rectangle(x = center_box_x, y =window.height*.9-button_height//2,**kwargs_box)
    title_box.opacity = 255
    CL_box = pyglet.shapes.Rectangle(x =center_box_x, y = window.height*button_pos[0]-button_height//2, **kwargs_box)
    CL_box.opacity = 100
    OL_box = pyglet.shapes.Rectangle(x = center_box_x, y = window.height*button_pos[1]-button_height//2, **kwargs_box)
    OL_box.opacity = 100
    comb_box = pyglet.shapes.Rectangle(x =center_box_x, y = window.height*button_pos[2]-button_height//2, **kwargs_box)
    comb_box.opacity = 100
    trim_box = pyglet.shapes.Rectangle(x = center_box_x, y = window.height*button_pos[3]-button_height//2,**kwargs_box)
    trim_box.opacity = 100
    knock_box = pyglet.shapes.Rectangle(x = center_box_x, y = window.height*button_pos[4]- button_height//2,**kwargs_box)
    knock_box.opacity = 100

    title = pyglet.text.Label("Logfile Data Viewer", font_name='Monospace', font_size = (50/1080)*window.height, x =window.width*.5, y =window.height*.90,
            anchor_x = 'center', anchor_y = 'center', batch = batch, group = top,color = (0,0,0,255))
    label_kwargs = {'font_name': 'Monospace', 'font_size':(40/1080)*window.height, 'x' : window.width*.5, 'anchor_x':'center', 'anchor_y':'center', 'batch':batch, 'group':top,'color':(0,0,0,255) }
    CL_label = pyglet.text.Label("Closed Loop Plots",  y = window.height*button_pos[0],**label_kwargs)
    OL_label = pyglet.text.Label("Open Loop Plots",  y = window.height*button_pos[1],**label_kwargs)
    comb_label = pyglet.text.Label("Combined Plots", y= window.height*button_pos[2], **label_kwargs)
    trim_label = pyglet.text.Label("Fuel Trim Distribution", y = window.height*button_pos[3], **label_kwargs)
    knock_label = pyglet.text.Label("Plot of Knock events", y = window.height*button_pos[4], **label_kwargs)
    #comb_label = pyglet.text.Label("Combined CL/OL Plots", font_name = 'Monospace', font_size)

    @window.event
    def on_draw():
        window.clear()
        batch.draw()

    @window.event
    def on_key_press(symbol, modifiers):
        global running
        if symbol == pyglet.window.key.O:
            running = False
            pyglet.app.exit()

    @window.event
    def on_mouse_press(x,y,button,modifiers):
        global window_height, window_width, button_pos,button_width, button_height
        global fig_CL_show, fig_OL_show, fig_cal_show, fig_fuel_show, fig_knock_show
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
                if i == 0:
                    #CL plots
                    #need to use threading
                    fig_CL_show = True
                elif i==1:
                    fig_OL_show = True
                elif i ==2:
                    #this shoudn't work
                    fig_cal_show = True
                elif i == 3:
                    fig_fuel_show = True
                elif i == 4:
                    fig_knock_show= True

    def update(dt):
        global fig_CL_show, fig_OL_show, fig_cal_show, fig_fuel_show, fig_knock_show
        global running

    pyglet.clock.schedule_interval(update, 1/10.)
    pyglet.app.run()

def show_figs():
    global fig_CL_show, fig_OL_show, fig_cal_show, fig_fuel_show, fig_knock_show
    global fig_CL, fig_OL, fig_cal, fig_fuel, fig_knock
    global running

    while 1:
        time.sleep(.5)
        if fig_CL_show == True:
            with open('CL_maf.pkl','rb') as fid:
                ax = pickle.load(fid)
            plt.show()
            print('printing figure')
            fig_CL_show = False
        if fig_OL_show == True:
            with open('OL_maf.pkl','rb') as fid:
                ax = pickle.load(fid)
            plt.show()
            print('printing figure')
            fig_OL_show = False
        if fig_cal_show == True:
            with open('MAF_corr.pkl','rb') as fid:
                ax = pickle.load(fid)
            plt.show()
            print('printing figure')
            fig_cal_show = False
        if fig_fuel_show == True:
            with open('fuel_dist.pkl','rb') as fid:
                ax = pickle.load(fid)
            plt.show()
            print('printing figure')
            fig_fuel_show = False
        if fig_knock_show == True:
            with open('knock.pkl','rb') as fid:
                ax = pickle.load(fid)
            plt.show()
            print('printing figure')
            fig_knock_show= False
        if running == False:
            break

#plotting_thread = threading.Thread(target = show_figs, args = ())
if __name__ == '__main__':
    plt.close('all')
    print('press o to exit gui')
    graphics_thread = threading.Thread(target = update_gui, args = ())
    #plotting_thread.start()
    graphics_thread.start()
    print('started graphics thread')
    show_figs()
    print('started plotting  thread')
    #update_gui()

    graphics_thread.join()
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
