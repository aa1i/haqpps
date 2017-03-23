# (C) 2015-2016 John Isham <isham.john@gmail.com>
# All rights reserved
# free for non-commercial use
# please report any fixes or improvements back to me
# free for use as a tool to regulate watches as a hobby or commerically, but
# this software cannot be sold or incorporated into a commercial product
# without my written authorization

# 2016-02 Added status timing output
# 2016-01 Added primitive, and not totally correct fix
#   for offset wrapping across a second boundary

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
import time

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

class Haq:
  def __init__(self):
    #frames = []

    self.left_max=0.0  # Watch Under Test
    self.right_max=0.0 # PPS

    self.sample_count = 0

    self.first_right=0
    self.first_left=0

    self.right_count=0
    self.left_count=0

    self.last_right=0
    self.last_left=0
    # meant to lock/gate out triggering once a pulse has been detected
    # to avoid false triggers on the pulse "ringing"
    # for PPS pulse, should be > 100msec
    # for watch stepper pulse, probably >30msec.
    # 250msec should be fine
    #self.TRIGGER_WIDTH=RATE/4
    self.GATE_START= 95 * RATE// 100
    # TODO - this should probably be a tigger gate open within +-5% of a full second
    # rather than a maximum(minimum?) interval for a missed pulse
    self.GATE_STOP = 105 * RATE // 100

    self.left_thresh=0.5
    self.right_thresh=0.5

    #avg_rate=float(RATE)
    #avg_rate=192004.388773 # from a previous run
    self.avg_rate=192004.507824 # from a previous run

    self.tickfile=open('ticks.txt','w')
    self.offsfile=open('offset.txt','w',1) # line buffered

    self.sw_avg=[]
    self.last_offset=0.0
    self.last_offset_sample=0

    self.last_tic=0
    self.last_tic_offset=0
    self.last_pps=0
    self.last_pps_offset=0

    self.exit = False
  # END Haq.init()

  def grab_audio(self):
    data = stream.read(CHUNK)

    # append to output file
    #frames.append(data)

    # decode/deinterleave soundard samples
    decoded = numpy.fromstring(data,"Int16")
    # Normalize by int16 max (32767) for convenience, also converts everything to floats
    # Note: there might be a performance gain by NOT normalizing the samples
    # and normalizing the thresholds instead, but this seems to keep up just fine on my machine
    normed_samples = decoded / float(numpy.iinfo(numpy.int16).max)
    # TODO - rename PPS/clock instead of left/right
    # TODO - instead of list pick/copy, can use use something more python-ish, like zip()?
    self.left_samples =  normed_samples[left_channel::2]
    self.right_samples = normed_samples[right_channel::2]

    # track maximum amplitude per channel
    # is maximum tracking still useful, or can this be deleted for performance?
    tmp= max(abs(j) for j in self.left_samples)
    self.left_max = max( self.left_max, tmp )

    tmp= max(abs(j) for j in self.right_samples)
    self.right_max = max( self.right_max, tmp )
  # END Haq.grab_audio()

  def print_pps_tick(self):
    # note: time may be off by as much as CHUNK/RATE seconds, but still useful as timestamp
    # sample_count is more accurate for computing time intervals in the stream,
    # but only when corrected for sound card rate error with avg_rate
    sys.stdout.write( '{0:f} {1:f} PPS {2:7d} {3:f} tic {4:7d} {5:f}\r'.format(
      time.time(), float(self.sample_count)/self.avg_rate,
      self.last_pps, self.last_pps_offset,
      self.last_tic, self.last_tic_offset))
    sys.stdout.flush()
  # END Haq.print_ppc_tick()
    
  def pps_tick(self):
    if 0 == self.first_right:
      self.first_right=self.sample_count
    if VERBOSE >= 2:
      print '{0:f} {1:f} PPS {2:7d} {3:f}'.format(
        time.time(),float(self.sample_count)/self.avg_rate,
        self.sample_count-self.last_right,float(self.sample_count-self.last_right)/self.avg_rate)
    #    
    self.last_pps=self.sample_count-self.last_right
    self.last_pps_offset=float(self.last_pps)/self.avg_rate
    self.last_right= self.sample_count
    #
    self.print_pps_tick()
    #
    self.right_count+=1
    # update sample rate referenced to PPS pulses
    if self.right_count >= 10:
      self.avg_rate=float(self.last_right-self.first_right)/float(self.right_count-1)
  # END Haq.pps_tick();

  def inhibition_avg(self):
    # Note: while the offsets have a logical sign convention,
    # this tends to generate the negative of the wacth rate as viewed by the rest of the world
    # i.e. -  increasing offset ref PPS means a slow clock which should be a negative rate
    # and decreasing offset REF PPS means a fast clock which should be a positive rate.
    self.sw_avg.append(self.offset)
    if INHIBITION <= len(self.sw_avg):
      avg_offset=math.fsum(self.sw_avg)/float(INHIBITION)
      print '\n{0:f} {1:f} offset {2:f}'.format(
        time.time(), self.cur_clock, avg_offset)
      self.offsfile.write('{0:f} {1:f} offset {2:f}\n'.format(
        time.time(), self.cur_clock, avg_offset))
      self.sw_avg=[]
      # primitive rate calc based on last two inihibition periods only
      # better results will be obtained from linear fit to more offset data over longer timebase
      if self.last_offset_sample > 0:
        # TODO - invert sign in rate calc
        rate=float(avg_offset-self.last_offset)*self.avg_rate/float(self.sample_count-self.last_offset_sample)
        print '{0:f} {1:f} rate {2:e} spd {3:f} spy {4:f}'.format(
          time.time(), self.cur_clock, rate, rate*86400.0, rate*86400.0*365.0)
      self.last_offset_sample=self.sample_count
      self.last_offset=avg_offset
  # END Haq.inhition_avg()

  def clock_tick(self):
    if 0 == self.first_left:
      self.first_left=self.sample_count
    self.cur_clock=float(self.sample_count)/self.avg_rate
    #
    # check for missing PPS pulse
    if self.sample_count - self.last_right > self.GATE_STOP:
      print '{0:f} {1:f} PPS REFERENCE UNLOCK'.format(
        time.time(),self.cur_clock)
      # reset counters/stats!!
      self.sw_avg=[]
      self.last_right=0
      self.first_right=0
      self.right_count=0
    else:
      # Note: while the offsets have a logical sign convention,
      # this tends to generate the negative of the wacth rate as viewed by the rest of the world
      # i.e. -  increasing offset ref PPS means a slow clock which should be a negative rate
      # and decreasing offset REF PPS means a fast clock which should be a positive rate.
      self.offset=float(self.sample_count-self.last_right)/self.avg_rate
      # normalize/un-wrap to +- 0.5 second from reference pulse
      # TODO - this could be *much* improved, and add tracking across second boundaries
      if self.offset > 0.5:
        self.offset=self.offset-1.0
      # 1) self.offset is divided by self.avg_rate, but self.GATE_STOP isn't,
      #    so this is probably always true
      # 2) self.sample_count - self.last_right > self.GATE_STOP is tested above,
      #    so this is always true (unless lf.sample_count - self.last_right == self.GATE_STOP )
      if self.offset < self.GATE_STOP:
        if VERBOSE >=1:
          print '{0:f} {1:f} tic {2:7d} {3:f}'.format(
            time.time(),self.cur_clock,
            self.sample_count-self.last_right,self.offset)
        #
        self.last_tic=(self.sample_count-self.last_right)
        self.last_tic_offset=self.offset
        #
        self.print_pps_tick()
        # log tick data to file
        self.tickfile.write('{0:f} {1:f} tic {2:7d} {3:f}\n'.format(
          time.time(),self.cur_clock,
          self.sample_count-self.last_right,self.offset))
        #
        # sliding window average over inhibition period
        self.inhibition_avg()
    self.last_left=self.sample_count               
    self.left_count+=1
  # END Haq.clock_tick()

  # the "public" method
  # TODO - add arguments for inhibition period, watch name, etc
  def measure(self):
    while (not self.exit):
      try:
        self.grab_audio()

        # detect pulses
        # we can probably replace sample_num with right below,
        # but since we use the same index for the left/tic data,
        # sample_num is more straightforward
        self.sample_num = 0
        for self.right  in  self.right_samples:
          # look for PPS reference pulses on right channel
          if (abs(self.right_samples[self.sample_num]) > self.right_thresh):
            if ((0 == self.last_right) or (self.sample_count -self.last_right > self.GATE_START)):
              self.pps_tick()

          # look for watch stepper pulses / 'tics' on left channel
          if (abs(self.left_samples[self.sample_num]) > self.left_thresh):
            if ((0 == self.last_left) or (self.sample_count -self.last_left > self.GATE_START)):
              self.clock_tick()
          self.sample_num+=1
          self.sample_count+=1

      except KeyboardInterrupt: 
        print "Caught KeyboardInterrupt" 
        self.exit=True
        break;
      except IOError:
        print "Caught IOError" 
        self.exit=True
        break;
  # END Haq.measure()

  def close(self):
    self.tickfile.close()
    self.offsfile.close()

    print
    print "Avg rate:",self.avg_rate
    print "PPS count:",self.right_count
    print "tic count:",self.left_count
    print "max PPS ampl:",self.right_max
    print "max tic ampl:",self.left_max

    #wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    #wf.setnchannels(CHANNELS)
    #wf.setsampwidth(p.get_sample_size(FORMAT))
    #wf.setframerate(RATE)
    #wf.writeframes(b''.join(frames))
    #wf.close()
  # END Haq.close()

# END Haq


p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


haq = Haq()

print("* recording")

haq.measure()

print ("* done recording")

haq.close()

stream.stop_stream()
stream.close()
p.terminate()

quit()
