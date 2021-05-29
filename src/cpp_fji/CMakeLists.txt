cmake_minimum_required(VERSION 3.17)
project(cpp_fji)

set(CMAKE_CXX_FLAGS_DEBUG "-Wall -Wpedantic -O3")
set(CMAKE_CXX_FLAGS_RELEASE "-Wall -Wpedantic -O3")

set(CMAKE_CXX_STANDARD 20)

add_executable(fji fji.cpp)

