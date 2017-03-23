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

    self.wut_max=0.0  # Watch Under Test
    self.pps_max=0.0 # PPS

    self.sample_count = 0

    self.first_pps_sample=0
    self.first_wut_sample=0

    self.pps_count=0
    self.wut_count=0

    self.last_pps_sample=0
    self.last_wut_sample=0
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

    # window of valid offsets when tracking across integer second "cycle" boundary
    self.CYCLE_EDGE_LOW  = 0.02
    self.CYCLE_EDGE_HIGH = 1.0 - self.CYCLE_EDGE_LOW
    
    self.wut_thresh=0.5
    self.pps_thresh=0.5

    #avg_rate=float(RATE)
    #avg_rate=192004.388773 # from a previous run
    self.avg_rate=192004.507824 # from a previous run

    self.tickfile=open('ticks.txt','w')
    self.offsfile=open('offset.txt','w',1) # line buffered

    self.sw_avg=[]
    self.last_avg=0.0
    self.last_avg_sample=0

    self.last_tic=0
    self.last_tic_offset=0
    self.last_pps=0
    self.last_pps_offset=0
    self.cycle=0
    
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
    # TODO - instead of list pick/copy, can use use something more python-ish, like zip()?
    self.wut_samples = normed_samples[left_channel ::2]
    self.pps_samples = normed_samples[right_channel::2]

    # track maximum amplitude per channel
    # is maximum tracking still useful, or can this be deleted for performance?
    tmp= max(abs(j) for j in self.wut_samples)
    self.wut_max = max( self.wut_max, tmp )

    tmp= max(abs(j) for j in self.pps_samples)
    self.pps_max = max( self.pps_max, tmp )
  # END Haq.grab_audio()

  def print_pps_tick(self):
    # note: time may be off by as much as CHUNK/RATE seconds, but still useful as timestamp
    # sample_count is more accurate for computing time intervals in the stream,
    # but only when corrected for sound card rate error with avg_rate
    sys.stdout.write( '{0:f} {1:f} PPS {2:7d} {3:f} tic {4:7d} {5:f} {6:d} {7:f}\r'.format(
      time.time(), float(self.sample_count) / self.avg_rate,
      self.last_pps, self.last_pps_offset,
      self.last_tic, self.last_tic_offset,
      self.cycle, self.last_tic_offset + self.cycle) )
    sys.stdout.flush()
  # END Haq.print_ppc_tick()
    
  def pps_tick(self):
    if 0 == self.first_pps_sample:
      self.first_pps_sample = self.sample_count
    if VERBOSE >= 2:
      print ('{0:f} {1:f} PPS {2:7d} {3:f}'.format(
        time.time(), float( self.sample_count ) / self.avg_rate,
        self.sample_count - self.last_pps_sample,
        float( self.sample_count - self.last_pps_sample ) / self.avg_rate ) )
    #    
    self.last_pps = self.sample_count - self.last_pps_sample
    self.last_pps_offset = float(self.last_pps) / self.avg_rate
    self.last_pps_sample = self.sample_count
    #
    self.print_pps_tick()
    #
    self.pps_count+=1
    # update sample rate referenced to PPS pulses
    if self.pps_count >= 10:
      self.avg_rate = float( self.last_pps_sample - self.first_pps_sample ) / float( self.pps_count-1 )
  # END Haq.pps_tick();

  def inhibition_avg(self):
    # Note: while the offsets have a logical sign convention,
    # this tends to generate the negative of the wacth rate as viewed by the rest of the world
    # i.e. -  increasing offset ref PPS means a slow clock which should be a negative rate
    # and decreasing offset REF PPS means a fast clock which should be a positive rate.
    self.sw_avg.append(self.offset + self.cycle)
    if INHIBITION <= len(self.sw_avg):
      avg_offset=math.fsum(self.sw_avg)/float(INHIBITION)
      print ('\n{0:f} {1:f} offset {2:f}'.format(
        time.time(), self.cur_clock, avg_offset) )
      self.offsfile.write('{0:f} {1:f} offset {2:f}\n'.format(
        time.time(), self.cur_clock, avg_offset))
      # reset average for next iteration
      self.sw_avg=[]
      # primitive rate calc based on last two inihibition periods only
      # better results will be obtained from linear fit to more offset data over longer timebase
      if self.last_avg_sample > 0:
        rate = (float( avg_offset - self.last_avg ) * self.avg_rate
                /  float( self.sample_count - self.last_avg_sample ) )
        # invert sign in rate calc to match real world convention (fast clock - decreasing offset)
        rate *= -1.0
        print ('{0:f} {1:f} rate {2:e} spd {3:f} spy {4:f}'.format(
          time.time(), self.cur_clock, rate, rate * 86400.0, rate * 86400.0 * 365.0) )
      self.last_avg_sample = self.sample_count
      self.last_avg = avg_offset
  # END Haq.inhition_avg()

  def clock_tick(self):
    if 0 == self.first_wut_sample:
      self.first_wut_sample = self.sample_count
    self.cur_clock = float( self.sample_count ) / self.avg_rate
    #
    # check for missing PPS pulse
    if self.sample_count - self.last_pps_sample > self.GATE_STOP:
      print ( '{0:f} {1:f} PPS REFERENCE UNLOCK'.format(
        time.time(), self.cur_clock) )
      # reset counters/stats!!
      self.sw_avg = []
      self.last_pps_sample = 0
      self.first_pps_sample = 0
      self.pps_count = 0
    else:
      # Note: while the offsets have a logical sign convention,
      # this tends to generate the negative of the watch rate as viewed by the rest of the world
      # i.e. -  increasing offset ref PPS means a slow clock which should be a negative rate
      # and decreasing offset REF PPS means a fast clock which should be a positive rate.
      # this will need to be corrected in the external process that computes best fit rates
      # from bulk tick data
      self.offset = float( self.sample_count - self.last_pps_sample ) / self.avg_rate
      # normalize/un-wrap to nearest 0-1 second "cycle" from reference pulse
      # TODO - this could be *much* improved, and add tracking across second boundaries
      # TODO need to compare  self.offset to self.last_tic_offset to update self.cycle, algorithm TBD
      #if abs( self.offset - self.last_tic_offset) > 0.1 and \
      #   abs( self.offset - self.last_tic_offset) <= (self.GATE_STOP // RATE):
      #  if ( self.offset - self.last_tic_offset ) < 0:
      #    self.cycle += 1
      #  else:
      #    self.cycle -= 1
      # hack to prevent false cycles
      # Do we need a complementary negative check? offset never negative?
      if (self.offset > 1.0): self.offset -= 1
      # self.CYCLE_EDGE_LOW, self.CYCLE_EDGE_HIGH
      if (self.offset >= 0.98) and (self.last_tic_offset <= 0.02):
        self.cycle -= 1
        if VERBOSE >= 1:
          print ('offset: {0:f} last: {1:f} -1 cycle {2:d}'.format(
            self.offset, self.last_tic_offset,
            self.cycle) )
      elif (self.offset <= 0.02) and (self.last_tic_offset >= 0.98):
        self.cycle += 1
        if VERBOSE >= 1:
          print ( 'offset: {0:f} last: {1:f} +1 cycle {2:d}'.format(
            self.offset, self.last_tic_offset,
            self.cycle) )
      # 1) self.offset is divided by self.avg_rate, but self.GATE_STOP isn't,
      #    so this is probably always true
      # 2) self.sample_count - self.last_pps_sample > self.GATE_STOP is tested above,
      #    so this is always true (unless lf.sample_count - self.last_pps_sample == self.GATE_STOP )
      if self.offset <= (self.GATE_STOP // RATE):
        if VERBOSE >=1:
          print ('{0:f} {1:f} tic {2:7d} {3:f} {4:d} {5:f}'.format(
            time.time(), self.cur_clock,
            self.sample_count - self.last_pps_sample,
            self.offset, self.cycle, self.offset + self.cycle) )
        #
        #self.offset = self.offset + self.cycle
        self.last_tic = (self.sample_count - self.last_pps_sample)
        #self.last_tic_offset = self.offset + self.cycle
        self.last_tic_offset = self.offset
        #
        self.print_pps_tick()
        #
        # log tick data to file
        self.tickfile.write('{0:f} {1:f} tic {2:7d} {3:f}\n'.format(
          time.time(), self.cur_clock,
          self.sample_count - self.last_pps_sample , self.offset + self.cycle))
        #
        # sliding window average over inhibition period
        self.inhibition_avg()
    self.last_wut_sample = self.sample_count               
    self.wut_count += 1
  # END Haq.clock_tick()

  # the "public" method
  # TODO - add arguments for inhibition period, watch name, etc
  def measure(self):
    while (not self.exit):
      try:
        self.grab_audio()

        # detect pulses
        for (self.pps, self.wut) in zip( self.pps_samples, self.wut_samples):
          # look for PPS reference pulses on right channel
          if (abs(self.pps) > self.pps_thresh):
            if ((0 == self.last_pps_sample) or (self.sample_count - self.last_pps_sample > self.GATE_START)):
              self.pps_tick()

          # look for watch under test "WUT" stepper pulses / 'tics' on left channel
          if (abs(self.wut) > self.wut_thresh):
            if ((0 == self.last_wut_sample) or (self.sample_count - self.last_wut_sample > self.GATE_START)):
              self.clock_tick()
          self.sample_count+=1

      except KeyboardInterrupt: 
        print ("Caught KeyboardInterrupt" )
        self.exit=True
        break;
      except IOError:
        print ("Caught IOError" )
        self.exit=True
        break;
  # END Haq.measure()

  def close(self):
    self.tickfile.close()
    self.offsfile.close()

    print ()
    print ("Avg rate:",self.avg_rate)
    print ("PPS count:",self.pps_count)
    print ("tic count:",self.wut_count)
    print ("max PPS ampl:",self.pps_max)
    print ("max tic ampl:",self.wut_max)

    #wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    #wf.setnchannels(CHANNELS)
    #wf.setsampwidth(p.get_sample_size(FORMAT))
    #wf.setframerate(RATE)
    #wf.writeframes(b''.join(frames))
    #wf.close()
  # END Haq.close()

# END Haq


p = pyaudio.PyAudio()

stream = p.open( format = FORMAT,
                 channels = CHANNELS,
                 rate = RATE,
                 input = True,
                 frames_per_buffer = CHUNK )


haq = Haq()

print("* recording")

haq.measure()

print ("* done recording")

haq.close()

stream.stop_stream()
stream.close()
p.terminate()

quit()
