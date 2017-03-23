#!/usr/bin/python

#import Tkinter as Tk
from Tkinter import *
import ttk

from time import sleep
import time

import threading


# busy thread for testing
class myThread (threading.Thread):
    exitFlag=0
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        print ("Starting " + self.name)
        self.print_time(self.name, self.counter, 30)
        print ("Exiting " + self.name)

    def print_time(self,threadName, delay, counter):
        while counter and not myThread.exitFlag:
            print ("%s: %s" % (threadName, time.ctime(time.time())))
            counter -= 1
            time.sleep(delay)

class measureThread (myThread):
    def print_time(self,threadName, delay, counter):
        while counter and not measureThread.exitFlag:
            print ("%s: %s" % (threadName, time.ctime(time.time())))
            counter -= 1
            time.sleep(delay)

class App:
    def __init__(self, master):

        # tk initialization
        self.frame = Frame(master)
        Label(text="frame").pack()
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

        Button(bottom_frame, text="Level Scope", command=self.wave_scope).pack(side=LEFT)
        Button(bottom_frame, text="Kill Scope", command=self.wave_scope_kill).pack(side=LEFT)
        
        Button(bottom_frame, text="Measure", command=self.measure).pack(side=LEFT)
        Button(bottom_frame, text="Kill Measure", command=self.measure_kill).pack(side=LEFT)

        Button(bottom_frame, text="Cancel", command=self.cancel).pack(side=RIGHT)
       
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

        # initialize threads
        self.threads=[]
        myThread.exitFlag=0
        measureThread.exitFlag=0
        self.measure_threads=[]
        
    def say_hi(self):
        print "hi there, everyone!"
        
    def show_info(self):
        print "watch: " + self.watch_name.get()
        print "inhib:" , self.inhib_period.get()

    def cancel(self):
        print "cancel STUB"
        
    def wave_scope(self):
        print "wave_scope START"
        myThread.exitFlag=0;
        thread1 = myThread(1, "WvScope-"+str(len(self.threads)+1), 1)
        thread1.start()
        self.threads.append(thread1)
        
    def wave_scope_kill(self):
        print "wave_scope_kill"
        myThread.exitFlag=1

        print ("Joining threads")
        for t in self.threads:
            t.join()
        print ("threads done.")
        self.threads=[]

    def measure(self):
        print "measure START"
        measureThread.exitFlag=0;
        thread1 = measureThread(1, "Measure-"+str(len(self.measure_threads)+1), 1)
        thread1.start()
        self.measure_threads.append(thread1)
        self.test.config(state='normal')

    def measure_kill(self):
        print "measure_kill"
        self.test.config(state='disabled')
        measureThread.exitFlag=1

        print ("Joining threads")
        for t in self.measure_threads:
            t.join()
        print ("threads done.")
        self.measure_threads=[]

    def quit(self):
        self.wave_scope_kill()
        self.measure_kill()
        print ("Exiting.")
        self.frame.quit()
        
root = Tk()
root.wm_title("HAQ PPS Measurement")

app = App(root)

root.mainloop()
#root.destroy() # optional; see description below
