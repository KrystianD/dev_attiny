set(DEV_DIR ${CMAKE_CURRENT_LIST_DIR})

include(${DEV_DIR}/devices.cmake)

set(DEVPACK_PATH ${PACK_PATH}/gcc/dev/${ATTINY_DEVICE}/)
add_link_options(-B ${DEVPACK_PATH})
add_compile_options(-B ${DEVPACK_PATH} -I ${PACK_PATH}/include)

include_directories(${CMAKE_CURRENT_LIST_DIR}/components)

set(common_compile_flags "-mmcu=${AVR_MCU} -fdata-sections -ffunction-sections")
set(common_linker_flags "-mmcu=${AVR_MCU} -Wl,--relax,--gc-sections -Wl,--gc-sections")

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${common_compile_flags}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${common_compile_flags} -Wno-reorder -fpermissive -std=c++17")

set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} ${common_linker_flags}")

set(CMAKE_CXX_FLAGS_DEBUG "-Os")
set(CMAKE_CXX_FLAGS_RELEASE "-Os")
set(CMAKE_CXX_FLAGS_RELWITHDEBINFO "-Os -ggdb")

function(add_avr_executable EXECUTABLE_NAME)
    if(NOT ARGN)
        message(FATAL_ERROR "No source files given for ${EXECUTABLE_NAME}.")
    endif(NOT ARGN)

    # set file names
    set(elf_file ${EXECUTABLE_NAME}.elf)
    set(lst_file ${EXECUTABLE_NAME}.lst)
    set(bin_file ${EXECUTABLE_NAME}.bin)
    set(hex_file ${EXECUTABLE_NAME}.hex)
    set(map_file ${EXECUTABLE_NAME}.map)
    set(eeprom_image ${EXECUTABLE_NAME}-eeprom.hex)

    set(common_linker_flags "-Wl,--relax,--gc-sections -Wl,--gc-sections")

    # Normal
    add_executable(${elf_file} EXCLUDE_FROM_ALL ${ARGN})
    set_target_properties(${elf_file} PROPERTIES FOLDER HiddenTargets)
    set_target_properties(
            ${elf_file}
            PROPERTIES
            COMPILE_FLAGS ""
            LINK_FLAGS "-Wl,-Map,${map_file}"
    )

    add_custom_command(
            TARGET ${elf_file}
            POST_BUILD
            COMMAND ${AVR_SIZE_TOOL} --mcu=${AVR_MCU} ${elf_file})

    add_custom_command(
            TARGET ${elf_file}
            POST_BUILD
            BYPRODUCTS ${hex_file}
            COMMAND ${AVR_OBJCOPY} -j .text -j .data -j .rodata -O ihex ${elf_file} ${hex_file}
    )

    add_custom_command(
            TARGET ${elf_file}
            POST_BUILD
            BYPRODUCTS ${lst_file}
            COMMAND ${AVR_OBJDUMP} -S ${elf_file} > ${lst_file}
    )

    add_custom_command(
            TARGET ${elf_file}
            POST_BUILD
            BYPRODUCTS ${bin_file}
            COMMAND ${AVR_OBJCOPY} -j .text -j .data -j .rodata -O binary ${elf_file} ${bin_file}
    )

#    # eeprom
#    add_custom_command(
#            OUTPUT ${eeprom_image}
#            COMMAND ${AVR_OBJCOPY} -j .eeprom --set-section-flags=.eeprom=alloc,load
#            --change-section-lma .eeprom=0 --no-change-warnings
#            -O ihex ${elf_file} ${eeprom_image}
#            DEPENDS ${elf_file}
#    )

    # clean
    get_directory_property(clean_files ADDITIONAL_MAKE_CLEAN_FILES)
    set_directory_properties(
            PROPERTIES
            ADDITIONAL_MAKE_CLEAN_FILES "${map_file}"
    )

    # all target
    add_custom_target(${EXECUTABLE_NAME} ALL DEPENDS ${hex_file} ${hex_file_crc} ${lst_file} ${bin_file})
    set_target_properties(${EXECUTABLE_NAME} PROPERTIES OUTPUT_NAME "${elf_file}")

    get_filename_component(hex_file_abs ${hex_file} ABSOLUTE BASE_DIR "${CMAKE_BINARY_DIR}")

    # upload - with avrdude
    add_custom_target(
            upload_${EXECUTABLE_NAME}
            ${DEV_DIR}/scripts/flash ${hex_file_abs} ${ATTINY_DEVICE} ${FLASHER_PORT}
            DEPENDS ${hex_file}
            COMMENT "Uploading ${hex_file} to ${AVR_MCU} using ${AVR_PROGRAMMER}"
    )
endfunction(add_avr_executable)


##########################################################################
# add_avr_library
# - IN_VAR: LIBRARY_NAME
#
# Calls add_library with an optionally concatenated name
# <LIBRARY_NAME>.
# This needs to be used for linking against the library, e.g. calling
# target_link_libraries(...).
##########################################################################
function(add_avr_library LIBRARY_NAME)
    if(NOT ARGN)
        message(FATAL_ERROR "No source files given for ${LIBRARY_NAME}.")
    endif(NOT ARGN)

    set(lib_file ${LIBRARY_NAME})

    add_library(${lib_file} STATIC ${ARGN})

    set_target_properties(
            ${lib_file}
            PROPERTIES
            COMPILE_FLAGS "-mmcu=${AVR_MCU} -fdata-sections -ffunction-sections"
            OUTPUT_NAME "${lib_file}"
    )

    if(NOT TARGET ${LIBRARY_NAME})
        add_custom_target(
                ${LIBRARY_NAME}
                ALL
                DEPENDS ${lib_file}
        )

        set_target_properties(
                ${LIBRARY_NAME}
                PROPERTIES
                OUTPUT_NAME "${lib_file}"
        )
    endif(NOT TARGET ${LIBRARY_NAME})

endfunction(add_avr_library)

##########################################################################
# avr_target_link_libraries
# - IN_VAR: EXECUTABLE_TARGET
# - ARGN  : targets and files to link to
#
# Calls target_link_libraries with AVR target names (concatenation,
# extensions and so on.
##########################################################################
function(avr_target_link_libraries EXECUTABLE_TARGET)
    if(NOT ARGN)
        message(FATAL_ERROR "Nothing to link to ${EXECUTABLE_TARGET}.")
    endif(NOT ARGN)

    get_target_property(TARGET_LIST ${EXECUTABLE_TARGET} OUTPUT_NAME)

    foreach(TGT ${ARGN})
        if(TARGET ${TGT})
            get_property(ARG_NAME TARGET ${TGT} PROPERTY OUTPUT_NAME)
            if(DEFINED(ARG_NAME))
                list(APPEND NON_TARGET_LIST ${ARG_NAME})
            else()
                list(APPEND NON_TARGET_LIST ${TGT})
            endif()
        else()
            list(APPEND NON_TARGET_LIST ${TGT})
        endif()
    endforeach(TGT ${ARGN})

    target_link_libraries(${TARGET_LIST} ${NON_TARGET_LIST})
endfunction(avr_target_link_libraries EXECUTABLE_TARGET)

##########################################################################
# avr_target_include_directories
#
# Calls target_include_directories with AVR target names
##########################################################################

function(avr_target_include_directories EXECUTABLE_TARGET)
    if(NOT ARGN)
        message(FATAL_ERROR "No include directories to add to ${EXECUTABLE_TARGET}.")
    endif()

    get_target_property(TARGET_LIST ${EXECUTABLE_TARGET} OUTPUT_NAME)
    set(extra_args ${ARGN})

    target_include_directories(${TARGET_LIST} ${extra_args})
endfunction()

function(avr_target_sources EXECUTABLE_TARGET)
    if(NOT ARGN)
        message(FATAL_ERROR "No source files to add to ${EXECUTABLE_TARGET}.")
    endif()

    get_target_property(TARGET_LIST ${EXECUTABLE_TARGET} OUTPUT_NAME)
    set(extra_args ${ARGN})

    target_sources(${TARGET_LIST} ${extra_args})
endfunction()

##########################################################################
# avr_target_compile_definitions
#
# Calls target_compile_definitions with AVR target names
##########################################################################

function(avr_target_compile_definitions EXECUTABLE_TARGET)
    if(NOT ARGN)
        message(FATAL_ERROR "No compile definitions to add to ${EXECUTABLE_TARGET}.")
    endif()

    get_target_property(TARGET_LIST ${EXECUTABLE_TARGET} OUTPUT_NAME)
    target_compile_definitions(${TARGET_LIST} ${ARGN})
endfunction()
