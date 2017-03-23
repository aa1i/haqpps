"""
Using Pyaudio, record sound from the audio device and display it live in a Window.
Usage example: python pyrecplotanimation.py
Gerald Schuller, October 2014 
http://www.dk0tu.de/users/DL5BBN/Python_Amateur_Radio_Programs/

Modified extensively 2016/Apr-May by John Isham (aa1i) <isham.john@gmail.com>
"""

import pyaudio
#import struct
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

CHANNELS = 2
RATE = 192000  #Sampling Rate in Hz
CHUNK = RATE   #Blocksize in samples, time basis for the display
WIDTH = 2      #2 bytes per sample



x = np.arange(0, RATE) * 1000  / RATE      # x-array


# http://stackoverflow.com/questions/29832055/animated-subplots-using-matplotlib
# create a figure with two subplots
#fig, (ax1, ax2) = plt.subplots(2,1)
fig, (ax1, ax2) = plt.subplots(2,sharex=True)

fig.canvas.set_window_title('PPS Amplitude')
fig.suptitle('Waveform Scope')

# intialize two line objects (one in each axes)
line1, = ax1.plot([], [], lw=2)
line2, = ax2.plot([], [], lw=2, color='r')
line = [line1, line2]

for ax in [ax1, ax2]:
    ax.set_ylim(-1.0, 1.0)
    ax.set_xlim(0, 1000)
    ax.grid(True)
    ax.set_xlabel('Time (msec)')
    
ax1.set_ylabel('Stepper Pulse')
ax2.set_ylabel('PPS Reference')

#ax1.set_title('axis 1 title')
#ax2.set_title('axis 2 title')


def animate(i):
    # update the data
    #Reading from audio input stream into data with block length "CHUNK":
    data = stream.read(CHUNK)

    #Convert from stream of bytes to a list of short integers (2 bytes here) in "samples":
    #shorts = (struct.unpack( "128h", data ))
    #shorts = (struct.unpack( 'h' * CHUNK*2, data ));
    #samples=np.array(list(shorts),dtype=float);
    # decode/deinterleave soundard samples
    decoded = np.fromstring(data,"Int16")
    # Normalize by int16 max (32767) for convenience, also converts everything to floats
    normed_samples = decoded / float(np.iinfo(np.int16).max)

    left_samples = normed_samples[0::2]
    right_samples = normed_samples[1::2]

    line1.set_data(x,left_samples)
    line2.set_data(x,right_samples)

    return line

def init():
    line1, = ax1.plot([], [], lw=2)
    line2, = ax2.plot([], [], lw=2, color='r')

    return line


p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(WIDTH),
                channels=CHANNELS,
                rate=RATE,
                input=True,
                #output=True,
                #input_device_index=3,
                frames_per_buffer=CHUNK)


print("* recording")

#try:

ani = animation.FuncAnimation(fig, animate, init_func=init, interval=25, blit=True)
plt.show()

#except KeyboardInterrupt: 
#    print "Caught KeyboardInterrupt" 
#    raise
#except IOError:
#    print "Caught IOError" 
#    raise
    
# When everything done, release the capture

print("* done")

#f.close()
plt.close()
stream.stop_stream()
stream.close()
p.terminate()

quit()
