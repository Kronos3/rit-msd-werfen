set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

set(COMPILER_PATH "/usr/bin")
if(AARCH EQUAL 32)
    set(ARCH_CFLAGS --target=arm-linux-gnueabihf)
else()
    set(ARCH_CFLAGS --target=aarch64-linux-gnu)
endif()

#set(CMAKE_CROSSCOMPILING ON)
#set(CROSS_COMPILE ${PREFIX}/c)
set(CMAKE_C_COMPILER /usr/bin/clang)
set(CMAKE_CXX_COMPILER /usr/bin/clang++)
set(CMAKE_ASM_COMPILER /usr/bin/clang)
#set(CMAKE_AR ${COMPILER_PATH}/${PREFIX}ar)
#set(CMAKE_AS ${COMPILER_PATH}/${PREFIX}as)
#set(SIZE ${COMPILER_PATH}/${PREFIX}size)

# Set up the board specific features
if (AARCH EQUAL 32)
    if(RASPPI EQUAL 1)
        set(ARCH_CFLAGS ${ARCH_FLAGS} -mcpu=arm1176jzf-s -marm -mfpu=vfp -mfloat-abi=${FLOAT_ABI})
        set(KERNEL_TARGET kernel)
    elseif(RASPPI EQUAL 2)
        set(ARCH_CFLAGS ${ARCH_FLAGS} -mcpu=cortex-a7 -marm -mfpu=neon-vfpv4 -mfloat-abi=${FLOAT_ABI})
        set(KERNEL_TARGET kernel7)
    elseif(RASPPI EQUAL 3)
        set(ARCH_CFLAGS ${ARCH_FLAGS} -mcpu=cortex-a53 -marm -mfpu=neon-fp-armv8 -mfloat-abi=${FLOAT_ABI})
        set(KERNEL_TARGET kernel8-32)
    elseif(RASPPI EQUAL 4)
        set(ARCH_CFLAGS ${ARCH_FLAGS} -mcpu=cortex-a53 -marm -mfpu=neon-fp-armv8 -mfloat-abi=${FLOAT_ABI})
        set(KERNEL_TARGET kernel7l)
    else()
        message(FATAL_ERROR "RASPPI must be 1, 2, 3, or 4: ${RASPPI}")
    endif()
elseif(AARCH EQUAL 64)
    if(RASPPI EQUAL 3)
#        set(ARCH_CFLAGS ${ARCH_FLAGS} -mcpu=cortex-a53 -mlittle-endian)
        set(KERNEL_TARGET kernel8)
    elseif(RASPPI EQUAL 4)
        set(ARCH_CFLAGS ${ARCH_FLAGS} -mcpu=cortex-a72 -mlittle-endian)
        set(KERNEL_TARGET kernel8-rpi4)
    else()
        message(FATAL_ERROR "RASPPI must be 3, or 4 for 64-bit: ${RASPPI}")
    endif()
else()
    message(FATAL_ERROR "AARCH must be 32 or 64: ${AARCH}")
endif()

message(STATUS "Building for ${AARCH}-bit Raspberry Pi ${RASPPI}")

# Set CFLAGS and CXXFLAGS
message(STATUS "Architecture flags: ${ARCH_CFLAGS}")
add_compile_options("${ARCH_CFLAGS}")
add_compile_options(-O2 -Wall -fsigned-char)
#add_link_options(-static)
add_compile_definitions(
        __unix__ __linux__
        RASPPI=${RASPPI}
        AARCH=${AARCH}
        )

#include_directories(/usr/aarch64-linux-gnu/include/aarch64-linux-gnu)
#
set(CMAKE_SYSTEM_NAME Linux)
set(CMAKE_SYSTEM_PROCESSOR arm)

set(CMAKE_SYSROOT /usr/aarch64-linux-gnu/)

set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM NEVER)
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_PACKAGE ONLY)

