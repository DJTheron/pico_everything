# pico_everything (C++ port) — Raspberry Pi Pico 2 W
cmake_minimum_required(VERSION 3.13)

# Board must be chosen before the SDK is imported. Default to the Pico 2 W
# (RP2350 + CYW43); override with -DPICO_BOARD=... if needed.
if(NOT DEFINED PICO_BOARD)
    set(PICO_BOARD pico2_w)
endif()

# Pulls the SDK source into this build tree by locating $PICO_SDK_PATH.
include(pico_sdk_import.cmake)

project(pico_everything C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

pico_sdk_init()

add_executable(pico_everything
    main.cpp
    lib/st7789.cpp
    lib/canvas.cpp
    lib/font.cpp
    lib/input.cpp
    lib/wifi.cpp
    apps/stopwatch.cpp
    apps/picotello/picotello.cpp
    apps/picotello/tello.cpp
    apps/picotello/hud.cpp
    apps/picotello/control.cpp
)

target_include_directories(pico_everything PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}                      # project root: lib/..., lwipopts.h
    ${CMAKE_CURRENT_LIST_DIR}/apps/picotello       # tello.h / hud.h from the app
)

target_link_libraries(pico_everything
    pico_stdlib
    hardware_spi
    hardware_dma
    hardware_pwm
    pico_cyw43_arch_lwip_threadsafe_background      # WiFi + lwIP (UDP) for the Tello link
)

# Debug over USB serial (replaces the MicroPython REPL). See picotool/minicom.
pico_enable_stdio_usb(pico_everything 1)
pico_enable_stdio_uart(pico_everything 0)

# Produce .uf2 (+ .bin/.hex/.dis/.elf.map) for drag-and-drop flashing.
pico_add_extra_outputs(pico_everything)
