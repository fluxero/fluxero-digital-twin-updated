cmake_minimum_required(VERSION 3.16)
project(spice_runner CXX)
set(CMAKE_CXX_STANDARD 17)

# Homebrew paths on macOS
include_directories(/opt/homebrew/include)
find_library(NGSPICE_LIB ngspice PATHS /opt/homebrew/lib /usr/local/lib)

add_executable(spice_runner src/main.cpp)
target_link_libraries(spice_runner ${NGSPICE_LIB})
