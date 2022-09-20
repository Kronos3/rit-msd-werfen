cmake_minimum_required(VERSION 3.15)

project(VO-CMPE460)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

option(ASAN_BUILD "Build FSW with AddressSanitizer" OFF)
option(TSAN_BUILD "Build FSW with ThreadSanitizer" OFF)

set(AARCH 64)
set(RASPPI 3)
set(FLOAT_ABI "hard")

enable_language(C CXX ASM)

# Initialize the compiler toolchain
set(CMAKE_SYSTEM_NAME Linux)

if (ASAN_BUILD)
    add_compile_options(-fsanitize=address -fno-omit-frame-pointer -O1)
    add_link_options(-fsanitize=address)
elseif(TSAN_BUILD)
    add_compile_options(-fsanitize=thread -fno-omit-frame-pointer -O1)
    add_link_options(-fsanitize=thread)
endif()

#find_package(OpenCV REQUIRED)
#include_directories(${OpenCV_INCLUDE_DIRS})

set(STAGING_DIR ${CMAKE_CURRENT_LIST_DIR}/staging)
link_directories(${STAGING_DIR}/lib/)
include_directories(
        ${STAGING_DIR}/include/
        ${STAGING_DIR}/include/libcamera/
        ${STAGING_DIR}/include/libdrm/
        ${STAGING_DIR}/include/opencv4
)

#add_compile_options(-isystem /usr/include)

if (RPI_PLATFORM EQUAL "bare_metal")
    add_subdirectory(circle)
endif()

add_compile_options(-pipe)

# Override default FPrime configuration
set(FPRIME_CONFIG_DIR "${PROJECT_SOURCE_DIR}/Cfg")
set(FPRIME_AC_CONSTANTS_FILE "${FPRIME_CONFIG_DIR}/AcConstants.ini")

##
# Required for FSW FPrime CMake configuration
##
set(FPRIME_FRAMEWORK_PATH ${PROJECT_SOURCE_DIR}/fprime)

# Set the locations to search for FPrime components
set(FPRIME_PROJECT_ROOT ${PROJECT_SOURCE_DIR})
set(FPRIME_INSTALL_DEST ${PROJECT_SOURCE_DIR})
set(FPRIME_LIBRARY_LOCATIONS
        ${FPRIME_FRAMEWORK_PATH}
        ${PROJECT_SOURCE_DIR}
#        ${PROJECT_SOURCE_DIR}/Kernel/${RPI_PLATFORM}
        )

#include_directories(
#        ${CMAKE_BINARY_DIR}/Kernel/${RPI_PLATFORM}
#)

##
# FPrime instantiation
##
#set(CMAKE_DEBUG_OUTPUT TRUE)  # debug the CMake configuration
include(${FPRIME_FRAMEWORK_PATH}/cmake/FPrime.cmake)

# Set the framework libraries provided by FPrime
include(${FPRIME_FRAMEWORK_PATH}/cmake/FPrime-Code.cmake)
set(CMAKE_CXX_STANDARD 17)

#add_subdirectory(Kernel)    # Deployment specific drivers
add_subdirectory(Rpi)   # FSW

cmake_policy(SET CMP0079 NEW)
