cmake_minimum_required(VERSION 3.10)
project(puuiy_engine VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(SOURCES
    renderer.cpp
)

add_library(puuiy_engine SHARED ${SOURCES})

target_include_directories(puuiy_engine PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_compile_definitions(puuiy_engine PRIVATE
    PUUIY_EXPORTS
)

if(WIN32)
    target_compile_definitions(puuiy_engine PRIVATE PUUIY_PLATFORM_WINDOWS)
elseif(UNIX AND NOT APPLE)
    target_compile_definitions(puuiy_engine PRIVATE PUUIY_PLATFORM_LINUX)
elseif(APPLE)
    target_compile_definitions(puuiy_engine PRIVATE PUUIY_PLATFORM_MACOS)
endif()

install(TARGETS puuiy_engine
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
    ARCHIVE DESTINATION lib
)

install(FILES renderer.h DESTINATION include)

find_package(Python3 COMPONENTS Interpreter Development)
if(Python3_FOUND AND SWIG_FOUND)
    include(UseSWIG)
    set(CMAKE_SWIG_FLAGS "")
    set_source_files_properties(puuiy_engine.i PROPERTIES CPLUSPLUS ON)
    swig_add_library(puuiy_swig LANGUAGE python SOURCES puuiy_engine.i)
    target_link_libraries(puuiy_swig PRIVATE puuiy_engine ${Python3_LIBRARIES})
    target_include_directories(puuiy_swig PRIVATE ${Python3_INCLUDE_DIRS})
endif()