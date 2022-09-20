# Rpi Vision Car Project

## Overview

Layout for this project:
  - /Rpi - Raspberry Pi FPrime modules
    - /Top - Main extry point with main()
  - /msp - MSP432P401R sources including all driver libraries
  - /seq - Sequences written for racing and calibration as well as configuration

How to read FPrime components:

The basics of are component are layed out in
the `ComponentAi.xml` file. This file will include port definitions
for messaging as well as import optional events, telemetry, and commands.

Actual C++ implementations of components are found in the `*Impl.cc` files.
Additional .cc/.h files may be shipped with the component when necessary.

##Actually building
To actually build the Rpi binary, you will need to clone:
```
git clone git@github.com:Kronos3/vo-cmpe460.git
cd vo-cmp460
git submodule init
git submodule update


# Now build
mkdir build
cd build
cmake ..
make -j5
```

The binary should now live in `build/Rpi/Top/fsw`

> Note: The `gcc-arm-10.2-2020.11-x86_64-arm-none-linux-gnueabihf` compiler toolchain needs to be used for the compilation to work

