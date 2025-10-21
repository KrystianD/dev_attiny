#pragma once

#include <avr/io.h>
#include <avr/common.h>

#include <stdint.h>

#include <kdevice.h>

template<uint16_t I2C>
class kI2C
{
	static constexpr TWI_t* Device() { return reinterpret_cast<TWI_t*>(I2C); }

public:
	// void put(char c)
	// {
	// 	// loop_until_bit_is_set(Device()->STATUS, USART_DREIF_bp);
	// 	//
	// 	// Device()->TXDATAL = c;
	// }
	//
	// char get()
	// {
	// 	// while (bit_is_clear(UCSRA, RXC));
	//
	// 	return 0;
	// }
};
