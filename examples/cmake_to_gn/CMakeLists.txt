cmake_minimum_required(VERSION 3.20)
project(hello_world)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

add_executable(hello_world
    main.cc
    utils.cc
)

add_library(utils STATIC
    string_utils.cc
    file_utils.cc
)

target_include_directories(utils PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

target_compile_options(utils PRIVATE -Wall -O2)

target_link_libraries(hello_world PRIVATE utils)
