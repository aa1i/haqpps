background/motivation: lightning deals unleashed my inner WIS. Needed a way to measure all these watches and feed my OCD, plus use that new GPS module I had bought.

goal:
 create a low cost, accurate measurement system for evaluating HAQ watches. Improve on the precision/accuracy of video methods, and at lower cost. Make it easier than manual stopwatch. Where possible use free and/or open source tools, and Ideally something that will work on Windows and Linux. Admittedly, also a way to use the GPS module I just bought for something useful. Although it is the most expensive part of the setup (other than the watches or the computer), it is a very cost effective timebase reference.

references
  measuring haq thread
  hans moleman for the measurement technique
  igna for the affordable telephone inductive pickup

new
  use commodity soundcard input for affordable 2 channels at 192KHz (5usec samples)
  use PPS signal for reference (requires $40 GPS) 20 nsec accuracy when locked.
  python/pyaudio for portable solution. Linux, windows, mac?

equipment
  computer with soundcard capable of 192Khz. 96/48/44.1 are probably fine too, but if 192khz available, no reason not to use it. 16 bit fine. any gain from 24/32 bit?
  inductive telephone pickup. [part number] ~$2
  stereo-to-mono splitter [not Y-cable]. [Hosa part #] ~$3-6
  Adafruit GPS [model #][plate with proto area preferred?] ~$40
    needs power - using USB via raspberry pi. could direct wire USB or bench supply
  misc LED/resistors.
  python program [link to source]

Results

problems

computer USB power noisy? [Part number for "plugable" supply]

souncard rate is not 192Khz, but can be corrected via PPS (192004.3)

 using gnuradio for plots for signal peaking.  Works, portable, but difficult. Easier python solution?

  learning python as I go. Code not up to usual standards...

PPS signal is too hot for mic input.  Added consumer headphone volume control [part #?]. Working on resistive voltage divider, requires soldering

PPS pulse is AC coupled and appears as a dual sawtooth, rather than a square pulse. Detection seems fine as long as gain is set so that signal decays in TBD time [add pictures][demonstrate saturation]

 pickup signal is low. Boosting signal too much results in spurious samples when noise exceeds threshold. Lower signals increase noise in measurements, but this seems to have less effect on measurments.
 Hand wind pickup for better gain?

  setting mics gains is essential. Would be nice to add real time plots. GnuRadio is hard to install.

 may need better filtering of spurious samples. time gating? effect on capture if initial sample noisy?

  office environment poor for GPS. PPS occasionally lost. good for testing, bad for measurement.

 is handling of PPS dropouts working as expected

 offline plots via gnuplot. Integrate in python?

  can't handle watches > 1 bps (yet). Precisionist 16 Hz.

future
  Validate various internet time programs [watchuseek, time.is, emerald time] via direct audio.
