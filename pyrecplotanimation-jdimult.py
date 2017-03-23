"""
Using Pyaudio, record sound from the audio device and plot, for 8 seconds, and display it live in a Window.
Usage example: python pyrecplotanimation.py
Gerald Schuller, October 2014 
http://www.dk0tu.de/users/DL5BBN/Python_Amateur_Radio_Programs/
"""

import pyaudio
import struct
#import math
#import array
import numpy as np
#import sys
#import wave
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#import pylab
#import cv2

CHANNELS = 1 #2
#CHANNELS = 2
RATE = 192000  #Sampling Rate in Hz
#CHUNK = 192 * 1024 #Blocksize in samples, time basis for the display
#CHUNK = 192 * 1000 #Blocksize in samples, time basis for the display
CHUNK = RATE * CHANNELS #Blocksize in samples, time basis for the display
WIDTH = 2 #2 bytes per sample
RECORD_SECONDS = 10


fig, ax = plt.subplots()

#http://matplotlib.org/examples/pylab_examples/subplots_demo.html#pylab-examples-subplots-demo
# Two subplots, the axes array is 1-d
f, axarr = plt.subplots(2, sharex=True)
axarr[0].plot(x, y)
axarr[0].set_title('Sharing X axis')
axarr[1].scatter(x, y)

# http://matplotlib.org/examples/animation/subplots.html
fig = plt.figure()
ax1 = fig.add_subplot(1, 2, 1)
ax2 = fig.add_subplot(2, 2, 2)
ax3 = fig.add_subplot(2, 2, 4)

# http://jakevdp.github.io/blog/2012/08/18/matplotlib-animation-tutorial/
#fig = plt.figure()
#ax = plt.axes(xlim=(0, 2), ylim=(-2, 2))
#line, = ax.plot([], [], lw=2)

plt.ylabel('amplitude (a.u.)')
plt.xlabel('time (samples)')

#left_plot = plt.subplot(211)
#right_plot = plt.subplot(212)

x = np.arange(0, CHUNK)       # x-array
#x = np.arange(0, CHUNK) / CHUNK       # x-array

#Scale axis as this sine function:
line, = ax.plot(x, 20000.0*np.sin(x))
#line, = ax.plot(x, float(np.iinfo(np.int16).max)*np.sin(x))
#line, = ax.plot([-float(np.iinfo(np.int16).max), float(np.iinfo(np.int16).max)] )
#left_line,right_line = ax.plot(x, 20000.0*np.sin(x), x, 20000.0*np.sin(x))

plt.axis([0, RATE, -float(np.iinfo(np.int16).max), float(np.iinfo(np.int16).max)])

def animate(i):
    # update the data
    #Reading from audio input stream into data with block length "CHUNK":
    data = stream.read(CHUNK)
    #Convert from stream of bytes to a list of short integers (2 bytes here) in "samples":
    #shorts = (struct.unpack( "128h", data ))
    shorts = (struct.unpack( 'h' * CHUNK, data ));
    samples=np.array(list(shorts),dtype=float);

    #left_samples= samples[0::2]
    #right_samples= samples[1::2]
    
    #plt.plot(samples)  #<-- here goes the signal processing.
    #line.set_ydata(np.log((np.abs(pylab.fft(samples))+0.1))/np.log(10.0))
    line.set_ydata(samples)
    #line.set_ydata(left_samples)
    #left_line.set_ydata(left_samples)
    #right_line.set_ydata(right_samples)

    return line,
    #return left_line,right_line

def init():
    line.set_ydata(np.ma.array(x, mask=True))
    #left_line.set_ydata(np.ma.array(x, mask=True))
    #right_line.set_ydata(np.ma.array(x, mask=True))

    return line,
    #return left_line,right_line


p = pyaudio.PyAudio()

#a = p.get_device_count()
#print("device count=",a)

#for i in range(0, a):
 #   print("i = ",i)
 #   b = p.get_device_info_by_index(i)['maxInputChannels']
 #   print(b)
 #   b = p.get_device_info_by_index(i)['defaultSampleRate']
 #   print(b)

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                output=True,
                #input_device_index=3,
                frames_per_buffer=CHUNK)


print("* recording")

ani = animation.FuncAnimation(fig, animate, np.arange(1, 200), init_func=init,
    interval=25, blit=True)
plt.show()


# When everything done, release the capture

print("* done")

#f.close()
stream.stop_stream()
stream.close()
p.terminate()

