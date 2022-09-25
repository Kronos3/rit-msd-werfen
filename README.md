# Rpi Werfen project

## Overview

Layout for this project:
  - /Rpi - Raspberry Pi FPrime modules
    - /Top - Main extry point with main()
  - /seq - Sequences written for camera calibration and testing


## Building
To actually build the Rpi binary, you will need to clone:
```
git clone --recursive git@github.com:at1777/msd-gem-5000.git
cd msd-gem-5000

# Now build
mkdir build
cd build
cmake ..
make -j5
```

The binary should now live in `build/Rpi/Top/fsw`

> Note: The `gcc-arm-10.2-2020.11-x86_64-arm-none-linux-gnueabihf` compiler toolchain needs to be used for the compilation to work
