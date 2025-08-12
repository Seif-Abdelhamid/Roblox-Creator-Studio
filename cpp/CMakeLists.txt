cmake_minimum_required(VERSION 3.16)
project(RobloxCreatorStudio VERSION 1.0.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Project metadata
set(PROJECT_DESCRIPTION "Roblox Creator Studio - High-performance C++ modules")
set(PROJECT_HOMEPAGE_URL "https://github.com/Seif-Abdelhamid/roblox-creator-studio")
set(PROJECT_AUTHOR "Seif Abdelhamid")
set(PROJECT_AUTHOR_EMAIL "seifwaelabdelhamid@gmail.com")

# Find required packages
find_package(OpenGL REQUIRED)
find_package(glfw3 REQUIRED)
find_package(glm REQUIRED)
find_package(assimp REQUIRED)
find_package(OpenAL REQUIRED)
find_package(Threads REQUIRED)

# Include directories
include_directories(
    ${CMAKE_SOURCE_DIR}/include
    ${CMAKE_SOURCE_DIR}/src
    ${OPENGL_INCLUDE_DIRS}
    ${GLM_INCLUDE_DIRS}
    ${ASSIMP_INCLUDE_DIRS}
    ${OPENAL_INCLUDE_DIR}
)

# Compiler flags
if(MSVC)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4 /O2")
else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -O3 -march=native")
endif()

# Platform-specific settings
if(WIN32)
    set(PLATFORM_LIBS opengl32 glu32)
elseif(APPLE)
    set(PLATFORM_LIBS "-framework OpenGL" "-framework GLUT" "-framework CoreAudio" "-framework AudioToolbox")
else()
    set(PLATFORM_LIBS GL GLU X11 Xrandr Xxf86vm Xi Xinerama Xcursor)
endif()

# Renderer module
add_library(Renderer SHARED
    src/renderer/Renderer.cpp
    src/renderer/Shader.cpp
    src/renderer/Texture.cpp
    src/renderer/Mesh.cpp
    src/renderer/Camera.cpp
    src/renderer/Lighting.cpp
    src/renderer/PostProcessor.cpp
)

target_link_libraries(Renderer
    ${OPENGL_LIBRARIES}
    glfw
    glm
    assimp
    ${PLATFORM_LIBS}
    Threads::Threads
)

# Physics module
add_library(Physics SHARED
    src/physics/PhysicsEngine.cpp
    src/physics/CollisionDetector.cpp
    src/physics/RigidBody.cpp
    src/physics/Constraint.cpp
    src/physics/World.cpp
)

target_link_libraries(Physics
    Threads::Threads
)

# Audio module
add_library(Audio SHARED
    src/audio/AudioEngine.cpp
    src/audio/Sound.cpp
    src/audio/Music.cpp
    src/audio/AudioSource.cpp
    src/audio/AudioListener.cpp
)

target_link_libraries(Audio
    ${OPENAL_LIBRARY}
    ${PLATFORM_LIBS}
)

# Main executable
add_executable(RobloxCreatorStudio
    src/main.cpp
    src/GameEngine.cpp
    src/InputManager.cpp
    src/ResourceManager.cpp
    src/SceneManager.cpp
)

target_link_libraries(RobloxCreatorStudio
    Renderer
    Physics
    Audio
    glfw
    glm
    ${PLATFORM_LIBS}
    Threads::Threads
)

# Python bindings (if Python is found)
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
if(Python3_FOUND)
    find_package(pybind11 REQUIRED)
    
    add_library(RobloxCreatorStudioPython SHARED
        src/python_bindings/bindings.cpp
    )
    
    target_link_libraries(RobloxCreatorStudioPython
        Renderer
        Physics
        Audio
        pybind11::module
    )
    
    pybind11_add_module(roblox_creator_studio_cpp src/python_bindings/bindings.cpp)
    target_link_libraries(roblox_creator_studio_cpp
        Renderer
        Physics
        Audio
    )
endif()

# Tests
enable_testing()
add_subdirectory(tests)

# Installation
install(TARGETS Renderer Physics Audio RobloxCreatorStudio
    LIBRARY DESTINATION lib
    ARCHIVE DESTINATION lib
    RUNTIME DESTINATION bin
)

install(DIRECTORY include/ DESTINATION include)

# Package configuration
include(CMakePackageConfigHelpers)
write_basic_package_version_file(
    "${CMAKE_CURRENT_BINARY_DIR}/RobloxCreatorStudioConfigVersion.cmake"
    VERSION ${PROJECT_VERSION}
    COMPATIBILITY AnyNewerVersion
)

configure_package_config_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/cmake/RobloxCreatorStudioConfig.cmake.in"
    "${CMAKE_CURRENT_BINARY_DIR}/RobloxCreatorStudioConfig.cmake"
    INSTALL_DESTINATION lib/cmake/RobloxCreatorStudio
)

install(FILES
    "${CMAKE_CURRENT_BINARY_DIR}/RobloxCreatorStudioConfig.cmake"
    "${CMAKE_CURRENT_BINARY_DIR}/RobloxCreatorStudioConfigVersion.cmake"
    DESTINATION lib/cmake/RobloxCreatorStudio
)

# Documentation
find_package(Doxygen)
if(DOXYGEN_FOUND)
    set(DOXYGEN_IN ${CMAKE_CURRENT_SOURCE_DIR}/docs/Doxyfile.in)
    set(DOXYGEN_OUT ${CMAKE_CURRENT_BINARY_DIR}/Doxyfile)
    
    configure_file(${DOXYGEN_IN} ${DOXYGEN_OUT} @ONLY)
    
    add_custom_target(docs ALL
        COMMAND ${DOXYGEN_EXECUTABLE} ${DOXYGEN_OUT}
        WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
        COMMENT "Generating API documentation with Doxygen"
        VERBATIM
    )
endif()

# Print configuration summary
message(STATUS "Roblox Creator Studio Configuration:")
message(STATUS "  Version: ${PROJECT_VERSION}")
message(STATUS "  Author: ${PROJECT_AUTHOR}")
message(STATUS "  C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  Build Type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  Install Prefix: ${CMAKE_INSTALL_PREFIX}")
message(STATUS "  OpenGL: ${OPENGL_LIBRARIES}")
message(STATUS "  GLFW: ${GLFW_LIBRARIES}")
message(STATUS "  GLM: ${GLM_INCLUDE_DIRS}")
message(STATUS "  Assimp: ${ASSIMP_LIBRARIES}")
message(STATUS "  OpenAL: ${OPENAL_LIBRARY}")
if(Python3_FOUND)
    message(STATUS "  Python: ${Python3_VERSION}")
    message(STATUS "  Python Bindings: Enabled")
else()
    message(STATUS "  Python Bindings: Disabled")
endif()
if(DOXYGEN_FOUND)
    message(STATUS "  Documentation: Enabled")
else()
    message(STATUS "  Documentation: Disabled")
endif()
