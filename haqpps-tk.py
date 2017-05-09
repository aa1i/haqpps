#!/usr/bin/python

#import Tkinter as Tk
from tkinter import *
from tkinter import ttk

from time import sleep
import time

#import rate_day
#import rate_cumulative
#import pps_amp_filt
import subprocess
#import popen

class App:
    def __init__(self, master):

        # tk initialization
        self.frame = Frame(master)
        Label(text="frame label").pack()
        self.frame.pack()

        bottom_frame = ttk.Labelframe(master, text="Actions:")
        bottom_frame.pack(side=BOTTOM,fill="x")

        info_frame = ttk.Labelframe(master, text="Info:")
        info_frame.pack(side=TOP,anchor="w")

        watch_frame = Frame(info_frame)
        watch_frame.pack(side=TOP)

        inhib_frame = Frame(info_frame)
        inhib_frame.pack(side=LEFT)
        
        
        # bottom_frame elements
        Button(bottom_frame, text="QUIT", fg="red", command=self.quit).pack(side=LEFT)

        Button(bottom_frame, text="Hello", command=self.say_hi).pack(side=LEFT)

        self.test = ttk.Button(bottom_frame, text="Hello2", command=self.say_hi)
        self.test.config(state='disabled')
        self.test.pack(side=RIGHT)

        # watch scope buttons
        scope_frame = ttk.Labelframe(bottom_frame, text="Scope:")
        scope_frame.pack(side=LEFT)
        Button(scope_frame, text="Level Scope", command=self.wave_scope).pack(side=LEFT)
        Button(scope_frame, text="Kill Scope", command=self.wave_scope_kill).pack(side=LEFT)

        # measurement buttons
        measure_frame = ttk.Labelframe(bottom_frame, text="Measure:")
        measure_frame.pack(side=LEFT)
        self.measure_button = ttk.Button(measure_frame, text="Measure", command=self.measure)
        self.measure_button.config(state='enabled')
        self.measure_button.pack(side=TOP)
        Button(measure_frame, text="Kill Measure", command=self.measure_kill).pack(side=BOTTOM)

        # plot generating buttons
        plot_frame = ttk.Labelframe(bottom_frame, text="Plots:")
        plot_frame.pack(side=RIGHT)
        Button(plot_frame, text="Close Plots",     command=self.plot_kill).pack(side=RIGHT)   
        Button(plot_frame, text="Plot Cumulative", command=self.rate_cum_plot).pack(side=RIGHT)   
        Button(plot_frame, text="Plot Rate",       command=self.rate_plot).pack(side=RIGHT)
       
        #bottom_frame.pack(side=BOTTOM)

        # info_frame elements
        self.watch_name = StringVar()
        self.watch_name.set("Longines VHP PC Cal L1.627.3")
        Label( watch_frame, text="Watch: ").pack(side=LEFT)
        #Entry( watch_frame, textvariable=self.watch_name, width=30).pack(side=LEFT)
        watch_combo = ttk.Combobox( watch_frame, textvariable=self.watch_name, width=70)
        watch_combo['values']=( 'Longines VHP PC Cal L1.627.3',
            'Longines VHP Ti Cal 174.2 ETA 255.561',
            'Longines VHP Cal 174.2 ETA 255.561',
            'Chr.Ward C7 Rapide Chronograph Mk2 v390 / Chronometer (ETA 251.264 COSC)',
            'Certina DS-2 3-hand Precidrive ETA F06.411',
            'Citzen Alterna "02-Blue" V010-5984 Cal 0610?' )
        watch_combo.pack(side=LEFT)
        # name = self.watch_name.get()

        Button(watch_frame, text="Show Info", command=self.show_info).pack(side=RIGHT)

        self.inhib_period = IntVar()
        self.inhib_period.set(480)
        
        Label( inhib_frame, text="inhibition period (secs): ").pack(side=LEFT)
        Radiobutton(inhib_frame, text="10",  variable=self.inhib_period, value=10).pack(side=LEFT)
        Radiobutton(inhib_frame, text="60",  variable=self.inhib_period, value=60).pack(side=LEFT)
        Radiobutton(inhib_frame, text="480", variable=self.inhib_period, value=480).pack(side=LEFT)
        Radiobutton(inhib_frame, text="960", variable=self.inhib_period, value=960).pack(side=LEFT)

        # initialize sub-process lists
        self.subprocs=[]
        self.plot_subprocs=[]
        self.scope_subprocs=[]
        
    def say_hi(self):
        print ("hi there, everyone!")
        
    def show_info(self):
        print ("watch: " + self.watch_name.get())
        print ("inhib:" , self.inhib_period.get())

    # obsolete?
    def cancel(self):
        print ("cancel STUB")
        
    def rate_plot(self):
        print ("rate_plot START")
        proc = subprocess.Popen(["python","rate_day.py"])
        self.plot_subprocs.append( proc )
        print ("rate_plot return")
        
    def rate_cum_plot(self):
        print ("cumulative_rate_plot START")
        proc = subprocess.Popen(["python","rate_cumulative.py"])
        self.plot_subprocs.append( proc )
        print ("cumulative_rate_plot return")
        
    def plot_kill(self):
        print ("plot_kill")
        print ("Killing plot subprocs")
        for p in self.plot_subprocs:
            p.kill()
        print ("plot subprocs done.")
        self.plot_subprocs=[]

    def wave_scope(self):
        print ("wave_scope START")
        proc = subprocess.Popen(["python","pps-amp-filt.py"])
        print ("wave_scope return")
        self.scope_subprocs.append( proc )
        
    def wave_scope_kill(self):
        print ("wave_scope_kill")
        print ("Killing scope subprocs")
        for p in self.scope_subprocs:
            p.kill()
        print ("scope subprocs done.")
        self.scope_subprocs=[]
        

    def measure(self):
        self.measure_button.config(state='disabled')
        self.test.config(state='normal')
        print ("measure START")
        proc = subprocess.Popen(["python","haqpps.py"])
        print ("measure return")
        self.subprocs.append( proc )

    def measure_kill(self):
        print ("measure_kill")
        print ("Killing measure subprocs")
        for p in self.subprocs:
            p.kill()
        print ("measure subprocs done.")
        self.subprocs=[]
        self.test.config(state='disabled')
        self.measure_button.config(state='normal')

    def quit(self):
        self.plot_kill()
        self.wave_scope_kill()
        self.measure_kill()
        print ("Exiting.")
        self.frame.quit()
        
root = Tk()
root.wm_title("HAQ PPS Measurement")

app = App(root)

root.mainloop()
#root.destroy() # optional
