# HAQPPS

Apologies - this is just sparse notes at this point, but should provide enough information to get a motivated person going, until I can flesh this out better.

## Description

A set of python scripts to facilitate using a computer sound card to measure the rate of HAQ (High Accuracy Quartz) watches, in conjunction with a GPS derived PPS (pulse per second) signal.

## Background

Some quartz watches use a small stepper motor to move their hands. This motor emits a pulse once a second, and this pulse can be detected with simple/cheap inductive sensors.

Regulating High Accuracy Quartz watches requires an accurate time reference. The GPS PPS signal is readible available, and reasonably cheap. GPS provides better accuracy (~20ns) than internet clocks (~10 us)(apps/ntp) and great long term stability

Other methods require a lot of manual operations - stopwatch timing, or reviewing high speed video frames.  This technique uses a computer soundcard to automate collection of rate data, with time resolution (192kHz) even better than high speed video methods (400Hz). Soundcard sample rates vary, but the PPS is used to correct for the local soundcard rate.

 Stop watch or video methods still needed to measure offset of watch to the nearest integer second. PPS only allows accurate measurement of fractional seconds. Fractional seconds can be tracked as they drift across integer seconds, but an external method is needed for the starting point.

  The bulk collection of this rate data allows averaging the watch's rate over long time periods, where previous methods only sampled it occasionally, perhaps daily. Recent improvements allow measurement across gaps with saprsely collected data.

## References

TBD - link to WUS threads

- [Watchuseek HAQ forum](http://forums.watchuseek.com/f9)
- [Methods of Determining the Accuracy of a Watch](http://forums.watchuseek.com/f9/methods-determining-accuracy-watch-382752.html)  thread on WUS
- [Hans Moleman's methods for determining the accuracy of his Longines VHP](http://forums.watchuseek.com/f9/just-data-molemans-hunt-milliseconds-168460.html)
- Igna's idea of [using an affordable telephone inductive pickup](http://forums.watchuseek.com/f9/methods-determining-accuracy-watch-382752-4.html#post13295914)
- WUS Thread where I initially [detail the setup I use](http://forums.watchuseek.com/f9/development-low-cost-high-accuracy-haq-rate-measurement-systen-2685921.html)  to measure my High Accuracy Quartz watches. Old, (December 2015) but the basic idea is there and there are some useful links.  I have moved away from the GNURadio and GNUplot approach detailed there to these Python scripts

## Requires

- python 3 (used to work on Python 2, probably still could with mininal effort)
- pyaudio
- tkinter
- numpy
- scipy
- matplotlib
- pickle (builtin?)

mostly builtins. Perhaps some basic Python package installtion? Should be portable. Tested on Linux, but should work on windows.

## Hardware

- GPS with PPS (I used [Adafruit ultimate GPS breakout](https://www.adafruit.com/products/746) )
- pickup sensor for watch (I used an AM broadcast band antenna - a coil wrapped around a ferrite core, inductive telephone pickups work too)
- computer soundcard. Testing done at 192kHz, but 96/48/44.1 should be fine

optional equipment

- external amplified GPS antenna
- adapter cable from GPS board to connector for antenna
- Various stereo mini patch cables
- various resistors to make voltage divider to step down PPS voltage
- PPS LED and current limiting resistor - nice for hacking watches.
- USB powered hub. I used a unit from plugable that is recommended.
    
## Usage

### main application

python3 haqpps-tk.py

### Adjust Audio Levels

- selection of soundcard channel is OS dependent.
- PPS "R"eference on R channel
- Watch under test on L channel
- channels can be flipped in software
- Optional filtering on audio - 100 Hz HPF attenuates much ambient noise and 60 Hz AC hum.  Filtering on PPS reference seems to only add timing jitter.
- make sure GPS has a lock
- adjust soundcard gains and/or external pots/amps/gain
- multiple instances can run, but why would you?

[ ]  Add image of reasonable levels

### Select watch information

1. inhibition period
2. integer seconds / cycle offset (from stopwatch measurements)
3. watch "name" - include useful info - model name/num, serial num, personalized "name"

### Measure Rate

- audio filtering
- should only have single measurment instance running

[ ]  selection of watch paramters from GUI

### Plot Rate

- captions from collection.py
- sense of rate and offsets.
-- positive rate - fast watch gains time, watch pulse drifts early compared to reference
-- negative rate - slow watch loses time, watch pulse drifts late compared to reference
- use matplotlib zoom and save to file

### Cumulative Rate Plots

- concatenate offset.txt and older offsets.  Timestamps including, measurement gaps handled

cat previous cumulative with current (normal usage):

`cat vhp_16_pc_adj04_off01_cumul11_2017_0620.txt offset.txt > offset_cumulative.txt`

create new "previous" cumulative (after terminating a measurement run):

`cat vhp_16_pc_adj04_off01_cumul10_2017_0619.txt offset.txt > vhp_16_pc_adj04_off01_cumul11_2017_0620.txt`

## Configuation

collection.py



## TODO

[ ] make watch selection/parameters work rather than pulling hardcoded values from collection.py
[ ] pass parameters to modules via local file/"pickle"
[ ] pass parameters via getopt
[ ] automatically pass integer seconds / cycle offset from measurement to watch data
[ ] aids to concatenating offset files for cumulative plots.  Possible selection of base/current/cumulative file names

## known issues

[ ] the first inhibition average seems to be skewed. Possibly a single zero sample leaking in, probably an off-by-one error somewhere.  It averages out in the long run, but short term averages are skewed by the error.


### Notes

- regenerating the html version of this markdown file on Linux:

`pandoc README.md > README.html`