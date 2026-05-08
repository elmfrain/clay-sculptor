cmake_minimum_required(VERSION 3.20)

option(BUILD_EXAMPLES "Enable building examples" ON)

if(BUILD_EXAMPLES)
    add_subdirectory("examples")
endif()
