cmake_minimum_required(VERSION 3.16.3)
add_definitions("-g -O3")
project(wtmp_cpp)
include_directories(".")
find_package(PythonLibs REQUIRED)
include_directories(${PYTHON_INCLUDE_DIRS})

add_library(${PROJECT_NAME} SHARED
            FSM.cpp
            reader.cpp
            python_api.cpp)
target_link_libraries(${PROJECT_NAME} ${PYTHON_LIBRARIES})
message("Python: " ${PYTHON_INCLUDE_DIRS})

add_executable(${PROJECT_NAME}_test print.cpp)
target_link_libraries(${PROJECT_NAME}_test ${PROJECT_NAME})
