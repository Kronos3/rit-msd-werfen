cmake_minimum_required(VERSION 3.10)

project(MC)
enable_language(C)

include_directories(include)
include_directories(motor)
include_directories(log)

add_subdirectory(comm)
add_subdirectory(motor)
add_subdirectory(log)
