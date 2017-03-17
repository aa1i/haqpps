#!/usr/bin/python

#import Tkinter as Tk
from Tkinter import *

#root = Tk()
#
#w = Label(root, text="Hello, world!")
#w.pack()
#
#root.mainloop()


class App:

    def __init__(self, master):

        frame = Frame(master)
        Label(text="frame").pack()
        frame.pack()


        self.button = Button(
            frame, text="QUIT", fg="red", command=frame.quit
            )
        self.button.pack(side=LEFT)

        self.hi_there = Button(frame, text="Hello", command=self.say_hi)
        self.hi_there.pack(side=LEFT)

        self.test = Button(frame, text="Hello2", command=self.say_hi)
        self.test.pack(side=RIGHT)

        Button(frame, text="Show Inhib", command=self.show_inhib).pack(side=LEFT)

        self.inhib_period = IntVar()
        self.inhib_period.set(480)
        
        Radiobutton(frame, text="10", variable=self.inhib_period, value=10).pack(anchor=W)
        Radiobutton(frame, text="60", variable=self.inhib_period, value=60).pack(anchor=W)
        Radiobutton(frame, text="480", variable=self.inhib_period, value=480).pack(anchor=W)
        Radiobutton(frame, text="960", variable=self.inhib_period, value=960).pack(anchor=W)
                         
    def say_hi(self):
        print "hi there, everyone!"

    def show_inhib(self):
        print "inhib:" , self.inhib_period.get()

root = Tk()
root.wm_title("Hello, world!")

app = App(root)

root.mainloop()
#root.destroy() # optional; see description below
