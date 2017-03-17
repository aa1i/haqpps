goal:
 create a low cost, accurate measurement system for evaluating HAQ

references
  hans moleman for the measurement technique
  igna for the affordable telephone inductive pickup

new
  use commodity soundcard input for affordable 2 channels at 192KHz (5usec samples)
  use PPS signal for reference (requires $40 GPS) 20 nsec accuracy when locked.
  python/pyaudio for portable solution. Linux, windows, mac?

equipment
  computer with soundcard capable of 192Khz. 16 bit fine. any gain from 24/32 bit?
  inductive telephone pickup. [part number] ~$2
  stereo-to-mono splitter [not Y-cable]. [Hosa part #] ~$3-6
  Adafruit GPS [model #][plate with proto area preferred?] ~$40
  misc LED/resistors.

problems

computer USB power noisy? [Part number for "plugable" supply]

souncard rate is not 192Khz, but can be corrected via PPS (192004.3)

 using gnuradio for plots for signal peaking.  Works, portable, but difficult. Easier python solution?

  learning python as I go. Code not up to usual standards...

PPS signal is too hot for mic input.  Added consumer headphone volume control [part #?]. Working on resistive voltage divider, requires soldering

PPS pulse is AC coupled and appears as a dual sawtooth, rather than a square pulse. Detection seems fine as long as gain is set so that signal decays in TBD time [add pictures][demonstrate saturation]

 pickup signal is low. Boosting signal too much results in spurious samples when noise exceeds threshold. Lower signals increase noise in measurements, but this seems to have less effect on measurments.
 Hand wind pickup for better gain?

 may need better filtering of spurious samples. time gating? effect on capture if initial sample noisy?

  office environment poor for GPS. PPS occasionally lost. good for testing, bad for measurement.

 is handling of PPS dropouts working as expected

 offline plots via gnuplot. Integrate in pthon?

future
  Validate various internet time programs [watchuseek, time.is, emerald time] via direct audio.
