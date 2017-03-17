
# (C) 2015 John Isham <isham.john@gmail.com>
# All rights reserved
# free for non-commercial use
# please report any fixes or improvements back to me
# free for use as a tool to regulate watches as a hobby or commerically, but
# this software cannot be sold or incorporated into a commercial product
# without my written authorization

# some help from
#https://gist.githubusercontent.com/Jach/6361147/raw/c91a311f9d3e83bb11d2d3f65457650e9b624965/audio_trigger.py
'''
Requires PyAudio and Numpy.

Windows users:
win32 Python 2.7: http://www.python.org/ftp/python/2.7.3/python-2.7.3.msi
Numpy: http://sourceforge.net/projects/numpy/files/NumPy/1.7.1/numpy-1.7.1-win32-superpack-python2.7.exe/download
PyAudio: http://people.csail.mit.edu/hubert/pyaudio/packages/pyaudio-0.2.7.py27.exe
'''
import pyaudio
import wave
import numpy
import math

#from __future__ import print_function
import sys

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 192000
RECORD_SECONDS = 15
#WAVE_OUTPUT_FILENAME = "output.wav"
#INHIBITION=10
#INHIBITION=60 
INHIBITION=480

VERBOSE=0

left_channel = 0
right_channel = 1

# window to flag a missed pulse - 1.05 seconds, in integer samples
MISSED_PULSE = 105 * RATE / 100

p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

print("* recording")

#frames = []

left_max=0.0  # Watch Under Test
right_max=0.0 # PPS

sample_count = 0

first_right=0
first_left=0

right_count=0
left_count=0

last_right=0
last_left=0
TRIGGER_WIDTH=RATE/4

left_thresh=0.5
right_thresh=0.5

#avg_rate=float(RATE)
avg_rate=192004.388773 # from a previous run

tickfile=open('ticks.txt','w')
offsfile=open('offset.txt','w',1) # line buffered

sw_avg=[]
last_offset=0.0
last_offset_sample=0
  
#for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
while True:
  try:
    data = stream.read(CHUNK)

    # append to output file
    #frames.append(data)

    # decode/deinterleave soundard samples
    decoded = numpy.fromstring(data,"Int16")
    # Normalize by int16 max (32767) for convenience, also converts everything to floats
    normed_samples = decoded / float(numpy.iinfo(numpy.int16).max)

    left_samples = normed_samples[left_channel::2]
    right_samples = normed_samples[right_channel::2]

    # track maximum amplitude per channel
    tmp=max(abs(j) for j in left_samples)
    left_max = max(left_max, tmp)

    tmp=max(abs(j) for j in right_samples)
    right_max=max(right_max ,tmp)

    # detect pulses
    # we can probable replace sample_num with right below,
    # but since we use the same index for the left/tic data,
    # sample_num is more straightforward
    sample_num = 0
    for right  in  right_samples:
        # look for PPS reference pulses on right channel
        if (abs(right_samples[sample_num]) > right_thresh):
          if ((0 == last_right) or (sample_count -last_right > TRIGGER_WIDTH)):
              if 0 == first_right:
                  first_right=sample_count
              if VERBOSE >= 2:
                  print '{0:09d} {1:f} PPS {2:7d} {3:f}'.format(
                      sample_count,float(sample_count)/avg_rate,
                      sample_count-last_right,float(sample_count-last_right)/avg_rate)
              sys.stdout.write( '{0:09d} {1:f} PPS {2:7d} {3:f}\r'.format(
                sample_count,float(sample_count)/avg_rate,
                sample_count-last_right,float(sample_count-last_right)/avg_rate))
              sys.stdout.flush()
              last_right= sample_count               
              right_count+=1
              # update sample rate referenced to PPS pulses
              if right_count >= 10:
                 avg_rate=float(last_right-first_right)/float(right_count-1)
        # look for watch 'tics' on left channel
        if (abs(left_samples[sample_num]) > left_thresh):
          if ((0 == last_left) or (sample_count -last_left > TRIGGER_WIDTH)):
              if 0 == first_left:
                  first_left=sample_count
              cur_clock=float(sample_count)/avg_rate

              # check for missing PPS pulse
              if sample_count - last_right > MISSED_PULSE:
                  print '{0:09d} {1:f} PPS REFERENCE UNLOCK'.format(
                      sample_count,cur_clock)
                  # TODO - reset counters/stats!!
                  sw_avg=[]
                  last_right=0
                  first_right=0
                  right_count=0
              else:
                 offset=float(sample_count-last_right)/avg_rate
                 # normalize/un-wrap to +- 0.5 second from reference pulse
                 if offset > 0.5:
                   offset=offset-1.0
                 if offset < MISSED_PULSE:
                     if VERBOSE >=1:
                         print '{0:09d} {1:f} tic {2:7d} {3:f}'.format(
                             sample_count,cur_clock,
                             sample_count-last_right,offset)
                     sys.stdout.write('{0:09d} {1:f} tic {2:7d} {3:f}\r'.format(
                             sample_count,cur_clock,
                             sample_count-last_right,offset))
                     sys.stdout.flush()
                     # log tick data to file
                     tickfile.write('{0:09d} {1:f} tic {2:7d} {3:f}\n'.format(
                         sample_count,cur_clock,
                         sample_count-last_right,offset))

                     # sliding window average over inhibition period
                     sw_avg.append(offset)
                     if INHIBITION == len(sw_avg):
                         avg_offset=math.fsum(sw_avg)/float(INHIBITION)
                         print '{0:09d} {1:f} offset {2:f}'.format(
                             sample_count,cur_clock,avg_offset)
                         offsfile.write('{0:09d} {1:f} offset {2:f}\n'.format(
                             sample_count,cur_clock,avg_offset))
                         sw_avg=[]
                         # primitive rate calc based on last two inihibition periods only
                         # better results will be obtained from linear fit to more offset data over longer timebase
                         if last_offset_sample > 0:
                             rate=float(avg_offset-last_offset)*avg_rate/float(sample_count-last_offset_sample)
                             print '{0:09d} {1:f} rate {2:e} spd {3:f} spy {4:f}'.format(
                                 sample_count, cur_clock, rate, rate*86400.0, rate*86400.0*365.0)
                         last_offset_sample=sample_count
                         last_offset=avg_offset
              last_left= sample_count               
              left_count+=1
        sample_num+=1
        sample_count+=1


  except KeyboardInterrupt: 
      print "Caught KeyboardInterrupt" 
      break;
  except IOError:
      print "Caught IOError" 
      break;

print ("* done recording")

stream.stop_stream()
stream.close()
p.terminate()

tickfile.close()
offsfile.close()

print
print "Avg rate:",avg_rate
print "PPS count:",right_count
print "tic count:",left_count
print "max PPS ampl:",right_max
print "max tic ampl:",left_max

#wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
#wf.setnchannels(CHANNELS)
#wf.setsampwidth(p.get_sample_size(FORMAT))
#wf.setframerate(RATE)
#wf.writeframes(b''.join(frames))
#wf.close()

quit()
