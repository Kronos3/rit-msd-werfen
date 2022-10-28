set(SOURCE_FILES
        ${CMAKE_CURRENT_SOURCE_DIR}/test_rpi_cam.cc
)

register_fprime_executable("rpi_cam")

target_link_libraries(rpi_cam
        opencv_core
        opencv_videoio
)

target_link_options(rpi_cam PUBLIC -Wl,--unresolved-symbols=ignore-all)
