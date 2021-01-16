For background information on this project and this repository as a whole, please read this post.( https://www.reddit.com/r/WRX/comments/ku077y/been_working_on_tuning_my_own_car/ ) Also, this project is in development as of now
and there will be more work done on it. I plan to post regularly as I work on this and post updates on the r/WRX subreddit. This repo may not always be up to date and I make no promises that this software will help you at all. Use
this at your own risk. I highly recommend reading up on the COBB support website before making any changes to your particular tune here: https://cobbtuning.atlassian.net/wiki/spaces/PRS/pages/28705206/SUBARU+ACCESSTUNER+SUPPORT.



To use this program in its current state (1/16/2020), we must have the following file structure and make the following modifications to the raw log files. First, we must have the following file structure

./(program directory)
---./Datalogs     (path containing folders with datalogs)
    ---./ver_xx       (versions of your tune)

---./main_vxx.py
---./manipulations.py (all the python code)
OR
---./main_v2.exe (compiled executable)

Right now, when the program is launched, it will prompt you to put in which folder to get the log files from and will also
display the different folders found in the datalog folders (at least on windows, no other compatability right now). Just type
in the name of the folder and it should work. For example, if you have different folders such as './ver_1', './ver_2', etc... and you wanted to look at data for version 2, then just type in 'ver_2' and it will load the corresponding data. 

Finally, for now we also have to make the following change to the first line of every csv file. In the first line, it will have
all of the different parameters that we are tracking in file and we need to put a space between the ',' and 'AP' in the last
entry to tell the pandas library to exclude that column. it should be something like this

Before editing:

Time (sec),AF Correction 1 (%),... (other things),Throttle Pos (%),Wastegate Duty (%),AP Info:[AP3-SUB-004 v1.7.4.0-17408][2018 USDM WRX MT COBB Custom Features Gen1][Reflash: advanced_timing.ptm - Realtime: advanced_timing.ptm]

After editing:
                                                                                    **|** note this space
Time (sec),AF Correction 1 (%),... (other things),Throttle Pos (%),Wastegate Duty (%), AP Info:[AP3-SUB-004 v1.7.4.0-17408][2018 USDM WRX MT COBB Custom Features Gen1][Reflash: advanced_timing.ptm - Realtime: advanced_timing.ptm]

As of now, this project is either CLI python script with the functions discussed in the original reddit post or as an executable. I'll update this more when this is more developed and I have time.
