# Fossil Hybrid HR SDK

this is a collection of tools to create apps that run natively on the the Fossil HR smartwatches.

[Timer](https://www.reddit.com/r/FossilHybrids/comments/ld9zc7/better_timer_v2/) and [Snake](https://www.reddit.com/r/FossilHybrids/comments/ldiah1/schnek_on_hr/) are two of the examples in the SDK.

## Prerequisites
- the thing probably won't run under windows natively. Subsystem works though.
- jerryscript and jerryscript-snapshot need to be installed and in the $PATH, both v2.1.0
- make needs to be installed
- adb needs to be working and connected to your phone
- Gadgetbridge needs to run on the phone and be connected to the watch (not authentication needed)
- some more stuff, dunno what yet. You and me can complete this together...

## Usage
- cd into one of the examples containing a Makefile
- `make` will build and install an example on the watch through GB (timer will override the default stopwatchApp)
- never change any example code, my code is already perfect and cannot possibly be made any better

## TODO's
- complete documentation

The documentation can be accessed [here](DOCUMENTATION.md).
