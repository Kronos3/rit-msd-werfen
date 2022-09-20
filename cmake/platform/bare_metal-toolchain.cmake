set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)

set(COMPILER_PATH "/usr/bin/")
if(AARCH EQUAL 32)
    set(PREFIX arm-none-eabi-)
else()
    set(PREFIX aarch64-none-elf-)
endif()

set(CMAKE_C_COMPILER ${COMPILER_PATH}/${PREFIX}gcc)
set(CMAKE_CXX_COMPILER ${COMPILER_PATH}/${PREFIX}g++)
set(CMAKE_ASM_COMPILER  ${COMPILER_PATH}/${PREFIX}gcc)
set(CMAKE_AR ${COMPILER_PATH}/${PREFIX}ar)
set(CMAKE_OBJCOPY ${COMPILER_PATH}/${PREFIX}objcopy)
set(CMAKE_OBJDUMP ${COMPILER_PATH}/${PREFIX}objdump)
set(SIZE ${COMPILER_PATH}/${PREFIX}size)


# Set up the board specific features
if (AARCH EQUAL 32)
    set(LOADADDR 0x8000)
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
    set(LOADADDR 0x80000)
    if(RASPPI EQUAL 3)
        set(ARCH_CFLAGS ${ARCH_FLAGS} -mcpu=cortex-a53 -mlittle-endian)
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

message(STATUS "Building for ${AARCH}-bit Raspberry Pi ${RASPPI} (${KERNEL_TARGET}.img)")

# Set CFLAGS and CXXFLAGS
message(STATUS "Architecture flags: ${ARCH_CFLAGS}")
add_compile_options("${ARCH_CFLAGS}")
add_compile_options(-O2 -Wall -fsigned-char -ffreestanding)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-aligned-new -fno-exceptions -fno-rtti")
add_compile_definitions(
        __circle__ __unix__ __linux__
        RASPPI=${RASPPI}
        AARCH=${AARCH}
        __VCCOREVER__=0x04000000)
if (ARM_ALLOW_MULTI_CORE)
    add_compile_definitions(ARM_ALLOW_MULTI_CORE)
endif()

set(LINKER_SCRIPT ${CMAKE_CURRENT_LIST_DIR}/circle.ld)

function(build_elf NAME)
    set(SOURCES ${ARGV})
    LIST(REMOVE_AT SOURCES 0)
    add_executable(
            ${NAME}
            ${SOURCES}
            ${LINKER_SCRIPT}
    )
    target_link_libraries(${NAME} circle gcc m)

    set(HEX_FILE ${CMAKE_CURRENT_BINARY_DIR}/${NAME}.hex)
    set(BIN_FILE ${CMAKE_CURRENT_BINARY_DIR}/${KERNEL_TARGET}.img)

    add_custom_command(TARGET ${NAME} POST_BUILD
            COMMAND ${CMAKE_OBJCOPY} $<TARGET_FILE:${NAME}> -O ihex ${HEX_FILE}
            COMMAND ${CMAKE_OBJCOPY} $<TARGET_FILE:${NAME}> -O binary ${BIN_FILE}
            COMMENT "Building ${HEX_FILE}\nBuilding ${BIN_FILE}")

    target_link_options(${NAME} PRIVATE
            "-Wl,-Map,${CMAKE_CURRENT_BINARY_DIR}/${NAME}.map")
endfunction()

#add_link_options(
#        ${ARCH_CFLAGS}
#        -T ${LINKER_SCRIPT}
#        -static
#        --specs=nosys.specs
#        -nostartfiles
#        -ffreestanding
#        -Wl,--section-start=.init=${LOADADDR}
#)

add_compile_options(-funwind-tables)
