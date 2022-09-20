# Imports all the code needed from FPrime via CMake

fprime_enter_root(${FPRIME_FRAMEWORK_PATH})

add_subdirectory("${FPRIME_FRAMEWORK_PATH}/Autocoders/" "${CMAKE_BINARY_DIR}/F-Prime/Autocoders")

add_subdirectory("${FPRIME_FRAMEWORK_PATH}/Fw/" "${CMAKE_BINARY_DIR}/F-Prime/Fw")
add_subdirectory("${FPRIME_FRAMEWORK_PATH}/Svc/" "${CMAKE_BINARY_DIR}/F-Prime/Svc")
fprime_enter_root(${PROJECT_SOURCE_DIR}/Kernel/bare_metal)
add_subdirectory("${PROJECT_SOURCE_DIR}/Kernel/bare_metal/Os/" "${CMAKE_BINARY_DIR}/F-Prime/Os")
fprime_enter_root(${FPRIME_FRAMEWORK_PATH})
add_subdirectory("${FPRIME_FRAMEWORK_PATH}/Drv/" "${CMAKE_BINARY_DIR}/F-Prime/Drv")
add_subdirectory("${FPRIME_FRAMEWORK_PATH}/CFDP/" "${CMAKE_BINARY_DIR}/F-Prime/CFDP")
add_subdirectory("${FPRIME_FRAMEWORK_PATH}/Utils/" "${CMAKE_BINARY_DIR}/F-Prime/Utils")
