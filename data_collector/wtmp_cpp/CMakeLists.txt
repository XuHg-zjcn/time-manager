cmake_minimum_required(VERSION 3.16.3)
project(wtmp_cpp)
include_directories("./")
add_executable(${PROJECT_NAME}
               FSM.cpp
               reader.cpp)
target_link_libraries(wtmp_cpp)
