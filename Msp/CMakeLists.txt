set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_VERSION 1)
cmake_minimum_required(VERSION 3.20)

# project settings
project(CMPE460 C CXX ASM)
set(CMAKE_C_STANDARD 99)

set(PLATFORM "msp432p4" CACHE STRING "Target board to platform drivers and targets for")
set(BOARD "msp432p4111" CACHE STRING "Board variant for platform")

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

function(gen_library name)
    add_library(${name} STATIC ${ARGN})
    target_compile_definitions(${name} PUBLIC __${name}_LINKED__)
endfunction()

include_directories(${PROJECT_SOURCE_DIR})
include(platform/${PLATFORM}/platform.cmake)

add_subdirectory(drv)

build_elf(werfen-mcu test_main.c)
target_link_libraries(werfen-mcu
        i2c
        tim
        pwm
        gpio
        uart
        uartlib
        )
target_compile_definitions(werfen-mcu PUBLIC __SYSTEM_CLOCK=48000000)
