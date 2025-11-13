cmake_minimum_required(VERSION 3.16)
project(spice_runner LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Homebrew ngspice (Apple Silicon or Intel)
include_directories(/opt/homebrew/include /usr/local/include)
find_library(NGSPICE_LIB NAMES ngspice PATHS /opt/homebrew/lib /usr/local/lib REQUIRED)

add_executable(spice_runner src/main.cpp)
target_link_libraries(spice_runner PRIVATE ${NGSPICE_LIB})
