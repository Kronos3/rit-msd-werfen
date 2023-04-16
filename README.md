# RIT-Werfen Inspection

## Overview

Layout for this project:
  - /pcb - KiCAD Design file for the PCB
  - /mc - Microcontroller firmware for STM32L476RG
  - /prototyping - Test images and Jupyter Notebooks used to prototype code
  - /src - Code running on the Raspberry Pi and in the browser
    - frontend/ - ReactJS (Typescript) program for frontend browser code
    - rit/ - Middleware that abstract the behavior of cameras and MC packet interface
    - web/ - FastAPI that exposes webendpoints for the frontend to submit requests to
    - camera_focusing.py - Script that boots up a QT Program to view the camera live

## Building

The microcontroller code can be built using CMake + GCC Arm toolchain.
You should use a relatively recent GCC Arm toolchain (`arm-none-eabi-gcc`)


### Dependency installation (Ubuntu)

On Ubuntu, run the following to install the dependencies:

```
sudo apt install gcc-arm-none-eabi cmake make
```

### Building PCB code

```
mkdir -p mc/build
cd mc/build
cmake -DCMAKE_C_COMPILER=arm-none-eabi-gcc -DCMAKE_CXX_COMPILER=arm-none-eabi-g++ ../
```

Now that the code is built, you can flash the PCB using an ST-Link or the ST-Link found on a STM32 Nucleo board using SWD via OpenOCD. I'd recommend using a Nucleo board for flashing along with an IDE like CLion that can set up, build and flash firmware for you.
