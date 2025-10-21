#if __AVR_DEV_LIB_NAME__ == tn414
#include <defines_attiny1624.h>
#elif __AVR_DEV_LIB_NAME__ == tn424
#include <defines_attiny1626.h>
#else
#error Unsupported device type
#endif

#include <avr/common.h>
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>