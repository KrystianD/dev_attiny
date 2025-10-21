# set TOOLCHAIN_PATH and PACK_PATH
include(local_paths.cmake)


find_program(AVR_CC ${TOOLCHAIN_PATH}/bin/avr-gcc)
find_program(AVR_CXX ${TOOLCHAIN_PATH}/bin/avr-g++)
find_program(AVR_OBJCOPY ${TOOLCHAIN_PATH}/bin/avr-objcopy)
find_program(AVR_SIZE_TOOL ${TOOLCHAIN_PATH}/bin/avr-size)
find_program(AVR_OBJDUMP ${TOOLCHAIN_PATH}/bin/avr-objdump)

set(CMAKE_SYSTEM_NAME Generic)
set(CMAKE_SYSTEM_PROCESSOR avr)
set(CMAKE_C_COMPILER ${AVR_CC})
set(CMAKE_CXX_COMPILER ${AVR_CXX})
set(CMAKE_C_COMPILER_WORKS 1)
set(CMAKE_CXX_COMPILER_WORKS 1)
